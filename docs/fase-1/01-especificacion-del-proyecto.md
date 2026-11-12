# Fase 1 — Análisis y especificación de ModaStock

- **Proyecto:** ModaStock
- **Tipo de producto:** aplicación web de gestión de inventario para tiendas y marcas de ropa
- **Versión del documento:** 1.0
- **Estado:** especificación inicial; los supuestos deberán validarse con usuarios reales antes de cerrar el análisis.
- **Fase del plan:** 1 de 10

## 1. Resumen ejecutivo

ModaStock busca resolver las dificultades de control de inventario que presentan los comercios de prendas de vestir cuando administran productos con múltiples referencias, tallas y colores. Una prenda comercial no se controla únicamente por su nombre: cada combinación de modelo, talla y color puede tener una existencia distinta y debe identificarse de forma inequívoca.

La solución propuesta es un sistema web centralizado que permita registrar el catálogo de prendas, definir sus variantes, consultar existencias, registrar entradas y salidas, controlar ajustes y consultar alertas e informes básicos. Las operaciones que alteren el inventario deberán quedar registradas para facilitar la trazabilidad.

El producto se construirá progresivamente mediante tecnologías orientadas a servicios. La arquitectura concreta, el motor de base de datos y las herramientas se decidirán y justificarán en la **Fase 2**, por lo que esta especificación no presupone que una tecnología ya esté implementada.

## 2. Problema y oportunidad

En una tienda de ropa, un mismo diseño puede venderse en diferentes tallas y colores. Llevar el control en hojas de cálculo, apuntes o registros separados puede ocasionar:

- Diferencias entre las existencias registradas y las unidades disponibles.
- Confusión entre referencias, tallas y colores similares.
- Dificultad para identificar productos agotados o próximos a agotarse.
- Falta de trazabilidad sobre quién registró una entrada, salida o ajuste y cuándo lo hizo.
- Demoras al consultar el inventario o preparar reposiciones.
- Dificultad para consolidar información y generar reportes confiables.

ModaStock centralizará estos datos y aplicará reglas de validación para reducir errores operativos. El sistema apoyará la gestión del inventario; no reemplazará por ahora un sistema contable ni un punto de venta completo.

## 3. Objetivos

### 3.1 Objetivo general

Especificar y desarrollar un sistema web de inventario especializado en el sector de la moda que permita administrar prendas y sus variantes, controlar existencias y registrar los movimientos de inventario con trazabilidad.

### 3.2 Objetivos específicos

1. Definir un catálogo de productos con referencias y categorías.
2. Representar las variantes de cada prenda mediante combinaciones de talla y color.
3. Consultar las existencias disponibles por variante.
4. Registrar entradas, salidas y ajustes con motivo, fecha y usuario responsable.
5. Configurar niveles mínimos y detectar existencias bajas.
6. Mantener información básica de proveedores.
7. Consultar reportes básicos de existencias y movimientos.
8. Aplicar autenticación, autorización por roles y validaciones de integridad.
9. Diseñar una solución modular que permita integrar sus componentes mediante servicios documentados.

## 4. Usuarios y actores

| Actor | Descripción | Necesidades principales |
|---|---|---|
| Administrador | Responsable de la configuración y administración del sistema | Gestionar usuarios, roles, catálogo y parámetros |
| Encargado de inventario | Responsable del control de existencias | Registrar productos, variantes, entradas, salidas y ajustes |
| Operador | Usuario autorizado para ejecutar operaciones asignadas | Consultar productos y registrar movimientos permitidos |
| Consultor | Usuario de solo lectura | Consultar existencias y reportes sin modificar información |

Los roles son una propuesta inicial. Los permisos exactos se detallarán durante el diseño de seguridad y deberán poder configurarse sin depender de que todos los comercios tengan la misma estructura de personal.

## 5. Alcance del producto

### 5.1 Alcance del producto mínimo viable (MVP)

La primera versión funcional comprenderá:

- Autenticación de usuarios.
- Gestión de usuarios y roles básicos.
- Registro, consulta, edición y desactivación lógica de productos.
- Gestión de categorías y referencias.
- Definición de tallas y colores.
- Creación de variantes por producto y combinación talla-color.
- Consulta de existencias por variante.
- Registro de entradas, salidas y ajustes de inventario.
- Historial de movimientos con fecha, responsable y motivo.
- Configuración de stock mínimo y alertas de existencias bajas.
- Registro y consulta de proveedores.
- Reportes básicos de existencias y movimientos.
- Validaciones para evitar referencias duplicadas y operaciones que dejen existencias negativas.

### 5.2 Fuera del alcance del MVP

Se consideran mejoras futuras y no condiciones para la primera entrega:

- Punto de venta (POS), caja y facturación electrónica.
- Contabilidad, nómina y gestión tributaria.
- Operación multi-sucursal y transferencias entre sedes.
- Aplicación móvil nativa y funcionamiento sin conexión.
- Integración con marketplaces, comercio electrónico o transportadoras.
- Lectura e impresión avanzada de códigos de barras o QR.
- Predicción de demanda mediante inteligencia artificial.
- Compras automatizadas y órdenes de compra avanzadas.

Estas funciones podrán incorporarse después de evaluar su valor, complejidad y prioridad.

## 6. Procesos principales

### 6.1 Registro de producto y variantes

1. Un usuario autorizado registra los datos generales de la prenda.
2. Selecciona o crea su categoría y referencia.
3. Define las tallas y colores disponibles.
4. El sistema crea una variante identificable para cada combinación válida.
5. Se registra el inventario inicial mediante un movimiento de entrada, no mediante una modificación silenciosa de la existencia.

### 6.2 Entrada de inventario

