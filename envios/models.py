# envios/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone

from config.choices import EstadoGeneral, EstadoEnvio
from clientes.models import Cliente
from rutas.models import Ruta
from .validators import validar_peso_positivo, validar_codigo_encomienda
from .querysets import EncomiendaQuerySet


# ─────────────────────────────────────────────────────────
#  Empleado
# ─────────────────────────────────────────────────────────

class Empleado(models.Model):

    dni           = models.CharField(max_length=8,  unique=True, verbose_name='DNI')
    codigo        = models.CharField(max_length=10, unique=True, verbose_name='Código')
    nombre        = models.CharField(max_length=100, verbose_name='Nombre')
    apellido      = models.CharField(max_length=100, verbose_name='Apellido')
    cargo         = models.CharField(max_length=100, verbose_name='Cargo')
    email         = models.EmailField(unique=True,  verbose_name='Email')
    telefono      = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')
    estado        = models.IntegerField(
        choices=EstadoGeneral.choices,
        default=EstadoGeneral.ACTIVO,
        verbose_name='Estado',
    )
    fecha_ingreso = models.DateField(verbose_name='Fecha de ingreso')

    # Un empleado puede gestionar varias rutas
    rutas_asignadas = models.ManyToManyField(
        'rutas.Ruta',
        blank=True,
        related_name='empleados_asignados',
        verbose_name='Rutas asignadas',
    )

    def nombre_completo(self):
        return f'{self.apellido}, {self.nombre}'

    def __str__(self):
        return f'{self.codigo} - {self.apellido}, {self.nombre}'

    class Meta:
        db_table            = 'empleados'
        verbose_name        = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering            = ['apellido', 'nombre']


# ─────────────────────────────────────────────────────────
#  Encomienda
# ─────────────────────────────────────────────────────────

class Encomienda(models.Model):

    # Manager personalizado
    objects = EncomiendaQuerySet.as_manager()

    # ── Identificación ─────────────────────────────────────
    codigo = models.CharField(
        max_length=20, unique=True,
        validators=[validar_codigo_encomienda],
        verbose_name='Código',
    )
    descripcion = models.TextField(verbose_name='Descripción')
    peso_kg = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[
            validar_peso_positivo,
            MinValueValidator(0.01, message='El peso mínimo es 0.01 kg'),
        ],
        verbose_name='Peso (kg)',
    )
    volumen_cm3 = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name='Volumen (cm³)',
    )

    # ── Relaciones ─────────────────────────────────────────
    remitente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='envios_como_remitente',
        verbose_name='Remitente',
    )
    destinatario = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='envios_como_destinatario',
        verbose_name='Destinatario',
    )
    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.PROTECT,
        related_name='encomiendas',
        verbose_name='Ruta',
    )
    empleado_registro = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name='encomiendas_registradas',
        verbose_name='Registrado por',
    )

    # ── Estado y costos ────────────────────────────────────
    estado = models.CharField(
        max_length=2,
        choices=EstadoEnvio.choices,
        default=EstadoEnvio.PENDIENTE,
        verbose_name='Estado',
    )
    costo_envio = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Costo de envío (S/.)',
    )

    # ── Fechas ─────────────────────────────────────────────
    fecha_envio        = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    fecha_entrega_est  = models.DateField(null=True, blank=True, verbose_name='Entrega estimada')
    fecha_entrega_real = models.DateField(null=True, blank=True, verbose_name='Entrega real')
    observaciones      = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    # ── Validaciones cruzadas ──────────────────────────────

    def clean(self):
        errors = {}

        if self.remitente_id and self.destinatario_id:
            if self.remitente_id == self.destinatario_id:
                errors['destinatario'] = ValidationError(
                    'El destinatario no puede ser el mismo que el remitente.'
                )

        if self.fecha_entrega_est:
            if self.fecha_entrega_est < timezone.now().date():
                errors['fecha_entrega_est'] = ValidationError(
                    'La fecha de entrega estimada no puede ser en el pasado.'
                )

        if self.fecha_entrega_est and self.fecha_entrega_real:
            if self.fecha_entrega_real < self.fecha_entrega_est:
                errors['fecha_entrega_real'] = ValidationError(
                    'La fecha de entrega real no puede ser anterior a la estimada.'
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ── Propiedades calculadas ─────────────────────────────

    @property
    def esta_entregada(self):
        return self.estado == EstadoEnvio.ENTREGADO

    @property
    def esta_en_transito(self):
        return self.estado == EstadoEnvio.EN_TRANSITO

    @property
    def dias_en_transito(self):
        if not self.fecha_envio:
            return 0
        return (timezone.now().date() - self.fecha_envio.date()).days

    @property
    def tiene_retraso(self):
        if not self.fecha_entrega_est or self.esta_entregada:
            return False
        return timezone.now().date() > self.fecha_entrega_est

    @property
    def descripcion_corta(self):
        return (self.descripcion[:50] + '...') if len(self.descripcion) > 50 else self.descripcion

    # ── Lógica de negocio ──────────────────────────────────

    def calcular_costo(self):
        """Precio base de ruta + S/. 2.50 por kg adicional sobre 5 kg."""
        PRECIO_POR_KG_EXTRA = 2.50
        PESO_BASE = 5.0
        costo = self.ruta.precio_base if hasattr(self.ruta, 'precio_base') else 0
        if self.peso_kg > PESO_BASE:
            costo += float(self.peso_kg - PESO_BASE) * PRECIO_POR_KG_EXTRA
        return round(costo, 2)

    def cambiar_estado(self, nuevo_estado, empleado, observacion=''):
        """Cambia el estado y registra automáticamente en HistorialEstado."""
        if nuevo_estado == self.estado:
            raise ValueError(
                f'La encomienda ya se encuentra en estado {self.get_estado_display()}'
            )

        estado_anterior = self.estado
        self.estado = nuevo_estado

        if nuevo_estado == EstadoEnvio.ENTREGADO:
            self.fecha_entrega_real = timezone.now().date()

        # Evitar doble full_clean en el save()
        super().save()

        HistorialEstado.objects.create(
            encomienda=self,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            empleado=empleado,
            observacion=observacion,
        )
        return self

    def __str__(self):
        return f'{self.codigo} [{self.get_estado_display()}]'

    class Meta:
        db_table            = 'encomiendas'
        verbose_name        = 'Encomienda'
        verbose_name_plural = 'Encomiendas'
        ordering            = ['-fecha_envio']


# ─────────────────────────────────────────────────────────
#  HistorialEstado
# ─────────────────────────────────────────────────────────

class HistorialEstado(models.Model):

    encomienda = models.ForeignKey(
        Encomienda,
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name='Encomienda',
    )
    estado_anterior = models.CharField(
        max_length=2, choices=EstadoEnvio.choices,
        verbose_name='Estado anterior',
    )
    estado_nuevo = models.CharField(
        max_length=2, choices=EstadoEnvio.choices,
        verbose_name='Estado nuevo',
    )
    observacion = models.TextField(blank=True, null=True, verbose_name='Observación')
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name='cambios_estado',
        verbose_name='Empleado',
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de cambio')

    def __str__(self):
        return (
            f'{self.encomienda.codigo}: '
            f'{self.get_estado_anterior_display()} → {self.get_estado_nuevo_display()}'
        )

    class Meta:
        db_table            = 'historial_estados'
        verbose_name        = 'Historial de estado'
        verbose_name_plural = 'Historial de estados'
        ordering            = ['-fecha_cambio']
