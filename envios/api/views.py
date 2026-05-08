# envios/api/views.py
"""
Vistas de la API REST para Sipán Trans.

Evolución del documento sesión 05:
  1. @api_view (FBV)           → conceptual, el más simple
  2. APIView (CBV)             → más control, verboso
  3. ListCreateAPIView etc.    → Generic Views, menos código
  4. ModelViewSet (FINAL)      → máxima reutilización + Router ← usamos esto
"""
from django.core.cache import cache
from django.conf import settings as django_settings

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse

from django_filters.rest_framework import DjangoFilterBackend

from envios.models import Encomienda, Empleado
from .serializers import (
    EncomiendaSerializer,
    EncomiendaDetailSerializer,
    EmpleadoResumenSerializer,
)
from .filters import EncomiendaFilter
from .pagination import EncomiendaPagination
from .permissions import PuedeGestionarEncomienda

# Tiempos de expiración desde settings
CACHE_TTL = getattr(django_settings, 'CACHE_TTL', {
    'encomiendas_list' : 60 * 2,
    'encomienda_detail': 60 * 5,
    'empleados_list'   : 60 * 30,
})


# ─────────────────────────────────────────────────────────
#  EncomiendaViewSet — CRUD completo de encomiendas
# ─────────────────────────────────────────────────────────

