# Sistema de Gestión de Encomiendas (Sipán Trans)

API REST completa y documentada para gestionar el ciclo de vida de envíos y encomiendas. Desarrollado con Django, Django REST Framework (DRF), Redis y PostgreSQL. Todo el entorno está contenerizado usando Docker.

## Arquitectura y Stack Tecnológico

*   **Backend:** Python 3.11, Django 5.0, Django REST Framework 3.15
*   **Base de Datos:** PostgreSQL 15 (Servicio en contenedor)
*   **Caché:** Redis 7 (Servicio en contenedor)
*   **Autenticación:** JSON Web Tokens (JWT) con `djangorestframework-simplejwt`
*   **Documentación de API:** Swagger (OpenAPI 3.0) generado con `drf-spectacular`
*   **Entorno:** Docker & Docker Compose

---

## Funcionalidades Implementadas (Sesiones 05 y 06)

### 1. Seguridad y Autenticación
*   **JWT (JSON Web Tokens):** Se implementó autenticación por tokens en los endpoints `/api/v1/auth/token/` y `/api/v1/auth/token/refresh/`.
*   **Sesiones HttpOnly:** Adicionalmente, se configuraron endpoints de Login y Logout para autenticación basada en cookies (`/api/v1/auth/login/` y `/api/v1/auth/logout/`).
*   **Permisos Granulares:** Clases de permisos personalizadas para la gestión jerárquica de la API:
    *   `EsSoloLectura`: Permite peticiones seguras a cualquier usuario autenticado.
    *   `EsAdminOSoloLectura`: Restringe la escritura solo al staff.
    *   `PuedeGestionarEncomienda`: Limita acciones según el rol específico del empleado (Administrador/Recepcionista).

### 2. Optimización de Base de Datos (Anti N+1)
*   Se resolvió el problema N+1 mediante el rediseño del `QuerySet` (métodos `para_listado_api` y `para_detalle_api`).
*   Uso de `select_related` para optimizar llaves foráneas (`remitente`, `destinatario`, `ruta`).
*   Uso de `prefetch_related` para campos Many-to-Many o historiales de estado.
*   Uso de `only` para traer de la DB exclusivamente los datos necesarios para la serialización.

### 3. Caché de Redis
*   Servicio de Redis orquestado desde `docker-compose.yml`.
*   Caché implementado en el método `list()` del `ViewSet` de encomiendas.
*   Claves de caché dinámicas basadas en los query parameters para soportar diferentes filtros.
*   Mecanismo de invalidación automática (usando `delete_pattern`) cuando hay inserciones (POST), actualizaciones (PUT/PATCH) o borrados (DELETE).

### 4. Endpoints y Acciones Especiales
*   Versionado de la API: `/api/v1/` y `/api/v2/`.
*   ViewSets completos para **Encomiendas**, **Clientes** y **Rutas**.
*   Acciones exclusivas:
    *   `bulk_create`: Permite enviar un arreglo de encomiendas y crearlas todas en un solo POST.
    *   `bulk_estado`: Permite modificar el estado de múltiples encomiendas al mismo tiempo.
    *   `cambiar_estado`: Registra un nuevo estado en el historial asociado al empleado que hizo el cambio.
    *   Filtros nativos: `pendientes`, `en_transito`, `con_retraso`, etc.

### 5. Documentación Interactiva
*   Interfaz de **Swagger** disponible en `/api/docs/` que refleja automáticamente cualquier cambio en la estructura de la API.
*   Toda la configuración y esquemas de parámetros mapeados mediante decoradores de `drf-spectacular` (`@extend_schema`).

---

## Cómo Levantar el Proyecto

1. Clona el repositorio y entra al directorio:
   ```bash
   git clone https://github.com/ldavilawalteral/DJango-y-Docker-CLASE.git
   cd DJango-y-Docker-CLASE
   ```

2. Copia el archivo de entorno y levanta los servicios:
   ```bash
   cp .env.example .env
   docker compose up --build
   ```

3. (Opcional) Ejecuta las migraciones si es necesario:
   ```bash
   docker compose exec web python manage.py migrate
   ```

4. Servicios disponibles:
   * **Aplicación Web + API:** `http://localhost:8000`
   * **Swagger API Docs:** `http://localhost:8000/api/docs/`
   * **pgAdmin:** `http://localhost:5051` (admin@admin.com / admin)
