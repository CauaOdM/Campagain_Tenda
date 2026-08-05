# Campagain_Tenda
Dashboard interativa para realizar estudos de campanhas para marcas que se relacionam com o Tenda Atacado.

## Execução local

1. Configure a variável de ambiente `DATABASE_URL` com a string do PostgreSQL. Exemplo:

	`postgresql+psycopg2://usuario:senha@localhost:5432/campagain_tenda`

2. Instale as dependências:

	`pip install -r requirements.txt`

3. Rode a aplicação:

	`streamlit run app/app.py`

## Fluxo atual

O login libera a dashboard para consulta. Cada marca criada no sistema passa a ter sua própria visão dentro do Streamlit, com dados isolados por marca e por safra mensal. O upload de XLSX continua disponível como etapa de ingestão inicial: ao sincronizar o arquivo, os dados são gravados no banco e a tela passa a consultar as tabelas persistidas.

Os cartões agregados mostram a comparação da marca selecionada com o consolidado Tenda, para que o usuário entenda rapidamente o desempenho relativo dentro do universo total.

## Modelo de carga

O arquivo Excel modelo alimenta o banco com:

1. Resultado por campanha da marca.
2. Recomposição por categoria, comprador e contato.
3. Safra mensal inferida pelo nome do arquivo quando disponível, ou pelo mês corrente como fallback.

Se quiser importar um novo mês da mesma marca, envie um arquivo com a safra correspondente no nome para manter o histórico separado no banco.

## Banco de dados

O projeto usa SQLAlchemy com fallback para SQLite apenas no desenvolvimento local sem `DATABASE_URL`. Para o uso previsto, a aplicação deve apontar para PostgreSQL.
