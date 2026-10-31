# Guion para video de defensa - TFI Bases de Datos I

**Duración estimada:** 10-15 minutos  
**Participantes:** Alejandro Fernández, Gabriel Di Lorenzo y Josue Gallardo

---

## Plan de grabación

La narración se organiza en este orden, sin alternar participantes:

1. Apertura breve con los tres integrantes (opcional, 20-30 segundos).
2. Bloque completo de Alejandro Fernández.
3. Bloque completo de Gabriel Di Lorenzo.
4. Bloque completo de Josue Gallardo.
5. Despedida breve con los tres integrantes (opcional, 15-20 segundos).

Cada integrante puede grabar su bloque de corrido o dividirlo en **hasta tres clips**, siempre en el orden indicado y sin intercalar voces. Si se graba en clips, se pueden unir directamente en la web. Las capturas, el código y las consultas se muestran como apoyo visual mientras continúa el audio del mismo integrante; no hace falta grabar de nuevo cada cambio de pantalla.

Los rótulos “A”, “B” y “C” de la versión anterior se reemplazan por los nombres para evitar confusiones: **A = Alejandro, B = Gabriel, C = Josue**.

---

## Apertura conjunta (opcional, 20-30 segundos)

**[Los tres integrantes en pantalla. Si no es posible grabarlos juntos, se puede omitir esta apertura: Alejandro comienza su bloque con la presentación.]**

**Alejandro:** Buenas tardes. Somos Alejandro Fernández, Gabriel Di Lorenzo y Josue Gallardo, de la comisión 2 de Bases de Datos I.

**Gabriel:** En este video presentamos nuestro Trabajo Final Integrador: un sistema de gestión de pedidos y ventas online implementado en MySQL 8.0.

**Josue:** Vamos a recorrer el modelo, la carga de datos, las consultas, la seguridad y las transacciones.

---

# Bloque 1 - Alejandro Fernández

**Grabación:** una toma continua o hasta tres clips consecutivos.  
**Duración orientativa:** 3-4 minutos.

### Clip 1 - Sistema y modelo

**[Mostrar el DER: `captura/png/00_der.png`; luego, la estructura de tablas.]**

El sistema representa un comercio electrónico con cinco entidades principales: cliente, pedido, detalle_pedido, producto y categoría. El recorrido principal es cliente, pedido, detalle del pedido, producto y categoría.

Aplicamos once correcciones al DER original para reforzar la integridad: agregamos restricciones CHECK para validar rangos, UNIQUE en los nombres de categoría, valores por defecto para fechas y un campo de stock en producto para controlar el inventario.

Una decisión importante fue guardar `precio_unitario` en `detalle_pedido`. Así conservamos el precio histórico de cada venta aunque después cambie el precio del producto. No agregamos una columna `total` a pedido porque el total se calcula dinámicamente en una vista.

Usamos MySQL 8.0.42 en una instancia portable, en el puerto 3307, con InnoDB y codificación utf8mb4.

### Clip 2 - Etapa 1: esquema y constraints

**[Mostrar `scripts/01_esquema.sql`; ejecutar `SHOW CREATE TABLE cliente;`. Después, mostrar `captura/png/01_ok_insert_1.png` y `captura/png/03_err_unique.png`.]**

El script `01_esquema.sql` crea las cinco tablas y sus restricciones. Nombramos explícitamente las claves y restricciones con prefijos como `pk_`, `fk_`, `uq_` y `chk_`, para facilitar su identificación y mantenimiento.

En cliente, por ejemplo, usamos `id_cliente` como clave primaria y una restricción UNIQUE para el DNI. También validamos el formato del email con CHECK. Las claves foráneas usan ON DELETE RESTRICT para evitar borrar registros que tienen información relacionada.

En las evidencias vemos inserciones válidas y tres casos rechazados: una categoría duplicada por UNIQUE, un stock negativo por CHECK y una referencia a un cliente inexistente por clave foránea. Los errores aparecen documentados en los scripts.

### Clip 3 - Etapa 3: índices

**[Mostrar `scripts/04_indices.sql`, `captura/png/29_tiempos_indices.png` y las evidencias `captura/png/20_explain_e1_con.png` y `captura/png/22_analyze_e1_sin.png`.]**

