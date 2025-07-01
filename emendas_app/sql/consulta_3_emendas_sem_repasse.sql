SELECT
    e.cod_emenda,
    e.numero_emenda,
    e.ano,
    e.tipo
FROM emendas_app_emenda AS e
LEFT JOIN emendas_app_repasse AS r
  ON r.cod_emenda_id = e.cod_emenda
WHERE r.cod_emenda_id IS NULL
ORDER BY e.ano, e.cod_emenda;
