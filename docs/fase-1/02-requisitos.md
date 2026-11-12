# Requisitos de ModaStock

**Documento:** catálogo inicial de requisitos  
**Versión:** 1.0  
**Estado:** propuesto; pendiente de validación con usuarios representativos.

## 1. Convenciones de prioridad

- **Must:** indispensable para el MVP.
- **Should:** importante, pero puede aplazarse si existe una justificación.
- **Could:** mejora opcional.
- Los requisitos describen el comportamiento esperado; su implementación y verificación corresponden a fases posteriores.

## 2. Requisitos funcionales

| ID | Requisito | Prioridad | Criterio verificable |
|---|---|---|---|
| RF-01 | El sistema debe permitir iniciar y cerrar sesión de forma segura. | Must | Un usuario válido accede y puede cerrar su sesión; credenciales inválidas son rechazadas. |
| RF-02 | El administrador debe poder crear, consultar, actualizar y desactivar usuarios. | Must | Las operaciones respetan permisos y conservan la integridad de los registros. |
| RF-03 | El sistema debe aplicar permisos según el rol asignado. | Must | Un usuario sin permiso no puede ejecutar la operación restringida. |
| RF-04 | Un usuario autorizado debe poder registrar y consultar productos. | Must | El producto conserva nombre, referencia, categoría y estado. |
| RF-05 | El sistema debe permitir gestionar categorías de prendas. | Must | Una categoría puede asociarse a varios productos. |
| RF-06 | Un producto debe admitir variantes por talla y color. | Must | Cada combinación válida puede consultarse de forma independiente. |
| RF-07 | El sistema debe impedir variantes duplicadas dentro del mismo producto. | Must | Una combinación repetida es rechazada. |
| RF-08 | El sistema debe permitir consultar existencias por producto y variante. | Must | La consulta distingue talla y color y muestra la cantidad actual. |
| RF-09 | Un usuario autorizado debe poder registrar entradas de inventario. | Must | La existencia aumenta y se registra el movimiento asociado. |
| RF-10 | Un usuario autorizado debe poder registrar salidas de inventario. | Must | La existencia disminuye si hay disponibilidad suficiente. |
| RF-11 | El sistema debe rechazar salidas superiores a las existencias disponibles. | Must | La cantidad no cambia y se informa la causa del rechazo. |
| RF-12 | El sistema debe permitir ajustes justificados de inventario. | Must | El ajuste registra diferencia, motivo, usuario y fecha. |
| RF-13 | El sistema debe conservar el historial de movimientos. | Must | Se puede consultar el tipo, cantidad, fecha, usuario y referencia del movimiento. |
| RF-14 | El sistema debe permitir configurar stock mínimo por variante. | Must | El valor mínimo queda asociado a la variante correspondiente. |
| RF-15 | El sistema debe mostrar alertas de existencias bajas. | Must | Se identifican variantes con existencia menor o igual al mínimo configurado. |
| RF-16 | El sistema debe permitir registrar y consultar proveedores. | Should | Se almacenan datos básicos y se pueden asociar a entradas. |
| RF-17 | El sistema debe generar reportes básicos de existencias y movimientos. | Must | Los totales del reporte coinciden con los datos consultados. |
| RF-18 | El sistema debe permitir filtrar productos y movimientos. | Should | Los filtros devuelven resultados correspondientes a los criterios. |
| RF-19 | El sistema debe permitir desactivar productos sin borrar su historial. | Must | El producto deja de estar disponible para operaciones ordinarias y conserva sus movimientos. |
| RF-20 | El sistema debe registrar eventos relevantes de administración. | Should | Los eventos definidos quedan asociados al usuario y fecha. |

## 3. Requisitos no funcionales

Los valores siguientes son objetivos iniciales de calidad que deberán revisarse durante la arquitectura y validarse mediante pruebas. No representan resultados ya medidos.