Para optimizar las consultas creamos cinco índices: uno compuesto sobre pedido por estado y fecha, otro por fecha, uno por id_cliente para los JOIN, y dos índices en detalle_pedido y producto.

Medimos tres consultas con y sin índices, realizando tres ejecuciones de cada una y comparando las medianas. La consulta de igualdad mejoró 1,5 veces, la de rango 2,2 veces y el JOIN 4,4 veces.

El EXPLAIN permite ver la diferencia: con índice se accede directamente a las filas correspondientes; sin índice, se recorren las 80.000 filas de la tabla pedido.

---

# Bloque 2 - Gabriel Di Lorenzo

**Grabación:** una toma continua o hasta tres clips consecutivos.  
**Duración orientativa:** 3-4 minutos.

### Clip 1 - Etapa 2: carga masiva

**[Mostrar `scripts/03_carga_masiva.sql`, la CTE `WITH RECURSIVE DIGITOS` y `captura/png/08_verif_conteos.png`.]**

Para la carga masiva usamos SQL, sin procedimientos. Una CTE recursiva genera los dígitos del cero al nueve y los combinamos con CROSS JOIN para producir hasta 10.000 combinaciones.

Con esa técnica generamos 20.000 clientes, 5.000 productos, 80.000 pedidos y 240.000 detalles; en total, 345.010 filas. Usamos funciones como MOD y CASE para definir distribuciones, por ejemplo, asignar más productos a ciertas categorías.

En las verificaciones comprobamos que cada tabla tenga la cantidad esperada, que no existan claves foráneas huérfanas y que las fechas estén dentro del rango 2020-2026. También revisamos la distribución de estados. Los 240.000 detalles para 80.000 pedidos dan un promedio de tres productos por pedido.

**[Mostrar `captura/png/12_verif_coherencia.png`.]**

### Clip 2 - Etapa 3: consultas y vistas

**[Mostrar `scripts/05_consultas.sql`; ejecutar la consulta de top pedidos. Luego, mostrar `scripts/06_vistas.sql` y `captura/png/32_vista_cliente_publico.png`.]**

Implementamos seis consultas de negocio: cuatro requeridas —dos con JOIN, una con GROUP BY y HAVING, y una subconsulta— y dos adicionales. Entre ellas, mostramos los diez pedidos de mayor monto, las ventas por categoría y los clientes VIP con más de 10.000 pesos en compras.

También creamos cuatro vistas: un resumen de pedidos que calcula el total, una vista de ventas por categoría y dos vistas orientadas al enmascaramiento de datos.

En esta evidencia se ve la vista de cliente público: presenta el nombre de forma parcial, oculta parte del email y oculta el teléfono para limitar la exposición de datos personales.

### Clip 3 - Etapa 4: roles y acceso

**[Mostrar `scripts/07_seguridad.sql`, `captura/png/42_grants_analista.png` y `captura/png/45_acceso_restringido.png`.]**

Para controlar el acceso creamos dos roles. `rol_analista` tiene SELECT únicamente sobre vistas de reporting. `rol_vendedor` puede consultar e insertar pedidos y detalles, pero no tiene acceso a las tablas maestras.

Los permisos del usuario `tfi_analista` muestran que puede consultar tres vistas, pero no las tablas base. Al intentar consultar directamente la tabla cliente recibe un error de acceso denegado; al hacer la consulta a través de la vista, funciona.

---

# Bloque 3 - Josue Gallardo

**Grabación:** una toma continua o hasta tres clips consecutivos.  
**Duración orientativa:** 4-5 minutos.

### Clip 1 - Seguridad: integridad y anti-inyección

**[Mostrar `sp_buscar_cliente_por_dni`, `captura/png/39_inyeccion_bloqueada.png` y `captura/png/37_integr_check.png`.]**

Para evitar inyección SQL, creamos un procedimiento almacenado parametrizado. El parámetro tiene tipo VARCHAR y se usa como valor; no concatenamos SQL ni ejecutamos consultas dinámicas con PREPARE.

Al probar la cadena `' OR '1'='1'`, el procedimiento la trata como un dato literal y devuelve cero filas, en lugar de devolver todos los clientes.

