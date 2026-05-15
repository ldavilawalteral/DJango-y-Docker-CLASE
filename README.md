# 🚚 Sipán Trans — Sistema de Gestión de Encomiendas

Sistema web completo para gestionar el ciclo de vida de envíos y encomiendas en tiempo real. Desarrollado con **Django**, **Django REST Framework**, **WebSockets (Django Channels)**, **Redis** y **PostgreSQL**. Todo el entorno está contenerizado con **Docker**.

---

## 🏗️ Arquitectura y Stack Tecnológico

| Capa | Tecnología |
|---|---|
| **Backend** | Python 3.11, Django 5.0, Django REST Framework 3.15 |
| **Servidor ASGI** | Daphne 4.0 (HTTP + WebSockets simultáneos) |
| **Base de Datos** | PostgreSQL 15 |
| **Caché / Broker** | Redis 7 |
| **WebSockets** | Django Channels 4.0 + channels-redis 4.1 |
| **Autenticación** | JWT (`djangorestframework-simplejwt`) + Sesiones |
| **Documentación API** | Swagger / OpenAPI 3.0 (`drf-spectacular`) |
| **Archivos Estáticos** | WhiteNoise 6.7 (servido por Daphne sin Nginx) |
| **Contenedores** | Docker & Docker Compose |

---

## ✅ Funcionalidades por Sesión

### 📦 Sesiones 03 y 04 — Modelos, Vistas y Docker

- Modelos relacionales: `Empleado`, `Encomienda`, `HistorialEstado`, `Cliente`, `Ruta`
- Máquina de estados para el ciclo de vida de encomiendas (Pendiente → En Tránsito → Entregado / Devuelto)
- Sistema de historial automático con señales Django
- Vistas CRUD completas con Bootstrap 5
- Dashboard con estadísticas en tiempo real
- Contenerización con Docker + PostgreSQL + pgAdmin

---

### 🔐 Sesiones 05 y 06 — API REST, JWT y Redis

#### 1. Seguridad y Autenticación
- **JWT:** Endpoints `/api/v1/auth/token/` y `/api/v1/auth/token/refresh/`
- **Sesiones HttpOnly:** Login/logout por cookies en `/api/v1/auth/login/` y `/api/v1/auth/logout/`
- **Permisos Granulares personalizados:**
  - `EsSoloLectura` — peticiones GET a cualquier autenticado
  - `EsAdminOSoloLectura` — escritura solo para staff
  - `PuedeGestionarEncomienda` — según cargo del empleado

#### 2. Optimización Anti N+1
- QuerySets optimizados con `select_related` y `prefetch_related`
- Métodos `para_listado_api` y `para_detalle_api` con `only()`

#### 3. Caché Redis
- Lista de encomiendas cacheada con claves dinámicas por query params
- Invalidación automática en POST / PUT / DELETE

#### 4. Endpoints API
- Versionado: `/api/v1/` y `/api/v2/`
- ViewSets: **Encomiendas**, **Clientes**, **Rutas**
- Acciones: `bulk_create`, `bulk_estado`, `cambiar_estado`
- Filtros: `pendientes`, `en_transito`, `con_retraso`

#### 5. Documentación Swagger
- Interfaz interactiva en `/api/docs/`
- Decoradores `@extend_schema` en todos los endpoints

---

### ⚡ Sesión 07 — Asincronía, WebSockets y Dashboard Reactivo

#### 1. Servidor ASGI con Daphne
Se reemplazó el servidor de desarrollo `runserver` por **Daphne**, capaz de manejar simultáneamente peticiones HTTP clásicas y conexiones WebSocket:

```yaml
# docker-compose.yml
command: sh -c "python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p 8000 config.asgi:application"
```

El `asgi.py` usa `ProtocolTypeRouter` para dirigir el tráfico:

```python
application = ProtocolTypeRouter({
    "http":      django_asgi_app,
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
```

#### 2. Django Channels + Redis como Broker
- `channels==4.0.0` y `channels-redis==4.1.0` instalados
- Channel Layer configurado con Redis:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("redis", 6379)]},
    }
}
```

#### 3. Consumer WebSocket (`envios/consumers.py`)
- Grupo `dashboard` al que se unen todos los clientes conectados
- Al conectarse → envía estadísticas actuales del sistema
- Recibe mensajes `stats_update` y `activity_update` y los retransmite al browser

```python
class DashboardConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)("dashboard", self.channel_name)
        self.accept()
        self.send(text_data=json.dumps({
            "type": "stats_update",
            "stats": get_stats(),
        }))
```

#### 4. Señales Reactivas (`envios/signals.py`)
Cada vez que cambia el estado de una `Encomienda` (via `HistorialEstado.post_save`), una señal Django:
1. Recalcula las estadísticas del sistema
2. Construye el evento de actividad (quién, qué, cuándo)
3. Emite ambos mensajes al grupo `dashboard` via Redis

```python
@receiver(post_save, sender=HistorialEstado)
def notificar_cambio_estado(sender, instance, created, **kwargs):
    if created:
        async_to_sync(channel_layer.group_send)("dashboard", {
            "type": "stats_update",
            "stats": get_stats(),
        })
