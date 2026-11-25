# Metodologia da análise

## 1. Pergunta de análise

Quais diferenças estruturais aparecem entre os registros rotulados como legítimos e os registros rotulados como phishing na base utilizada?

A pergunta é descritiva. O projeto não treina um classificador e não afirma que os indicadores identificam fraudes com certeza.

## 2. Entrada e validação

O arquivo de entrada é um CSV com duas colunas obrigatórias: url e label. O processo:

1. verifica a existência do arquivo e das colunas obrigatórias;
2. lê os campos como texto para evitar conversões inesperadas;
3. remove espaços externos e padroniza os rótulos em letras minúsculas;
4. descarta URLs vazias e rótulos fora das categorias legitima e phishing;
5. rejeita uma URL que apareça associada a mais de um rótulo;
6. remove duplicatas idênticas de URL e rótulo.

A rejeição de rótulos conflitantes é intencional: manter o mesmo endereço nas duas classes distorceria as comparações.

## 3. Transformação

As características são calculadas diretamente sobre o texto da URL. A biblioteca padrão urllib.parse separa componentes como host e query string; ipaddress verifica se o host representa um endereço IP.

Entradas malformadas são tratadas de forma tolerante para que um único registro não interrompa a análise. Isso não significa que a URL seja considerada válida ou segura.

A contagem de subdomínios é aproximada e não utiliza uma base de sufixos públicos. Por isso, deve ser interpretada como uma métrica simples, não como uma classificação definitiva da estrutura de domínio. Endereços IP não recebem contagem de subdomínios.

## 4. Indicadores

- Comprimento: número total de caracteres.
- Pontos, hífens e dígitos: contagens literais no texto.
- HTTPS: presença do prefixo https://.
- Host IP: host que pode ser interpretado como IPv4 ou IPv6.
- Arroba: presença de @ na autoridade da URL, e não em qualquer trecho da query ou do caminho.
- Subdomínios: contagem aproximada de componentes adicionais do host.
- Parâmetros: quantidade de pares na query string, incluindo parâmetros com valor vazio.
- Palavra selecionada: presença de termos definidos no código para triagem exploratória.

## 5. Redirecionamentos e segurança

O código não acessa endereços, não realiza requisições HTTP e não segue redirecionamentos. Uma contagem de redirecionamentos não pode ser inferida apenas pelo texto de uma URL. Para analisar essa variável, seria necessário obter uma coluna de uma fonte externa confiável, documentando como e quando foi coletada.

## 6. Estatística e visualização

O pipeline calcula contagens, médias e medianas por rótulo e gera gráficos de distribuição. Em uma base real, seria necessário avaliar:

- tamanho e representatividade da amostra;
- equilíbrio entre as classes;
- duplicatas e possíveis vazamentos entre conjuntos;
- data de coleta e validade temporal;
- qualidade e consistência dos rótulos;
- vieses da fonte.

## 7. Interpretação

Uma diferença entre grupos não demonstra causalidade. HTTPS, por exemplo, é utilizado tanto por sites legítimos quanto por páginas fraudulentas. O resultado deve ser descrito como associação observada na base, sem generalizar além dos dados disponíveis.

## 8. Natureza da base atual

O CSV incluído no repositório é sintético e didático. Ele permite verificar a execução do código e a geração dos arquivos, mas não sustenta conclusões sobre prevalência ou comportamento real de phishing. Uma versão de portfólio com conclusões empíricas exige uma base pública real, com fonte, licença e documentação registradas.
