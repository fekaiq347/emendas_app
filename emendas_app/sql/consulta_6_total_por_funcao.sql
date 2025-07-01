SELECT
    f.nome,
    SUM(a.valor_empenhado) AS total_empenhado
FROM emendas_app_acaoorcamentaria AS a
JOIN emendas_app_emenda AS e ON a.cod_emenda_id = e.cod_emenda
JOIN emendas_app_funcao AS f ON e.cod_funcao_id = f.cod_funcao
GROUP BY f.nome
ORDER BY f.nome;
