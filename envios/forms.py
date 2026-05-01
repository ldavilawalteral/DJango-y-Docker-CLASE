# envios/forms.py
from django import forms
from .models import Encomienda
from config.choices import EstadoEnvio


class EncomiendaForm(forms.ModelForm):

    class Meta:
        model  = Encomienda
        fields = [
            'codigo', 'descripcion', 'peso_kg', 'volumen_cm3',
            'remitente', 'destinatario', 'ruta',
            'costo_envio', 'fecha_entrega_est', 'observaciones',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ENC-20240501-ABC123',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del paquete...',
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Ej: 2.50',
            }),
            'volumen_cm3': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Opcional',
            }),
            'remitente': forms.Select(attrs={'class': 'form-select'}),
            'destinatario': forms.Select(attrs={'class': 'form-select'}),
            'ruta': forms.Select(attrs={'class': 'form-select'}),
            'costo_envio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Costo en soles',
            }),
            'fecha_entrega_est': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones adicionales (opcional)...',
            }),
        }
        labels = {
            'codigo':           'Código de Encomienda',
            'descripcion':      'Descripción del paquete',
            'peso_kg':          'Peso (kg)',
            'volumen_cm3':      'Volumen (cm³)',
            'remitente':        'Remitente',
            'destinatario':     'Destinatario',
            'ruta':             'Ruta',
            'costo_envio':      'Costo de envío (S/.)',
            'fecha_entrega_est':'Fecha de entrega estimada',
            'observaciones':    'Observaciones',
        }


class CambiarEstadoForm(forms.Form):
    nuevo_estado = forms.ChoiceField(
        choices=EstadoEnvio.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Nuevo estado',
    )
    observacion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Observación del cambio (opcional)...',
        }),
        label='Observación',
    )
