-- 3.4 Queries Analíticas - Teste Intuitive Care

-- Query 1: Quais as 5 operadoras com maior crescimento percentual de despesas entre o primeiro e o último trimestre analisado?
-- Desafio: Considere operadoras que podem não ter dados em todos os trimestres. Como tratar? Justifique.

WITH limites_temporais AS (
    SELECT 
        registro_ans,
        MIN(ano * 100 + trimestre) as periodo_inicial,
        MAX(ano * 100 + trimestre) as periodo_final
    FROM demonstracoes_contabeis
    GROUP BY registro_ans
    HAVING MIN(ano * 100 + trimestre) <> MAX(ano * 100 + trimestre)
),
valores_extremos AS (
    SELECT 
        d.registro_ans,
        (SELECT valor_despesa FROM demonstracoes_contabeis d1 
         WHERE d1.registro_ans = d.registro_ans 
         AND (d1.ano * 100 + d1.trimestre) = l.periodo_inicial) as valor_inicial,
         
        (SELECT valor_despesa FROM demonstracoes_contabeis d2 
         WHERE d2.registro_ans = d.registro_ans 
         AND (d2.ano * 100 + d2.trimestre) = l.periodo_final) as valor_final
    FROM limites_temporais l
    JOIN demonstracoes_contabeis d ON d.registro_ans = l.registro_ans
    GROUP BY d.registro_ans, l.periodo_inicial, l.periodo_final
)
SELECT 
    v.registro_ans,
    o.razao_social,
    v.valor_inicial,
    v.valor_final,
    ROUND(((v.valor_final - v.valor_inicial) / v.valor_inicial) * 100, 2) as crescimento_pct
FROM valores_extremos v
JOIN operadoras o ON v.registro_ans = o.registro_ans
WHERE v.valor_inicial > 0
ORDER BY crescimento_pct DESC
LIMIT 5;


-- Query 2: Qual a distribuição de despesas por UF? Liste os 5 estados com maiores despesas totais.
-- Desafio adicional: Calcule também a média de despesas por operadora em cada UF (não apenas o total).

SELECT 
    da.uf,
    SUM(da.total_despesas) as despesa_total_estado,
    ROUND(AVG(da.total_despesas), 2) as media_por_operadora
FROM despesas_agregadas da
WHERE da.uf IS NOT NULL
GROUP BY da.uf
ORDER BY despesa_total_estado DESC
LIMIT 5;


-- Query 3: Quantas operadoras tiveram despesas acima da média geral em pelo menos 2 dos 3 trimestres analisados?

WITH media_mercado AS (
    SELECT 
        ano, 
        trimestre, 
        AVG(valor_despesa) as media_geral
    FROM demonstracoes_contabeis
    GROUP BY ano, trimestre
),
performance_individual AS (
    SELECT 
        d.registro_ans,
        CASE 
            WHEN d.valor_despesa > m.media_geral THEN 1 
            ELSE 0 
        END as acima_da_media
    FROM demonstracoes_contabeis d
    JOIN media_mercado m ON d.ano = m.ano AND d.trimestre = m.trimestre
)
SELECT 
    p.registro_ans,
    o.razao_social,
    COUNT(*) as qtd_trimestres_acima
FROM performance_individual p
JOIN operadoras o ON p.registro_ans = o.registro_ans
WHERE p.acima_da_media = 1
GROUP BY p.registro_ans, o.razao_social
HAVING COUNT(*) >= 2
ORDER BY qtd_trimestres_acima DESC, o.razao_social
LIMIT 10;