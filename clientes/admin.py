# clientes/admin.py
from django.contrib import admin
from .models import Cliente

# ── Personalización global del Admin ────────────────────────────
admin.site.site_header = '📦 Sistema de Encomiendas'
admin.site.site_title  = 'Sistema de Encomiendas'
admin.site.index_title = 'Panel de Administración'


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ('dni', 'apellido', 'nombre', 'telefono', 'email')
    search_fields = ('dni', 'apellido', 'nombre', 'email')
    ordering      = ('apellido', 'nombre')
