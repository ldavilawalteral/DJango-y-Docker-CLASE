# envios/routing.py — Sesión 07: WebSocket URL patterns
from django.urls import path
from .consumers import DashboardConsumer

websocket_urlpatterns = [
    # ws://localhost:8000/ws/dashboard/
    path('ws/dashboard/', DashboardConsumer.as_asgi()),
]
