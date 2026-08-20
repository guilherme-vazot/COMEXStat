# COMEXStat

Pipeline Docker do comércio exterior brasileiro. Baixa CSVs do COMEXSTAT/MDIC, ingere em DuckDB e oferece notebook de consultas com visualizações em pandas.

## Início Rápido

```bash
# Docker
docker compose build
docker compose up comexstat
# Acessar http://localhost:8888

# Docker pipeline (baixa dados + ingeri no banco)
docker compose run pipeline --start 2023 --end 2026 --type both --engine duckdb --tables

# Local
pip install -r requirements.txt
python pipeline.py -s 2023 -e 2026 -E duckdb --tables
```

## O que faz

1. **Download** — Baixa CSVs de exportação e importação do MDIC
2. **Ingestão** — Carrega dados no DuckDB (ou SQLite)
3. **Referência** — Tabelas auxiliares: NCM, País, UF, Via, URF, blocos econômicos
4. **Análise** — Notebook com queries e gráficos em pandas

## Estrutura

```
├── pipeline.py        # Download + ingestão
├── download.py        # Módulo de download
├── entrypoint.sh      # Docker entrypoint
├── tutorial.ipynb     # Notebook de consultas
├── data/              # CSVs brutos (gerado)
├── tabelas/           # Tabelas de referência (gerado)
└── db/                # Banco DuckDB (gerado)
```

## Comandos

```bash
# Pipeline completo
python pipeline.py -s 2023 -e 2026 -E duckdb --tables

# Só download
python download.py -s 2023 -e 2026

# Docker pipeline
docker compose run pipeline --start 2023 --end 2026 --type both --engine duckdb --tables
```

## Fonte dos Dados

[COMEXSTAT - MDIC](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta)

## Ferramentas

- **DuckDB** — banco colunar para análises
- **Pandas** — manipulação e visualização
- **Docker** — reprodutibilidade

---

*Projeto desenvolvido com auxílio do [opencode](https://opencode.ai), um assistente de programação por IA.*
