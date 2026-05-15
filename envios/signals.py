# envios/signals.py — Sesión 07: Disparadores reactivos via Django Signals
"""
Cuando se crea un HistorialEstado (cambio de estado en una Encomienda),
esta señal dispara automáticamente:
  1. stats_update  → actualiza todos los contadores del dashboard
  2. activity_update → agrega una entrada al feed de actividad lateral

Usamos async_to_sync porque channel_layer es asíncrono pero
post_save funciona en contexto síncrono.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from .consumers import DASHBOARD_GROUP, _get_stats


@receiver(post_save, sender='envios.HistorialEstado')
def notificar_cambio_estado(sender, instance, created, **kwargs):
    """
    Se dispara cada vez que se guarda un HistorialEstado.
    Solo actúa en creaciones (not updates) para evitar doble notificación.
    """
    if not created:
        return

    channel_layer = get_channel_layer()
    if channel_layer is None:
        # Redis no disponible — seguimos funcionando sin tiempo real
        return

    # ── 1. Actualizar estadísticas ────────────────────────────────
    try:
        stats = _get_stats()
        async_to_sync(channel_layer.group_send)(
            DASHBOARD_GROUP,
            {
                'type': 'stats_update',    # → DashboardConsumer.stats_update()
                'stats': stats,
            }
        )
    except Exception:
        # Si Redis falla, no interrumpir el flujo normal de Django
        pass

    # ── 2. Feed de actividad ──────────────────────────────────────
    try:
        encomienda = instance.encomienda
        empleado   = instance.empleado

        async_to_sync(channel_layer.group_send)(
            DASHBOARD_GROUP,
            {
                'type': 'activity_update',  # → DashboardConsumer.activity_update()
                'activity': {
                    'codigo':           encomienda.codigo,
                    'estado_anterior':  instance.get_estado_anterior_display(),
                    'estado_nuevo':     instance.get_estado_nuevo_display(),
                    'empleado':         empleado.nombre_completo() if empleado else '—',
                    'observacion':      instance.observacion or '',
                    'timestamp':        timezone.now().strftime('%H:%M:%S'),
                    'fecha':            timezone.now().strftime('%d/%m/%Y'),
                    'encomienda_id':    encomienda.pk,
                },
            }
        )
    except Exception:
        pass
