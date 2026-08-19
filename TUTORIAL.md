# COMEXSTAT - Tutorial Completo

Pipeline automatizada para download e analise dos dados de comercio exterior brasileiro
fonte: https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta

---

## 1. Estrutura do Projeto

```
COMEXStat/
├── download.py          # Modulo de download dos CSVs
├── pipeline.py          # Pipeline: download + ingestao no banco
├── Dockerfile           # Container Jupyter + dependencias
├── docker-compose.yml   # Orquestracao do container
├── requirements.txt     # Dependencias Python
├── data/                # CSVs baixados (gerado automaticamente)
│   ├── EXP_2023.csv
│   ├── EXP_2024.csv
│   ├── ...
│   └── tabelas/         # Tabelas de referencia
│       ├── NCM.csv
│       ├── NCM_SH.csv
│       ├── NCM_CUCI.csv
│       ├── NCM_ISIC.csv
│       └── NCM_CGCE.csv
└── db/                  # Banco de dados (gerado automaticamente)
    ├── comexstat.db     # SQLite
    └── comexstat.duckdb # DuckDB
```

---

## 2. Instalacao

### Opcao A: Ambiente local

```bash
# Clonar o repositorio
git clone <url-do-repo>
cd COMEXStat

# Instalar dependencias
pip install -r requirements.txt
```

### Opcao B: Docker (recomendado para reprodutibilidade)

```bash
# Instalar Docker (Ubuntu/Debian)
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
# Fazer logout/login

# Build e executar
cd COMEXStat
docker compose build
docker compose up
# Acessar http://localhost:8888
```

---

## 3. Comandos do Pipeline

### 3.1 Download + Ingestao (completo)

```bash
# Exportacao + Importacao, 2023-2025, SQLite (padrao)
python pipeline.py -s 2023 -e 2025

# Exportacao + Importacao, 2023-2025, DuckDB
python pipeline.py -s 2023 -e 2025 -E duckdb

# Apenas exportacao
python pipeline.py -s 2023 -e 2025 -t exp

# Apenas importacao
python pipeline.py -s 2023 -e 2025 -t imp
```

### 3.2 Com tabelas de referencia

```bash
# Dados + tabelas de referencia (NCM, SH, CUCI, ISIC, CGCE)
python pipeline.py -s 2023 -e 2025 --tables

# Dados + tabelas, DuckDB
python pipeline.py -s 2023 -e 2025 -E duckdb --tables
```

### 3.3 Só download (sem ingestao)

```bash
# Apenas baixar CSVs, sem salvar no banco
python download.py -s 2023 -e 2025
python download.py -s 2023 -e 2025 -t exp
python download.py -s 2023 -e 2025 -t imp
```

### 3.4 Apenas tabelas de referencia

```bash
# Baixar e ingerir so as tabelas de referencia
python pipeline.py -s 1 -e 1 --tables
```

---

## 4. Referencia dos Argumentos

### pipeline.py

| Argumento | Abrev | Valores | Padrao | Descricao |
|-----------|-------|---------|--------|-----------|
| `--start` | `-s` | ano | obrigatorio | Ano inicial |
| `--end` | `-e` | ano | obrigatorio | Ano final |
| `--type` | `-t` | `exp`, `imp`, `both` | `both` | Tipo de dado |
| `--engine` | `-E` | `sqlite`, `duckdb` | `sqlite` | Banco de dados |
| `--tables` | - | flag | false | Ingerir tabelas de referencia |
| `--output` | `-o` | caminho | `./data` | Diretorio dos CSVs |
| `--db` | - | caminho | auto | Caminho do banco |
| `--quiet` | `-q` | flag | false | Modo silencioso |

### download.py

| Argumento | Abrev | Valores | Padrao | Descricao |
|-----------|-------|---------|--------|-----------|
| `--start` | `-s` | ano | obrigatorio | Ano inicial |
| `--end` | `-e` | ano | obrigatorio | Ano final |
| `--type` | `-t` | `exp`, `imp`, `both` | `both` | Tipo de arquivo |
| `--output` | `-o` | caminho | `./data` | Diretorio de saida |
| `--quiet` | `-q` | flag | false | Modo silencioso |

---

## 5. Banco de Dados

### 5.1 Tabelas de dados

| Tabela | Descricao |
|--------|-----------|
| `exp` | Dados de exportacao (todas os anos juntos) |
| `imp` | Dados de importacao (todas os anos juntos) |

