# Fase 6 — Frontend e interfaz de ModaStock

## Objetivo
Construir una interfaz web adaptable para que los usuarios interactúen con el backend mediante flujos claros y consistentes.

## Stack
- React 18.
- TypeScript 5.
- Vite 6.
- Lucide React para iconografía.
- CSS responsive propio.

## Estructura
- `frontend/src/main.tsx`: punto de entrada.
- `frontend/src/App.tsx`: shell de aplicación, autenticación, navegación y vistas iniciales.
- `frontend/src/api.ts`: cliente HTTP tipado y manejo de errores.
- `frontend/src/styles.css`: sistema visual y responsive.
- `frontend/index.html`: documento base y metadatos.

## Vistas
1. Acceso: inicio de sesión y registro público.
2. Resumen: bienvenida, conteo real de productos y referencias recientes.
3. Productos: consulta, búsqueda y alta para ADMIN/MANAGER.
4. Movimientos: formulario de entrada/salida con clave de idempotencia.
5. Reportes: estado vacío explícito hasta implementar endpoints analíticos.
6. Configuración: datos de cuenta y cierre de sesión.

## Integración API
El cliente consume:
- `POST /auth/login`
- `POST /auth/register`
- `GET /auth/me`
- `GET /products`
- `POST /products`
- `POST /inventory/movements`

La URL base se configura mediante `VITE_API_URL`. El backend valida identidad y permisos; ocultar botones en la interfaz solo mejora la experiencia y no constituye un control de seguridad.

## Decisiones UX y seguridad
- Sesión guardada en sessionStorage, no localStorage persistente.
- La sesión se valida contra el endpoint de perfil al cargar.
- Errores HTTP y de conectividad se muestran sin simular datos.
- Los roles STAFF no ven la acción de crear productos; la API sigue siendo la autoridad.
- Diseño responsive con navegación lateral y menú móvil.

## Limitaciones y siguientes mejoras
- Selección de variantes por SKU pendiente de endpoint de consulta; el formulario de movimientos usa UUID temporalmente.
- Reportes y alertas pendientes de endpoints de agregación.
- Para producción, migrar tokens a cookies HttpOnly/Secure/SameSite con estrategia CSRF adecuada, habilitar HTTPS, CSP y políticas de despliegue.
- Ejecutar la compilación de frontend en CI antes de integrar esta fase.
