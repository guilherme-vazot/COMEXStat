import argparse
import os
import sys

import pandas as pd

from download import download_comexstat, download_tables, REFERENCE_TABLES

DEFAULT_DB_DIR = "./db"

SQLITE_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS {table} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    CO_ANO INTEGER,
    CO_MES INTEGER,
    CO_NCM TEXT,
    CO_UNID INTEGER,
    CO_PAIS INTEGER,
    SG_UF_NCM TEXT,
    CO_VIA INTEGER,
    CO_URF TEXT,
    QT_ESTAT REAL,
    KG_LIQUIDO REAL,
    VL_FOB REAL,
    file_year INTEGER
);
"""

SQLITE_INSERT = """
INSERT INTO {table} (
    CO_ANO, CO_MES, CO_NCM, CO_UNID, CO_PAIS,
    SG_UF_NCM, CO_VIA, CO_URF, QT_ESTAT, KG_LIQUIDO, VL_FOB, file_year
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

DUCKDB_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS {table} (
    CO_ANO INTEGER,
    CO_MES INTEGER,
    CO_NCM VARCHAR,
    CO_UNID INTEGER,
    CO_PAIS INTEGER,
    SG_UF_NCM VARCHAR,
    CO_VIA INTEGER,
    CO_URF VARCHAR,
    QT_ESTAT DOUBLE,
    KG_LIQUIDO DOUBLE,
    VL_FOB DOUBLE,
    file_year INTEGER
);
"""

CSV_COLUMNS = [
    "CO_ANO", "CO_MES", "CO_NCM", "CO_UNID", "CO_PAIS",
    "SG_UF_NCM", "CO_VIA", "CO_URF", "QT_ESTAT", "KG_LIQUIDO", "VL_FOB",
]

TABLE_NAME_MAP = {
    "NCM": "ncm",
    "NCM_SH": "ncm_sh",
    "NCM_CUCI": "ncm_cuci",
    "NCM_ISIC": "ncm_isic",
    "NCM_CGCE": "ncm_cgce",
    "PAIS": "pais",
    "PAIS_BLOCO": "pais_bloco",
    "UF": "uf",
    "UF_MUN": "uf_mun",
    "VIA": "via",
    "URF": "urf",
}


def _get_db_path(engine: str) -> str:
    ext = "duckdb" if engine == "duckdb" else "db"
    return os.path.join(DEFAULT_DB_DIR, f"comexstat.{ext}")


def init_db(engine: str, db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if engine == "duckdb":
        import duckdb
        conn = duckdb.connect(db_path)
        for table in ("exp", "imp"):
            conn.execute(DUCKDB_CREATE_TABLE.format(table=table))
        return conn
    else:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        for table in ("exp", "imp"):
            cur.execute(SQLITE_CREATE_TABLE.format(table=table))
        conn.commit()
        return conn


def table_count(conn, engine: str, table: str) -> int:
    if engine == "duckdb":
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    else:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def ingest_csv(conn, engine: str, filepath: str, table: str, verbose: bool) -> int:
    if verbose:
        print(f"  lendo {os.path.basename(filepath)} ...", end=" ", flush=True)

    if engine == "duckdb":
        count = conn.execute(f"""
            INSERT INTO {table}
            SELECT
                CAST("CO_ANO" AS INTEGER),
                CAST("CO_MES" AS INTEGER),
                "CO_NCM"::VARCHAR,
                CAST("CO_UNID" AS INTEGER),
                CAST("CO_PAIS" AS INTEGER),
                "SG_UF_NCM"::VARCHAR,
                CAST("CO_VIA" AS INTEGER),
                "CO_URF"::VARCHAR,
                CAST("QT_ESTAT" AS DOUBLE),
                CAST("KG_LIQUIDO" AS DOUBLE),
                CAST("VL_FOB" AS DOUBLE),
                CAST("CO_ANO" AS INTEGER) AS file_year
            FROM read_csv_auto('{filepath}', delim=';', header=true)
        """).fetchone()[0]
        conn.commit()
        if verbose:
            print(f"{count} registros")
        return count
    else:
        df = pd.read_csv(filepath, sep=";", dtype=str)
        df.columns = [c.strip().strip('"') for c in df.columns]

        for col in ["CO_ANO", "CO_MES", "CO_UNID", "CO_PAIS", "CO_VIA", "CO_URF"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        for col in ["QT_ESTAT", "KG_LIQUIDO", "VL_FOB"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        year = int(df["CO_ANO"].mode().iloc[0]) if not df.empty else 0
        df["file_year"] = year

        rows = df[CSV_COLUMNS + ["file_year"]].values.tolist()
        conn.executemany(SQLITE_INSERT.format(table=table), rows)
        conn.commit()
        if verbose:
            print(f"{len(rows)} registros")
        return len(rows)


def ingest_tables(
    conn, engine: str, data_dir: str = "./data/tabelas", verbose: bool = True,
) -> dict[str, int]:
    tables_dir = os.path.join(os.path.dirname(data_dir.rstrip("/")), "tabelas")
    results: dict[str, int] = {}

    if verbose:
        print(f"\n=== ETAPA 3: Tabelas de Referencia ===")

    download_results = download_tables(output_dir=tables_dir, verbose=verbose)

    for csv_name, table_name in TABLE_NAME_MAP.items():
        filepath = os.path.join(tables_dir, f"{csv_name}.csv")
        if not os.path.exists(filepath):
            continue

        if verbose:
            print(f"  lendo {csv_name}.csv -> {table_name} ...", end=" ", flush=True)

        if engine == "duckdb":
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.execute(f"""
                CREATE TABLE {table_name} AS
                SELECT * FROM read_csv_auto('{filepath}', delim=';', header=true, encoding='latin-1', strict_mode=false, ignore_errors=true)
            """)
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        else:
            df = pd.read_csv(filepath, sep=";", dtype=str, encoding="latin-1")
            df.columns = [c.strip().strip('"') for c in df.columns]
            count = len(df)
            df.to_sql(table_name, conn, if_exists="replace", index=False)

        conn.commit()
        if verbose:
            print(f"{count} registros")
        results[csv_name] = count

    return results


def run_pipeline(
    start: int,
    end: int,
    types: list[str],
    engine: str = "sqlite",
    data_dir: str = "./data",
    db_path: str | None = None,
    verbose: bool = True,
    include_tables: bool = False,
) -> dict:
    if db_path is None:
        db_path = _get_db_path(engine)

    if verbose:
        print("=== ETAPA 1: Download ===")
    download_results = download_comexstat(
        start=start, end=end, types=types,
        output_dir=data_dir, verbose=verbose,
    )

    if verbose:
        print(f"\n=== ETAPA 2: Ingestao {engine.upper()} ===")
    conn = init_db(engine, db_path)
    type_to_table = {"EXP": "exp", "IMP": "imp"}
    ingest_results: dict[str, int] = {}

    for file_type in types:
        table = type_to_table[file_type]
        before = table_count(conn, engine, table)
        for year in range(start, end + 1):
            filename = f"{file_type}_{year}.csv"
            filepath = os.path.join(data_dir, filename)
            if not os.path.exists(filepath):
                continue
            count = ingest_csv(conn, engine, filepath, table, verbose)
            ingest_results[filename] = count

        after = table_count(conn, engine, table)
        if verbose:
            print(f"  tabela '{table}': {before} -> {after} registros (+{after - before})")

    conn.close()

    if include_tables:
        conn = init_db(engine, db_path)
        ingest_tables(conn, engine, data_dir=data_dir, verbose=verbose)
        conn.close()

    return {"downloads": download_results, "ingested": ingest_results}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pipeline COMEXSTAT: download CSV + ingestao em SQLite ou DuckDB.",
    )
    parser.add_argument("--start", "-s", type=int, required=True, help="Ano inicial.")
    parser.add_argument("--end", "-e", type=int, required=True, help="Ano final.")
    parser.add_argument(
        "--type", "-t", default="both", choices=["exp", "imp", "both"],
        help="Tipo: exp, imp ou both (padrao: both).",
    )
    parser.add_argument(
        "--engine", "-E", default="sqlite", choices=["sqlite", "duckdb"],
        help="Banco de dados: sqlite ou duckdb (padrao: sqlite).",
    )
    parser.add_argument("--output", "-o", default="./data", help="Dir de CSVs.")
    parser.add_argument("--db", default=None, help="Caminho do banco (auto se omitido).")
    parser.add_argument(
        "--tables", action="store_true",
        help="Ingerir tabelas de referencia (NCM, SH, CUCI, ISIC, CGCE).",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Silencioso.")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.start > args.end:
        parser.error("start deve ser <= end")

    type_map = {"exp": ["EXP"], "imp": ["IMP"], "both": ["EXP", "IMP"]}
    types = type_map[args.type]
    db_path = args.db or _get_db_path(args.engine)

    print(f"COMEXSTAT Pipeline — {args.start}-{args.end}, tipos={types}")
    print(f"Engine: {args.engine}")
    print(f"CSVs:  {os.path.abspath(args.output)}")
    print(f"DB:    {os.path.abspath(db_path)}")
    print()

    results = run_pipeline(
        start=args.start,
        end=args.end,
        types=types,
        engine=args.engine,
        data_dir=args.output,
        db_path=db_path,
        verbose=not args.quiet,
        include_tables=args.tables,
    )

    ingested = sum(results["ingested"].values())
    print(f"\nPronto: {ingested} registros inseridos.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
