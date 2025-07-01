from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('dashboard/', views.dashboard_view, name="dashboard"),
    path('emendas_sem_repasses/', views.emendas_sem_repasses, name="emendas_sem_repasses"),
    path('instituicoes_acima_media/', views.instituicoes_acima_media, name="instituicoes_acima_media"),
    path('instituicoes_repasses_acima_media/', views.instituicoes_repasses_acima_media, name="instituicoes_repasses_acima_media"),
    path('ranking_proponentes/', views.ranking_proponentes, name="ranking_proponentes"),
    path('emendas/', views.emendas_list, name="emendas_list"),
    path('emenda/<int:cod_emenda>/', views.emenda_detail, name="emenda_detail"),
]
