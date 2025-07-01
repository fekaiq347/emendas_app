SELECT
    i.nome,
    SUM(a.valor_empenhado) AS total_empenhado
FROM emendas_app_instituicao AS i
JOIN emendas_app_repasse AS r
  ON r.cod_instituicao_id = i.cod_instituicao
JOIN emendas_app_acaoorcamentaria AS a
  ON a.cod_emenda_id = r.cod_emenda_id
GROUP BY i.nome
HAVING SUM(a.valor_empenhado) > (
    SELECT AVG(total) FROM (
        SELECT
            i2.nome,
            SUM(a2.valor_empenhado) AS total
        FROM emendas_app_instituicao AS i2
        JOIN emendas_app_repasse AS r2 ON r2.cod_instituicao_id = i2.cod_instituicao
        JOIN emendas_app_acaoorcamentaria AS a2 ON a2.cod_emenda_id = r2.cod_emenda_id
        GROUP BY i2.nome
    ) AS medias
)
ORDER BY total_empenhado DESC;
