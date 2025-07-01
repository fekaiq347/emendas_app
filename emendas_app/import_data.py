import pandas as pd
import unicodedata, re
from pathlib import Path
from django.db import transaction

BASE_DIR = Path(__file__).resolve().parent.parent

from .models import (
    Proponente, Funcao, Localidade, Instituicao,
    Programa, Emenda, AcaoOrcamentaria, Repasse
)

def _load_df(entity_name: str) -> pd.DataFrame:
    file_path = BASE_DIR / f'{entity_name}.xlsx'
    df = pd.read_excel(file_path)
    # 1) remove acentos, 2) deixa tudo lowercase, 3) não‐alnum vira underscore
    def clean(col):
        col = str(col)
        nfkd = unicodedata.normalize('NFKD', col)
        no_accents = ''.join(c for c in nfkd if not unicodedata.category(c).startswith('M'))
        lower = no_accents.lower()
        return re.sub(r'[^a-z0-9]+', '_', lower).strip('_')
    df.columns = [clean(c) for c in df.columns]
    return df

def import_proponente():
    df = _load_df('proponente')
    existing = set(Proponente.objects.values_list('cod_proponente', flat=True))
    to_create = []
    total = len(df)
    print(f"Iniciando importação de {total} proponentes...")
    for i, row in enumerate(df.itertuples(index=False), start=1):
        try:
            cod = int(row.cod_proponente)
        except (ValueError, TypeError):
            print(f"[{i}/{total}] Ignorado (código inválido): {row.cod_proponente}")
            continue

        if cod in existing:
            print(f"[{i}/{total}] Já existe: {cod}")
            continue

        to_create.append(Proponente(
            cod_proponente=cod,
            nome=row.nome
        ))
        existing.add(cod)
        print(f"[{i}/{total}] Agendado criação: {cod}")

    if to_create:
        with transaction.atomic():
            Proponente.objects.bulk_create(to_create)
        print(f"✅ {len(to_create)} proponentes criados em lote.")
    else:
        print("✅ Nenhum proponente novo para criar.")

def import_funcao():
    df = _load_df('funcao')
    existing = set(Funcao.objects.values_list('cod_funcao', flat=True))
    to_create = []
    total = len(df)
    print(f"Iniciando importação de {total} funções...")
    for i, row in enumerate(df.itertuples(index=False), start=1):
        cod = row.cod_funcao
        if cod in existing:
            print(f"[{i}/{total}] Já existe: {cod}")
            continue
        to_create.append(Funcao(cod_funcao=cod, nome=row.nome))
        existing.add(cod)
        print(f"[{i}/{total}] Agendado criação: {cod}")

    if to_create:
        with transaction.atomic():
            Funcao.objects.bulk_create(to_create)
        print(f"✅ {len(to_create)} funções criadas em lote.")
    else:
        print("✅ Nenhuma função nova para criar.")

def import_localidade():
    df = _load_df('localidade')  # sua função que já padroniza colunas para lowercase
    # cache das localidades existentes
    cache = {
        (loc.municipio, loc.uf): loc
        for loc in Localidade.objects.all()
    }
    to_create = []
    total = len(df)
    print(f"Iniciando importação de {total} localidades...")

    for i, row in enumerate(df.itertuples(index=False), start=1):
        raw_uf = str(row.uf).strip().upper()
        # valida UF: deve ter exatamente 2 caracteres
        if len(raw_uf) != 2:
            print(f"[{i}/{total}] Ignorado (UF inválida “{row.uf}”): {row.municipio}")
            continue

        key = (row.municipio, raw_uf)
        if key in cache:
            print(f"[{i}/{total}] Já existe: {row.municipio} - {raw_uf}")
            continue

        loc = Localidade(municipio=row.municipio, uf=raw_uf)
        to_create.append(loc)
        cache[key] = loc
        print(f"[{i}/{total}] Agendado criação: {row.municipio} - {raw_uf}")

    if to_create:
        with transaction.atomic():
            Localidade.objects.bulk_create(to_create)
        print(f"✅ {len(to_create)} localidades criadas em lote.")
    else:
        print("✅ Nenhuma localidade nova para criar.")

