# Trade-offs e Decisões Técnicas

## 1.1 Acesso à API de Dados Abertos da ANS

O primeiro desafio foi acessar os arquivos de Demonstrações Contábeis da ANS, organizados em pastas por ano e trimestre. O enunciado do teste indica que essa estrutura pode mudar ao longo do tempo.

Para evitar que o código quebre caso haja alteração nos nomes das pastas, inclusão de novos anos ou mudança na ordem dos arquivos, optei por não utilizar URLs fixas. O script lê o HTML do diretório e identifica dinamicamente os anos disponíveis e os arquivos ZIP em cada pasta.

Essa abordagem torna o processo de ingestão mais robusto e reduz a necessidade de manutenção manual.

O acesso aos dados foi implementado utilizando `requests` e `BeautifulSoup`. Como o site da ANS é estático e não depende de JavaScript ou interações do usuário, o uso de ferramentas mais pesadas, como Selenium, não se mostrou necessário.

Também foi considerado o tamanho dos arquivos. O download é realizado em modo streaming, gravando o conteúdo em partes no disco, evitando o carregamento completo do arquivo na memória.

## 1.2 Processamento de Arquivos

Após o download, os arquivos ZIP são extraídos automaticamente para uma pasta intermediária. A partir daí, o processamento é feito arquivo por arquivo.

Os CSVs da ANS não seguem um padrão rígido de estrutura. Há variações no nome das colunas e os arquivos misturam diferentes tipos de contas contábeis (ativo, passivo, receitas e despesas).

Para lidar com isso, o processamento aplica um mapeamento de colunas e ignora qualquer arquivo que não contenha as informações mínimas necessárias (`REG_ANS`, `DESCRICAO` e `VL_SALDO_FINAL`).

O filtro aplicado é propositalmente rígido. Apenas registros cuja descrição seja exatamente “Despesas com Eventos/Sinistros” entram no cálculo. Contas semelhantes, como provisões ou participações relacionadas, são descartadas.

Essa decisão evita somas incorretas e garante que o valor consolidado represente apenas a despesa efetiva solicitada no teste.

Em relação ao uso de memória, optei por processar os arquivos de forma incremental. Cada CSV é lido, filtrado e agregado individualmente antes de seguir para o próximo. Isso mantém o consumo de memória previsível e evita problemas caso o volume de dados aumente.

## 1.3 Consolidação e Análise de Inconsistências

Durante a consolidação, surgiram algumas inconsistências esperadas.

A principal delas é que os arquivos de Demonstrações Contábeis não possuem CNPJ nem Razão Social, apenas o código `REG_ANS`. Mesmo assim, o layout final exigido pelo teste pede essas colunas.

A decisão foi manter o `REG_ANS` como chave real de consolidação, já que é o identificador confiável disponível nesta etapa. A coluna `RazaoSocial` é preenchida provisoriamente com o código da operadora, apenas para atender ao formato exigido. A coluna `CNPJ` permanece vazia, pois esse dado será tratado corretamente em uma etapa posterior de enriquecimento cadastral.

Outro ponto crítico foi a identificação do trimestre. A data presente dentro dos arquivos muitas vezes vem como genérica (por exemplo, 01/01), o que faz com que todos os registros pareçam pertencer ao primeiro trimestre.

Para evitar esse erro, o trimestre e o ano são definidos a partir do nome do arquivo original (ex: `1T2025.csv`). Essa abordagem garante que os dados fiquem corretamente separados por período.

Valores zerados ou negativos são descartados no momento do processamento. Como o objetivo é consolidar despesas efetivas, esses registros não agregam valor analítico e poderiam distorcer o resultado final.

Ao final, os dados dos três trimestres são consolidados em um único CSV e compactados no arquivo `consolidado_despesas.zip`, conforme solicitado no teste.

## 2.1 Validação de Dados

Na validação cadastral, decidi verificar apenas o formato do CNPJ (14 dígitos numéricos) e não o cálculo matemático dos dígitos verificadores.

O trade-off aqui é integridade financeira versus pureza cadastral. Bases históricas costumam ter erros de digitação. Se eu descartasse uma despesa válida por causa de um dígito errado no cadastro, o relatório financeiro ficaria incorreto. Preferi manter o dado financeiro e apenas gerar um aviso no log.

## 2.2 Enriquecimento de Dados

O arquivo da etapa anterior mantinha a coluna `CNPJ` vazia para respeitar o layout sem criar dados falsos na origem. Como não dava para usar uma coluna vazia como chave de join, utilizei o `REG_ANS` que existe nas duas bases.

O processo seguiu a lógica:
1. Recuperei o `REG_ANS` que havia sido preservado no campo Razão Social.
2. Realizei o cruzamento utilizando o `REG_ANS`.
3. Uma vez feito o vínculo, preenchi a coluna `CNPJ` (que estava vazia) com o dado oficial vindo do cadastro.

Utilizei **Left Join** (tabela de despesas à esquerda). O motivo é que o arquivo de cadastro só tem operadoras ativas. Se uma empresa teve despesas no trimestre mas fechou depois, os dados dela sumiriam num Inner Join. O Left Join preserva a contabilidade correta.

