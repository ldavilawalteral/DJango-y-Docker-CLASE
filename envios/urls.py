# envios/urls.py
from django.urls import path
from . import views
from .views_auth import perfil_view

app_name = 'envios'

urlpatterns = [
    # Dashboard
    path('',
         views.home,
         name='home'),

    # Lista de encomiendas
    path('encomiendas/',
         views.EncomiendaListView.as_view(),
         name='encomienda-list'),

    # Nueva encomienda
    path('encomiendas/nueva/',
         views.encomienda_crear,
         name='encomienda-create'),

    # Detalle de encomienda
    path('encomiendas/<int:pk>/',
         views.encomienda_detalle,
         name='encomienda-detail'),

    # Cambiar estado de encomienda
    path('encomiendas/<int:pk>/cambiar-estado/',
         views.encomienda_cambiar_estado,
         name='encomienda-cambiar-estado'),

    # Perfil
    path('perfil/',
         perfil_view,
         name='perfil'),
]