def import_instituicao():
    df = _load_df('instituicao')

    # ——— DESCARTA linhas sem UF ou MUNICÍPIO ———
    df = df.dropna(subset=['uf', 'municipio'])
    # ——— fim do dropna ———

    # — Converte cod_instituicao para inteiro, descartando inválidos —
    df['cod_instituicao'] = pd.to_numeric(df['cod_instituicao'], errors='coerce')
    df = df.dropna(subset=['cod_instituicao'])
    df['cod_instituicao'] = df['cod_instituicao'].astype(int)

    # — Padroniza município e UF —
    df['municipio'] = (
        df['municipio']
          .astype(str)
          .str.strip()
          .str.upper()
    )
    df['uf'] = (
        df['uf']
          .astype(str)
          .str.strip()
          .str.upper()
    )

    # — Cache de localidades por (municipio, uf) —
    loc_cache = {
        (loc.municipio, loc.uf): loc
        for loc in Localidade.objects.all()
    }

    existing = set(Instituicao.objects.values_list('cod_instituicao', flat=True))
    to_create = []
    total = len(df)
    print(f"Iniciando importação de {total} instituições (apenas com UF e município)…")

    for i, row in enumerate(df.itertuples(index=False), start=1):
        ce   = row.cod_instituicao
        muni = row.municipio
        uf   = row.uf
        nome = row.nome
        tipo = row.tipo

        if ce in existing:
            continue

        loc = loc_cache.get((muni, uf))
        if not loc:
            print(f"[{i}/{total}] IGNORADO: Localidade ({muni}, {uf}) não encontrada.")
            continue

        to_create.append(Instituicao(
            cod_instituicao=ce,
            nome=nome,
            tipo=tipo,
            id_local=loc
        ))
        existing.add(ce)

    if to_create:
        with transaction.atomic():
            Instituicao.objects.bulk_create(to_create)
        print(f"✅ {len(to_create)} instituições criadas em lote.")
    else:
        print("✅ Nenhuma instituição nova para criar.")

def import_programa():
    df = _load_df('programa')
    existing = set(Programa.objects.values_list('cod_programa', flat=True))
    to_create = []
    total = len(df)
    print(f"Iniciando importação de {total} programas...")
    for i, row in enumerate(df.itertuples(index=False), start=1):
        cod = row.cod_programa
        if cod in existing:
            print(f"[{i}/{total}] Já existe: {cod}")
            continue
        to_create.append(Programa(cod_programa=cod, nome=row.nome))
        existing.add(cod)
        print(f"[{i}/{total}] Agendado criação: {cod}")

    if to_create:
        with transaction.atomic():
            Programa.objects.bulk_create(to_create)
        print(f"✅ {len(to_create)} programas criados em lote.")
    else:
        print("✅ Nenhum programa novo para criar.")

def import_emenda():
    df = _load_df('emenda')

    # 1) renomeia as colunas “originais” para o padrão do modelo
    df.rename(columns={
        'codigo_da_emenda':           'cod_emenda',
        'codigo_do_autor_da_emenda':  'cod_proponente',
        'subfuncao':                  'cod_funcao',
        'tipo_de_emenda':             'tipo',
        'ano_da_emenda':              'ano',
        'numero_da_emenda':           'numero_emenda',
    }, inplace=True)

    print("Colunas após renomeação:", df.columns.tolist())
    

    # forçar conversão para número, valores inválidos viram NaN
    df['cod_emenda']      = pd.to_numeric(df['cod_emenda'],      errors='coerce')
    df['cod_proponente']  = pd.to_numeric(df['cod_proponente'],  errors='coerce')
    df['cod_funcao']      = pd.to_numeric(df['cod_funcao'],      errors='coerce')

    # opcional: relatório de quantas linhas serão descartadas
    invalid = df[df[['cod_emenda','cod_proponente','cod_funcao']].isnull().any(axis=1)]
    if not invalid.empty:
        print(f"Ignorando {len(invalid)} linhas com códigos inválidos:")
        print(invalid[['cod_emenda','cod_proponente','cod_funcao']].drop_duplicates())

    # descartar linhas sem todos os três códigos
    df = df.dropna(subset=['cod_emenda','cod_proponente','cod_funcao'])

    # agora podemos converter para int com segurança
    df['cod_emenda']     = df['cod_emenda'].astype(int)
    df['cod_proponente'] = df['cod_proponente'].astype(int)
    df['cod_funcao']     = df['cod_funcao'].astype(int)

    # 2) valida presença das colunas essenciais
    faltantes = {'cod_emenda', 'cod_proponente', 'cod_funcao'} - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltam colunas obrigatórias em emenda.xlsx: {faltantes}")

    # 3) prepara caches e existentes
    func_cache = {f.cod_funcao: f for f in Funcao.objects.all()}
    prop_cache = {p.cod_proponente: p for p in Proponente.objects.all()}
    existing  = set(Emenda.objects.values_list('cod_emenda', flat=True))

    to_create = []
    total     = len(df)
    print(f"Iniciando importação de {total} emendas...")

    # 4) itera e agenda
    for i, row in enumerate(df.itertuples(index=False), start=1):
        cod = row.cod_emenda

        if cod in existing:
            print(f"[{i}/{total}] Já existe: {cod}")
            continue

        func = func_cache.get(row.cod_funcao)
        prop = prop_cache.get(row.cod_proponente)
        if not func or not prop:
            print(f"[{i}/{total}] Erro FK não encontrada (func={row.cod_funcao}, prop={row.cod_proponente})")
            continue

        to_create.append(Emenda(
            cod_emenda      = cod,
            tipo            = row.tipo,
            ano             = row.ano if not pd.isna(row.ano) else None,
            numero_emenda   = row.numero_emenda if not pd.isna(row.numero_emenda) else None,
            cod_funcao   = func,
            cod_proponente = prop
        ))
        existing.add(cod)
        print(f"[{i}/{total}] Agendado criação: {cod}")

    # 5) executa o bulk_create
    if to_create:
        with transaction.atomic():
            Emenda.objects.bulk_create(to_create)
        print(f"✅ {len(to_create)} emendas criadas em lote.")
    else:
        print("✅ Nenhuma emenda nova para criar.")

