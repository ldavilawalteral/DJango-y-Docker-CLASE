# envios/validators.py
import re
from django.core.exceptions import ValidationError


def validar_peso_positivo(value):
    """El peso debe ser estrictamente positivo."""
    if value <= 0:
        raise ValidationError('El peso debe ser un valor positivo mayor que 0.')


def validar_codigo_encomienda(value):
    """
    El código debe tener el formato ENC-YYYYMMDD-XXXXXX
    o simplemente ser alfanumérico con guiones (al menos 3 chars).
    """
    if len(value) < 3:
        raise ValidationError('El código debe tener al menos 3 caracteres.')
    if not re.match(r'^[A-Z0-9\-]+$', value.upper()):
        raise ValidationError(
            'El código solo puede contener letras mayúsculas, números y guiones.'
        )
