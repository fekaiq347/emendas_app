from django.contrib import admin
from .models import (
    Proponente, Funcao, Localidade,
    Instituicao, Emenda, AcaoOrcamentaria, Repasse
)

admin.site.register(Proponente)
admin.site.register(Funcao)
admin.site.register(Localidade)
admin.site.register(Instituicao)
admin.site.register(Emenda)
admin.site.register(AcaoOrcamentaria)
admin.site.register(Repasse)

