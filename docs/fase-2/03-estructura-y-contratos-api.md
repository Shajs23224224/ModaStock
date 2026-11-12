# Estructura del proyecto y contratos iniciales de API

- **Fase:** 2 — Arquitectura del software
- **Versión:** 1.0
- **Estado:** diseño lógico; no representa endpoints implementados.

## 1. Estructura de carpetas propuesta

```text
modastock/
├── frontend/
│   ├── src/
│   │   ├── app/                 # rutas, configuración y composición
│   │   ├── components/          # componentes reutilizables
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── catalog/
│   │   │   ├── inventory/
│   │   │   ├── suppliers/
│   │   │   └── reports/
│   │   ├── services/            # cliente HTTP y contratos
│   │   ├── hooks/
│   │   └── styles/
│   ├── tests/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/v1/              # routers y dependencias HTTP
│   │   ├── core/                # configuración, seguridad y logging
│   │   ├── modules/
│   │   │   ├── users/
│   │   │   ├── catalog/
│   │   │   ├── inventory/
│   │   │   ├── suppliers/
│   │   │   ├── reports/
│   │   │   └── audit/
│   │   ├── shared/              # componentes compartidos justificados
│   │   └── main.py
│   ├── migrations/
│   ├── tests/
│   └── pyproject.toml
├── docs/
│   ├── fase-1/
│   └── fase-2/
├── infra/                       # configuración de despliegue cuando exista
├── .gitignore
└── README.md
```

Dentro de cada módulo backend se recomienda separar, cuando aplique:

- `router.py`: endpoints y traducción HTTP.
- `schemas.py`: modelos de entrada y salida.
- `models.py`: mapeo de persistencia.
- `repository.py`: consultas y persistencia.
- `service.py`: casos de uso y reglas de aplicación.
- `domain.py`: entidades y reglas de dominio cuando su complejidad lo justifique.

No es obligatorio crear archivos vacíos ni duplicar capas por formalidad. La estructura debe crecer con funcionalidades reales.

## 2. Convenciones generales de API

- Base: `/api/v1`.
- JSON como formato de intercambio.
- Identificadores opacos (UUID recomendado) en recursos expuestos.
- Nombres de recursos en plural.
- Métodos HTTP semánticos: GET, POST, PATCH y DELETE cuando proceda.
- Listados paginados con `limit` y `offset`.
- Respuestas de error uniformes.
- La API valida autorización y reglas de negocio, aunque el frontend oculte acciones.
- Operaciones de inventario requieren usuario autenticado y permiso explícito.

## 3. Endpoints previstos para el MVP

| Método | Ruta | Propósito | Permiso conceptual |
|---|---|---|---|
| POST | `/api/v1/auth/login` | Iniciar sesión | Público con limitación de intentos |
| POST | `/api/v1/auth/logout` | Cerrar sesión | Usuario autenticado |
| GET | `/api/v1/users/me` | Consultar usuario actual | Usuario autenticado |
| GET / POST | `/api/v1/products` | Listar / crear productos | Lectura / catálogo |
| GET / PATCH | `/api/v1/products/{product_id}` | Consultar / actualizar producto | Lectura / catálogo |
| GET / POST | `/api/v1/products/{product_id}/variants` | Listar / crear variantes | Lectura / catálogo |
| GET | `/api/v1/variants/{variant_id}/stock` | Consultar existencia | Inventario lectura |
| POST | `/api/v1/inventory/movements` | Registrar entrada, salida o ajuste | Inventario escritura |
| GET | `/api/v1/inventory/movements` | Consultar historial | Inventario lectura |
| GET / PATCH | `/api/v1/suppliers` | Listar / crear proveedores | Proveedores |
| GET | `/api/v1/reports/stock` | Reporte de existencias | Reportes lectura |
| GET | `/api/v1/reports/movements` | Reporte de movimientos | Reportes lectura |

La tabla es un contrato preliminar: métodos y rutas podrán refinarse al implementar. No afirma que estos endpoints existan actualmente.

## 4. Ejemplo conceptual de solicitud de movimiento

```json
{
  "variant_id": "UUID_DE_LA_VARIANTE",
  "type": "OUT",
  "quantity": 2,
  "reason": "Salida por venta",
  "reference": "DOC-000123"
}
```

Ejemplo conceptual de respuesta:

```json
{
  "movement_id": "UUID_DEL_MOVIMIENTO",
  "variant_id": "UUID_DE_LA_VARIANTE",
  "type": "OUT",
  "quantity": 2,
  "stock_before": 12,
  "stock_after": 10,
  "created_at": "2026-11-12T15:00:00Z"
}
```

El servidor calcula `stock_before` y `stock_after`; el cliente no puede enviar ni imponer la existencia resultante. Los identificadores son ilustrativos.

## 5. Errores de API

Formato conceptual:

```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "No hay existencias suficientes para completar la salida.",
    "details": {
      "available": 1,
      "requested": 2
    },
    "request_id": "UUID_DE_SOLICITUD"
  }
}
```

Códigos HTTP previstos:

- `400`: solicitud inválida a nivel de operación.
- `401`: falta autenticación o credenciales inválidas.
- `403`: usuario autenticado sin permiso.
- `404`: recurso inexistente o no accesible.
- `409`: conflicto de estado, duplicidad o stock insuficiente.
- `422`: error de validación de datos.
- `429`: límite de solicitudes excedido.
- `500`: error inesperado, sin revelar detalles internos.

La clasificación final debe ser coherente y documentada en OpenAPI.

## 6. Reglas de integridad relevantes para la API

- La variante debe existir y estar activa para operaciones ordinarias.
- Cantidad de movimiento estrictamente positiva.
- Salida nunca puede dejar stock negativo.
- La operación de stock y el movimiento se confirman en una sola transacción.
- Las solicitudes concurrentes deben protegerse ante condiciones de carrera.
- Los movimientos confirmados no se editan ni eliminan; se corrigen con movimiento compensatorio.
- Un ajuste requiere motivo y permiso.
- Las rutas de consulta aplican paginación y filtros validados.

## 7. Límites entre frontend y backend

El frontend es responsable de experiencia de uso, accesibilidad, validación inmediata y presentación. El backend es responsable de identidad, permisos, validación definitiva, reglas de negocio, consistencia y persistencia. La base de datos protege integridad mediante claves, restricciones y transacciones.

## 8. Relación con las siguientes fases

- **Fase 3:** transformar entidades y relaciones en un modelo relacional y restricciones concretas.
- **Fase 4:** implementar módulos backend, transacciones y endpoints.
- **Fase 5:** cerrar el diseño de sesión, credenciales y permisos.
- **Fase 6:** construir la interfaz y cliente API.
- **Fase 8:** integrar frontend, API y base de datos en entornos reproducibles.
- **Fase 9:** verificar contratos, seguridad, consistencia y rendimiento.
