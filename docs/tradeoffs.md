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
