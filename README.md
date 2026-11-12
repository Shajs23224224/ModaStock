# ModaStock

Sistema web de gestión de inventario especializado en tiendas y marcas de ropa.

## Objetivo
Administrar productos de moda, variantes por talla y color, existencias y movimientos de inventario con trazabilidad y reglas de negocio consistentes.

## Estado del proyecto
- Fases 1–3: análisis, arquitectura y diseño de datos integrados documentalmente.
- Fase 4: backend FastAPI inicial integrado.
- Fase 5: autenticación y autorización inicial integradas.
- Fase 6: frontend React integrado.
- Fase 7: módulos de inventario integrados; CI de backend y frontend aprobada.
- Fase 8: integración tecnológica; Backend CI con PostgreSQL 16 aprobada en PR #8.
- Fase 9: pruebas y aseguramiento de calidad en desarrollo.

Las fases 1–7 están fusionadas en `main`. La Fase 8 está en el PR #8 y la Fase 9 se desarrolla sobre esa rama en un PR independiente.

Consulta la documentación por fase en `docs/fase-1/` a `docs/fase-9/`.

## Tecnologías
- Frontend: React + TypeScript + Vite.
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
