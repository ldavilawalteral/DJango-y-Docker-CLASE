# rutas/models.py
from django.db import models
from django.core.validators import MinValueValidator


class Ruta(models.Model):
    codigo       = models.CharField(max_length=20, unique=True, verbose_name='Código')
    origen       = models.CharField(max_length=100, verbose_name='Origen')
    destino      = models.CharField(max_length=100, verbose_name='Destino')
    distancia_km = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        verbose_name='Distancia (km)',
    )
    precio_base  = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(0)],
        verbose_name='Precio base (S/.)',
    )
    dias_entrega = models.PositiveIntegerField(
        default=1,
        verbose_name='Días de entrega estimados',
    )
    activa = models.BooleanField(default=True, verbose_name='Activa')

    def __str__(self):
        return f'{self.codigo}: {self.origen} → {self.destino}'

    class Meta:
        db_table            = 'rutas'
        verbose_name        = 'Ruta'
        verbose_name_plural = 'Rutas'
        ordering            = ['codigo']
