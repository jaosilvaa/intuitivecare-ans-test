# Trade-offs e Decisões Técnicas

## 1.1 Acesso à API de Dados Abertos da ANS

O primeiro desafio foi acessar os arquivos de Demonstrações Contábeis da ANS, organizados em pastas por ano e trimestre. O enunciado do teste indica que essa estrutura pode mudar ao longo do tempo.

Para evitar que o código quebre caso haja alteração nos nomes das pastas, inclusão de novos anos ou mudança na ordem dos arquivos, optei por não utilizar URLs fixas. O script lê o HTML do diretório e identifica dinamicamente os anos disponíveis e os arquivos ZIP em cada pasta.

Essa abordagem torna o processo de ingestão mais robusto e reduz a necessidade de manutenção manual.

O acesso aos dados foi implementado utilizando `requests` e `BeautifulSoup`. Como o site da ANS é estático e não depende de JavaScript ou interações do usuário, o uso de ferramentas mais pesadas, como Selenium, não se mostrou necessário.

Também foi considerado o tamanho dos arquivos. O download é realizado em modo streaming, gravando o conteúdo em partes no disco, evitando o carregamento completo do arquivo na memória.
