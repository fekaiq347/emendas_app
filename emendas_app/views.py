from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Sum
import json
import unicodedata
from . import queries
from .models import Emenda, AcaoOrcamentaria, Repasse


def home(request):
    """Renderiza a página inicial."""
    return render(request, "home.html")


def dashboard_view(request):
    """Exibe o dashboard com o total empenhado por ano."""
    dados = queries.consulta_1_total_empenhado_por_ano()
    dados = [d for d in dados if d.get("total_empenhado")]  # remove anos sem valores
    anos = [d["ano"] for d in dados]
    totais = [float(d["total_empenhado"]) for d in dados]
    context = {
        "years_json": json.dumps(anos),
        "totals_json": json.dumps(totais),
    }
    return render(request, "dashboard.html", context)


def emendas_sem_repasses(request):
    """Lista emendas que não possuem repasses."""
    dados = queries.consulta_3_emendas_sem_repasse()
    paginator = Paginator(dados, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "emendas_sem_repasses.html", {"page_obj": page_obj})


def instituicoes_acima_media(request):
    """Exibe instituições com repasse acima da média."""
    dados = queries.consulta_2_instituicoes_acima_media()
    # Limita a quantidade de barras exibidas no gráfico para evitar excesso de
    # informações e facilitar a leitura. O restante das instituições será
    # apresentado em formato de tabela na mesma página.
    top_dados = dados[:10]

    nomes = [d["nome"] for d in top_dados]
    totais = [float(d["total_empenhado"]) for d in top_dados]
    context = {
        "nomes_json": json.dumps(nomes),
        "totais_json": json.dumps(totais),
        "instituicoes": dados,
    }
    return render(request, "instituicoes_acima_media.html", context)


def instituicoes_repasses_acima_media(request):
    """Exibe instituições com total de repasses acima da média."""
    dados = queries.consulta_8_instituicoes_repasses_acima_media()
    top_dados = dados[:10]

    nomes = [d["nome"] for d in top_dados]
    totais = [int(d["total_repasses"]) for d in top_dados]
    context = {
        "nomes_json": json.dumps(nomes),
        "totais_json": json.dumps(totais),
        "instituicoes": dados,
    }
    return render(request, "instituicoes_repasses_acima_media.html", context)


def ranking_proponentes(request):
    """Exibe ranking de proponentes pelo valor pago."""
    dados = queries.consulta_7_ranking_proponentes()
    top_dados = dados[:10]
    nomes = [d["nome"] for d in top_dados]
    totais = [float(d["total_pago"]) for d in top_dados]
    context = {
        "nomes_json": json.dumps(nomes),
        "totais_json": json.dumps(totais),
        "proponentes": dados,
    }
    return render(request, "ranking_proponentes.html", context)


def emendas_list(request):
    """Lista geral de emendas com múltiplos filtros."""
    numero = request.GET.get("numero")
    ano = request.GET.get("ano")
    codigo = request.GET.get("codigo")
    tipo = request.GET.get("tipo")
    proponente = request.GET.get("proponente")
    funcao = request.GET.get("funcao")

    emendas_qs = Emenda.objects.select_related(
        "cod_proponente", "cod_funcao"
    ).annotate(
        total_empenhado=Sum("acaoorcamentaria__valor_empenhado"),
        total_pago=Sum("acaoorcamentaria__valor_pago"),
    )

    if numero:
        emendas_qs = emendas_qs.filter(numero_emenda__icontains=numero)
    if ano:
        emendas_qs = emendas_qs.filter(ano=ano)
    if codigo:
        emendas_qs = emendas_qs.filter(cod_emenda=codigo)
    if tipo:
        emendas_qs = emendas_qs.filter(tipo__icontains=tipo)
    if proponente:
        emendas_qs = emendas_qs.filter(cod_proponente__nome__icontains=proponente)
    if funcao:
        emendas_qs = emendas_qs.filter(cod_funcao__nome__icontains=funcao)

    paginator = Paginator(emendas_qs.order_by("ano", "cod_emenda"), 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "numero": numero or "",
        "ano": ano or "",
        "codigo": codigo or "",
        "tipo": tipo or "",
        "proponente": proponente or "",
        "funcao": funcao or "",
    }
    return render(request, "emendas_list.html", context)


def emenda_detail(request, cod_emenda):
    """Exibe detalhes de uma emenda específica."""
    emenda = get_object_or_404(
        Emenda.objects.select_related("cod_proponente", "cod_funcao"),
        pk=cod_emenda,
    )

    acoes = AcaoOrcamentaria.objects.filter(cod_emenda=emenda)
    repasses = Repasse.objects.select_related("cod_instituicao").filter(
        cod_emenda=emenda
    )

    context = {
        "emenda": emenda,
        "acoes": acoes,
        "repasses": repasses,
    }
    return render(request, "emenda_detail.html", context)


