# clientes/models.py
from django.db import models


class Cliente(models.Model):
    dni       = models.CharField(max_length=8, unique=True, verbose_name='DNI')
    nombre    = models.CharField(max_length=100, verbose_name='Nombre')
    apellido  = models.CharField(max_length=100, verbose_name='Apellido')
    telefono  = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')
    email     = models.EmailField(blank=True, verbose_name='Email')
    direccion = models.TextField(blank=True, verbose_name='Dirección')

    def nombre_completo(self):
        return f'{self.apellido}, {self.nombre}'

    def __str__(self):
        return f'{self.dni} - {self.apellido}, {self.nombre}'

    class Meta:
        db_table            = 'clientes'
        verbose_name        = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering            = ['apellido', 'nombre']
