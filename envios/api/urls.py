# envios/api/urls.py
"""
Router de la API REST.

El DefaultRouter registra automáticamente:
  /api/encomiendas/                    → list, create
  /api/encomiendas/{id}/               → retrieve, update, partial_update, destroy
  /api/encomiendas/pendientes/         → @action
  /api/encomiendas/en-transito/        → @action
  /api/encomiendas/con-retraso/        → @action
  /api/encomiendas/por-estado/{est}/   → @action
  /api/encomiendas/{id}/cambiar-estado/→ @action
  /api/encomiendas/{id}/historial/     → @action
  /api/empleados/                      → list
  /api/empleados/{id}/                 → retrieve
  /api/                                → raíz navegable (BrowsableAPI)
"""
from rest_framework.routers import DefaultRouter
from .views import EncomiendaViewSet, EmpleadoViewSet

router = DefaultRouter()
router.register(r'encomiendas', EncomiendaViewSet, basename='encomienda')
router.register(r'empleados',   EmpleadoViewSet,   basename='empleado')

urlpatterns = router.urls
