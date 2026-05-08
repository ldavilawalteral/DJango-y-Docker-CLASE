from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rutas.models import Ruta
from .serializers import RutaSerializer

class RutaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Rutas disponibles
    """
    queryset = Ruta.objects.filter(activa=True)
    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticated]
