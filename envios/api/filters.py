# envios/api/filters.py
"""
Filtros personalizados para la API de Encomiendas.

Uso desde la URL:
  /api/encomiendas/?estado=PE
  /api/encomiendas/?estado=TR&ruta=2
  /api/encomiendas/?peso_kg__gte=5&peso_kg__lte=20
  /api/encomiendas/?fecha_envio__date=2026-05-01
  /api/encomiendas/?search=ENC-001          ← búsqueda global
  /api/encomiendas/?ordering=-fecha_envio   ← ordenamiento
  /api/encomiendas/?con_retraso=true
"""
import django_filters
from django.utils import timezone

from envios.models import Encomienda
from config.choices import EstadoEnvio


class EncomiendaFilter(django_filters.FilterSet):

    # ── Por estado ─────────────────────────────────────────
    estado = django_filters.ChoiceFilter(
        choices=EstadoEnvio.choices,
        label='Estado',
    )

    # ── Por rango de peso ─────────────────────────────────
    peso_min = django_filters.NumberFilter(
        field_name='peso_kg', lookup_expr='gte', label='Peso mínimo (kg)'
    )
    peso_max = django_filters.NumberFilter(
        field_name='peso_kg', lookup_expr='lte', label='Peso máximo (kg)'
    )

    # ── Por rango de costo ─────────────────────────────────
    costo_min = django_filters.NumberFilter(
        field_name='costo_envio', lookup_expr='gte', label='Costo mínimo (S/.)'
    )
    costo_max = django_filters.NumberFilter(
        field_name='costo_envio', lookup_expr='lte', label='Costo máximo (S/.)'
    )

    # ── Por ruta / remitente / destinatario ───────────────
    ruta        = django_filters.NumberFilter(field_name='ruta__id',        label='ID de ruta')
    remitente   = django_filters.NumberFilter(field_name='remitente__id',   label='ID de remitente')
    destinatario= django_filters.NumberFilter(field_name='destinatario__id',label='ID de destinatario')

    # ── Por fechas ────────────────────────────────────────
    fecha_desde = django_filters.DateFilter(
        field_name='fecha_envio', lookup_expr='date__gte', label='Registrada desde'
    )
    fecha_hasta = django_filters.DateFilter(
        field_name='fecha_envio', lookup_expr='date__lte', label='Registrada hasta'
    )
    entrega_est_desde = django_filters.DateFilter(
        field_name='fecha_entrega_est', lookup_expr='gte', label='Entrega estimada desde'
    )
    entrega_est_hasta = django_filters.DateFilter(
        field_name='fecha_entrega_est', lookup_expr='lte', label='Entrega estimada hasta'
    )

    # ── Filtro booleano: ¿tiene retraso? ──────────────────
    con_retraso = django_filters.BooleanFilter(
        method='filtrar_con_retraso', label='Con retraso'
    )

    def filtrar_con_retraso(self, queryset, name, value):
        hoy = timezone.now().date()
        if value:
            return queryset.filter(
                fecha_entrega_est__lt=hoy,
                estado__in=[EstadoEnvio.PENDIENTE, EstadoEnvio.EN_TRANSITO],
            )
        return queryset.exclude(
            fecha_entrega_est__lt=hoy,
            estado__in=[EstadoEnvio.PENDIENTE, EstadoEnvio.EN_TRANSITO],
        )

    class Meta:
        model  = Encomienda
        fields = [
            'estado', 'ruta', 'remitente', 'destinatario',
            'peso_min', 'peso_max', 'costo_min', 'costo_max',
            'fecha_desde', 'fecha_hasta',
            'entrega_est_desde', 'entrega_est_hasta',
            'con_retraso',
        ]
