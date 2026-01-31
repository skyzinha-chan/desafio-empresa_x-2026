-- =================================================================
-- QUERY 1: Top 5 operadoras com maior crescimento de despesas
-- (Último trimestre vs Primeiro trimestre)
-- =================================================================
WITH limites AS (
    -- Descobre dinamicamente qual é o primeiro e o último período carregado
    SELECT 
        MIN(ano * 10 + trimestre) as periodo_ini, 
        MAX(ano * 10 + trimestre) as periodo_fim 
    FROM despesas
),
valores_pontas AS (
    SELECT 
        d.cnpj_operadora,
        SUM(CASE WHEN (d.ano * 10 + d.trimestre) = l.periodo_ini THEN d.valor_despesa ELSE 0 END) as vlr_inicial,
        SUM(CASE WHEN (d.ano * 10 + d.trimestre) = l.periodo_fim THEN d.valor_despesa ELSE 0 END) as vlr_final
    FROM despesas d, limites l
    GROUP BY d.cnpj_operadora
)
SELECT 
    o.razao_social,
    v.vlr_inicial,
    v.vlr_final,
    ROUND(((v.vlr_final - v.vlr_inicial) / NULLIF(v.vlr_inicial, 0)) * 100, 2) as crescimento_pct
FROM valores_pontas v
JOIN operadoras o ON v.cnpj_operadora = o.cnpj
WHERE v.vlr_inicial > 0 -- Evita divisão por zero e empresas novas
ORDER BY crescimento_pct DESC
LIMIT 5;

-- =================================================================
-- QUERY 2: Distribuição de despesas por UF (Top 5 Estados)
-- =================================================================
SELECT 
    o.uf,
    SUM(d.valor_despesa) as total_despesas,
    ROUND(AVG(d.valor_despesa), 2) as media_por_lancamento
FROM despesas d
JOIN operadoras o ON d.cnpj_operadora = o.cnpj
WHERE o.uf IS NOT NULL
GROUP BY o.uf
ORDER BY total_despesas DESC
LIMIT 5;

-- =================================================================
-- QUERY 3: Operadoras com despesas acima da média em > 2 trimestres
-- =================================================================
WITH media_por_trimestre AS (
    -- 1. Calcula a média geral de despesas de TODO O MERCADO por trimestre
    SELECT ano, trimestre, AVG(valor_despesa) as media_mercado
    FROM despesas
    GROUP BY ano, trimestre
),
performance_operadora AS (
    -- 2. Compara cada operadora com a média do mercado naquele trimestre
    SELECT 
        d.cnpj_operadora,
        d.ano,
        d.trimestre,
        SUM(d.valor_despesa) as total_op,
        m.media_mercado
    FROM despesas d
    JOIN media_por_trimestre m ON d.ano = m.ano AND d.trimestre = m.trimestre
    GROUP BY d.cnpj_operadora, d.ano, d.trimestre, m.media_mercado
)
SELECT 
    p.cnpj_operadora,
    COUNT(*) as qtd_trimestres_acima
FROM performance_operadora p
WHERE p.total_op > p.media_mercado
GROUP BY p.cnpj_operadora
HAVING COUNT(*) >= 2; -- Filtro final: Pelo menos 2 trimestres