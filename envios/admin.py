# envios/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Empleado, Encomienda, HistorialEstado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display   = ('codigo', 'dni', 'apellido', 'nombre', 'cargo', 'email', 'telefono', 'estado')
    list_filter    = ('estado', 'cargo')
    search_fields  = ('dni', 'codigo', 'apellido', 'nombre', 'email')
    filter_horizontal = ('rutas_asignadas',)
    ordering       = ('apellido', 'nombre')


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display   = (
        'codigo', 'remitente', 'destinatario', 'ruta',
        'peso_kg', 'costo_envio', 'estado_badge',
        'fecha_envio', 'fecha_entrega_est', 'fecha_entrega_real',
    )
    list_filter    = ('estado', 'ruta')
    search_fields  = ('codigo', 'descripcion', 'remitente__apellido', 'destinatario__apellido')
    date_hierarchy = 'fecha_envio'
    ordering       = ('-fecha_envio',)
    readonly_fields = ('fecha_envio',)

    fieldsets = (
        ('📦 Paquete', {
            'fields': ('codigo', 'descripcion', 'peso_kg', 'volumen_cm3', 'observaciones'),
        }),
        ('👥 Partes', {
            'fields': ('remitente', 'destinatario', 'ruta', 'empleado_registro'),
        }),
        ('📊 Estado y Costos', {
            'fields': ('estado', 'costo_envio', 'fecha_envio', 'fecha_entrega_est', 'fecha_entrega_real'),
        }),
    )

    @admin.display(description='Estado', ordering='estado')
    def estado_badge(self, obj):
        colores = {
            'PE': ('#92400e', '#fef3c7'),
            'TR': ('#065f46', '#d1fae5'),
            'EN': ('#1e40af', '#dbeafe'),
            'DE': ('#991b1b', '#fee2e2'),
        }
        texto = obj.get_estado_display()
        fg, bg = colores.get(obj.estado, ('#374151', '#f3f4f6'))
        return format_html(
            '<span style="background:{bg};color:{fg};padding:.25em .75em;'
            'border-radius:2rem;font-size:.8rem;font-weight:600;">{texto}</span>',
            bg=bg, fg=fg, texto=texto,
        )


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display   = ('encomienda', 'estado_anterior', 'estado_nuevo', 'empleado', 'fecha_cambio', 'observacion')
    list_filter    = ('estado_nuevo',)
    search_fields  = ('encomienda__codigo',)
    date_hierarchy = 'fecha_cambio'
    ordering       = ('-fecha_cambio',)
    readonly_fields = ('fecha_cambio',)
