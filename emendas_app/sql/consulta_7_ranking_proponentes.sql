SELECT
    p.nome,
    SUM(a.valor_pago) AS total_pago
FROM emendas_app_proponente AS p
JOIN emendas_app_emenda AS e ON e.cod_proponente_id = p.cod_proponente
JOIN emendas_app_acaoorcamentaria AS a ON a.cod_emenda_id = e.cod_emenda
GROUP BY p.nome
ORDER BY total_pago DESC;
