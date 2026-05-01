# envios/views_auth.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def perfil_view(request):
    """Vista del perfil del usuario/empleado logueado."""
    return render(request, 'accounts/register.html', {
        'user': request.user,
    })