Schema das tabelas `exp` e `imp`:

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| `id` | INTEGER | Chave primaria (autoincrement, so SQLite) |
| `CO_ANO` | INTEGER | Ano |
| `CO_MES` | INTEGER | Mes |
| `CO_NCM` | TEXT/VARCHAR | Codigo NCM |
| `CO_UNID` | INTEGER | Codigo da unidade |
| `CO_PAIS` | INTEGER | Codigo do pais |
| `SG_UF_NCM` | TEXT/VARCHAR | Sigla da UF |
| `CO_VIA` | INTEGER | Codigo da via |
| `CO_URF` | TEXT/VARCHAR | Codigo da URF |
| `QT_ESTAT` | REAL/DOUBLE | Quantidade estatistica |
| `KG_LIQUIDO` | REAL/DOUBLE | Peso liquido (kg) |
| `VL_FOB` | REAL/DOUBLE | Valor FOB (USD) |
| `file_year` | INTEGER | Ano do arquivo original |

### 5.2 Tabelas de referencia

| Tabela | Registros | Descricao |
|--------|-----------|-----------|
| `ncm` | ~13.700 | Nomenclatura Comum do Mercosul |
| `ncm_sh` | ~6.600 | NCM x Sistema Harmonizado |
| `ncm_cuci` | ~2.900 | NCM x CUCI |
| `ncm_isic` | ~420 | NCM x ISIC |
| `ncm_cgce` | ~19 | NCM x CGCE |

### 5.3 Escolha do engine

| Caracteristica | SQLite | DuckDB |
|----------------|--------|--------|
| Tipo | Arquivo (.db) | Arquivo (.duckdb) |
| Servidor | Nao | Nao |
| Velocidade | Boa | Muito boa (colunar) |
| Analitico (GROUP BY) | OK | Excelente |
| Integracao Pandas | Excelente | Excelente |
| Uso recomendado | Geral | Analises pesadas |

---

## 6. Exemplos de Consultas

### 6.1 SQLite

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("db/comexstat.db")

# Total por ano
df = pd.read_sql("""
    SELECT CO_ANO, SUM(VL_FOB) as total_fob
    FROM exp
    GROUP BY CO_ANO
    ORDER BY CO_ANO
""", conn)

# Top 10 UFS por exportacao
df = pd.read_sql("""
    SELECT SG_UF_NCM, SUM(VL_FOB) as total_fob
    FROM exp
    WHERE CO_ANO = 2024
    GROUP BY SG_UF_NCM
    ORDER BY total_fob DESC
    LIMIT 10
""", conn)
```

### 6.2 DuckDB

```python
import duckdb

conn = duckdb.connect("db/comexstat.duckdb")

# Total por ano
df = conn.execute("""
    SELECT CO_ANO, SUM(VL_FOB) as total_fob
    FROM exp
    GROUP BY CO_ANO
    ORDER BY CO_ANO
""").fetchdf()

# Top 10 UFS por exportacao
df = conn.execute("""
    SELECT SG_UF_NCM, SUM(VL_FOB) as total_fob
    FROM exp
    WHERE CO_ANO = 2024
    GROUP BY SG_UF_NCM
    ORDER BY total_fob DESC
    LIMIT 10
""").fetchdf()
```

### 6.3 JOIN com tabelas de referencia

```python
import duckdb

conn = duckdb.connect("db/comexstat.duckdb")

# Exportacao com descricao NCM
df = conn.execute("""
    SELECT
        e.CO_ANO,
        e.CO_NCM,
        n.NO_NCM_POR as descricao,
        n.CO_SH6,
        e.VL_FOB
    FROM exp e
    JOIN ncm n ON e.CO_NCM = n.CO_NCM
    WHERE e.CO_ANO = 2024
    ORDER BY e.VL_FOB DESC
    LIMIT 20
""").fetchdf()

# Exportacao por secao SH
df = conn.execute("""
    SELECT
        sh.NO_SEC_POR as secao,
        SUM(e.VL_FOB) as total_fob
    FROM exp e
    JOIN ncm n ON e.CO_NCM = n.CO_NCM
    JOIN ncm_sh sh ON n.CO_SH6 = sh.CO_SH6
    WHERE e.CO_ANO = 2024
    GROUP BY sh.NO_SEC_POR
    ORDER BY total_fob DESC
""").fetchdf()
```

### 6.4 DuckDB lendo CSV direto (sem pipeline)

```python
import duckdb

