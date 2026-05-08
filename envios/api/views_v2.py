from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from envios.models import Encomienda
from .serializers import EncomiendaSerializer

class EncomiendaViewSetV2(viewsets.ReadOnlyModelViewSet):
    """
    API v2 para encomiendas (Solo lectura por ahora).
    """
    queryset = Encomienda.objects.all()
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Encomienda.objects.para_listado_api()
