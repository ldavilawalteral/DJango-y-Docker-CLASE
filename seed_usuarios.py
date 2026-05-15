"""
seed_usuarios.py — Crea usuarios Django para cada empleado con permisos según su cargo.
Ejecutar dentro del contenedor:
  docker compose exec web python seed_usuarios.py
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from envios.models import Empleado, Encomienda, HistorialEstado
from clientes.models import Cliente
from rutas.models import Ruta

User = get_user_model()

print("\n👤 Sipán Trans — Creando usuarios y grupos de permisos...\n")

# ── 1. DEFINIR GRUPOS CON SUS PERMISOS ───────────────────────────────────────

# Obtenemos los content types necesarios
ct_encomienda    = ContentType.objects.get_for_model(Encomienda)
ct_historial     = ContentType.objects.get_for_model(HistorialEstado)
ct_cliente       = ContentType.objects.get_for_model(Cliente)
ct_ruta          = ContentType.objects.get_for_model(Ruta)
ct_empleado      = ContentType.objects.get_for_model(Empleado)

def get_perms(ct, codenames):
    return [Permission.objects.get(content_type=ct, codename=c) for c in codenames]

# Permisos estándar Django: add, change, delete, view
grupos_config = {
    # ── Administrador → prácticamente todo menos usuarios de sistema
    'Administrador': {
        'descripcion': 'Acceso total al sistema de encomiendas',
        'permisos': (
            get_perms(ct_encomienda, ['add_encomienda','change_encomienda','delete_encomienda','view_encomienda']) +
            get_perms(ct_historial,  ['add_historialestado','view_historialestado']) +
            get_perms(ct_cliente,    ['add_cliente','change_cliente','delete_cliente','view_cliente']) +
            get_perms(ct_ruta,       ['add_ruta','change_ruta','delete_ruta','view_ruta']) +
            get_perms(ct_empleado,   ['add_empleado','change_empleado','view_empleado'])
        ),
        'is_staff': True,
    },
    # ── Operador de Registro → puede crear y ver encomiendas y clientes, no borrar
    'Operador': {
        'descripcion': 'Registro de encomiendas y consulta de clientes',
        'permisos': (
            get_perms(ct_encomienda, ['add_encomienda','change_encomienda','view_encomienda']) +
            get_perms(ct_historial,  ['add_historialestado','view_historialestado']) +
            get_perms(ct_cliente,    ['add_cliente','view_cliente']) +
            get_perms(ct_ruta,       ['view_ruta'])
        ),
        'is_staff': False,
    },
    # ── Despachador → puede cambiar estado y ver todo, no crea clientes ni rutas
    'Despachador': {
        'descripcion': 'Despacho y cambio de estados de encomiendas',
        'permisos': (
            get_perms(ct_encomienda, ['change_encomienda','view_encomienda']) +
            get_perms(ct_historial,  ['add_historialestado','view_historialestado']) +
            get_perms(ct_cliente,    ['view_cliente']) +
            get_perms(ct_ruta,       ['view_ruta'])
        ),
        'is_staff': False,
    },
    # ── Supervisor de Rutas → administra rutas y ve todo, no modifica encomiendas directamente
    'SupervisorRutas': {
        'descripcion': 'Supervisión y gestión de rutas de transporte',
        'permisos': (
            get_perms(ct_encomienda, ['view_encomienda']) +
            get_perms(ct_historial,  ['view_historialestado']) +
            get_perms(ct_cliente,    ['view_cliente']) +
            get_perms(ct_ruta,       ['add_ruta','change_ruta','view_ruta']) +
            get_perms(ct_empleado,   ['view_empleado'])
        ),
        'is_staff': False,
    },
    # ── Chofer → solo puede ver encomiendas asignadas a sus rutas
    'Chofer': {
        'descripcion': 'Consulta de encomiendas en sus rutas asignadas',
        'permisos': (
            get_perms(ct_encomienda, ['view_encomienda']) +
            get_perms(ct_historial,  ['view_historialestado']) +
            get_perms(ct_ruta,       ['view_ruta'])
        ),
        'is_staff': False,
    },
}

grupos_creados = {}
for nombre, config in grupos_config.items():
    grupo, created = Group.objects.get_or_create(name=nombre)
    grupo.permissions.set(config['permisos'])
    grupo.save()
    grupos_creados[nombre] = (grupo, config['is_staff'])
    print(f"   {'✅ Creado' if created else '🔄 Actualizado'}: Grupo [{nombre}] — {len(config['permisos'])} permisos")

# ── 2. MAPEO CARGO → GRUPO ────────────────────────────────────────────────────
cargo_a_grupo = {
    'Administrador':       'Administrador',
    'Operador de Registro':'Operador',
    'Despachador':         'Despachador',
    'Supervisora de Rutas':'SupervisorRutas',
    'Chofer':              'Chofer',
}

# ── 3. USUARIOS POR EMPLEADO ──────────────────────────────────────────────────
print("\n👷 Creando/actualizando usuarios de empleados...\n")

empleados_usuarios = [
    # (dni_empleado,  username,       password,      )
    ('12345678',     'admin',         'admin123'     ),  # Walter - Administrador (ya existe)
    ('23456789',     'rosa.carrasco', 'sipan2026'    ),  # Rosa   - Operador
    ('34567890',     'marco.v',       'sipan2026'    ),  # Marco  - Despachador
    ('45678901',     'sofia.p',       'sipan2026'    ),  # Sofía  - Supervisora Rutas
    ('56789012',     'diego.n',       'sipan2026'    ),  # Diego  - Chofer
]

tabla_resumen = []

for dni, username, password in empleados_usuarios:
    try:
        empleado = Empleado.objects.get(dni=dni)
    except Empleado.DoesNotExist:
        print(f"   ⚠️  Empleado con DNI {dni} no encontrado. Saltando...")
        continue

    nombre_grupo = cargo_a_grupo.get(empleado.cargo)
    if not nombre_grupo:
        print(f"   ⚠️  Cargo desconocido: {empleado.cargo}. Saltando...")
        continue

    grupo, is_staff = grupos_creados[nombre_grupo]

    # Crear o actualizar usuario
    user, created = User.objects.get_or_create(username=username)
    user.first_name = empleado.nombre
    user.last_name  = empleado.apellido
    user.email      = empleado.email
    user.is_staff   = is_staff
    user.is_active  = True
    user.is_superuser = (username == 'admin')
    user.set_password(password)
    user.save()

    # Asignar grupo (reemplaza cualquier grupo anterior)
    user.groups.set([grupo])

    accion = '✅ Creado' if created else '🔄 Actualizado'
    print(f"   {accion}: {username}")
    print(f"           Empleado: {empleado.nombre_completo()}")
    print(f"           Cargo:    {empleado.cargo}")
    print(f"           Grupo:    {nombre_grupo}")
    print(f"           Staff:    {'Sí (acceso al Admin)' if is_staff else 'No'}")
    print()

    tabla_resumen.append({
        'username': username,
        'password': password,
        'empleado': empleado.nombre_completo(),
        'cargo':    empleado.cargo,
        'grupo':    nombre_grupo,
        'staff':    is_staff,
    })

# ── 4. TABLA RESUMEN ─────────────────────────────────────────────────────────
print("=" * 72)
print(f"{'USUARIO':<18} {'CONTRASEÑA':<12} {'CARGO':<22} {'GRUPO':<16} {'ADMIN'}")
print("=" * 72)
for u in tabla_resumen:
    admin_tag = '✓ Sí' if u['staff'] else '✗ No'
    print(f"{u['username']:<18} {u['password']:<12} {u['cargo']:<22} {u['grupo']:<16} {admin_tag}")
print("=" * 72)

print("\n📋 PERMISOS POR GRUPO:")
print("─" * 72)
permisos_desc = {
    'Administrador':  'Ver, crear, editar, eliminar: todo el sistema',
    'Operador':       'Ver, crear y editar encomiendas/clientes. NO eliminar',
    'Despachador':    'Ver todo y cambiar estado de encomiendas',
    'SupervisorRutas':'Ver todo, gestionar rutas (crear/editar)',
    'Chofer':         'Solo VER encomiendas e historial de sus rutas',
}
for g, desc in permisos_desc.items():
    print(f"  [{g}]: {desc}")

print("\n✅ Usuarios y permisos configurados correctamente.\n")