También verificamos las restricciones de integridad: CHECK rechaza estados inválidos, la clave foránea impide referencias a clientes inexistentes y UNIQUE evita duplicados.

### Clip 2 - Etapa 5: transacciones

**[Mostrar `scripts/08_transacciones.sql`, `captura/png/47_tx_commit.png` y `captura/png/48_tx_stock_insuficiente.png`.]**

Para registrar una venta completa implementamos `sp_registrar_venta`. El procedimiento controla el stock con una transacción, bloquea la fila del producto con SELECT FOR UPDATE, valida las condiciones de negocio y confirma con COMMIT o revierte con ROLLBACK.

En el caso exitoso, el stock pasa de 50 a 45. Si no hay stock suficiente, se ejecuta el rollback y el stock queda sin cambios. También se valida que el cliente esté activo y que el producto exista; si una condición falla, no se persiste la venta.

### Clip 3 - Concurrencia y cierre

**[Mostrar `scripts/09_concurrencia_guiada.sql`, `captura/png/53_deadlock.png`, `captura/png/54_deadlock_innodb.png` y `captura/png/55_isolation.png`.]**

Para probar concurrencia simulamos un deadlock con dos sesiones. La sesión A bloquea el producto 1 y la sesión B bloquea el producto 2. Después cada una intenta actualizar el producto bloqueado por la otra. InnoDB detecta el ciclo y aborta una transacción con el error 1213. El procedimiento contempla este error y reintenta hasta tres veces con una espera incremental.

También comparamos los niveles REPEATABLE READ y READ COMMITTED. En REPEATABLE READ, una segunda lectura dentro de la misma transacción conserva la primera imagen de los datos. En READ COMMITTED, la segunda lectura puede ver los cambios confirmados por otra transacción.

En conclusión, implementamos las etapas del trabajo con 345.010 registros, consultas optimizadas, vistas y roles de seguridad, validaciones contra inyección y manejo transaccional del stock y la concurrencia. Los scripts permiten reproducir las pruebas y las capturas documentan sus resultados. Muchas gracias por su atención.

**[Pantalla final: título del trabajo y nombres de los tres integrantes.]**

---

## Indicaciones para la grabación

### Antes de grabar

- Encender MySQL con `herramientas\start_mysql.bat`.
- Verificar que las capturas estén generadas en `capturas/png/` (se esperan 56 archivos).
- Probar las consultas que se ejecutarán en vivo.
- Cada integrante graba su bloque completo; si necesita pausas, puede grabar hasta tres clips consecutivos.

### Durante la grabación

- Mantener el orden: Alejandro, Gabriel y Josue, sin intercalar participantes.
- Dejar el audio del integrante como pista continua y mostrar encima el código, las consultas o las capturas indicadas.
- Compartir pantalla cuando corresponda y señalar con el cursor lo que se está explicando.
- Hablar con claridad y ritmo moderado. Si algo falla, explicar qué ocurrió y continuar.

### Después de grabar

- Unir los bloques en el orden indicado. Agregar la apertura y la despedida conjunta sólo si pudieron grabarlas.
- Revisar claridad del audio y legibilidad de las capturas.
- Recortar pausas largas o errores triviales; agregar subtítulos si hace falta.
- Subir el video a la plataforma y pegar el enlace en el PDF.

## Duración orientativa

- Apertura conjunta opcional: 20-30 segundos.
- Alejandro: 3-4 minutos.
- Gabriel: 3-4 minutos.
- Josue: 4-5 minutos.
- Despedida conjunta opcional: 15-20 segundos.
- **Total estimado:** 10-15 minutos.

## Checklist antes de entregar

- [ ] Los tres integrantes aparecen al inicio si se incluye la apertura conjunta.
- [ ] Duración entre 10 y 15 minutos.
- [ ] Audio claro y comprensible.
- [ ] Capturas legibles en pantalla.
- [ ] Ejecuciones en vivo funcionando correctamente.
- [ ] Grabación con voces reales, sin voz sintética.
- [ ] Video subido a la plataforma.
- [ ] Enlace del video pegado en el PDF (sección 9).
