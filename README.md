# Teste Técnico - Intuitive Care

Este projeto implementa um pipeline de dados para coleta, processamento e consolidação das Demonstrações Contábeis disponibilizadas pela ANS (Agência Nacional de Saúde Suplementar).

O objetivo é automatizar o acesso aos dados públicos da ANS, processar e consolidar as Demonstrações Contábeis dos últimos trimestres disponíveis, aplicando regras de negócio contábeis e gerando arquivos estruturados para análise posterior.

## Estrutura do Projeto

- **`ingestion/`** Scripts responsáveis pelo web scraping no site da ANS e download automatizado dos arquivos ZIP.

- **`processing/`** Scripts de ETL (Extração, Transformação e Carga). Realizam a descompactação, filtragem contábil ("Despesas com Eventos/Sinistros") e consolidação dos dados.
  - `data_processor.py`: Limpeza e consolidação.
  - `data_enrichment.py`: Enriquecimento com dados cadastrais e geração de estatísticas.

- **`sql/`** Scripts SQL para criação do banco de dados e consultas analíticas.
  - `create_tables.sql`: Estrutura das tabelas (DDL).
  - `analytical_queries.sql`: Respostas para as perguntas de negócio (DML).

- **`backend/`** API REST desenvolvida com FastAPI para expor os dados processados.
  - `main.py`: Definição das rotas e inicialização do servidor.
  - `database.py`: Configuração da conexão com o banco de dados.
  - `models.py`: Modelagem das tabelas (SQLAlchemy).

- **`data/`** - **`raw/`**: Armazena os arquivos ZIP brutos baixados (ignorado pelo Git).
  - **`processed/`**: Armazena os CSVs extraídos e os arquivos finais (`consolidado_despesas.csv`, `despesas_agregadas.csv` e `.zip`).

- **`docs/`** Documentação das decisões técnicas e trade-offs adotados no projeto. Também contém a collection do Postman (`api_collection.json`).

- **`main.py`**
  Script orquestrador que executa o pipeline completo (Ingestão + Processamento + Geração de SQL).

- **`db_importer.py`**
  Script utilitário que lê os CSVs processados e gera o arquivo `inserts.sql` para carga no banco de dados.

## Pré-requisitos

- Python 3.10 ou superior  
- Gerenciador de pacotes `pip`
- Banco de Dados PostgreSQL (Recomendado para etapa de SQL e    API)

## Como Executar

### 1. Instalação das dependências

Na raiz do projeto, execute:

```bash
pip install -r requirements.txt