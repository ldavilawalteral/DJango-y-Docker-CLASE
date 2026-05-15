# envios/consumers.py — Sesión 07: WebSocket Consumer para el Dashboard
"""
DashboardConsumer:
- Grupo "dashboard": todos los clientes conectados al dashboard comparten este canal
- Al conectarse: recibe estadísticas actuales inmediatamente
- Al desconectarse: abandona el grupo limpiamente
- stats_update: re-envía el payload de estadísticas al cliente JS
- activity_update: re-envía eventos de cambio de estado al feed lateral
"""

import json
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone

from config.choices import EstadoEnvio


DASHBOARD_GROUP = 'dashboard'


def _get_stats():
    """Calcula y devuelve las estadísticas actualizadas desde la base de datos."""
    # Importación local para evitar problemas al inicio de la app
    from envios.models import Encomienda

    hoy = timezone.now().date()
    return {
        'total':          Encomienda.objects.count(),
        'pendientes':     Encomienda.objects.filter(estado=EstadoEnvio.PENDIENTE).count(),
        'en_transito':    Encomienda.objects.en_transito().count(),
        'entregados':     Encomienda.objects.filter(estado=EstadoEnvio.ENTREGADO).count(),
        'con_retraso':    Encomienda.objects.con_retraso().count(),
        'entregadas_hoy': Encomienda.objects.filter(
                              estado=EstadoEnvio.ENTREGADO,
                              fecha_entrega_real=hoy,
                          ).count(),
    }


class DashboardConsumer(JsonWebsocketConsumer):
    """Consumer síncrono para el dashboard en tiempo real."""

    # ── Ciclo de vida de la conexión ──────────────────────────────

    def connect(self):
        """El cliente abre el WebSocket."""
        # Solo usuarios autenticados pueden conectarse
        if not self.scope['user'].is_authenticated:
            self.close()
            return

        # Unir al grupo global "dashboard"
        async_to_sync(self.channel_layer.group_add)(
            DASHBOARD_GROUP,
            self.channel_name,
        )
        self.accept()

        # Enviar estadísticas actuales inmediatamente al conectar
        self.send_json({
            'type': 'stats_update',
            'stats': _get_stats(),
        })

    def disconnect(self, close_code):
        """El cliente cierra el WebSocket."""
        async_to_sync(self.channel_layer.group_discard)(
            DASHBOARD_GROUP,
            self.channel_name,
        )

    def receive_json(self, content, **kwargs):
        """El cliente puede solicitar refresh manual enviando {"action": "refresh"}."""
        if content.get('action') == 'refresh':
            self.send_json({
                'type': 'stats_update',
                'stats': _get_stats(),
            })

    # ── Manejadores de eventos del grupo ─────────────────────────
    # Estos métodos son llamados por channel_layer.group_send()
    # El nombre del método = type del evento con '.' reemplazado por '_'

    def stats_update(self, event):
        """Reenvía actualización de estadísticas al cliente WebSocket."""
        self.send_json(event)

    def activity_update(self, event):
        """Reenvía un evento de cambio de estado al feed de actividad."""
        self.send_json(event)
