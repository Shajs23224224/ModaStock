# ModaStock Frontend

Interfaz web del sistema ModaStock construida con React, TypeScript y Vite.

## Requisitos e instalación
Node.js 20 o superior y backend FastAPI activo.
```bash
npm install
cp .env.example .env
npm run dev
```
Configura VITE_API_URL; por defecto apunta a http://localhost:8000/api/v1.

## Compilar
```bash
npm run build
npm run preview
```

## Funcionalidades
- Inicio de sesión y registro, validación de perfil y cierre de sesión.
- Panel de resumen y catálogo de productos.
- Consulta de variantes por SKU, producto, talla y color.
- Selección de variante desde el formulario de movimientos, mostrando stock actual.
- Registro de entradas/salidas con Idempotency-Key.
- Vista de cuenta y estados explícitos para módulos aún no implementados.
- Diseño adaptable a móvil, tablet y escritorio.

## Límites conocidos
- La creación de variantes y los catálogos de tallas/colores se exponen en la API; la interfaz de administración completa de esas entidades queda para una iteración posterior.
- El historial de movimientos y los reportes analíticos todavía no tienen una vista dedicada en la interfaz.
- El token se mantiene en sessionStorage. Para producción, valorar cookies HttpOnly/Secure/SameSite con protección CSRF.
- La autorización se verifica en backend; ocultar controles en frontend no es una medida de seguridad.
