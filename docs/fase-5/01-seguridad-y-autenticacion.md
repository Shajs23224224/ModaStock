# Fase 5 — Seguridad y autenticación

## Controles implementados
- Hash de contraseñas con Argon2 mediante pwdlib; nunca se almacena la contraseña en texto plano.
- Tokens JWT firmados con HS256, sujeto UUID, rol, emisión y expiración configurable.
- Endpoints de registro, inicio de sesión y perfil autenticado.
- Registro público asigna exclusivamente el rol STAFF; no permite autoconcederse ADMIN o MANAGER.
- Dependencias reutilizables para identidad y autorización por roles.
- Los movimientos obtienen el user_id del usuario autenticado, nunca del cuerpo HTTP.
- Las rutas de catálogo requieren token; las operaciones de escritura requieren ADMIN o MANAGER.
- La escritura de movimientos requiere STAFF, MANAGER o ADMIN.
- Roles iniciales cargados mediante `python -m app.seed_roles`.

## Configuración
Definir `JWT_SECRET_KEY` como secreto aleatorio de al menos 32 caracteres y `ACCESS_TOKEN_EXPIRE_MINUTES` según la política del entorno. No subir secretos al repositorio. El valor de desarrollo del ejemplo no es apto para producción.

## Flujo inicial
1. Configurar variables de entorno y PostgreSQL.
2. Aplicar migraciones existentes.
3. Ejecutar `python -m app.seed_roles`.
4. Registrar una cuenta; el registro público crea STAFF.
5. Asignar ADMIN a la primera cuenta mediante un procedimiento administrativo seguro directamente en la base de datos; nunca mediante el endpoint público.
6. Iniciar sesión en `POST /api/v1/auth/login` y enviar el token como `Authorization: Bearer <token>`.

## Matriz de permisos
| Operación | STAFF | MANAGER | ADMIN |
|---|---:|---:|---:|
| Consultar catálogo y stock | Sí | Sí | Sí |
| Crear productos y variantes | No | Sí | Sí |
| Registrar movimientos | Sí | Sí | Sí |
| Asignar roles | No | No | Operación administrativa fuera del MVP |

## Límites
JWT es bearer-token stateless; el cierre de sesión del cliente elimina el token. La revocación inmediata y refresh tokens no forman parte de este MVP. Se deben usar HTTPS, rotación de secretos, límites de intentos de login y auditoría operativa antes de producción. Los tests unitarios no sustituyen pruebas de integración en PostgreSQL.
