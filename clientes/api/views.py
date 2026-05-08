from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from clientes.models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Listado de clientes activos
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
