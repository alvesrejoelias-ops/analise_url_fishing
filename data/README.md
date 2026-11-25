# Dados do projeto

## raw/

Contém os dados de entrada. O arquivo urls_exemplo.csv é uma amostra **sintética e didática**, criada para demonstrar a execução do projeto.

Colunas obrigatórias:

- url: endereço representado como texto; o programa não o acessa.
- label: classificação de referência, com os valores legitima ou phishing.

## processed/

Recebe os arquivos gerados pelo pipeline. Os resultados são criados localmente quando python main.py é executado e não são versionados pelo Git.

## Uso de uma base real

Antes de substituir o exemplo, verifique a licença, a origem, a data de coleta, a definição dos rótulos e as condições de uso. Mantenha o mesmo formato de colunas e documente a fonte no relatório. Não inclua dados pessoais ou links que não tenha autorização para compartilhar. URLs repetidas com rótulos diferentes são rejeitadas para evitar resultados inconsistentes.
