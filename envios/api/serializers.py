# envios/api/serializers.py
from rest_framework import serializers

from envios.models import Encomienda, Empleado, HistorialEstado
from clientes.models import Cliente
from rutas.models import Ruta


# ─────────────────────────────────────────────────────────
#  Serializers de apoyo (nested / read-only)
# ─────────────────────────────────────────────────────────

class ClienteResumenSerializer(serializers.ModelSerializer):
    """Representación resumida de un cliente para incluir en encomiendas."""
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model  = Cliente
        fields = ['id', 'nombre_completo', 'dni', 'telefono']

    def get_nombre_completo(self, obj):
        return obj.nombre_completo()


class RutaResumenSerializer(serializers.ModelSerializer):
    """Representación resumida de una ruta."""

    class Meta:
        model  = Ruta
        fields = ['id', 'codigo', 'origen', 'destino', 'precio_base', 'dias_entrega']


class EmpleadoResumenSerializer(serializers.ModelSerializer):
    """Representación resumida de un empleado."""
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model  = Empleado
        fields = ['id', 'nombre_completo', 'codigo', 'cargo']

    def get_nombre_completo(self, obj):
        return obj.nombre_completo()


class HistorialEstadoSerializer(serializers.ModelSerializer):
    """Historial de cambios de estado de una encomienda."""
    estado_anterior_display = serializers.CharField(
        source='get_estado_anterior_display', read_only=True
    )
    estado_nuevo_display = serializers.CharField(
        source='get_estado_nuevo_display', read_only=True
    )
    empleado = EmpleadoResumenSerializer(read_only=True)

    class Meta:
        model  = HistorialEstado
        fields = [
            'id', 'estado_anterior', 'estado_anterior_display',
            'estado_nuevo', 'estado_nuevo_display',
            'empleado', 'observacion', 'fecha_cambio',
        ]


# ─────────────────────────────────────────────────────────
#  EncomiendaSerializer — para listados
# ─────────────────────────────────────────────────────────

class EncomiendaSerializer(serializers.ModelSerializer):
    """
    Serializer de listado: muestra datos esenciales con representaciones
    legibles del estado y las relaciones como IDs + nombre resumido.
    """
    estado_display       = serializers.CharField(source='get_estado_display', read_only=True)
    remitente_nombre     = serializers.SerializerMethodField()
    destinatario_nombre  = serializers.SerializerMethodField()
    ruta_nombre          = serializers.SerializerMethodField()
    tiene_retraso        = serializers.BooleanField(read_only=True)
    dias_en_transito     = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Encomienda
        fields = [
            'id', 'codigo', 'descripcion_corta', 'peso_kg', 'costo_envio',
            'estado', 'estado_display',
            'remitente', 'remitente_nombre',
            'destinatario', 'destinatario_nombre',
            'ruta', 'ruta_nombre',
            'fecha_envio', 'fecha_entrega_est',
            'tiene_retraso', 'dias_en_transito',
        ]

    def get_remitente_nombre(self, obj):
        c = obj.remitente
        return f'{c.apellido}, {c.nombre}' if hasattr(c, 'apellido') else str(c)

    def get_destinatario_nombre(self, obj):
        c = obj.destinatario
        return f'{c.apellido}, {c.nombre}' if hasattr(c, 'apellido') else str(c)

    def get_ruta_nombre(self, obj):
        r = obj.ruta
        return f'{r.codigo}: {r.origen} → {r.destino}'


# ─────────────────────────────────────────────────────────
#  EncomiendaDetailSerializer — para detalle / escritura
# ─────────────────────────────────────────────────────────

class EncomiendaDetailSerializer(serializers.ModelSerializer):
    """
    Serializer de detalle: incluye objetos anidados para lectura
    y acepta IDs para escritura (crear / actualizar).
    """
    # Campos de lectura (nested)
    remitente_detalle    = ClienteResumenSerializer(source='remitente',         read_only=True)
    destinatario_detalle = ClienteResumenSerializer(source='destinatario',      read_only=True)
    ruta_detalle         = RutaResumenSerializer(source='ruta',                 read_only=True)
    empleado_detalle     = EmpleadoResumenSerializer(source='empleado_registro', read_only=True)
    historial            = HistorialEstadoSerializer(many=True, read_only=True)

    # Campos de sólo lectura calculados
    estado_display   = serializers.CharField(source='get_estado_display',  read_only=True)
    esta_entregada   = serializers.BooleanField(read_only=True)
    tiene_retraso    = serializers.BooleanField(read_only=True)
    dias_en_transito = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Encomienda
        fields = [
            # Identificación
            'id', 'codigo', 'descripcion', 'peso_kg', 'volumen_cm3',
            # Relaciones (IDs para escritura)
            'remitente', 'remitente_detalle',
            'destinatario', 'destinatario_detalle',
            'ruta', 'ruta_detalle',
            'empleado_registro', 'empleado_detalle',
            # Estado y costos
            'estado', 'estado_display', 'costo_envio',
            # Fechas
            'fecha_envio', 'fecha_entrega_est', 'fecha_entrega_real',
            'observaciones',
            # Propiedades calculadas
            'esta_entregada', 'tiene_retraso', 'dias_en_transito',
            # Historial
            'historial',
        ]
        read_only_fields = ['fecha_envio']

    def validate(self, data):
        """Validaciones cruzadas a nivel de serializer."""
        remitente    = data.get('remitente',    getattr(self.instance, 'remitente',    None))
        destinatario = data.get('destinatario', getattr(self.instance, 'destinatario', None))

        if remitente and destinatario and remitente == destinatario:
            raise serializers.ValidationError(
                {'destinatario': 'El destinatario no puede ser el mismo que el remitente.'}
            )
        return data