```

#### 5. Dashboard Reactivo (Frontend)
El `dashboard.html` mantiene una conexión WebSocket persistente con:
- 🟢 **Badge "En vivo"** — indica la conexión activa al usuario
- 📊 **Tarjetas de estadísticas** — se actualizan con animación sin recargar la página
- 📡 **Feed "Actividad en Tiempo Real"** — muestra los últimos cambios de estado al instante
- 🔄 **Reconexión automática** con backoff exponencial

```javascript
const ws = new WebSocket(`ws://${location.host}/ws/dashboard/`);
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'stats_update') updateStats(data.stats);
    if (data.type === 'activity_update') addActivityFeed(data.activity);
};
```

#### 6. Archivos Estáticos con WhiteNoise
Daphne no sirve estáticos por defecto. Se configuró **WhiteNoise** para servir CSS, JS e iconos del admin sin necesitar Nginx:

```python
# settings.py — Middleware (posición 2)
'whitenoise.middleware.WhiteNoiseMiddleware',

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### 7. Monitoreo de Redis
Nuevo endpoint para verificar la salud de la conexión:
```
GET /api/redis-health/
→ {"status": "ok", "redis": "connected"}
```

#### 8. Usuarios y Grupos de Permisos por Cargo
Se implementó un sistema de control de acceso basado en grupos Django:

| Grupo | Cargo | Permisos |
|---|---|---|
| **Administrador** | Administrador | CRUD completo en todo el sistema |
| **Operador** | Operador de Registro | Crear/editar encomiendas y clientes |
| **Despachador** | Despachador | Ver todo + cambiar estados |
| **SupervisorRutas** | Supervisora de Rutas | Ver todo + gestionar rutas |
| **Chofer** | Chofer | Solo lectura |

#### 9. Datos de Prueba (Seeds)
Scripts de carga de datos listos para ejecutar:

```bash
# Cargar encomiendas, clientes, rutas y empleados de ejemplo
docker compose exec web python seed_data.py

# Crear usuarios con permisos por cargo
docker compose exec web python seed_usuarios.py
```

---

## 🚀 Cómo Levantar el Proyecto

### Requisitos previos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/ldavilawalteral/DJango-y-Docker-CLASE.git
cd DJango-y-Docker-CLASE

# 2. Levantar todos los servicios (build automático)
docker compose up --build -d

# 3. Ejecutar migraciones
docker compose exec web python manage.py migrate

# 4. Cargar datos de prueba
docker compose exec web python seed_data.py
docker compose exec web python seed_usuarios.py
```

### Servicios disponibles

| Servicio | URL |
|---|---|
| 🌐 **Aplicación Web** | http://localhost:8000 |
| 📖 **Swagger API Docs** | http://localhost:8000/api/docs/ |
| 🔴 **Redis Health** | http://localhost:8000/api/redis-health/ |
| 🗄️ **pgAdmin** | http://localhost:5051 |

---

## 🔑 Credenciales de Prueba

| Usuario | Contraseña | Cargo | Admin |
|---|---|---|---|
| `admin` | `admin123` | Administrador | ✅ |
| `rosa.carrasco` | `sipan2026` | Operador de Registro | ❌ |
| `marco.v` | `sipan2026` | Despachador | ❌ |
| `sofia.p` | `sipan2026` | Supervisora de Rutas | ❌ |
| `diego.n` | `sipan2026` | Chofer | ❌ |

---

## 📁 Estructura del Proyecto

```
mi-proyecto-docker/
├── config/                 # Configuración central del proyecto
│   ├── settings.py         # Configuración: DB, Redis, Channels, WhiteNoise
│   ├── asgi.py             # Router ASGI: HTTP + WebSocket
│   ├── urls.py             # URLs raíz + redis-health
│   └── api_routers.py      # Routers DRF v1 y v2
├── envios/                 # App principal
│   ├── models.py           # Empleado, Encomienda, HistorialEstado
│   ├── consumers.py        # 🆕 WebSocket Consumer (Sesión 07)
│   ├── routing.py          # 🆕 URLs WebSocket
│   ├── signals.py          # 🆕 Señal reactiva post_save
│   └── api/                # ViewSets, Serializers, Permisos
├── clientes/               # App de clientes
├── rutas/                  # App de rutas
├── templates/              # HTML (dashboard con WebSocket)
├── static/                 # CSS y JS personalizados
├── seed_data.py            # 🆕 Script de datos de prueba
├── seed_usuarios.py        # 🆕 Script de usuarios y permisos
├── docker-compose.yml      # Servicios: web, db, redis, pgadmin
├── Dockerfile              # Imagen Python 3.11-slim
└── requirements.txt        # Dependencias Python
```
