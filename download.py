import argparse
import os
import sys

import requests

BASE_URL = "https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm"
TABLES_URL = "https://balanca.mdic.gov.br/balanca/bd/tabelas"

REFERENCE_TABLES = [
    "NCM", "NCM_SH", "NCM_CUCI", "NCM_ISIC", "NCM_CGCE",
    "PAIS", "PAIS_BLOCO", "UF", "UF_MUN", "VIA", "URF",
]


def download_comexstat(
    start: int,
    end: int,
    types: list[str] | None = None,
    output_dir: str = "./data",
    verbose: bool = True,
) -> dict[str, str]:
    if types is None:
        types = ["EXP", "IMP"]

    os.makedirs(output_dir, exist_ok=True)

    year_range = range(start, end + 1)
    results: dict[str, str] = {}

    for file_type in types:
        for year in year_range:
            filename = f"{file_type}_{year}.csv"
            filepath = os.path.join(output_dir, filename)
            url = f"{BASE_URL}/{filename}"

            if os.path.exists(filepath):
                if verbose:
                    print(f"  skip  {filename} (ja existe)")
                results[filename] = "skip"
                continue

            if verbose:
                print(f"  baixando {filename} ...", end=" ", flush=True)

            try:
                resp = requests.get(url, timeout=120, verify=False)
                resp.raise_for_status()
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                size_mb = len(resp.content) / (1024 * 1024)
                if verbose:
                    print(f"ok ({size_mb:.1f} MB)")
                results[filename] = "ok"
            except requests.exceptions.HTTPError as e:
                if verbose:
                    print(f"erro {e.response.status_code}")
                results[filename] = f"erro: {e.response.status_code}"
            except requests.exceptions.ConnectionError:
                if verbose:
                    print("erro: conexao")
                results[filename] = "erro: conexao"
            except requests.exceptions.Timeout:
                if verbose:
                    print("erro: timeout")
                results[filename] = "erro: timeout"
            except Exception as e:
                if verbose:
                    print(f"erro: {e}")
                results[filename] = f"erro: {e}"

    return results


def download_tables(
    output_dir: str = "./data/tabelas",
    verbose: bool = True,
) -> dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    results: dict[str, str] = {}

    for table_name in REFERENCE_TABLES:
        filename = f"{table_name}.csv"
        filepath = os.path.join(output_dir, filename)
        url = f"{TABLES_URL}/{filename}"

        if os.path.exists(filepath):
            if verbose:
                print(f"  skip  {filename} (ja existe)")
            results[filename] = "skip"
            continue

        if verbose:
            print(f"  baixando {filename} ...", end=" ", flush=True)

        try:
            resp = requests.get(url, timeout=120, verify=False)
            resp.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(resp.content)
            size_mb = len(resp.content) / (1024 * 1024)
            if verbose:
                print(f"ok ({size_mb:.1f} MB)")
            results[filename] = "ok"
        except requests.exceptions.HTTPError as e:
            if verbose:
                print(f"erro {e.response.status_code}")
            results[filename] = f"erro: {e.response.status_code}"
        except requests.exceptions.ConnectionError:
            if verbose:
                print("erro: conexao")
            results[filename] = "erro: conexao"
        except requests.exceptions.Timeout:
            if verbose:
                print("erro: timeout")
            results[filename] = "erro: timeout"
        except Exception as e:
            if verbose:
                print(f"erro: {e}")
            results[filename] = f"erro: {e}"

    return results


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Baixa arquivos CSV do COMEXSTAT (MDIC) por ano.",
    )
    parser.add_argument(
        "--start", "-s",
        type=int,
        required=True,
        help="Ano inicial.",
    )
    parser.add_argument(
        "--end", "-e",
        type=int,
        required=True,
        help="Ano final.",
    )
    parser.add_argument(
        "--type", "-t",
        default="both",
        choices=["exp", "imp", "both"],
        help="Tipo de arquivo: exp, imp ou both (padrao: both).",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./data",
        help="Diretorio de saida (padrao: ./data).",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Modo silencioso.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.start > args.end:
        parser.error("start deve ser <= end")

    type_map = {"exp": ["EXP"], "imp": ["IMP"], "both": ["EXP", "IMP"]}
    types = type_map[args.type]

    print(f"COMEXSTAT Download — {args.start}-{args.end}, tipos={types}")
    print(f"Diretorio: {os.path.abspath(args.output)}")
    print()

    results = download_comexstat(
        start=args.start,
        end=args.end,
        types=types,
        output_dir=args.output,
        verbose=not args.quiet,
    )

    ok = sum(1 for v in results.values() if v == "ok")
    skip = sum(1 for v in results.values() if v == "skip")
    erro = sum(1 for v in results.values() if v.startswith("erro"))

    print()
    print(f"Resumo: {ok} baixados, {skip} pulados, {erro} erros")

    return 1 if erro > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
