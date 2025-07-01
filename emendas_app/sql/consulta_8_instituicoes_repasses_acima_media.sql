SELECT
    i.nome,
    COUNT(r.cod_emenda_id) AS total_repasses
FROM emendas_app_instituicao AS i
JOIN emendas_app_repasse AS r ON r.cod_instituicao_id = i.cod_instituicao
GROUP BY i.nome
HAVING COUNT(r.cod_emenda_id) > (
    SELECT AVG(total) FROM (
        SELECT COUNT(*) AS total
        FROM emendas_app_repasse
        GROUP BY cod_instituicao_id
    ) AS medias
)
ORDER BY total_repasses DESC;
