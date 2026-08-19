# COMEXSTAT - Tutorial Completo

Pipeline automatizada para download e analise dos dados de comercio exterior brasileiro
fonte: https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta

---

## 1. Estrutura do Projeto

```
COMEXStat/
├── download.py          # Modulo de download dos CSVs
├── pipeline.py          # Pipeline: download + ingestao no banco
├── entrypoint.sh        # Entry point do Docker (Jupyter ou Pipeline)
├── Dockerfile           # Container Jupyter + dependencias
├── docker-compose.yml   # Orquestracao do container
├── requirements.txt     # Dependencias Python
├── tutorial.ipynb       # Notebook de consultas com DuckDB + pandas
├── developer_agent.md   # Contexto do projeto para agentes
├── data/                # CSVs baixados (gerado automaticamente)
│   ├── EXP_2023.csv
│   ├── IMP_2023.csv
│   └── ...
├── tabelas/             # Tabelas de referencia (gerado automaticamente)
│   ├── NCM.csv
│   ├── NCM_SH.csv
│   ├── NCM_CUCI.csv
│   ├── NCM_ISIC.csv
│   ├── NCM_CGCE.csv
│   ├── PAIS.csv
│   ├── PAIS_BLOCO.csv
│   ├── UF.csv
│   ├── UF_MUN.csv
│   ├── VIA.csv
│   └── URF.csv
└── db/                  # Banco de dados (gerado automaticamente)
    ├── comexstat.db     # SQLite
    └── comexstat.duckdb # DuckDB
```

---

## 2. Instalacao

### Opcao A: Ambiente local

```bash
# Clonar o repositorio
git clone https://github.com/guilherme-vazot/COMEXStat.git
cd COMEXStat

# Instalar dependencias
pip install -r requirements.txt
```

### Opcao B: Docker (recomendado)

```bash
# Instalar Docker (Ubuntu/Debian)
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
# Fazer logout/login

# Build e executar
cd COMEXStat
docker compose build
docker compose up comexstat
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
# Dados + tabelas de referencia (NCM, SH, CUCI, ISIC, CGCE, PAIS, UF, VIA, etc.)
python pipeline.py -s 2023 -e 2025 --tables

# Dados + tabelas, DuckDB
python pipeline.py -s 2023 -e 2025 -E duckdb --tables
```

### 3.3 So download (sem ingestao)

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
| `CO_ANO` | INTEGER | Ano |
| `CO_MES` | INTEGER | Mes |
| `CO_NCM` | VARCHAR | Codigo NCM |
| `CO_UNID` | INTEGER | Codigo da unidade |
| `CO_PAIS` | INTEGER | Codigo do pais |
| `SG_UF_NCM` | VARCHAR | Sigla da UF |
| `CO_VIA` | INTEGER | Codigo da via |
| `CO_URF` | VARCHAR | Codigo da URF |
| `QT_ESTAT` | DOUBLE | Quantidade estatistica |
| `KG_LIQUIDO` | DOUBLE | Peso liquido (kg) |
| `VL_FOB` | DOUBLE | Valor FOB (USD) |
| `file_year` | INTEGER | Ano do arquivo original |

### 5.2 Tabelas de referencia

| Tabela | Registros | Descricao |
|--------|-----------|-----------|
| `ncm` | ~13.700 | Nomenclatura Comum do Mercosul |
| `ncm_sh` | ~6.600 | NCM x Sistema Harmonizado |
| `ncm_cuci` | ~2.900 | NCM x CUCI |
| `ncm_isic` | ~420 | NCM x ISIC |
| `ncm_cgce` | ~19 | NCM x CGCE |
| `pais` | 281 | Paises (codigo, nome PT/EN/ES) |
| `pais_bloco` | 324 | Pais x bloco economico |
| `uf` | 34 | Unidades federativas |
| `uf_mun` | 5.570 | Municipios |
| `via` | 17 | Vias de transporte |
| `urf` | 281 | Unidades da Receita Federal |

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

### 6.1 DuckDB

