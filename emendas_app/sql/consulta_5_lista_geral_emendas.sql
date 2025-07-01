SELECT
    e.cod_emenda,
    e.numero_emenda,
    e.ano,
    e.tipo,
    p.nome AS proponente,
    f.nome AS funcao,
    SUM(a.valor_empenhado) AS total_empenhado,
    SUM(a.valor_pago) AS total_pago
FROM emendas_app_emenda AS e
JOIN emendas_app_proponente AS p
  ON e.cod_proponente_id = p.cod_proponente
JOIN emendas_app_funcao AS f
  ON e.cod_funcao_id = f.cod_funcao
LEFT JOIN emendas_app_acaoorcamentaria AS a
  ON a.cod_emenda_id = e.cod_emenda
GROUP BY e.cod_emenda, e.numero_emenda, e.ano, e.tipo, p.nome, f.nome
ORDER BY e.ano, e.cod_emenda;