| ID | Atributo | Requisito / objetivo verificable | Prioridad |
|---|---|---|---|
| RNF-01 | Seguridad | Las contraseñas nunca se almacenarán en texto plano; se utilizará un algoritmo moderno de hash de contraseñas con parámetros seguros. | Must |
| RNF-02 | Autorización | El servidor validará permisos en cada operación protegida; ocultar controles en la interfaz no será suficiente. | Must |
| RNF-03 | Integridad | El cambio de existencias y el registro del movimiento deberán confirmarse de forma atómica. | Must |
| RNF-04 | Consistencia | Las reglas de unicidad y cantidades no negativas deberán protegerse también en la capa de persistencia cuando corresponda. | Must |
| RNF-05 | Rendimiento | Objetivo inicial: respuestas de consulta comunes con percentil 95 inferior a 2 segundos bajo una carga de referencia definida en la Fase 9. | Should |
| RNF-06 | Disponibilidad | La aplicación deberá comunicar claramente los errores de conexión y no presentar operaciones fallidas como exitosas. | Must |
| RNF-07 | Usabilidad | Los formularios deberán identificar campos obligatorios, validar entradas y mostrar mensajes comprensibles. | Must |
| RNF-08 | Accesibilidad | La interfaz deberá permitir navegación por teclado y etiquetas comprensibles en controles y formularios principales. | Should |
| RNF-09 | Mantenibilidad | El código se organizará por responsabilidades y módulos; las interfaces de servicio estarán documentadas. | Must |
| RNF-10 | Interoperabilidad | Los componentes se comunicarán mediante contratos explícitos y formatos de datos documentados. | Must |
| RNF-11 | Trazabilidad | Las operaciones de inventario deberán poder relacionarse con el usuario y el momento en que ocurrieron. | Must |
| RNF-12 | Respaldo | Se definirá un procedimiento de copia de seguridad y restauración antes del despliegue. | Should |
| RNF-13 | Compatibilidad | La aplicación web deberá funcionar en versiones recientes de navegadores modernos de escritorio. | Should |
| RNF-14 | Privacidad | Solo se recopilarán datos personales necesarios para operar el sistema y se limitará su acceso por rol. | Must |
| RNF-15 | Observabilidad | Los errores técnicos relevantes deberán registrarse sin exponer contraseñas, tokens ni datos sensibles. | Should |

## 4. Datos mínimos identificados

### Producto
- Identificador interno.
- Nombre.
- Referencia o SKU de modelo.
- Categoría.
- Descripción opcional.
- Estado activo/inactivo.

### Variante
- Identificador interno.
- Producto asociado.
- Talla.
- Color.
- Código/SKU de variante.
- Existencia actual.
- Stock mínimo opcional.

### Movimiento
- Identificador.
- Variante afectada.
- Tipo: entrada, salida o ajuste.
- Cantidad.
- Motivo o referencia.
- Fecha y hora.
- Usuario responsable.
- Existencia resultante o información suficiente para reconstruirla.

### Proveedor
- Identificador.
- Nombre comercial.
- Datos de contacto opcionales.
- Estado.

### Usuario
- Identificador.
- Nombre visible.
- Correo o identificador de acceso.
- Hash de contraseña.
- Rol.
- Estado.

El modelo definitivo, los tipos de datos, las claves, las relaciones y las restricciones se establecerán en la Fase 3.

## 5. Trazabilidad requisito-entrega

| Grupo | Fase principal de implementación/verificación |
|---|---|
| RF-01 a RF-03, RNF-01, RNF-02 | Fase 5 — Seguridad y autenticación |
| RF-04 a RF-08, RF-14, RF-19 | Fase 7 — Módulos de inventario |
| RF-09 a RF-13, RNF-03, RNF-04, RNF-11 | Fases 4 y 7 — Servicios y movimientos |
| RF-16 a RF-18 | Fases 4, 6 y 7 |
| RNF-05 a RNF-15 | Fases 2, 4, 5, 6, 8 y 9 |
| Todos los requisitos | Fase 9 — Verificación integral |

## 6. Pendientes de validación

1. Confirmar si el inventario inicial será de una sola tienda o si se requiere más de una ubicación desde el MVP.
2. Confirmar si se necesitan tallas especiales, unidades distintas o variantes adicionales.
3. Definir qué datos de proveedores son obligatorios.
4. Acordar quién puede aprobar ajustes y salidas.
5. Precisar los reportes prioritarios para el comercio.
6. Definir carga de referencia y entorno para medir rendimiento.
