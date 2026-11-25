-- Consultas analíticas para SQLite.
-- Execute após rodar: python main.py
-- A tabela urls_analysis é criada automaticamente pelo pipeline Python.

-- 1. Verifica o volume de registros por classificação.
SELECT
    label AS classificacao,
    COUNT(*) AS quantidade_registros
FROM urls_analysis
GROUP BY label
ORDER BY quantidade_registros DESC;

-- 2. Compara comprimento médio e mediano aproximado por classificação.
-- SQLite não possui MEDIAN nativo em todas as versões; por isso,
-- esta consulta apresenta a média. A mediana é calculada no relatório Python.
SELECT
    label AS classificacao,
    ROUND(AVG(url_length), 2) AS comprimento_medio,
    ROUND(AVG(dot_count), 2) AS media_pontos,
    ROUND(AVG(hyphen_count), 2) AS media_hifens,
    ROUND(AVG(digit_count), 2) AS media_digitos
FROM urls_analysis
GROUP BY label;

-- 3. Calcula a proporção de URLs com HTTPS por classificação.
SELECT
    label AS classificacao,
    ROUND(AVG(has_https) * 100, 2) AS percentual_https
FROM urls_analysis
GROUP BY label;

-- 4. Compara indicadores estruturais.
-- Estes indicadores descrevem padrões; não determinam se um endereço é fraudulento.
SELECT
    label AS classificacao,
    ROUND(AVG(has_ip_address) * 100, 2) AS percentual_host_ip,
    ROUND(AVG(has_at_symbol) * 100, 2) AS percentual_com_arroba,
    ROUND(AVG(has_suspicious_keyword) * 100, 2) AS percentual_com_termo_selecionado
FROM urls_analysis
GROUP BY label;

-- 5. Lista os registros com maior comprimento textual para inspeção exploratória.
SELECT
    url,
    label,
    url_length,
    query_parameter_count
FROM urls_analysis
ORDER BY url_length DESC
LIMIT 10;
