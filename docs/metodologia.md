# Metodologia da análise

## 1. Pergunta de análise

Quais diferenças estruturais aparecem entre os registros rotulados como legítimos e os registros rotulados como phishing na base utilizada?

A pergunta é descritiva. O projeto não treina um classificador e não afirma que os indicadores identificam fraudes com certeza.

## 2. Entrada e validação

O arquivo de entrada é um CSV com duas colunas obrigatórias: `url` e `label`. O processo:
1. verifica a existência das colunas;
2. remove espaços externos;
3. padroniza os rótulos em letras minúsculas;
4. descarta URLs vazias e rótulos fora das categorias esperadas;
5. remove duplicatas idênticas de URL e rótulo.

## 3. Transformação

As características são calculadas diretamente sobre o texto da URL. A biblioteca padrão `urllib.parse` separa componentes como host e query string; `ipaddress` verifica se o host representa um endereço IP.

A contagem de subdomínios é aproximada e não utiliza uma base de sufixos públicos. Portanto, deve ser interpretada como uma métrica simples, não como uma classificação definitiva da estrutura de domínio.

## 4. Indicadores

- Comprimento: número total de caracteres.
- Pontos, hífens e dígitos: contagens literais no texto.
- HTTPS: presença do esquema HTTPS declarado.
- Host IP: host que pode ser interpretado como endereço IP.
- Arroba: presença do caractere @.
- Subdomínios: contagem aproximada de componentes adicionais do host.
- Parâmetros: quantidade de pares separados por & na query string.
- Palavra selecionada: presença de termos definidos no código para triagem.

## 5. Redirecionamentos e segurança

O código não acessa endereços, não realiza requisições HTTP e não segue redirecionamentos. Uma contagem de redirecionamentos não pode ser inferida apenas pelo texto de uma URL. Para analisar essa variável, seria necessário obter uma coluna de uma fonte externa confiável, documentando como e quando foi coletada.

## 6. Estatística e visualização

O pipeline calcula contagens, médias e medianas por rótulo e gera gráficos de distribuição. Em uma base real, seria necessário avaliar:
- tamanho e representatividade da amostra;
- equilíbrio entre as classes;
- duplicatas e possíveis vazamentos entre conjuntos;
- data de coleta e validade temporal;
- qualidade dos rótulos;
- vieses da fonte.

## 7. Interpretação

Uma diferença entre grupos não demonstra causalidade. HTTPS, por exemplo, é utilizado tanto por sites legítimos quanto por páginas fraudulentas. O resultado deve ser descrito como associação observada na base, sem generalizar além dos dados disponíveis.

## 8. Natureza da base atual

O CSV incluído no repositório é sintético e didático. Ele permite verificar a execução do código e a geração dos arquivos, mas não sustenta conclusões sobre a prevalência ou o comportamento real de phishing. Uma versão de portfólio com conclusões empíricas exige uma base pública real, com fonte, licença e documentação registradas.