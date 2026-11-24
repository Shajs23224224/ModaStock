# Gestión y validación de requisitos de ModaStock con GitHub

- **Proyecto:** ModaStock
- **Herramienta de gestión:** GitHub Issues y GitHub Projects
- **Metodología de organización propuesta:** Scrum
- **Documento de referencia:** `docs/fase-1/02-requisitos.md`
- **Estado:** requisitos registrados; validación funcional pendiente con usuarios representativos.

## 1. Selección de la herramienta

Se selecciona GitHub para gestionar los requisitos porque el repositorio de ModaStock ya se encuentra alojado en esta plataforma y contiene el código fuente, documentación técnica y evidencias de evolución del producto.

La gestión se apoya en dos componentes complementarios:

- **GitHub Issues:** registro individual y trazable de cada requisito. Cada Issue contiene identificador, descripción, prioridad, criterios de aceptación y referencia al catálogo oficial.
- **GitHub Projects:** tablero visual para priorizar el Product Backlog, seleccionar el trabajo de cada Sprint y controlar su avance.

Esta solución mantiene vinculados los requisitos con el repositorio y con los cambios de software que los implementen.

## 2. Organización del trabajo con Scrum

El catálogo de requisitos se administra como Product Backlog. La priorización inicial conserva la clasificación del documento de requisitos:

- **Must:** indispensable para el MVP.
- **Should:** importante; puede aplazarse con justificación.

Durante la planificación de cada Sprint, se seleccionan del Product Backlog los Issues que puedan completarse dentro del Sprint y se trasladan al Sprint Backlog. El alcance del Sprint se revisa según la capacidad disponible y los criterios de aceptación.

### Flujo sugerido del tablero

1. **Product Backlog:** requisitos registrados y aún no seleccionados para un Sprint.
2. **Sprint Backlog:** requisitos seleccionados para el Sprint vigente.
3. **En desarrollo:** trabajo de implementación activo.
4. **En revisión y pruebas:** comprobación de criterios de aceptación y revisión técnica.
5. **Hecho:** requisito implementado y verificado con evidencia.

Un Issue no se moverá a “Hecho” únicamente porque exista código relacionado. Se requiere comprobar todos sus criterios de aceptación y conservar evidencia de prueba o validación.

## 3. Campos de seguimiento recomendados

| Campo | Valores o contenido |
|---|---|
| Identificador | RF-01 a RF-20; RNF-01 a RNF-15 |
| Tipo | Funcional / No funcional |
| Prioridad | Must / Should / Could |
| Estado | Product Backlog / Sprint Backlog / En desarrollo / En revisión y pruebas / Hecho |
| Sprint | Número o nombre del Sprint asignado |
| Criterios de aceptación | Condiciones observables para validar el requisito |
| Evidencia | Prueba, resultado, captura o enlace a cambio relacionado |

## 4. Procedimiento de validación

1. Revisar el requisito y su justificación con el usuario o representante del comercio.
2. Confirmar que la descripción sea clara, necesaria, coherente y verificable.
3. Revisar que no contradiga otras reglas de negocio o requisitos.
4. Ajustar el texto y los criterios de aceptación cuando se detecten ambigüedades.
5. Registrar los cambios en el documento fuente y actualizar el Issue correspondiente.
6. Implementar el requisito dentro del Sprint planificado.
7. Ejecutar las pruebas correspondientes y adjuntar la evidencia.
8. Cambiar el estado a “Hecho” solo cuando se cumplan los criterios de aceptación.

## 5. Criterio de finalización

Un requisito se considera terminado cuando:

- Su implementación corresponde con la descripción aprobada.
- Todos sus criterios de aceptación han sido comprobados.
- Las pruebas pertinentes han finalizado satisfactoriamente.
- No quedan defectos bloqueantes asociados.
- Existe evidencia verificable y trazabilidad con el cambio realizado.

## 6. Inventario de requisitos registrados

Los 35 requisitos del catálogo original se han creado como Issues independientes. Los enlaces directos son:

