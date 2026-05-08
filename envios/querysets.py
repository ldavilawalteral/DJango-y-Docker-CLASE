# envios/querysets.py
from django.db import models
from django.utils import timezone


class EncomiendaQuerySet(models.QuerySet):

    def activas(self):
        """Encomiendas que no están entregadas ni devueltas."""
        return self.exclude(estado__in=['EN', 'DE'])

    def en_transito(self):
        """Encomiendas actualmente en tránsito."""
        return self.filter(estado='TR')

    def con_retraso(self):
        """
        Pendientes o en tránsito cuya fecha_entrega_est ya pasó.
        """
        return self.filter(
            estado__in=['PE', 'TR'],
            fecha_entrega_est__lt=timezone.now().date(),
        )

    def entregadas_hoy(self):
        """Encomiendas entregadas hoy."""
        return self.filter(
            estado='EN',
            fecha_entrega_real=timezone.now().date(),
        )

    def con_relaciones(self):
        """Prefetch de FK para evitar N+1 queries (uso general)."""
        return self.select_related(
            'remitente', 'destinatario', 'ruta', 'empleado_registro'
        )

    # ── Métodos optimizados para la API REST ───────────────────────

    def para_listado_api(self):
        """
        Optimización para el serializer de listado (EncomiendaSerializer).

        Problema N+1 sin optimización:
          - 1 query para obtener encomiendas
          - N queries para remitente (una por encomienda)
          - N queries para destinatario
          - N queries para ruta
          Total: 1 + 3N queries → con 100 encomiendas = 301 queries 🔴

        Con select_related + only():
          - 1 query con JOINs → siempre 1 query 🟢
        """
        return self.select_related(
            'remitente', 'destinatario', 'ruta'
        ).only(
            # Campos propios de Encomienda
            'id', 'codigo', 'descripcion', 'peso_kg', 'costo_envio',
            'estado', 'fecha_envio', 'fecha_entrega_est',
            # Campos de relaciones (se incluyen automáticamente con select_related)
            'remitente__id', 'remitente__nombre', 'remitente__apellido', 'remitente__dni',
            'remitente__telefono',
            'destinatario__id', 'destinatario__nombre', 'destinatario__apellido',
            'destinatario__dni', 'destinatario__telefono',
            'ruta__id', 'ruta__codigo', 'ruta__origen', 'ruta__destino',
            'ruta__precio_base', 'ruta__dias_entrega',
        )

    def para_detalle_api(self):
        """
        Optimización para el serializer de detalle (EncomiendaDetailSerializer).
        Incluye historial completo con prefetch_related.

        Sin optimización:
          - 1 query encomienda
          - N queries historial (una por entrada)
          - N queries empleado del historial
          Total: 1 + N + N queries 🔴

        Con select_related + prefetch_related:
          - 1 query encomienda + JOINs FK
          - 1 query historial
          - 1 query empleados del historial
          Total: siempre 3 queries fijas 🟢
        """
        from envios.models import HistorialEstado  # import local para evitar circular

        return self.select_related(
            'remitente', 'destinatario', 'ruta', 'empleado_registro'
        ).prefetch_related(
            models.Prefetch(
                'historial',
                queryset=HistorialEstado.objects.select_related('empleado')
                                                .order_by('-fecha_cambio'),
            )
        )