conn = duckdb.connect()

# Ler CSV direto
df = conn.execute("""
    SELECT * FROM read_csv_auto('./data/EXP_2025.csv', delim=';', header=true)
    LIMIT 10
""").fetchdf()

# Salvar no banco
conn.execute("""
    CREATE TABLE exp AS
    SELECT * FROM read_csv_auto('./data/EXP_2025.csv', delim=';', header=true)
""")
```

---

## 7. Analises com Graficos

```python
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

conn = duckdb.connect("db/comexstat.duckdb")

# Evolucao mensal de exportacoes (2024)
df = conn.execute("""
    SELECT CO_MES, SUM(VL_FOB) as total_fob
    FROM exp
    WHERE CO_ANO = 2024
    GROUP BY CO_MES
    ORDER BY CO_MES
""").fetchdf()

plt.figure(figsize=(10, 6))
plt.bar(df["CO_MES"], df["total_fob"] / 1e9)
plt.xlabel("Mes")
plt.ylabel("Valor FOB (bilhoes USD)")
plt.title("Exportacoes Brasileiras - 2024")
plt.xticks(range(1, 13))
plt.tight_layout()
plt.savefig("exportacoes_2024.png")
plt.show()
```

---

## 8. Uso como Modulo (Pipeline)

### Funcoes disponiveis

```python
from download import download_comexstat, download_tables
from pipeline import run_pipeline, init_db, ingest_csv, ingest_tables
```

### Exemplo: rodar pipeline programaticamente

```python
from pipeline import run_pipeline

# Download + ingestao completo
results = run_pipeline(
    start=2020,
    end=2025,
    types=["EXP", "IMP"],
    engine="duckdb",
    data_dir="./data",
    db_path="./db/comexstat.duckdb",
    verbose=True,
    include_tables=True,
)

print(results["ingested"])
# {"EXP_2020.csv": 1500000, "EXP_2021.csv": 1600000, ...}
```

### Exemplo: so baixar CSVs

```python
from download import download_comexstat

results = download_comexstat(
    start=2023,
    end=2025,
    types=["EXP", "IMP"],
    output_dir="./data",
    verbose=True,
)
```

### Exemplo: so tabelas de referencia

```python
from download import download_tables

results = download_tables(output_dir="./data/tabelas")
```

---

## 9. Docker

### Comandos

```bash
# Build da imagem
docker compose build

# Executar (Jupyter)
docker compose up
# Acessar http://localhost:8888

# Executar pipeline no container
docker compose run comexstat python pipeline.py -s 2023 -e 2025

# Executar com DuckDB
docker compose run comexstat python pipeline.py -s 2023 -e 2025 -E duckdb

# Executar com tabelas de referencia
docker compose run comexstat python pipeline.py -s 2023 -e 2025 --tables
```

### Persistencia

Os volumes `./data` e `./db` sao montados no container, entao:
- CSVs baixados persistem entre execucoes
- Banco de dados persiste entre execucoes

---

## 10. Fontes de Dados

| URL | Conteudo |
|-----|----------|
| `balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_{ano}.csv` | Exportacao por NCM |
| `balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_{ano}.csv` | Importacao por NCM |
| `balanca.mdic.gov.br/balanca/bd/tabelas/NCM.csv` | Tabela NCM |
| `balanca.mdic.gov.br/balanca/bd/tabelas/NCM_SH.csv` | NCM x SH |
| `balanca.mdic.gov.br/balanca/bd/tabelas/NCM_CUCI.csv` | NCM x CUCI |
| `balanca.mdic.gov.br/balanca/bd/tabelas/NCM_ISIC.csv` | NCM x ISIC |
| `balanca.mdic.gov.br/balanca/bd/tabelas/NCM_CGCE.csv` | NCM x CGCE |

---

## 11. Troubleshooting

### Erro de conexao ao baixar
O site da MDIC pode estar instavel. O script trata erros de conexao e timeout.
Execute novamente — arquivos ja baixados serao pulados.

### Erro de encoding no DuckDB
As tabelas de referencia usam encoding `latin-1`. O pipeline ja trata isso automaticamente.

### DuckDB: "Invalid unicode"
Execute com `--tables` novamente — o script usa `strict_mode=false` e `ignore_errors=true`.

### Limpar banco e recomecar
```bash
rm -f db/comexstat.db     # SQLite
rm -f db/comexstat.duckdb  # DuckDB
```
