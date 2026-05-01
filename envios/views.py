# envios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, DetailView

from config.choices import EstadoEnvio
from .models import Encomienda, Empleado, HistorialEstado
from .forms import EncomiendaForm, CambiarEstadoForm


# ─────────────────────────────────────────────────────────
#  Dashboard / Home
# ─────────────────────────────────────────────────────────

@login_required
def home(request):
    """Vista principal del sistema con estadísticas."""
    hoy = timezone.now().date()

    context = {
        'total':          Encomienda.objects.count(),
        'pendientes':     Encomienda.objects.filter(estado=EstadoEnvio.PENDIENTE).count(),
        'en_transito':    Encomienda.objects.en_transito().count(),
        'entregados':     Encomienda.objects.filter(estado=EstadoEnvio.ENTREGADO).count(),
        'con_retraso':    Encomienda.objects.con_retraso().count(),
        'entregadas_hoy': Encomienda.objects.filter(
                              estado=EstadoEnvio.ENTREGADO,
                              fecha_entrega_real=hoy,
                          ).count(),
        'ultimas':        Encomienda.objects.con_relaciones()[:5],
        'EstadoEnvio':    EstadoEnvio,
    }
    return render(request, 'dashboard.html', context)


# ─────────────────────────────────────────────────────────
#  Lista de encomiendas (CBV con filtro por estado)
# ─────────────────────────────────────────────────────────

class EncomiendaListView(LoginRequiredMixin, ListView):
    model               = Encomienda
    template_name       = 'lista.html'
    context_object_name = 'encomiendas'
    paginate_by         = 15

    def get_queryset(self):
        qs     = Encomienda.objects.con_relaciones().order_by('-fecha_envio')
        estado = self.request.GET.get('estado', '')
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['estado_actual']  = self.request.GET.get('estado', '')
        ctx['estado_choices'] = EstadoEnvio.choices
        ctx['EstadoEnvio']    = EstadoEnvio
        return ctx


# ─────────────────────────────────────────────────────────
#  Detalle de encomienda
# ─────────────────────────────────────────────────────────

@login_required
def encomienda_detalle(request, pk):
    """Muestra toda la info de la encomienda y su historial de estados."""
    encomienda = get_object_or_404(
        Encomienda.objects.con_relaciones().prefetch_related('historial__empleado'),
        pk=pk,
    )
    historial   = encomienda.historial.order_by('-fecha_cambio')
    form_estado = CambiarEstadoForm()

    return render(request, 'detalle.html', {
        'encomienda':  encomienda,
        'historial':   historial,
        'form_estado': form_estado,
        'EstadoEnvio': EstadoEnvio,
    })


# ─────────────────────────────────────────────────────────
#  Crear encomienda
# ─────────────────────────────────────────────────────────

@login_required
def encomienda_crear(request):
    """
    GET  → muestra formulario vacío
    POST → valida, guarda y redirige al detalle
    El empleado_registro se asigna por email del usuario logueado.
    """
    if request.method == 'POST':
        form = EncomiendaForm(request.POST)
        if form.is_valid():
            try:
                enc = form.save(commit=False)
                enc.empleado_registro = Empleado.objects.get(email=request.user.email)
                enc.save()
                messages.success(
                    request,
                    f'✅ Encomienda <strong>{enc.codigo}</strong> registrada correctamente.',
                    extra_tags='safe',
                )
                return redirect('envios:encomienda-detail', pk=enc.pk)
            except Empleado.DoesNotExist:
                messages.error(
                    request,
                    f'⚠️ No existe un Empleado con el email "{request.user.email}". '
                    'Créalo en el panel de administración primero.',
                )
        else:
            messages.error(request, '❌ Por favor corrige los errores del formulario.')
    else:
        form = EncomiendaForm()

    return render(request, 'form.html', {'form': form, 'titulo': 'Nueva Encomienda'})


# ─────────────────────────────────────────────────────────
#  Cambiar estado de encomienda
# ─────────────────────────────────────────────────────────

@login_required
def encomienda_cambiar_estado(request, pk):
    """Cambia el estado y registra en el historial. Solo acepta POST."""
    encomienda = get_object_or_404(Encomienda, pk=pk)

    if request.method == 'POST':
        form = CambiarEstadoForm(request.POST)
        if form.is_valid():
            nuevo_estado = form.cleaned_data['nuevo_estado']
            observacion  = form.cleaned_data.get('observacion', '')

            try:
                empleado = Empleado.objects.get(email=request.user.email)
            except Empleado.DoesNotExist:
                empleado = Empleado.objects.filter(estado=1).first()

            if not empleado:
                messages.error(request, 'No hay empleados registrados para registrar el cambio.')
                return redirect('envios:encomienda-detail', pk=pk)

            try:
                encomienda.cambiar_estado(nuevo_estado, empleado=empleado, observacion=observacion)
                messages.success(
                    request,
                    f'✅ Estado actualizado a "<strong>{encomienda.get_estado_display()}</strong>".',
                    extra_tags='safe',
                )
            except ValueError as e:
                messages.warning(request, str(e))

    return redirect('envios:encomienda-detail', pk=pk)
