from rest_framework.routers import DefaultRouter
from envios.api.views import EncomiendaViewSet
from envios.api.views_v2 import EncomiendaViewSetV2
from clientes.api.views import ClienteViewSet
from rutas.api.views import RutaViewSet

# Router v1
router_v1 = DefaultRouter()
router_v1.register(r'encomiendas', EncomiendaViewSet, basename='v1-encomiendas')
router_v1.register(r'clientes', ClienteViewSet, basename='v1-clientes')
router_v1.register(r'rutas', RutaViewSet, basename='v1-rutas')

# Router v2
router_v2 = DefaultRouter()
router_v2.register(r'encomiendas', EncomiendaViewSetV2, basename='v2-encomiendas')
