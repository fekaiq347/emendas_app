SELECT
    e.ano AS ano,
    SUM(a.valor_empenhado) AS total_empenhado
FROM emendas_app_acaoorcamentaria AS a
JOIN emendas_app_emenda AS e
  ON a.cod_emenda_id = e.cod_emenda
GROUP BY e.ano
ORDER BY e.ano;
