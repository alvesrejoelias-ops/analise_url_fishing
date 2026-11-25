# Orientações para o dashboard no Power BI

O dashboard deve ser construído a partir de `data/processed/urls_analisadas.csv`, gerado ao executar `python main.py`.

## 1. Importação

1. Abra o Power BI Desktop.
2. Selecione **Obter dados > Texto/CSV**.
3. Escolha `data/processed/urls_analisadas.csv`.
4. Confira os tipos de dados: colunas de contagem e indicadores devem ser numéricas; `label` e `url` devem ser texto.
5. Selecione **Carregar**.

## 2. Indicadores sugeridos

Crie medidas DAX:

```DAX
Total de URLs = COUNTROWS(urls_analisadas)

URLs legítimas =
CALCULATE(
    [Total de URLs],
    urls_analisadas[label] = "legitima"
)

URLs classificadas como phishing =
CALCULATE(
    [Total de URLs],
    urls_analisadas[label] = "phishing"
)

Comprimento médio =
AVERAGE(urls_analisadas[url_length])

Percentual com HTTPS =
AVERAGE(urls_analisadas[has_https])
```

Formate a última medida como percentual.

## 3. Visuais recomendados

- Cartões: total de URLs, total legítimas e total rotuladas como phishing.
- Gráfico de colunas: quantidade de registros por classificação.
- Gráfico de barras: comprimento médio por classificação.
- Gráfico de colunas agrupadas: proporção de HTTPS, host IP e presença de termos selecionados por classificação.
- Tabela: URL, classificação, comprimento e quantidade de parâmetros.

## 4. Filtros

Adicione um segmentador para `label`. Se a base crescer, considere também filtros por fonte e período de coleta, desde que esses campos existam e estejam documentados.

## 5. Cuidados de apresentação

Identifique no dashboard que a base atual é sintética. Não apresente os indicadores como um detector de phishing nem utilize cores ou títulos que impliquem certeza. Antes de publicar conclusões, substitua a amostra por dados reais documentados e atualize a descrição do relatório.

O arquivo PBIX é criado no Power BI Desktop e deve ser salvo manualmente no computador.