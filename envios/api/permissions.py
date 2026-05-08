# envios/api/permissions.py
"""
Permisos personalizados para la API de Sipán Trans.

Jerarquía aplicada:
  - Admin (is_staff)     → acceso total (CRUD)
  - Autenticado          → lectura + cambiar estado (no borrar)
  - Anónimo              → ningún acceso
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class EsSoloLectura(BasePermission):
    """Permite cualquier método seguro (GET, HEAD, OPTIONS) a cualquier usuario."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class EsAdminOSoloLectura(BasePermission):
    """
    - Admin (is_staff) → todo permitido
    - Autenticado      → sólo lectura
    - Anónimo          → denegado
    """
    message = 'Necesita ser administrador para modificar encomiendas.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff


class PuedeGestionarEncomienda(BasePermission):
    """
    Permiso específico para encomiendas:
      - GET / HEAD / OPTIONS  → cualquier usuario autenticado
      - POST (crear)          → usuario autenticado
      - PATCH cambiar-estado  → usuario autenticado
      - PUT / DELETE          → sólo is_staff
    """
    message = 'No tiene permisos suficientes para esta operación.'

    def has_permission(self, request, view):
        # Sin autenticar → siempre denegado
        if not request.user or not request.user.is_authenticated:
            return False

        # Lectura → cualquier autenticado
        if request.method in SAFE_METHODS:
            return True

        # Acción cambiar-estado → cualquier autenticado
        if view.action == 'cambiar_estado':
            return True

        # Crear → cualquier autenticado
        if view.action == 'create':
            return True

        # Actualizar / Borrar → sólo staff
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        """Permiso a nivel de objeto (un registro concreto)."""
        if request.method in SAFE_METHODS:
            return True
        # Sólo staff puede modificar o borrar un objeto concreto
        return request.user.is_staff
