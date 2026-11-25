# Análise de URLs: padrões associados a phishing

Projeto de análise exploratória de dados desenvolvido com **Python, Pandas, NumPy, SQL/SQLite e Matplotlib**, com possibilidade de visualização complementar no Power BI.

> **Importante:** a base incluída é sintética e didática. Ela serve para demonstrar o pipeline e testar o código, mas não representa uma amostra real da internet nem permite medir a eficácia de um detector. Os indicadores são sinais exploratórios, não provas de fraude.

## Visão geral do processo

![Diagrama do fluxo de análise](images/fluxo_projeto.svg)

## Objetivos

- Validar e preparar uma base tabular de URLs.
- Extrair características estruturais sem abrir os endereços ou fazer requisições de rede.
- Comparar padrões entre registros rotulados como legítimos e phishing.
- Exportar os dados tratados para CSV e SQLite.
- Gerar estatísticas descritivas e gráficos que apoiem a análise exploratória.
- Disponibilizar uma base tratada para construção de um dashboard no Power BI.

## Tecnologias

| Tecnologia | Aplicação |
|---|---|
| Python | Organização e execução do pipeline |
| Pandas | Leitura, limpeza, transformação e agregação |
| NumPy | Tratamento de valores numéricos não finitos |
| SQL / SQLite | Armazenamento e consultas analíticas |
| Matplotlib | Geração de gráficos |
| unittest | Testes automatizados |
| GitHub Actions | Execução automática dos testes em diferentes versões do Python |
| Power BI | Construção opcional de dashboard |

## Estrutura do projeto

\`\`\`text
analise_url_fishing/
├── .github/workflows/tests.yml
├── data/
│   ├── raw/urls_exemplo.csv
│   └── README.md
├── docs/
│   ├── metodologia.md
│   └── power_bi.md
├── images/fluxo_projeto.svg
├── sql/analises.sql
├── src/
│   ├── __init__.py
│   ├── features.py
│   └── pipeline.py
├── tests/test_analysis.py
├── .gitignore
├── main.py
└── requirements.txt
\`\`\`

## Como executar

### Pré-requisitos

- Python 3.10 ou superior.
- Git, caso queira clonar o repositório.
- Power BI Desktop, somente para criar o dashboard opcional.

### Instalação no Windows (PowerShell)

\`\`\`powershell
git clone https://github.com/alvesrejoelias-ops/analise_url_fishing.git
cd analise_url_fishing
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
\`\`\`

### Executar a análise

\`\`\`powershell
python main.py
\`\`\`

Para analisar outro CSV com as colunas url e label:

\`\`\`powershell
python main.py --input "caminho\\para\\seu_arquivo.csv"
\`\`\`

### Executar os testes

\`\`\`powershell
python -m unittest discover -s tests -v
\`\`\`

Os testes verificam extração de características, URLs malformadas, endereços IPv4/IPv6, validação de CSV, rótulos conflitantes, resumo estatístico e gravação no SQLite. O GitHub Actions também executa a suíte automaticamente em Python 3.10, 3.11 e 3.12.

## Arquivos gerados

Depois de executar python main.py, os seguintes arquivos são criados localmente:

- data/processed/urls_analisadas.csv: dados de entrada validados e enriquecidos.
- data/processed/analise_urls.db: banco SQLite com a tabela urls_analysis.
- reports/resumo_por_classe.csv: estatísticas agrupadas por classificação.
- reports/figures/distribuicao_classes.png: quantidade de registros por classe.
- reports/figures/comprimento_urls.png: distribuição do comprimento textual.
- reports/figures/indicadores_estruturais.png: proporção de indicadores por classe.

Arquivos gerados e bancos locais não são versionados pelo Git.

## Características analisadas

| Campo | Descrição |
|---|---|
| url_length | Quantidade de caracteres da URL |
| dot_count | Quantidade de pontos no texto |
| hyphen_count | Quantidade de hífens no texto |
| digit_count | Quantidade de dígitos |
| has_https | Indica se a URL começa com o esquema HTTPS |
| has_ip_address | Indica se o host é um endereço IPv4 ou IPv6 |
| has_at_symbol | Indica a presença de @ na autoridade da URL |
| subdomain_count | Contagem aproximada de subdomínios; não se aplica a hosts IP |
| query_parameter_count | Quantidade de pares na query string, incluindo valores vazios |
| has_suspicious_keyword | Indica a presença de termos selecionados no texto |

A contagem de subdomínios é aproximada e não utiliza uma lista de sufixos públicos. A presença de HTTPS não valida certificado, reputação ou segurança do site. Os termos selecionados podem aparecer em páginas legítimas.

## Consultas SQL

As consultas estão em sql/analises.sql. Elas demonstram contagem por classe, médias de características e comparação de indicadores. O banco SQLite é criado automaticamente pelo pipeline.

## Power BI

Consulte docs/power_bi.md para importar o CSV tratado e montar medidas e visuais. O arquivo PBIX deve ser criado e salvo manualmente no Power BI Desktop.

## Limitações e responsabilidade

- O conjunto de exemplo é sintético e não sustenta conclusões sobre phishing no mundo real.
- Uma URL com HTTPS, domínio longo ou palavra específica não é necessariamente fraudulenta.
- A ausência desses sinais não garante que um endereço seja seguro.
- O código não acessa URLs, não executa requisições HTTP e não segue redirecionamentos.
- URLs repetidas com rótulos conflitantes são rejeitadas para evitar estatísticas inconsistentes.
- Não utilize o projeto como ferramenta de bloqueio, decisão operacional ou classificação definitiva de segurança.

Leia docs/metodologia.md para conhecer as decisões de tratamento e as limitações da análise.

## Próximas evoluções

1. Substituir a base demonstrativa por uma fonte pública real, com licença e metodologia documentadas.
2. Registrar fonte, data de coleta e qualidade dos rótulos.
3. Ampliar a análise temporal e avaliar o equilíbrio entre classes.
4. Construir e documentar um dashboard no Power BI com dados reais apropriados.
5. Somente em uma etapa separada, avaliar modelos preditivos com divisão de dados e métricas adequadas.

---
Projeto educacional de análise de dados.
