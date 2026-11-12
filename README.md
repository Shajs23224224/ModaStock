# ModaStock

Sistema web de gestión de inventario especializado en tiendas y marcas de ropa.

## Objetivo
Administrar productos de moda, variantes por talla y color, existencias y movimientos de inventario con trazabilidad y reglas de negocio consistentes.

## Estado del proyecto
- Fase 1: análisis y especificación.
- Fase 2: arquitectura del software.
- Fase 3: diseño de base de datos.
- Fase 4: primera implementación del backend FastAPI.
- Fase 5: seguridad y autenticación inicial.
- Fase 6: frontend e interfaz inicial en revisión.

Consulta la documentación por fase en `docs/fase-1/` a `docs/fase-6/`.

## Tecnologías
- Frontend previsto: React + TypeScript + Vite.
- Backend: Python + FastAPI.
- Persistencia: SQLAlchemy + Alembic + PostgreSQL.
- Seguridad: Argon2 para contraseñas y JWT para autenticación.
- Pruebas: Pytest.

## Backend
Consulta `backend/README.md` para instalación, configuración, roles y ejecución. El registro público solo crea cuentas STAFF. Las rutas de catálogo e inventario requieren autenticación y permisos según rol.

## Frontend\nConsulta `frontend/README.md` para instalar y ejecutar la interfaz React.\n\n## Roadmap
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