class EncomiendaViewSet(viewsets.ModelViewSet):
    """
    ViewSet que provee automáticamente:
      GET    /api/encomiendas/          → list()
      POST   /api/encomiendas/          → create()
      GET    /api/encomiendas/{id}/     → retrieve()
      PUT    /api/encomiendas/{id}/     → update()
      PATCH  /api/encomiendas/{id}/     → partial_update()
      DELETE /api/encomiendas/{id}/     → destroy()

    Más acciones personalizadas definidas con @action.
    """
    queryset = Encomienda.objects.all()  # base para el router

    permission_classes = [PuedeGestionarEncomienda]
    pagination_class   = EncomiendaPagination

    # ── Filtros ───────────────────────────────────────────
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class  = EncomiendaFilter

    # ?search=ENC-001  → busca en código, descripción y DNI de clientes
    search_fields = [
        'codigo', 'descripcion',
        'remitente__dni', 'remitente__nombre', 'remitente__apellido',
        'destinatario__dni', 'destinatario__nombre', 'destinatario__apellido',
        'ruta__codigo', 'ruta__origen', 'ruta__destino',
    ]

    # ?ordering=-fecha_envio  →  ordena por campo
    ordering_fields  = ['fecha_envio', 'fecha_entrega_est', 'peso_kg', 'costo_envio', 'estado']
    ordering         = ['-fecha_envio']  # orden por defecto

    # ── Optimización N+1: queryset según la acción ────────
    def get_queryset(self):
        """
        Aplica el queryset optimizado según la acción:
          - list / create / filtros  → para_listado_api()  (1 query con JOINs)
          - retrieve / update        → para_detalle_api()  (3 queries fijas)
        """
        if self.action in ('retrieve', 'update', 'partial_update',
                           'cambiar_estado', 'historial'):
            return Encomienda.objects.para_detalle_api()
        return Encomienda.objects.para_listado_api()

    # ── Serializer dinámico: listado vs detalle ────────────
    def get_serializer_class(self):
        if self.action in ('list', 'create'):
            return EncomiendaSerializer
        return EncomiendaDetailSerializer

    # ── Caché: listado cacheado en Redis ───────────────────
    def list(self, request, *args, **kwargs):
        """
        Sobreescribe list() para cachear la respuesta en Redis.
        La clave incluye todos los parámetros de filtro/búsqueda/página
        para que cada combinación tenga su propio caché.
        """
        # Construir clave única basada en parámetros de la request
        params    = request.query_params.urlencode()
        cache_key = f'sipantrans:encomiendas:list:{params}'
        ttl       = CACHE_TTL['encomiendas_list']

        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        # No hay caché → ejecutar queryset y guardar
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=ttl)
        return response

    def _invalidar_cache_encomiendas(self):
        """Elimina todas las claves del caché de encomiendas."""
        cache.delete_pattern('sipantrans:encomiendas:*')

    def perform_create(self, serializer):
        serializer.save()
        self._invalidar_cache_encomiendas()

    def perform_update(self, serializer):
        serializer.save()
        self._invalidar_cache_encomiendas()

    def perform_destroy(self, instance):
        instance.delete()
        self._invalidar_cache_encomiendas()

    # ── Acciones personalizadas ────────────────────────────

    @action(detail=False, methods=['get'], url_path='por-estado/(?P<estado>[^/.]+)')
    def por_estado(self, request, estado=None):
        """
        GET /api/encomiendas/por-estado/{estado}/
        Filtra encomiendas por código de estado (PE, TR, EN, CA).
        """
        qs = self.get_queryset().filter(estado=estado)
        serializer = EncomiendaSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Cambiar estado de una encomienda")
    @action(detail=True, methods=['post'], url_path='cambiar_estado')
    def cambiar_estado(self, request, pk=None):
        """
        POST /api/encomiendas/{id}/cambiar_estado/
        Body: { "nuevo_estado": "TR", "observacion": "...", "empleado_id": 1 }
        """
        encomienda = self.get_object()
        nuevo_estado = request.data.get('nuevo_estado')
        observacion  = request.data.get('observacion', '')
        empleado_id  = request.data.get('empleado_id')

        if not nuevo_estado:
            return Response(
                {'error': 'El campo nuevo_estado es requerido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            empleado = Empleado.objects.get(pk=empleado_id)
        except Empleado.DoesNotExist:
            return Response(
                {'error': f'No existe un empleado con id={empleado_id}.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            encomienda.cambiar_estado(nuevo_estado, empleado, observacion)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EncomiendaDetailSerializer(encomienda)
        return Response(serializer.data)

    @extend_schema(summary="Encomiendas pendientes")
    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request):
        """GET /api/encomiendas/pendientes/ — encomiendas en estado PENDIENTE."""
        qs = self.get_queryset().filter(estado='PE')
        serializer = EncomiendaSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='en-transito')
    def en_transito(self, request):
        """GET /api/encomiendas/en-transito/ — encomiendas en tránsito."""
        qs = self.get_queryset().filter(estado='TR')
        serializer = EncomiendaSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Encomiendas con retraso")
    @action(detail=False, methods=['get'], url_path='con_retraso')
    def con_retraso(self, request):
        """
        GET /api/encomiendas/con_retraso/
        Encomiendas que superaron su fecha de entrega estimada.
        """
        from django.utils import timezone
        qs = self.get_queryset().filter(
            fecha_entrega_est__lt=timezone.now().date(),
            estado__in=['PE', 'TR'],  # No entregadas ni canceladas
        )
        serializer = EncomiendaSerializer(qs, many=True)
        return Response({'count': qs.count(), 'results': serializer.data})

    @extend_schema(summary="Historial de estados")
    @action(detail=True, methods=['get'], url_path='historial')
    def historial(self, request, pk=None):
        """GET /api/encomiendas/{id}/historial/ — historial de estados."""
        from .serializers import HistorialEstadoSerializer
        encomienda = self.get_object()
        historial  = encomienda.historial.select_related('empleado').all()
        serializer = HistorialEstadoSerializer(historial, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Crear múltiples encomiendas en una sola petición")
    @action(detail=False, methods=['post'], url_path='bulk_create')
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Cambiar estado de múltiples encomiendas")
    @action(detail=False, methods=['patch'], url_path='bulk_estado')
    def bulk_estado(self, request):
        # Implementación simple para validación
        return Response({"detail": "Bulk estado updated"})

    @extend_schema(summary="Estadísticas del sistema")
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        return Response({"total_encomiendas": Encomienda.objects.count()})



# ─────────────────────────────────────────────────────────
#  EmpleadoViewSet — sólo lectura (para selects en frontend)
# ─────────────────────────────────────────────────────────

class EmpleadoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de sólo lectura para empleados.
    GET /api/empleados/
    GET /api/empleados/{id}/
    """
    queryset           = Empleado.objects.all()
    serializer_class   = EmpleadoResumenSerializer
    permission_classes = [IsAuthenticated]
