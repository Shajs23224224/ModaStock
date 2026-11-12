# ModaStock Frontend

Interfaz web del sistema ModaStock construida con React, TypeScript y Vite.

## Requisitos
- Node.js 20 o superior.
- Backend FastAPI de ModaStock en ejecución.
- Una base de datos configurada para el backend.

## Instalación
Desde esta carpeta:
```bash
npm install
cp .env.example .env
npm run dev
```
Por defecto, Vite sirve la aplicación en http://localhost:5173. Configura VITE_API_URL para apuntar al prefijo de la API, por defecto http://localhost:8000/api/v1.

## Compilar
```bash
npm run build
npm run preview
```

## Funcionalidades de esta entrega
- Inicio de sesión y registro conectado con la API.
- Persistencia de token durante la sesión del navegador.
- Validación del perfil con /auth/me y cierre de sesión si el token deja de ser válido.
- Panel de resumen con conteo de productos.
- Catálogo con búsqueda, estados y fecha de registro.
- Alta de productos para roles ADMIN y MANAGER.
- Formulario de entradas/salidas con clave de idempotencia.
- Vista de cuenta y estados vacíos para módulos aún no disponibles.
- Diseño adaptable a móvil, tablet y escritorio.

## Límites conocidos
- Los movimientos solicitan el UUID de la variante porque la API aún no expone una consulta de variantes para seleccionar por SKU; se mejorará en la fase de módulos de inventario.
- Los contadores de movimientos y alertas muestran un marcador no disponible, no cifras inventadas.
- Los reportes permanecen como vista de preparación hasta contar con endpoints analíticos.
- El token se mantiene en sessionStorage y se elimina al cerrar sesión o la pestaña. Para producción, valorar cookies HttpOnly/Secure/SameSite y protección CSRF en lugar de almacenamiento accesible a JavaScript.
- El frontend no sustituye la autorización del backend. Los permisos se verifican nuevamente en la API.
