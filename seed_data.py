"""
seed_data.py — Script de carga de datos de prueba para Sipán Trans
Ejecutar dentro del contenedor:
  docker compose exec web python seed_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

from clientes.models import Cliente
from rutas.models import Ruta
from envios.models import Empleado, Encomienda, HistorialEstado
from config.choices import EstadoGeneral, EstadoEnvio

User = get_user_model()

print("\n🚚 Sipán Trans — Cargando datos de prueba...\n")

# ── 1. RUTAS ──────────────────────────────────────────────────────────────────
print("📍 Creando rutas...")
rutas_data = [
    dict(codigo='RT-001', origen='Chiclayo', destino='Lima',      distancia_km=770, precio_base=35.00, dias_entrega=1),
    dict(codigo='RT-002', origen='Chiclayo', destino='Trujillo',  distancia_km=209, precio_base=18.00, dias_entrega=1),
    dict(codigo='RT-003', origen='Chiclayo', destino='Piura',     distancia_km=245, precio_base=20.00, dias_entrega=1),
    dict(codigo='RT-004', origen='Chiclayo', destino='Cajamarca', distancia_km=262, precio_base=22.00, dias_entrega=1),
    dict(codigo='RT-005', origen='Chiclayo', destino='Chimbote',  distancia_km=370, precio_base=25.00, dias_entrega=1),
    dict(codigo='RT-006', origen='Chiclayo', destino='Ica',       distancia_km=960, precio_base=42.00, dias_entrega=2),
    dict(codigo='RT-007', origen='Lima',     destino='Chiclayo',  distancia_km=770, precio_base=35.00, dias_entrega=1),
    dict(codigo='RT-008', origen='Trujillo', destino='Chiclayo',  distancia_km=209, precio_base=18.00, dias_entrega=1),
    dict(codigo='RT-009', origen='Chiclayo', destino='Huaraz',    distancia_km=480, precio_base=30.00, dias_entrega=2),
    dict(codigo='RT-010', origen='Chiclayo', destino='Tumbes',    distancia_km=440, precio_base=28.00, dias_entrega=1),
]
rutas = {}
for d in rutas_data:
    r, created = Ruta.objects.get_or_create(codigo=d['codigo'], defaults=d)
    rutas[d['codigo']] = r
    print(f"   {'✅ Creada' if created else '⏭  Ya existe'}: {r}")

# ── 2. CLIENTES ───────────────────────────────────────────────────────────────
print("\n👥 Creando clientes...")
clientes_data = [
    dict(dni='45612378', nombre='Carlos',   apellido='Mendoza Ríos',     telefono='944123456', email='carlos.mendoza@gmail.com',    direccion='Av. Balta 320, Chiclayo'),
    dict(dni='73491028', nombre='María',    apellido='García López',     telefono='966234567', email='maria.garcia@hotmail.com',     direccion='Calle San José 145, Trujillo'),
    dict(dni='62841095', nombre='Juan',     apellido='Pérez Torres',     telefono='912345678', email='juan.perez@yahoo.com',         direccion='Jr. Amazonas 890, Lima'),
    dict(dni='51234089', nombre='Ana',      apellido='Rodríguez Vargas', telefono='955678901', email='ana.rodriguez@gmail.com',      direccion='Av. Grau 567, Piura'),
    dict(dni='81723640', nombre='Luis',     apellido='Flores Castillo',  telefono='934567890', email='luis.flores@outlook.com',      direccion='Calle Las Flores 234, Cajamarca'),
    dict(dni='71293847', nombre='Rosa',     apellido='Vásquez Sánchez',  telefono='978901234', email='rosa.vasquez@gmail.com',       direccion='Jr. Junín 678, Chiclayo'),
    dict(dni='60912847', nombre='Pedro',    apellido='Díaz Morales',     telefono='923456789', email='pedro.diaz@gmail.com',         direccion='Av. Salaverry 1200, Lima'),
    dict(dni='82716349', nombre='Carmen',   apellido='Torres Huamán',    telefono='967890123', email='carmen.torres@hotmail.com',    direccion='Urb. Santa Victoria 89, Chiclayo'),
    dict(dni='70284619', nombre='Roberto',  apellido='Castro Medina',    telefono='945678901', email='roberto.castro@gmail.com',     direccion='Av. España 456, Trujillo'),
    dict(dni='91827364', nombre='Patricia', apellido='Ramírez Chávez',   telefono='912876543', email='patricia.ramirez@yahoo.com',   direccion='Calle Los Álamos 12, Ica'),
    dict(dni='52901837', nombre='Miguel',   apellido='Sánchez Quispe',   telefono='956712345', email='miguel.sanchez@gmail.com',     direccion='Jr. Libertad 345, Piura'),
    dict(dni='63748291', nombre='Elena',    apellido='Herrera Paredes',  telefono='931234567', email='elena.herrera@outlook.com',    direccion='Av. Pardo 789, Chiclayo'),
    dict(dni='74839201', nombre='Jorge',    apellido='Quispe Mamani',    telefono='976543210', email='jorge.quispe@gmail.com',       direccion='Calle Ucayali 23, Lima'),
    dict(dni='85920374', nombre='Lucía',    apellido='Mendoza Campos',   telefono='942109876', email='lucia.mendoza@hotmail.com',    direccion='Urb. Miraflores 67, Chiclayo'),
    dict(dni='96031485', nombre='Fernando', apellido='López Gutiérrez',  telefono='967890456', email='fernando.lopez@gmail.com',     direccion='Av. Tacna 890, Lima'),
]
clientes = []
for d in clientes_data:
    c, created = Cliente.objects.get_or_create(dni=d['dni'], defaults=d)
    clientes.append(c)
    print(f"   {'✅ Creado' if created else '⏭  Ya existe'}: {c}")

# ── 3. EMPLEADOS ──────────────────────────────────────────────────────────────
print("\n👷 Creando empleados...")
admin_user, _ = User.objects.get_or_create(username='admin')
admin_user.set_password('admin123')
admin_user.is_superuser = True
admin_user.is_staff = True
admin_user.email = 'admin@sipantrans.com'
admin_user.save()

empleados_data = [
    dict(dni='12345678', codigo='EMP-001', nombre='Walter',  apellido='Llata Torres',
         cargo='Administrador', email='admin@sipantrans.com',
         telefono='944000001', estado=EstadoGeneral.ACTIVO, fecha_ingreso=date(2022, 1, 15)),
    dict(dni='23456789', codigo='EMP-002', nombre='Rosa',    apellido='Carrasco Díaz',
         cargo='Operador de Registro', email='rosa.carrasco@sipantrans.com',
         telefono='944000002', estado=EstadoGeneral.ACTIVO, fecha_ingreso=date(2022, 3, 1)),
    dict(dni='34567890', codigo='EMP-003', nombre='Marco',   apellido='Villalobos Soto',
         cargo='Despachador', email='marco.villalobos@sipantrans.com',
         telefono='944000003', estado=EstadoGeneral.ACTIVO, fecha_ingreso=date(2023, 6, 10)),
    dict(dni='45678901', codigo='EMP-004', nombre='Sofía',   apellido='Paredes Linares',
         cargo='Supervisora de Rutas', email='sofia.paredes@sipantrans.com',
         telefono='944000004', estado=EstadoGeneral.ACTIVO, fecha_ingreso=date(2021, 8, 20)),
    dict(dni='56789012', codigo='EMP-005', nombre='Diego',   apellido='Núñez Cabellos',
         cargo='Chofer', email='diego.nunez@sipantrans.com',
         telefono='944000005', estado=EstadoGeneral.ACTIVO, fecha_ingreso=date(2023, 2, 14)),
]
empleados = []
for d in empleados_data:
    e, created = Empleado.objects.get_or_create(dni=d['dni'], defaults=d)
    empleados.append(e)
    print(f"   {'✅ Creado' if created else '⏭  Ya existe'}: {e}")

emp_principal = empleados[0]  # Walter — admin

# Asignar rutas a empleados
empleados[0].rutas_asignadas.set([rutas['RT-001'], rutas['RT-002'], rutas['RT-003']])
empleados[3].rutas_asignadas.set([rutas['RT-004'], rutas['RT-005'], rutas['RT-006']])
empleados[4].rutas_asignadas.set([rutas['RT-007'], rutas['RT-008']])

# ── 4. ENCOMIENDAS ────────────────────────────────────────────────────────────
print("\n📦 Creando encomiendas...")
hoy = timezone.now().date()
# Usamos fecha futura para pasar la validación; luego actualizamos con UPDATE directo
fecha_valida = hoy + timedelta(days=5)

def crear_encomienda(codigo, descripcion, peso_kg, costo_envio,
                     remitente, destinatario, ruta,
                     estado_final, fecha_est_real, fecha_entrega_real=None):
    """Crea una encomienda saltando la validación de fechas históricas."""
    try:
        enc = Encomienda.objects.get(codigo=codigo)
        print(f"   ⏭  Ya existe: {codigo}")
        return enc
    except Encomienda.DoesNotExist:
        pass

    # Crear con fecha futura válida, luego actualizamos
    enc = Encomienda(
        codigo=codigo, descripcion=descripcion,
        peso_kg=peso_kg, costo_envio=costo_envio,
        remitente=remitente, destinatario=destinatario,
        ruta=ruta, empleado_registro=emp_principal,
        estado=EstadoEnvio.PENDIENTE,
        fecha_entrega_est=fecha_valida,  # fecha válida para pasar validación
    )
    # super().save() directo para no llamar full_clean
    super(Encomienda, enc).save()

    # Corregir la fecha estimada real con UPDATE (sin pasar por validación)
    Encomienda.objects.filter(pk=enc.pk).update(fecha_entrega_est=fecha_est_real)
    enc.fecha_entrega_est = fecha_est_real

    # Avanzar estados con historial
    pasos = {
        EstadoEnvio.EN_TRANSITO: [EstadoEnvio.EN_TRANSITO],
        EstadoEnvio.ENTREGADO:   [EstadoEnvio.EN_TRANSITO, EstadoEnvio.ENTREGADO],
        EstadoEnvio.DEVUELTO:    [EstadoEnvio.EN_TRANSITO, EstadoEnvio.DEVUELTO],
    }
    for nuevo in pasos.get(estado_final, []):
        try:
            enc.cambiar_estado(nuevo, empleado=emp_principal,
                               observacion=f'Registro de estado {enc.get_estado_display()}')
        except ValueError:
            pass

    if fecha_entrega_real:
        Encomienda.objects.filter(pk=enc.pk).update(fecha_entrega_real=fecha_entrega_real)

    print(f"   ✅ Creada: {codigo} [{enc.get_estado_display()}]")
    return enc


# Entregadas históricas
crear_encomienda('ENC-2026-001', 'Caja con repuestos de moto',
    Decimal('8.50'), Decimal('48.75'), clientes[0], clientes[2], rutas['RT-001'],
    EstadoEnvio.ENTREGADO, hoy - timedelta(days=10), hoy - timedelta(days=11))

crear_encomienda('ENC-2026-002', 'Documentos legales urgentes',
    Decimal('0.50'), Decimal('18.00'), clientes[1], clientes[4], rutas['RT-002'],
    EstadoEnvio.ENTREGADO, hoy - timedelta(days=8), hoy - timedelta(days=8))

crear_encomienda('ENC-2026-003', 'Ropa y calzado - temporada',
    Decimal('15.00'), Decimal('60.00'), clientes[7], clientes[12], rutas['RT-001'],
    EstadoEnvio.ENTREGADO, hoy - timedelta(days=5), hoy - timedelta(days=5))

# En tránsito (a tiempo)
crear_encomienda('ENC-2026-004', 'Electrodomésticos: licuadora y plancha',
    Decimal('6.20'), Decimal('38.00'), clientes[3], clientes[8], rutas['RT-003'],
    EstadoEnvio.EN_TRANSITO, hoy + timedelta(days=1))

crear_encomienda('ENC-2026-005', 'Medicamentos y suplementos vitamínicos',
    Decimal('3.00'), Decimal('25.00'), clientes[5], clientes[9], rutas['RT-006'],
    EstadoEnvio.EN_TRANSITO, hoy + timedelta(days=2))

crear_encomienda('ENC-2026-006', 'Libros y material universitario',
    Decimal('12.00'), Decimal('52.50'), clientes[10], clientes[2], rutas['RT-001'],
    EstadoEnvio.EN_TRANSITO, hoy + timedelta(days=1))

crear_encomienda('ENC-2026-007', 'Herramientas de construcción',
    Decimal('22.00'), Decimal('77.50'), clientes[6], clientes[13], rutas['RT-005'],
    EstadoEnvio.EN_TRANSITO, hoy + timedelta(days=1))

# Pendientes
crear_encomienda('ENC-2026-008', 'Productos alimenticios envasados',
    Decimal('18.50'), Decimal('68.75'), clientes[11], clientes[0], rutas['RT-008'],
    EstadoEnvio.PENDIENTE, hoy + timedelta(days=2))

crear_encomienda('ENC-2026-009', 'Laptop y accesorios de cómputo',
    Decimal('4.50'), Decimal('29.75'), clientes[14], clientes[7], rutas['RT-007'],
    EstadoEnvio.PENDIENTE, hoy + timedelta(days=3))

crear_encomienda('ENC-2026-010', 'Artículos deportivos: raquetas y pelotas',
    Decimal('5.50'), Decimal('32.50'), clientes[2], clientes[5], rutas['RT-002'],
    EstadoEnvio.PENDIENTE, hoy + timedelta(days=2))

crear_encomienda('ENC-2026-011', 'Muestras de tela para confección',
    Decimal('2.00'), Decimal('20.00'), clientes[4], clientes[11], rutas['RT-004'],
    EstadoEnvio.PENDIENTE, hoy + timedelta(days=4))

crear_encomienda('ENC-2026-012', 'Juguetes y artículos para niños',
    Decimal('7.00'), Decimal('42.50'), clientes[9], clientes[3], rutas['RT-009'],
    EstadoEnvio.PENDIENTE, hoy + timedelta(days=3))

# Con retraso (en tránsito, fecha ya pasó)
crear_encomienda('ENC-2026-013', 'Repuestos de maquinaria industrial',
    Decimal('30.00'), Decimal('100.00'), clientes[6], clientes[1], rutas['RT-001'],
    EstadoEnvio.EN_TRANSITO, hoy - timedelta(days=2))  # ← con retraso

crear_encomienda('ENC-2026-014', 'Pinturas y materiales de arte',
    Decimal('9.00'), Decimal('47.50'), clientes[8], clientes[14], rutas['RT-010'],
    EstadoEnvio.EN_TRANSITO, hoy - timedelta(days=1))  # ← con retraso

# Devuelta
crear_encomienda('ENC-2026-015', 'Electrodoméstico defectuoso - devolución',
    Decimal('11.00'), Decimal('22.00'), clientes[13], clientes[6], rutas['RT-007'],
    EstadoEnvio.DEVUELTO, hoy - timedelta(days=3))

# Entregadas HOY
crear_encomienda('ENC-2026-016', 'Flores y arreglos florales frescos',
    Decimal('3.50'), Decimal('23.75'), clientes[0], clientes[12], rutas['RT-002'],
    EstadoEnvio.ENTREGADO, hoy, hoy)

crear_encomienda('ENC-2026-017', 'Repuestos electrónicos - garantía',
    Decimal('1.20'), Decimal('19.00'), clientes[7], clientes[10], rutas['RT-003'],
    EstadoEnvio.ENTREGADO, hoy, hoy)

# Más pendientes y en tránsito
crear_encomienda('ENC-2026-018', 'Cerámica artesanal - frágil',
    Decimal('6.00'), Decimal('37.50'), clientes[11], clientes[4], rutas['RT-001'],
    EstadoEnvio.PENDIENTE, hoy + timedelta(days=2))

crear_encomienda('ENC-2026-019', 'Equipos de audio: parlantes y auriculares',
    Decimal('4.00'), Decimal('28.00'), clientes[3], clientes[8], rutas['RT-005'],
    EstadoEnvio.PENDIENTE, hoy + timedelta(days=3))

crear_encomienda('ENC-2026-020', 'Insumos de panadería y repostería',
    Decimal('25.00'), Decimal('87.50'), clientes[14], clientes[5], rutas['RT-008'],
    EstadoEnvio.EN_TRANSITO, hoy + timedelta(days=1))

# ── Resumen ───────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("📊 RESUMEN DE DATOS CARGADOS:")
print(f"   📍 Rutas:       {Ruta.objects.count():>3}")
print(f"   👥 Clientes:    {Cliente.objects.count():>3}")
print(f"   👷 Empleados:   {Empleado.objects.count():>3}")
print(f"   📦 Encomiendas: {Encomienda.objects.count():>3}")
print(f"      ├─ Pendientes:    {Encomienda.objects.filter(estado=EstadoEnvio.PENDIENTE).count()}")
print(f"      ├─ En tránsito:   {Encomienda.objects.en_transito().count()}")
print(f"      ├─ Entregadas:    {Encomienda.objects.filter(estado=EstadoEnvio.ENTREGADO).count()}")
print(f"      ├─ Devueltas:     {Encomienda.objects.filter(estado=EstadoEnvio.DEVUELTO).count()}")
print(f"      └─ Con retraso:   {Encomienda.objects.con_retraso().count()}")
print(f"   📋 Historial:   {HistorialEstado.objects.count():>3} cambios de estado")
print("="*60)
print("\n✅ Datos cargados exitosamente.")
print("   🔑 Login: admin / admin123")
print("   🌐 http://localhost:8000/\n")
