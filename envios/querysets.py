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
        """Prefetch de FK para evitar N+1 queries."""
        return self.select_related(
            'remitente', 'destinatario', 'ruta', 'empleado_registro'
        )
