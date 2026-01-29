# Teste Técnico - Intuitive Care

Este projeto implementa um pipeline de dados para coleta e processamento das Demonstrações Contábeis disponibilizadas pela ANS (Agência Nacional de Saúde Suplementar).

O foco inicial é automatizar o acesso aos dados públicos, garantindo uma solução organizada e resiliente a mudanças na estrutura do site.

## Estrutura do Projeto

- **`ingestion/`**  
  Scripts responsáveis por acessar o site da ANS e realizar o download automatizado dos arquivos.

- **`data/raw/`**  
  Diretório local onde os arquivos ZIP brutos são armazenados.  
  Esse diretório é ignorado pelo Git.

- **`docs/`**  
  Documentação das decisões técnicas e trade-offs adotados no projeto.

## Pré-requisitos

- Python 3.10 ou superior  
- Gerenciador de pacotes `pip`

## Como Executar

### 1. Instalação das dependências

Na raiz do projeto, execute:

```bash
pip install -r requirements.txt
