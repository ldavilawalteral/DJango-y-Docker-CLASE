"""
ASGI config for Sipán Trans — Sesión 07: Django Channels + WebSockets

Enruta:
  - HTTP  → get_asgi_application()     (Django normal)
  - WS    → DashboardConsumer          (tiempo real)
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Inicializar Django ANTES de importar channels/routing
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.auth import AuthMiddlewareStack              # noqa: E402
from envios.routing import websocket_urlpatterns           # noqa: E402

application = ProtocolTypeRouter({
    # Peticiones HTTP tradicionales
    'http': django_asgi_app,

    # Conexiones WebSocket — protegidas con sesión/auth de Django
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
