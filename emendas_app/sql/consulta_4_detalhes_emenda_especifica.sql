SELECT
    e.cod_emenda,
    e.ano,
    e.numero_emenda,
    e.tipo,
    p.nome AS proponente,
    f.nome AS funcao,
    a.descricao AS acao_descricao,
    a.valor_empenhado,
    a.valor_pago,
    i.nome AS instituicao,
    r.possui_convenio
FROM emendas_app_emenda AS e
LEFT JOIN emendas_app_proponente AS p
  ON e.cod_proponente_id = p.cod_proponente
LEFT JOIN emendas_app_funcao AS f
  ON e.cod_funcao_id = f.cod_funcao
LEFT JOIN emendas_app_acaoorcamentaria AS a
  ON a.cod_emenda_id = e.cod_emenda
LEFT JOIN emendas_app_repasse AS r
  ON r.cod_emenda_id = e.cod_emenda
LEFT JOIN emendas_app_instituicao AS i
  ON i.cod_instituicao = r.cod_instituicao_id
WHERE e.cod_emenda = %s;
