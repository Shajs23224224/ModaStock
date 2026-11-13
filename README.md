# ModaStock

Sistema web de gestión de inventario especializado en tiendas y marcas de ropa.

## Objetivo
Administrar productos de moda, variantes por talla y color, existencias y movimientos de inventario con trazabilidad y reglas de negocio consistentes.

## Estado del proyecto
- Fases 1–3: análisis, arquitectura y diseño de datos documentados e integrados.
- Fase 4: backend FastAPI inicial integrado.
- Fase 5: autenticación y autorización inicial integradas.
- Fase 6: frontend React integrado.
- Fase 7: módulos de inventario integrados.
- Fase 8: integración tecnológica y readiness de PostgreSQL integrados.
- Fase 9: pruebas de backend/frontend y concurrencia PostgreSQL integradas.
- Fase 10: contenedores Docker, Compose, Nginx, documentación operativa y migración inicial Alembic integrados.

**Las fases 1–10 están integradas en `main`.** La CI valida backend, frontend, construcción de imágenes y upgrade/downgrade de la migración inicial contra PostgreSQL efímero. Esto no significa que se haya desplegado el sistema ni que se hayan aplicado migraciones a una base de datos persistente.

Consulta la documentación por fase en `docs/fase-1/` a `docs/fase-10/`.

## Ejecución con Docker
Consulta `docs/fase-10/01-despliegue-y-operacion.md`. La plantilla Compose requiere copiar `.env.example` a `.env`, configurar secretos, construir imágenes, ejecutar las migraciones de forma explícita y luego iniciar API/frontend. No se ejecutan migraciones automáticamente al arrancar.

## Tecnologías
- Frontend: React + TypeScript + Vite + Nginx.
- Backend: Python + FastAPI.
- Persistencia: SQLAlchemy + Alembic + PostgreSQL.
- Seguridad: Argon2 para contraseñas y JWT para autenticación.
- Pruebas: Pytest, Vitest y GitHub Actions.

## Backend
Consulta `backend/README.md` para instalación, configuración, roles y ejecución. El registro público solo crea cuentas STAFF. Las rutas de catálogo e inventario requieren autenticación y permisos según rol.

## Frontend
Consulta `frontend/README.md` para instalar y ejecutar la interfaz.

## Roadmap
1. Análisis y especificación.
2. Arquitectura del software.
3. Diseño de base de datos.
4. Backend y servicios API.
5. Seguridad y autenticación.
6. Frontend e interfaz.
7. Módulos de inventario.
8. Integración tecnológica.
9. Pruebas y aseguramiento de calidad.
10. Despliegue y documentación.
