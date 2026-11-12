# Decisiones tecnológicas — ModaStock

- **Fase:** 2 — Arquitectura del software
- **Versión:** 1.0
- **Estado:** decisiones propuestas para el MVP; sujetas a validación y a pruebas de implementación.

## 1. Stack propuesto

| Capa | Tecnología | Uso previsto | Justificación |
|---|---|---|---|
| Frontend | React + TypeScript | Interfaz web | Ecosistema amplio, componentes reutilizables y tipado estático |
| Herramientas frontend | Vite | Desarrollo y compilación | Configuración sencilla y ciclo de desarrollo rápido |
| Estilos | CSS modular o solución ligera equivalente | Diseño adaptable y consistente | Evita introducir un framework visual obligatorio antes de definir la interfaz |
| Backend | Python + FastAPI | API REST | Tipado, validación, documentación OpenAPI y facilidad de pruebas |
| Validación backend | Pydantic | Esquemas de entrada y salida | Contratos explícitos y validación centralizada |
| ORM | SQLAlchemy | Persistencia relacional | Modelo explícito y control transaccional |
| Migraciones | Alembic | Evolución del esquema | Cambios versionados y reproducibles |
| Base de datos | PostgreSQL | Datos operativos | Transacciones, restricciones, integridad y concurrencia |
| Pruebas backend | Pytest | Pruebas unitarias e integración | Ecosistema maduro y parametrización |
| Pruebas frontend | Vitest y React Testing Library | Componentes y lógica de interfaz | Integración con Vite y pruebas centradas en comportamiento |
| Contrato | OpenAPI | Documentación de API | Contrato legible y verificable |
| Control de versiones | Git + GitHub | Código, revisiones y cambios | Historial y colaboración |
| Entorno reproducible | Docker Compose (opcional en desarrollo) | Servicios locales | Reduce diferencias entre entornos |

Las versiones concretas se fijarán mediante archivos de dependencias y bloqueo cuando inicie la implementación. No se deben instalar versiones flotantes sin control ni afirmar compatibilidad antes de ejecutar pruebas.

## 2. Decisiones y razones

### ADR-001 — Backend monolítico modular

**Contexto:** el MVP tiene un dominio acotado y operaciones de inventario que deben actualizar existencias e historial de forma atómica.

**Decisión:** una sola aplicación backend organizada en módulos con límites explícitos.

**Alternativas:** microservicios, backend sin separación por capas.

**Consecuencias:** despliegue sencillo y transacciones locales; los módulos deberán respetar dependencias internas y evitar acoplamiento.

### ADR-002 — API REST sobre HTTP/JSON

**Contexto:** el cliente web necesita consultar y ejecutar operaciones de forma independiente del backend.

**Decisión:** API versionada bajo `/api/v1`, con contratos JSON y documentación OpenAPI.

**Alternativas:** GraphQL, comunicación directa del frontend con la base de datos.

**Consecuencias:** contratos explícitos, fácil inspección y compatibilidad con futuros clientes; se deberá gestionar versionado y errores de forma uniforme.

### ADR-003 — PostgreSQL como persistencia relacional

**Contexto:** productos, variantes, proveedores, usuarios y movimientos presentan relaciones y restricciones de integridad.

**Decisión:** PostgreSQL como base de datos principal.

**Alternativas:** SQLite, documentos NoSQL.

**Consecuencias:** claves foráneas, restricciones y transacciones adecuadas al dominio; requiere administrar migraciones y respaldos. SQLite puede servir en pruebas unitarias aisladas, pero no sustituye pruebas de integración con PostgreSQL.

### ADR-004 — React + TypeScript para frontend

**Contexto:** se requiere una interfaz web con formularios, filtros, tablas y navegación por roles.

**Decisión:** React con TypeScript y Vite.

**Alternativas:** Vue, Angular, plantillas renderizadas desde el backend.

**Consecuencias:** interfaz desacoplada y tipada; añade un proceso de compilación y exige validar contratos con la API.

### ADR-005 — FastAPI + Pydantic + SQLAlchemy

**Contexto:** el backend requiere validación, endpoints documentados, transacciones y pruebas.

**Decisión:** FastAPI, Pydantic y SQLAlchemy; Alembic para migraciones.

**Alternativas:** Django/DRF, Flask.

**Consecuencias:** estructura ligera y explícita; el equipo debe definir convenciones de proyecto, gestión de sesión y límites entre capas.

### ADR-006 — Pruebas automatizadas desde el inicio

**Contexto:** errores en inventario pueden causar inconsistencias y pérdida de trazabilidad.

**Decisión:** Pytest para backend y Vitest/React Testing Library para frontend; pruebas de integración contra PostgreSQL.

**Consecuencias:** el desarrollo debe incluir pruebas con cada módulo. La cobertura porcentual no será el único indicador; se priorizarán reglas críticas, errores y concurrencia.

## 3. Criterios para revisar el stack

Revisar las decisiones si ocurre alguno de estos escenarios:

- El hosting disponible no soporta de forma razonable el stack seleccionado.
- El rendimiento medido no alcanza los objetivos bajo carga representativa.
- El equipo responsable carece de capacidad para mantener alguna tecnología.
- Se requiere operación multi-sucursal o integración externa con restricciones específicas.
- Se identifican vulnerabilidades o incompatibilidades sin mitigación razonable.

## 4. Gestión de dependencias y versiones

- Fijar versiones compatibles en archivos de dependencias.
- Mantener lockfiles del frontend y del backend cuando aplique.
- Separar dependencias de producción y desarrollo.
- Revisar avisos de seguridad antes de actualizar.
- Automatizar instalación limpia y pruebas en integración continua.
- No almacenar credenciales ni archivos `.env` reales en el repositorio.

## 5. Decisiones pendientes

1. Elegir estrategia definitiva de sesión/autenticación en Fase 5.
2. Definir proveedor de alojamiento y base de datos en Fase 10, con base en presupuesto.
3. Confirmar si se utilizará biblioteca de componentes visuales o CSS propio en Fase 6.
4. Definir política concreta de logs, retención y respaldos según entorno.
5. Fijar versiones compatibles durante el scaffold técnico y validarlas con CI.

## 6. Estado

Las tecnologías anteriores constituyen una selección arquitectónica razonada para el MVP, no una declaración de que ya estén instaladas o funcionando. Su validación técnica ocurrirá al crear el esqueleto del proyecto y ejecutar las pruebas correspondientes.