```python
import duckdb

conn = duckdb.connect("db/comexstat.duckdb")

# Total por ano
df = conn.execute("""
    SELECT CO_ANO, SUM(VL_FOB) as total_fob
    FROM exp
    GROUP BY CO_ANO
    ORDER BY CO_ANO
""").df()

# Top 10 UFs por exportacao
df = conn.execute("""
    SELECT SG_UF_NCM, SUM(VL_FOB) as total_fob
    FROM exp
    WHERE CO_ANO = 2024
    GROUP BY SG_UF_NCM
    ORDER BY total_fob DESC
    LIMIT 10
""").df()
```

### 6.2 JOIN com tabelas de referencia

```python
# Exportacao com descricao NCM
df = conn.execute("""
    SELECT
        e.CO_ANO,
        e.CO_NCM,
        n.NO_NCM_POR as descricao,
        e.VL_FOB
    FROM exp e
    LEFT JOIN ncm n ON e.CO_NCM = n.CO_NCM
    WHERE e.CO_ANO = 2024
    ORDER BY e.VL_FOB DESC
    LIMIT 20
""").df()

# Exportacao por secao SH
df = conn.execute("""
    SELECT
        sh.NO_SEC_POR as secao,
        SUM(e.VL_FOB) as total_fob
    FROM exp e
    LEFT JOIN ncm n ON e.CO_NCM = n.CO_NCM
    LEFT JOIN ncm_sh sh ON n.CO_SH6 = sh.CO_SH6
    WHERE e.CO_ANO = 2024
    GROUP BY sh.NO_SEC_POR
    ORDER BY total_fob DESC
""").df()
```

### 6.3 JOIN com pais e via

```python
# Top parceiros comerciais
df = conn.execute("""
    SELECT
        p.NO_PAIS AS pais,
        SUM(e.VL_FOB) AS total_fob
    FROM exp e
    LEFT JOIN pais p ON e.CO_PAIS = p.CO_PAIS
    WHERE e.CO_ANO = 2024
    GROUP BY p.NO_PAIS
    ORDER BY total_fob DESC
    LIMIT 10
""").df()

# Exportacao por via de transporte
df = conn.execute("""
    SELECT
        v.NO_VIA AS via,
        SUM(e.VL_FOB) AS total_fob
    FROM exp e
    LEFT JOIN via v ON e.CO_VIA = v.CO_VIA
    WHERE e.CO_ANO = 2024
    GROUP BY v.NO_VIA
    ORDER BY total_fob DESC
""").df()
```

### 6.4 DuckDB lendo CSV direto (sem pipeline)

```python
import duckdb

conn = duckdb.connect()

# Ler CSV direto
df = conn.execute("""
    SELECT * FROM read_csv_auto('./data/EXP_2025.csv', delim=';', header=true)
    LIMIT 10
""").df()
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
""").df()

plt.figure(figsize=(10, 6))
plt.bar(df["CO_MES"], df["total_fob"] / 1e9)
plt.xlabel("Mes")
plt.ylabel("Valor FOB (bilhoes USD)")
plt.title("Exportacoes Brasileiras - 2024")
plt.xticks(range(1, 13))
plt.tight_layout()
plt.show()
```

---

## 8. Uso como Modulo

### Funcoes disponiveis

```python
from download import download_comexstat, download_tables
from pipeline import run_pipeline, init_db, ingest_csv, ingest_tables
```

### Exemplo: rodar pipeline programaticamente

```python
from pipeline import run_pipeline

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
```

---

## 9. Docker

### Comandos

```bash
# Jupyter (padrao)
docker compose up comexstat
# Acessar http://localhost:8888

# Pipeline
docker compose run pipeline --start 2023 --end 2026 --type both --engine duckdb --tables

# Shell interativo
docker compose run --entrypoint bash comexstat
```

### Persistencia

Os volumes `./data` e `./db` sao montados no container:
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
| `balanca.mdic.gov.br/balanca/bd/tabelas/PAIS.csv` | Paises |
| `balanca.mdic.gov.br/balanca/bd/tabelas/PAIS_BLOCO.csv` | Paises x Blocos |
| `balanca.mdic.gov.br/balanca/bd/tabelas/UF.csv` | Unidades Federativas |
| `balanca.mdic.gov.br/balanca/bd/tabelas/UF_MUN.csv` | Municipios |
| `balanca.mdic.gov.br/balanca/bd/tabelas/VIA.csv` | Vias de Transporte |
| `balanca.mdic.gov.br/balanca/bd/tabelas/URF.csv` | Unidades da RF |

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
