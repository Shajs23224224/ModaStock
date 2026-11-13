# Fase 9 — Pruebas y aseguramiento de calidad

## Objetivo
Verificar los contratos principales de ModaStock en backend, persistencia PostgreSQL y cliente HTTP del frontend. Las pruebas se ejecutan automáticamente en GitHub Actions y deben detectar regresiones antes de integrar cambios.

## Estrategia de pruebas
1. **Unitarias de backend:** validación de esquemas, reglas de inventario, idempotencia y restricciones de cantidades.
2. **API/integración SQLite:** autenticación, asignación del rol STAFF al registro público, login, perfil, permisos, catálogo, variantes, ajustes de stock y movimientos.
3. **Integración PostgreSQL 16:** readiness y concurrencia real de dos ventas simultáneas sobre el mismo saldo.
4. **Unitarias de frontend:** serialización JSON, cabecera Bearer, Idempotency-Key y normalización de errores HTTP/red.
5. **Build frontend:** TypeScript estricto y compilación de Vite.
6. **Auditoría de dependencias:** reporte de vulnerabilidades npm en cada ejecución de CI.

## Casos críticos cubiertos
- Registro público no permite autoasignación de ADMIN; el rol creado es STAFF.
- Credenciales incorrectas y tokens inválidos se rechazan.
- STAFF no puede crear variantes ni modificar mínimos de stock.
- Una referencia duplicada devuelve conflicto.
- Un movimiento no puede llevar el saldo por debajo de cero.
- Reintentar la misma operación con la misma clave idempotente no duplica el movimiento.
- Reutilizar una clave idempotente con una operación distinta devuelve HTTP 409.
- Los ajustes de aumento y disminución actualizan el saldo y mantienen el antes/después.
- Dos salidas concurrentes de 7 unidades contra un saldo inicial de 10: solo una puede confirmarse; la otra debe recibir conflicto y el saldo final debe ser 3.

## Resultado de CI verificado
En el commit `641e3df9002605c7bc5b437eae77a92f099218b3`:
- Backend CI: exitoso; Pytest ejecutado con PostgreSQL 16 como servicio.
- Frontend CI: exitoso; 5 pruebas Vitest aprobadas y compilación TypeScript/Vite completada.
- `npm audit`: 0 vulnerabilidades reportadas después de actualizar Vitest a 4.1.12.

La auditoría inicial había detectado 6 vulnerabilidades transitivas/directas (incluidas 2 críticas). La actualización de Vitest a 4.1.12 resolvió los hallazgos reportados por npm audit en la ejecución posterior.

## Ejecución local
Backend:
```bash
cd backend
pip install -e ".[test]"
pytest
```
La prueba PostgreSQL se omite localmente si no está definida `TEST_DATABASE_URL`; para ejecutarla se necesita una base PostgreSQL aislada y desechable. La suite no debe apuntar a datos reales.

Frontend:
```bash
cd frontend
npm install
npm run test -- --run
npm run build
```

## CI
- Backend CI usa SQLite para pruebas aisladas y PostgreSQL 16 como servicio efímero para integración.
- Frontend CI ejecuta Vitest, TypeScript, build y auditoría npm.
- Los checks deben estar en verde en el PR antes de solicitar integración.

## Alcance y limitaciones
- La prueba PostgreSQL de concurrencia valida bloqueo transaccional con dos sesiones independientes, no carga de alto volumen.
- No se ejecutan pruebas de penetración, rendimiento, accesibilidad automatizada ni pruebas E2E de navegador en esta fase.
- Las migraciones Alembic deben disponer de revisiones versionadas para poder agregar una prueba de upgrade/downgrade; esta fase no aplica cambios a bases persistentes.
