from pathlib import Path
from django.db import connection

SQL_DIR = Path(__file__).resolve().parent / "sql"


def _execute_sql(filename: str, params=None):
    """Executes a raw SQL file and returns a list of dictionaries."""
    sql_path = SQL_DIR / filename
    with open(sql_path, "r", encoding="utf-8") as f:
        query = f.read()

    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [col[0] for col in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def consulta_1_total_empenhado_por_ano():
    return _execute_sql("consulta_1_total_empenhado_por_ano.sql")


def consulta_2_instituicoes_acima_media():
    return _execute_sql("consulta_2_instituicoes_acima_media.sql")


def consulta_3_emendas_sem_repasse():
    return _execute_sql("consulta_3_emendas_sem_repasse.sql")


def consulta_4_detalhes_emenda_especifica(cod_emenda):
    return _execute_sql("consulta_4_detalhes_emenda_especifica.sql", [cod_emenda])


def consulta_5_lista_geral_emendas():
    return _execute_sql("consulta_5_lista_geral_emendas.sql")


def consulta_6_total_por_funcao():
    """Retorna o total empenhado agrupado por função."""
    return _execute_sql("consulta_6_total_por_funcao.sql")


def consulta_7_ranking_proponentes():
    """Retorna o ranking de proponentes por valor pago."""
    return _execute_sql("consulta_7_ranking_proponentes.sql")


def consulta_8_instituicoes_repasses_acima_media():
    """Retorna instituições com número de repasses acima da média."""
    return _execute_sql("consulta_8_instituicoes_repasses_acima_media.sql")