## 2.3 Agregação e Estatísticas

Além da soma e média, incluí o Desvio Padrão. No contexto de saúde, desvio alto indica volatilidade na operação e gastos que oscilam muito entre trimestres, servindo como indicador de risco.

A ordenação foi feita pelo maior volume total de despesas, focando nas operadoras de maior impacto. Salvei o arquivo final usando encoding `utf-8-sig`. Essa escolha garante que acentos (como em "SAÚDE") abram corretamente no Excel e Windows, evitando caracteres estranhos.

Por fim, optei por manter as colunas RegistroANS e Modalidade no arquivo final agregado. Mesmo com a agregação sendo feita por operadora, esses campos fazem parte do cadastro da empresa e ajudam a manter a rastreabilidade dos dados. Além disso, essa escolha garante o cumprimento do que foi solicitado na etapa 2.2 e facilita etapas futuras, como a carga e o uso desses dados em um banco de dados.

## 3.2 Modelagem de Banco de Dados

Para a estrutura das tabelas, optei pela **Opção B (Normalização)**, separando os dados em duas tabelas principais: `operadoras` (dados cadastrais) e `demonstracoes_contabeis` (fatos financeiros).

Essa decisão foi tomada pensando na manutenção e integridade:
1.  Evita a repetição desnecessária da Razão Social e UF milhões de vezes na tabela de despesas.
2.  Se uma operadora mudar de nome ou endereço, a atualização ocorre em apenas um registro.
3.  Facilita o armazenamento, já que dados textuais ocupam mais espaço que chaves numéricas.

Sobre a Chave Primária, escolhi o **Registro ANS** (`registro_ans`) em vez do CNPJ. O motivo é prático: nos arquivos de despesas da ANS, o CNPJ muitas vezes não está presente, mas o Registro ANS é obrigatório e único. Usar o CNPJ como chave impediria a importação de registros financeiros válidos que ainda não tiveram o CNPJ enriquecido.

Para os valores monetários, utilizei o tipo `NUMERIC(18,2)`. Evitei o uso de `FLOAT` porque operações financeiras exigem precisão exata nos centavos, e tipos de ponto flutuante podem gerar erros de arredondamento acumulativos.

## 3.3 Importação e Limpeza de Dados

Os arquivos CSV gerados estão no padrão brasileiro (vírgula para decimal), enquanto o banco de dados (PostgreSQL) espera o padrão americano (ponto).

Em vez de tentar realizar transformações complexas diretamente no comando de importação do banco, optei por criar um script auxiliar em Python (`db_importer.py`) que:
1.  Lê os CSVs.
2.  Normaliza os números (troca vírgula por ponto).
3.  Trata strings (escapa aspas simples).
4.  Gera um arquivo padronizado (`inserts.sql`).

Essa abordagem desacopla a regra de negócio da infraestrutura do banco. O arquivo SQL gerado pode ser auditado antes de rodar e executado em qualquer ambiente sem depender de configurações regionais do servidor.

Durante a importação, encontrei um caso crítico de integridade: algumas operadoras com dados históricos de despesas não constavam no arquivo de operadoras ativas (provavelmente empresas que já fecharam). Isso gerava erro de Chave Estrangeira.

Para resolver sem perder o dado financeiro, o script identifica essas operadoras faltantes e cria automaticamente um cadastro provisório ("Operadora Histórica") na tabela de operadoras. Assim, mantemos a integridade referencial do banco sem descartar o histórico financeiro.

## 3.4 Queries Analíticas

Para calcular o crescimento percentual das despesas, a comparação foi feita entre o primeiro e o último trimestre disponível para cada operadora. Como nem todas possuem dados em todos os períodos, a query identifica dinamicamente esses limites temporais a partir da base. Operadoras com apenas um registro histórico são desconsideradas, pois não existe base válida para comparação. Essa decisão evita distorções matemáticas e garante que o crescimento calculado represente apenas o período efetivamente registrado de cada empresa.

A distribuição de despesas por UF foi calculada utilizando a tabela `despesas_agregadas`, criada durante a etapa de processamento. Essa tabela já contém os valores consolidados por operadora e estado, o que permite obter o total de despesas por UF e a média por operadora na mesma consulta. O uso dessa estrutura reduz o custo computacional, evita joins repetitivos com a tabela de fatos contábeis e atende diretamente ao desafio adicional proposto no documento em pdf.

A verificação das operadoras acima da média geral foi realizada comparando as despesas individuais com a média do mercado em cada trimestre. O cálculo da média trimestral foi isolado em uma etapa própria, o que facilita a leitura e evita repetições desnecessárias na query principal. A partir dessa comparação, são contabilizados os trimestres em que a operadora ficou acima da média, mantendo apenas aquelas que atenderam ao critério de pelo menos dois dos três períodos analisados. A estrutura com CTEs torna a lógica mais clara e evita o uso de subqueries aninhadas, mantendo o código simples e fácil de manter, sem impacto relevante de performance para o volume de dados utilizado.



