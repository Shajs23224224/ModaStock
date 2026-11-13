# Fase 8 — Integración tecnológica

## Objetivo
Integrar y verificar los componentes del sistema ModaStock: frontend React, API FastAPI y persistencia PostgreSQL, con configuración explícita por entorno y comprobaciones operativas.

## Estado de implementación
- La API expone `GET /health` como comprobación de vida del proceso (liveness).
- La API expone `GET /health/ready` como comprobación de disponibilidad de PostgreSQL (readiness), mediante `SELECT 1`. Si la base de datos no responde, devuelve HTTP 503.
- CORS se configura mediante `CORS_ORIGINS` y admite los métodos y cabeceras utilizados por la aplicación, incluidas las solicitudes OPTIONS de preflight.
- La configuración reconoce `APP_ENV`; fuera de desarrollo/pruebas rechaza el secreto JWT de ejemplo. La duración del token tiene límites de configuración.
- El pipeline de backend inicia PostgreSQL 16 como servicio y ejecuta una prueba de integración contra ese motor. Las pruebas unitarias existentes continúan aisladas en SQLite.
- El frontend mantiene `VITE_API_URL` como URL pública de la API; su valor se inyecta durante la compilación de Vite.

## Contratos operativos
| Endpoint | Propósito | Resultado esperado |
|---|---|---|
| `GET /health` | Liveness | HTTP 200 si el proceso responde |
| `GET /health/ready` | Readiness | HTTP 200 si `SELECT 1` funciona; HTTP 503 si PostgreSQL no está disponible |

## Variables de entorno
Backend: `APP_ENV`, `DATABASE_URL`, `CORS_ORIGINS`, `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`.

Frontend: `VITE_API_URL`. Esta variable es pública y no debe contener secretos.

## Validación
El workflow `Backend CI` instala dependencias, inicia PostgreSQL 16 con healthcheck y ejecuta Pytest. La prueba de integración crea y elimina el esquema definido por los modelos en la base efímera del workflow y consulta el endpoint readiness.

## Límites pendientes
- No se han ejecutado migraciones Alembic contra una base de datos persistente.
- No se ha desplegado el sistema ni configurado un dominio/HTTPS.
- No se ha probado concurrencia de movimientos con múltiples transacciones PostgreSQL en esta fase.
- La prueba de integración valida conectividad y disponibilidad, no sustituye las pruebas de migraciones ni de carga.
- El frontend y la API requieren que `VITE_API_URL` y `CORS_ORIGINS` coincidan con los orígenes reales del entorno.

## Criterio de aceptación
La integración se considera validada cuando las pruebas unitarias y de integración PostgreSQL pasan en GitHub Actions, el frontend compila y la documentación de variables y endpoints está sincronizada con la implementación.
