# Fase 10 — despliegue y documentación operativa

## 1. Objetivo y alcance

Preparar ModaStock para ejecutarse de forma reproducible en contenedores, con PostgreSQL persistente, API FastAPI y frontend React servido por Nginx. Esta fase entrega artefactos de despliegue y una guía operativa; **no publica imágenes, no crea infraestructura externa, no aplica migraciones a una base persistente y no realiza un despliegue real**.

## 2. Arquitectura de ejecución

- **db:** PostgreSQL 16, con volumen Docker `postgres_data` y healthcheck `pg_isready`.
- **api:** FastAPI + Uvicorn, imagen basada en Python 3.12. Ejecuta como usuario no privilegiado y expone internamente el puerto 8000.
- **frontend:** build de React/Vite con Node 20 y publicación de archivos estáticos mediante Nginx.
- **proxy:** Nginx sirve la SPA y reenvía `/api/*` y `/health/*` al servicio API dentro de la red privada de Compose.
- **migrate:** servicio de ejecución puntual para `alembic upgrade head`, habilitado bajo el perfil `tools`. Las migraciones no se ejecutan automáticamente al iniciar la API.

La API utiliza `GET /health/ready` como healthcheck de contenedor; ese endpoint verifica la conectividad a PostgreSQL mediante `SELECT 1`. No certifica que el esquema de negocio esté migrado.

## 3. Requisitos previos

- Docker Engine actualizado.
- Docker Compose v2 (`docker compose`).
- Git para obtener el repositorio.
- Puertos disponibles: 8080 para la interfaz (configurable con `WEB_PORT`).

## 4. Preparación del entorno

Desde la raíz del repositorio:

```bash
cp .env.example .env
```

Edita `.env` y reemplaza obligatoriamente:
- `POSTGRES_PASSWORD`: contraseña larga y aleatoria para PostgreSQL.
- `JWT_SECRET_KEY`: secreto aleatorio criptográficamente seguro de al menos 32 caracteres.

Usa caracteres URL-safe para `POSTGRES_PASSWORD` porque Compose construye `DATABASE_URL` con ese valor. No reutilices contraseñas ni el secreto JWT entre entornos. No guardes `.env` en Git ni lo incluyas en imágenes.

Para generar valores localmente puedes usar un generador criptográfico del sistema, por ejemplo:

```bash
openssl rand -base64 36
openssl rand -hex 32
```

Si el primer resultado contiene caracteres no URL-safe, conviértelo a una cadena URL-safe antes de usarlo como contraseña de PostgreSQL.

## 5. Construcción e inicio controlado

Primero construye las imágenes:

```bash
docker compose build api migrate frontend
```

Inicia PostgreSQL y espera a que esté saludable:

```bash
docker compose up -d db
docker compose ps
```

Ejecuta las migraciones de forma explícita y controlada:

```bash
docker compose run --rm migrate
```

Inicializa los roles del sistema:

```bash
docker compose run --rm api python -m app.seed_roles
```

Inicia la API y el frontend:

```bash
docker compose up -d api frontend
docker compose ps
```

Abre `http://localhost:8080` (o el puerto configurado en `WEB_PORT`). La documentación OpenAPI de la API está disponible internamente en `/docs`; para una exposición externa, protégela o desactívala según la política del entorno.

El primer usuario ADMIN debe asignarse mediante el procedimiento administrativo controlado descrito en `backend/README.md`. El registro público crea únicamente usuarios STAFF. No se debe habilitar un endpoint público para elevar privilegios.

## 6. Operación habitual

```bash
# Estado de los servicios
docker compose ps

# Logs
docker compose logs --tail=200 api frontend db

# Seguir logs de la API
docker compose logs -f api

# Detener servicios sin borrar datos
docker compose down

# Actualizar imágenes locales después de traer cambios
docker compose build --pull api migrate frontend
```

`docker compose down` conserva el volumen nombrado. **No ejecutes `docker compose down -v` en un entorno con datos que deban conservarse**, porque elimina el volumen de PostgreSQL.

## 7. Migraciones, actualización y reversión

1. Realiza una copia de seguridad antes de cualquier cambio de esquema.
2. Revisa el diff de código y las revisiones Alembic incluidas en la versión.
3. Construye la imagen `migrate` de la misma versión que se va a desplegar.
4. Ejecuta `docker compose run --rm migrate` en una ventana controlada.
5. Verifica readiness, logs y operaciones críticas de inventario.
6. Si la versión nueva falla, vuelve a la imagen anterior solo si el esquema es compatible. Si la migración es irreversible o incompatible, restaura la copia de seguridad en un procedimiento de recuperación aprobado.

No se recomienda ejecutar `alembic downgrade` a ciegas en producción. Cada migración debe tener estrategia de compatibilidad, respaldo y rollback documentada. Las migraciones deben probarse primero en una base PostgreSQL desechable y con datos representativos.

## 8. Copias de seguridad y restauración

Generar un respaldo lógico en formato custom:

```bash
mkdir -p backups
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > backups/modastock-$(date +%Y%m%d-%H%M%S).dump
```

Verificar que el archivo exista y tenga tamaño mayor que cero. Conserva copias cifradas fuera del servidor y prueba periódicamente su restauración.

Restauración de referencia (requiere ventana de mantenimiento y destino preparado):

```bash
docker compose stop api frontend
cat backups/ARCHIVO.dump | docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists'
docker compose up -d api frontend
```

La restauración con `--clean` elimina objetos existentes que estén incluidos en el respaldo. Confirma el destino y la copia antes de ejecutarla. Para recuperación ante desastre, es preferible restaurar primero en una base separada y validar los datos antes de sustituir la base activa.

## 9. Seguridad antes de producción

- Terminar TLS/HTTPS en un proxy o balanceador administrado y restringir el acceso directo a contenedores.
- Usar secretos gestionados por la plataforma; no almacenar `.env` en el repositorio, artefactos ni logs.
- Rotar credenciales y definir permisos mínimos de PostgreSQL.
- Restringir CORS a los dominios reales.
- Definir política de backups, cifrado, retención y pruebas de recuperación.
- Supervisar logs, readiness, uso de recursos y errores HTTP.
- Aplicar rate limiting y protección contra fuerza bruta en el perímetro.
- Revisar la estrategia de sesión: el frontend actual conserva JWT en `sessionStorage`; evaluar cookies HttpOnly/Secure/SameSite con protección CSRF antes de producción.
- Revisar la exposición de `/docs`, cabeceras, dependencias y configuración de Nginx.
- Ejecutar pruebas E2E, de seguridad, carga y accesibilidad antes de abrir el servicio a usuarios.

## 10. Validación automatizada

El workflow `Container CI`:
- valida el archivo Compose con `docker compose config --quiet`;
- construye las imágenes de API y frontend;
- no publica imágenes en un registry y no despliega.

Los workflows de backend y frontend siguen siendo responsables de pruebas unitarias, integración PostgreSQL, TypeScript y build. La construcción de imágenes no sustituye pruebas E2E ni una validación de despliegue en un entorno de staging.

## 11. Limitaciones y estado

- No se ejecutó despliegue real ni se publicaron imágenes.
- No se aplicaron migraciones a una base persistente.
- No se configuraron dominio, TLS, proxy externo, secretos gestionados ni monitoreo de producción.
- No se ha certificado alta disponibilidad, escalado horizontal, recuperación ante desastre ni rendimiento bajo carga.
- El servicio Compose está diseñado como plantilla reproducible de ejecución; requiere endurecimiento y validación específica antes de producción.