def import_acao_orcamentaria():
    df = _load_df('acao_orcamentaria')
    print("Colunas em acaoorcamentaria.xlsx →", df.columns.tolist())

    # converte pra número; valores inválidos viram NaN
    df['cod_acao'] = pd.to_numeric(df['cod_acao'], errors='coerce')

    # reporta quais serão descartados
    invalid = df[df['cod_acao'].isna()]
    if not invalid.empty:
        print(f"Ignorando {len(invalid)} linhas com cod_acao inválido:")
        print(invalid[['cod_acao', 'descricao']].drop_duplicates().head())

    # descarta linhas sem cod_acao numérico
    df = df.dropna(subset=['cod_acao'])

    # agora cod_acao é float, converte pra int
    df['cod_acao'] = df['cod_acao'].astype(int)
    em_cache = {e.cod_emenda: e for e in Emenda.objects.all()}
    pr_cache = {p.cod_programa: p for p in Programa.objects.all()}
    existing = set(AcaoOrcamentaria.objects.values_list('cod_acao', flat=True))
    to_create = []
    total = len(df)
    print(f"Iniciando importação de {total} ações orçamentárias...")
    for i, row in enumerate(df.itertuples(index=False), start=1):
        cod = row.cod_acao
        if cod in existing:
            print(f"[{i}/{total}] Já existe: {cod}")
            continue
        em = em_cache.get(row.cod_emenda)
        pr = pr_cache.get(row.cod_programa) if not pd.isna(row.cod_programa) else None
        if not em:
            print(f"[{i}/{total}] Erro: emenda não encontrada para ação {cod}")
            continue

        to_create.append(AcaoOrcamentaria(
            cod_acao=cod,
            descricao=row.descricao,
            valor_empenhado=row.valor_empenhado or 0,
            valor_pago=row.valor_pago or 0,
            cod_emenda=em,
            cod_programa=pr
        ))
        existing.add(cod)
        print(f"[{i}/{total}] Agendado criação: {cod}")

    if to_create:
        with transaction.atomic():
            AcaoOrcamentaria.objects.bulk_create(to_create)
        print(f"✅ {len(to_create)} ações orçamentárias criadas em lote.")
    else:
        print("✅ Nenhuma ação orçamentária nova para criar.")

def import_repasse():
    df = _load_df('repasse')

    # —————— converte para numérico ——————
    df['cod_emenda']      = pd.to_numeric(df['cod_emenda'], errors='coerce')
    df['cod_instituicao'] = pd.to_numeric(df['cod_instituicao'], errors='coerce')
    df = df.dropna(subset=['cod_emenda', 'cod_instituicao'])
    df['cod_emenda']      = df['cod_emenda'].astype(int)
    df['cod_instituicao'] = df['cod_instituicao'].astype(int)

    # —————— mapeia convenio ——————
    df['possui_convenio'] = (
        df['possui_convenio']
          .astype(str)
          .str.upper()
          .map({'SIM': True, 'NÃO': False})
          .fillna(False)
    )

    em_cache   = {e.cod_emenda: e for e in Emenda.objects.all()}
    inst_cache = {i.cod_instituicao: i for i in Instituicao.objects.all()}
    existing   = set(Repasse.objects.values_list('cod_emenda_id', 'cod_instituicao_id'))

    to_create = []
    total     = len(df)
    print(f"Iniciando importação de {total} repasses...")

    for i, row in enumerate(df.itertuples(index=False), start=1):
        ce, ci = row.cod_emenda, row.cod_instituicao

        if (ce, ci) in existing:
            print(f"[{i}/{total}] Já existe repasse ({ce}, {ci})")
            continue

        em   = em_cache.get(ce)
        inst = inst_cache.get(ci)

        if not em:
            print(f"[{i}/{total}] Emenda NÃO encontrada: {ce}")
        if not inst:
            print(f"[{i}/{total}] Instituição NÃO encontrada: {ci}")
        if not em or not inst:
            continue

        to_create.append(Repasse(
            cod_emenda=em,
            cod_instituicao=inst,
            possui_convenio=row.possui_convenio
        ))
        existing.add((ce, ci))
        print(f"[{i}/{total}] Agendado criação: ({ce}, {ci})")

    if to_create:
        with transaction.atomic():
            Repasse.objects.bulk_create(to_create)
        print(f"✅ {len(to_create)} repasses criados em lote.")
    else:
        print("✅ Nenhum repasse novo para criar.")

    # (se quiser manter seu relatório de chaves “faltantes” depois, basta recolher
    # pares_excel antes do dropna e comparar com os caches)

def importar_tudo():
    import_proponente()
    import_funcao()
    import_localidade()
    import_instituicao()
    import_programa()
    import_emenda()
    import_acao_orcamentaria()
    import_repasse()
    print("🎉 Importação completa!")