| ID | Requisito | Issue |
|---|---|---|
| RF-01 | Inicio y cierre de sesión segura | [#15](https://github.com/Shajs23224224/ModaStock/issues/15) |
| RF-02 | Administración de usuarios | [#16](https://github.com/Shajs23224224/ModaStock/issues/16) |
| RF-03 | Autorización basada en roles | [#17](https://github.com/Shajs23224224/ModaStock/issues/17) |
| RF-04 | Registro y consulta de productos | [#18](https://github.com/Shajs23224224/ModaStock/issues/18) |
| RF-05 | Gestión de categorías | [#19](https://github.com/Shajs23224224/ModaStock/issues/19) |
| RF-06 | Variantes por talla y color | [#20](https://github.com/Shajs23224224/ModaStock/issues/20) |
| RF-07 | Prevención de variantes duplicadas | [#21](https://github.com/Shajs23224224/ModaStock/issues/21) |
| RF-08 | Consulta de existencias por variante | [#22](https://github.com/Shajs23224224/ModaStock/issues/22) |
| RF-09 | Registro de entradas de inventario | [#23](https://github.com/Shajs23224224/ModaStock/issues/23) |
| RF-10 | Registro de salidas de inventario | [#24](https://github.com/Shajs23224224/ModaStock/issues/24) |
| RF-11 | Bloqueo de salidas con stock insuficiente | [#25](https://github.com/Shajs23224224/ModaStock/issues/25) |
| RF-12 | Ajustes justificados de inventario | [#26](https://github.com/Shajs23224224/ModaStock/issues/26) |
| RF-13 | Historial de movimientos | [#27](https://github.com/Shajs23224224/ModaStock/issues/27) |
| RF-14 | Configuración de stock mínimo por variante | [#28](https://github.com/Shajs23224224/ModaStock/issues/28) |
| RF-15 | Alertas de existencias bajas | [#29](https://github.com/Shajs23224224/ModaStock/issues/29) |
| RF-16 | Registro y consulta de proveedores | [#30](https://github.com/Shajs23224224/ModaStock/issues/30) |
| RF-17 | Reportes de existencias y movimientos | [#31](https://github.com/Shajs23224224/ModaStock/issues/31) |
| RF-18 | Filtros de productos y movimientos | [#32](https://github.com/Shajs23224224/ModaStock/issues/32) |
| RF-19 | Desactivación lógica de productos | [#33](https://github.com/Shajs23224224/ModaStock/issues/33) |
| RF-20 | Registro de eventos administrativos | [#34](https://github.com/Shajs23224224/ModaStock/issues/34) |
| RNF-01 | Almacenamiento seguro de contraseñas | [#35](https://github.com/Shajs23224224/ModaStock/issues/35) |
| RNF-02 | Autorización verificada en el servidor | [#36](https://github.com/Shajs23224224/ModaStock/issues/36) |
| RNF-03 | Atomicidad de movimientos y existencias | [#37](https://github.com/Shajs23224224/ModaStock/issues/37) |
| RNF-04 | Integridad y consistencia de datos | [#38](https://github.com/Shajs23224224/ModaStock/issues/38) |
| RNF-05 | Rendimiento de consultas comunes | [#39](https://github.com/Shajs23224224/ModaStock/issues/39) |
| RNF-06 | Manejo explícito de indisponibilidad y errores | [#40](https://github.com/Shajs23224224/ModaStock/issues/40) |
| RNF-07 | Usabilidad y validación de formularios | [#41](https://github.com/Shajs23224224/ModaStock/issues/41) |
| RNF-08 | Accesibilidad de la interfaz | [#42](https://github.com/Shajs23224224/ModaStock/issues/42) |
| RNF-09 | Modularidad y mantenibilidad | [#43](https://github.com/Shajs23224224/ModaStock/issues/43) |
| RNF-10 | Interoperabilidad mediante contratos explícitos | [#44](https://github.com/Shajs23224224/ModaStock/issues/44) |
| RNF-11 | Trazabilidad de operaciones | [#45](https://github.com/Shajs23224224/ModaStock/issues/45) |
| RNF-12 | Procedimiento de respaldo y restauración | [#46](https://github.com/Shajs23224224/ModaStock/issues/46) |
| RNF-13 | Compatibilidad con navegadores modernos | [#47](https://github.com/Shajs23224224/ModaStock/issues/47) |
| RNF-14 | Minimización y protección de datos personales | [#48](https://github.com/Shajs23224224/ModaStock/issues/48) |
| RNF-15 | Observabilidad sin exposición de secretos | [#49](https://github.com/Shajs23224224/ModaStock/issues/49) |

## 7. Estado de implementación de la herramienta

- Los 20 requisitos funcionales y los 15 no funcionales se encuentran registrados como Issues abiertos.
- Cada Issue contiene su descripción, criterios de aceptación, prioridad y vínculo al catálogo.
- Los Issues permanecen abiertos y pendientes de revisión/validación; no se declaran aprobados por anticipado.
- **Pendiente:** crear el tablero de GitHub Projects desde la interfaz web y añadir los 35 Issues a la vista del Product Backlog. La conexión utilizada para esta operación permite crear y consultar Issues y archivos, pero no expone la acción de creación de Projects V2.
- **Pendiente:** confirmar la metodología con el documento de metodología del proyecto y validar el catálogo con un usuario representativo.

## 8. Evidencias que deben conservarse

Para la entrega de la evidencia SENA, conservar capturas de:

1. Repositorio ModaStock y su estructura documental.
2. Listado de Issues con requisitos funcionales y no funcionales.
3. Detalle de un Issue funcional con sus criterios de aceptación.
4. Detalle de un Issue no funcional con su objetivo verificable.
5. Tablero de GitHub Projects con el Product Backlog y los estados.
6. Registro de una revisión o ajuste realizado durante la validación.

La existencia de los Issues demuestra el registro y la organización inicial de los requisitos. La validación con el cliente o usuario, así como el funcionamiento del tablero, deben demostrarse con sus respectivas evidencias.