1. El usuario selecciona la variante.
2. Indica una cantidad positiva y, cuando corresponda, el proveedor y el documento de soporte.
3. El sistema valida los datos.
4. La operación incrementa la existencia y genera un movimiento trazable.

### 6.3 Salida de inventario

1. El usuario selecciona la variante e indica la cantidad.
2. El sistema verifica que exista disponibilidad suficiente.
3. Si la operación es válida, descuenta las unidades y registra el movimiento.
4. Si no hay unidades suficientes, rechaza la operación y explica el motivo.

### 6.4 Ajuste de inventario

1. Un usuario con permiso registra la cantidad que debe ajustarse y el motivo.
2. El sistema conserva el valor anterior, la diferencia, el usuario y la fecha.
3. El ajuste queda en el historial y no elimina movimientos anteriores.

### 6.5 Consulta y alertas

El usuario consulta existencias por producto, referencia, talla y color. El sistema identifica variantes cuya existencia sea igual o inferior al mínimo configurado.

## 7. Reglas de negocio iniciales

- **RN-01 — Identificación de variante:** cada variante debe pertenecer a un producto y representar una combinación válida de talla y color.
- **RN-02 — Unicidad:** no se permiten dos variantes activas con la misma combinación de producto, talla y color.
- **RN-03 — Existencia no negativa:** una operación ordinaria no puede dejar el inventario por debajo de cero.
- **RN-04 — Movimientos trazables:** toda entrada, salida o ajuste debe registrar tipo, cantidad, fecha, usuario y motivo o referencia.
- **RN-05 — Cantidad válida:** la cantidad de cada movimiento debe ser un número entero positivo; la dirección del movimiento determina si suma o resta.
- **RN-06 — Historial:** los movimientos confirmados no se borran ni se modifican silenciosamente. Los errores se corrigen mediante un movimiento compensatorio autorizado.
- **RN-07 — Stock mínimo:** el nivel mínimo se configura por variante; si no se define, la alerta no se activa para esa variante.
- **RN-08 — Productos inactivos:** un producto desactivado no podrá recibir nuevas operaciones ordinarias, pero su historial seguirá disponible.
- **RN-09 — Permisos:** solo los roles autorizados pueden crear, modificar, desactivar o registrar movimientos.
- **RN-10 — Integridad de operación:** la actualización de existencias y la creación del movimiento deben confirmarse como una única operación lógica; no debe quedar una sin la otra.

## 8. Supuestos, restricciones y dependencias

### Supuestos por validar

- El escenario inicial es una tienda con un único inventario central.
- Las cantidades de prendas se manejan en unidades enteras.
- Las variantes se distinguen inicialmente por talla y color.
- La primera versión será web y requerirá conexión a Internet.
- Los usuarios dispondrán de credenciales individuales.

### Restricciones

- El proyecto se desarrollará por fases y con recursos limitados.
- La solución debe priorizar claridad, mantenibilidad, seguridad e integridad de datos.
- No se afirmará que existen integraciones o funciones que aún no hayan sido construidas y probadas.

### Dependencias

- Validación del alcance con un usuario que conozca la operación de una tienda de ropa.
- Selección de arquitectura y tecnologías en la Fase 2.
- Diseño del modelo de datos en la Fase 3.
- Implementación y pruebas de los servicios en las fases posteriores.

## 9. Criterios generales de aceptación del MVP

El MVP podrá considerarse funcionalmente aceptado cuando se demuestre que:

1. Un usuario autorizado puede iniciar sesión y acceder únicamente a las funciones permitidas.
2. Se puede registrar un producto con varias tallas y colores.
3. Cada combinación de variante mantiene una existencia independiente.
4. Una entrada incrementa la existencia y genera su movimiento correspondiente.
5. Una salida válida disminuye la existencia y genera su movimiento correspondiente.
6. Una salida superior a la existencia disponible es rechazada.
7. Un ajuste requiere motivo y queda reflejado en el historial.
8. Una variante igual o inferior a su stock mínimo aparece en las alertas.
9. Los reportes básicos coinciden con los registros almacenados.
10. Las operaciones críticas mantienen la consistencia entre existencias e historial.

La aceptación deberá sustentarse con casos de prueba y evidencias en la Fase 9; esta lista define resultados esperados, no afirma que ya hayan sido probados.

## 10. Riesgos iniciales

| Riesgo | Consecuencia | Mitigación prevista |
|---|---|---|
| Requisitos incompletos | Retrabajo y cambios de alcance | Validar procesos y supuestos antes de cerrar la fase |
| Variantes mal identificadas | Existencias mezcladas o duplicadas | Definir claves únicas y pruebas por talla-color |
| Movimientos sin trazabilidad | Pérdida de confianza en el inventario | Historial obligatorio y permisos |
| Pérdida o exposición de datos | Impacto operativo y de privacidad | Autenticación, copias de seguridad y controles de acceso |
| Crecimiento prematuro del alcance | Retrasos | Priorizar el MVP y registrar mejoras futuras |

## 11. Entregables de la Fase 1

- Especificación del problema y objetivos.
- Identificación de actores y necesidades.
- Alcance del MVP y exclusiones.
- Requisitos funcionales y no funcionales.
- Reglas de negocio.
- Procesos principales.
- Criterios de aceptación.
- Riesgos, supuestos y dependencias.
- Hoja de ruta de diez fases.

## 12. Cierre de fase

La Fase 1 establece una base funcional verificable para ModaStock. Antes de considerar esta especificación definitiva, se deben validar los supuestos con un comercio real o un usuario representativo. La Fase 2 utilizará estos requisitos para comparar y justificar la arquitectura, los componentes y las tecnologías de implementación.
