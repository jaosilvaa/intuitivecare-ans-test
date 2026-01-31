# Teste Técnico - Intuitive Care

Este projeto implementa um pipeline de dados para coleta, processamento e consolidação das Demonstrações Contábeis disponibilizadas pela ANS (Agência Nacional de Saúde Suplementar).

O objetivo é automatizar o acesso aos dados públicos, aplicar regras de negócio contábeis e gerar um relatório consolidado pronto para análise.

## Estrutura do Projeto

- **`ingestion/`** Scripts responsáveis pelo web scraping no site da ANS e download automatizado dos arquivos ZIP.

- **`processing/`** Scripts de ETL (Extração, Transformação e Carga). Realizam a descompactação, filtragem contábil ("Despesas com Eventos/Sinistros") e consolidação dos dados.

- **`data/`** - **`raw/`**: Armazena os arquivos ZIP brutos baixados (ignorado pelo Git).
  - **`processed/`**: Armazena os CSVs extraídos e o arquivo final consolidado (`consolidado_despesas.csv` e `.zip`).

- **`docs/`** Documentação das decisões técnicas e trade-offs adotados no projeto.

- **`main.py`**
  Script orquestrador que executa o pipeline completo (Ingestão + Processamento).

## Pré-requisitos

- Python 3.10 ou superior  
- Gerenciador de pacotes `pip`

## Como Executar

### 1. Instalação das dependências

Na raiz do projeto, execute:

```bash
pip install -r requirements.txt