# CONTEXTO DEL PROYECTO — Condimentos la Mano de Dios

> Para la IA: lee esto completo antes de cambiar código.
> Para mí: en un chat nuevo, pego este archivo y digo qué quiero cambiar.

## Qué es
Plataforma web (PWA) para llevar stock, inventario y ganancias de productos que se venden por rollos (ej. Clavitos). Inspirada en Maní García pero con diseño propio: tema oscuro, estilo burbuja, barra inferior flotante.
HTML + CSS + JavaScript puro, sin frameworks. Datos en localStorage del teléfono (con respaldo en JSON). Idioma: español de Colombia, moneda COP. Se publica con GitHub Pages.

## Estructura
- index.html: pantalla base
- manifest.json: PWA
- css/styles.css: estilos
- js/app.js: toda la lógica y las vistas

## Regla de negocio
- Los aliños se compran por kilos o libras (1 libra = 500 g). El STOCK se guarda y se muestra en GRAMOS.
- Se venden por rollos. Cada producto tiene: gramos por rollo (Clavitos = 33 g; se pesa un rollo), unidades por rollo (Clavitos = 14), precio de venta por rollo (Clavitos = 2000), costo por kilo y aviso de stock mínimo (en gramos).
- Ingresar kilos o libras: gramos = cantidad × 1000 (kilo) o × 500 (libra), se suman al stock en gramos. El costo se puede escribir por kilo o por libra (se guarda por kilo).
- Vender/registrar rollos: se descuenta rollos × gramos por rollo del stock (ej. 20 rollos × 33 g = 660 g). Deshacer la venta devuelve esos gramos.
- La app muestra cuántos rollos salen por kilo y por libra (1000 ÷ gramos por rollo) y para cuántos rollos alcanza el stock.
- Costo por rollo = costo por kilo × gramos por rollo ÷ 1000. Ganancia por rollo = precio − costo por rollo.
- Cada venta guarda su costo, ganancia y gramos descontados en ese momento, así los cambios de precio no alteran el historial.
- Ganancia del día y del mes = suma de las ganancias de las ventas.
- Sin gramos por rollo no se puede vender el producto (se define al crearlo, en Editar o en cada ingreso).
- Cada producto tiene categoría (Aliños, Salsas, Otro). En Stock y Vender se puede filtrar por categoría y buscar por nombre.
- Campos del producto: stockG, minimoG, gramosPorRollo (antes stock, minimo, rollosPorKilo). Los datos viejos se convierten solos al abrir (migrar() en app.js), también al restaurar un respaldo o leer de Firebase.

## Firebase
- Realtime Database, nodo "negocio" con productos, entradas y ventas (cada registro guardado por su id).
- Login con USUARIO y contraseña (sin correo real): la app agrega @manodedios.app para Firebase Authentication. La sesión queda guardada en el teléfono. Cualquiera puede crear cuenta en la pantalla de login; queda en espera hasta que el administrador la apruebe en ⚙️ → Usuarios. La primera cuenta creada es la administradora. Datos en el nodo "usuarios" (nombre, aprobado, admin) y las reglas usan ese nodo. Un administrador puede dar o quitar administrador a otros usuarios aprobados (⚙️ → Usuarios). Con la nube activa ya no hay descargar/restaurar copia; esos botones solo salen en modo local.
- Reglas: solo los UID autorizados leen y escriben (el repo es público, no se deja abierto a cualquiera con sesión).
- La configuración (pública) va en js/firebase-config.js. Si ese archivo está vacío, la app funciona solo en el teléfono (localStorage).
- Con la nube vacía, al primer ingreso ofrece subir los datos guardados en el teléfono.

## Cómo trabajo (para la IA)
- Programo desde el celular con Termux. Dar el código en bloques para copiar y pegar con cat > archivo << 'EOF'. Si el archivo es largo, partirlo en bloques pequeños (el portapapeles se corta) usando cat > en el primero y cat >> en los siguientes.
- Después de cada cambio: git add -A && git commit -m "mensaje" && git push
- Respuestas cortas, en español.

## Hecho
- [x] Código de Firebase (Realtime Database + login por correo) listo
- [x] Diseño base oscuro con burbujas y barra inferior
- [x] Productos: crear, editar, borrar
- [x] Ingreso por kilos con conversión automática a rollos
- [x] Registro de ventas con stock descontado y opción de deshacer
- [x] Ganancia del día (Inicio) y del mes (Ganancias, con día por día y por producto)
- [x] Alerta de stock bajo
- [x] Respaldo: descargar y restaurar JSON
- [x] Precio, rollos por kilo y costo editables por producto y en cada ingreso de kilos
- [x] Categorías, filtro y buscador en Stock y Vender
- [x] Nombre de la plataforma: Condimentos la Mano de Dios
- [x] Categoría con desplegable: Aliños, Salsas, Otro
- [x] Ganancias: total por producto y total de todos los productos al mes
- [x] Stock en gramos: ingreso en kilos/libras, gramos por rollo, la venta descuenta gramos
- [x] Historiales detallados (ventas, pedidos, rollos hechos, ingresos de materia): al tocar uno se ve cliente, fecha, hora, quién lo registró y más
- [x] Rollos hechos puede pasarse del stock: se registra y avisa que salieron más de lo calculado
- [x] Sin emojis en el menú lateral ni en el botón Rollos hechos: ahora son iconos de línea (ICO en app.js)
- [x] Quitada la línea "Con ese stock se pueden hacer N rollos · ≈ N unidades" de cada producto en Stock

## Pendiente
- [ ] Definir los gramos por rollo reales de cada producto
- [ ] Base de datos: se deja para después. El cliente pidió cambios, revisarlos antes de conectar Firebase
- [ ] Confirmar con el cliente si "se hicieron N rollos" debe ser un paso aparte de la venta (producción) o si descontar al vender está bien
- [ ] Confirmar cómo se venden las salsas (¿también por rollos o por otra unidad?)
- [ ] Login y usuarios (empleados)
- [ ] Guardar datos en la nube (Firebase) para usar en varios celulares
- [ ] Gastos del mes (restar a la ganancia)
- [ ] Iconos propios de la app y modo sin internet

## Cambios parche8
- Botón atrás: cada pantalla, ventana y el menú lateral quedan en el historial. Atrás cierra ventana/menú y luego vuelve a la pantalla anterior.
- Login rápido: copia de datos en el teléfono (lmd_cache_v1) que se muestra al instante mientras sincroniza con Firebase por detrás (solo consulta mientras tanto). Sin sesión, el login sale de inmediato. Firebase se carga por detrás (cargarFirebase en app.js).
- Colores: el amarillo pasó a durazno suave (#F5C6A0).
- Menú lateral (hamburguesa) reemplaza al engranaje: Pedidos, Usuarios (admin), Respaldo (modo local), Cerrar sesión.
- Pedidos: nodo "pedidos" dentro de "negocio". Un pedido pendiente aparta gramos del stock (disponible = stockG - apartado). Al entregar se crean las ventas (con pedidoId) y se descuenta el stock; la ganancia cuenta el día de la entrega. Deshacer entrega borra esas ventas. Cancelar libera lo apartado.

## Cambios parche9
- Rollos hechos (producción): en Stock, botón "Rollos hechos" por producto. Se escribe cuántos rollos se hicieron y el día; descuenta gramos del stock (rollos x gramos por rollo) y suma a p.hechos. Se guarda en el nodo "produccion". El stock muestra los gramos que quedan y los rollos que aún se pueden hacer.
- Vender y pedidos ahora descuentan ROLLOS HECHOS (p.hechos), no gramos. Las ventas nuevas llevan modo:'hechos'; las viejas (sin modo) devolvían gramos al deshacer. Los pedidos pendientes apartan rollos hechos; se pueden crear sin rollos hechos, pero entregar exige tenerlos.
- Ganancias (por mes): resumen con rollos hechos, materia ingresada, producción por producto y por día. Cada mes empieza de cero; el stock que queda pasa al mes siguiente.
- Ingreso de materia: unidades Kilos, Libras o Gramos; pregunta si se ingresan 100 kilos o más.

## Cambios parche10
- Historiales detallados. Ventas, pedidos, rollos hechos e ingresos de materia guardan ahora hora (hora), quién lo registró (por: usuario de la nube, vacío en modo local) y datos extra. Los registros viejos no tienen hora: el detalle dice "No se registró".
- Tocar un registro abre su detalle (funciones detalleVenta, detallePedido, detalleProd, detalleIngreso). En Ganancias, tocar un día (Día por día o Rollos hechos por día) lista las ventas o la producción de ese día, y desde ahí se abre cada detalle con "Volver al día".
- Venta: campo opcional Cliente en Vender (v.cliente). Venta por pedido guarda cliente, hora de entrega, unidades y rollos hechos que quedaron; el detalle también muestra cuándo se hizo el pedido, la entrega prometida y la nota.
- Pedido: guarda hora (cuándo se anotó) y por; al entregar guarda entregadoHora y entregadoPor. El detalle muestra puntualidad (a tiempo, adelantado o tarde) y la ganancia del pedido.
- Stock: nueva lista "Últimos ingresos de materia" (sin deshacer).
- Rollos hechos: se pueden registrar más rollos de los que da el stock. El stock queda en 0 g y se guarda excesoG (gramos que faltaban), excesoR (rollos de más) y alcanzaba (rollos que alcanzaban). Sale aviso rojo "Salieron más de lo calculado" al escribir, en el aviso al registrar, en la lista y en el detalle. Deshacer devuelve solo los gramos que sí habían salido del stock (gramos - excesoG).

## Cambios parche11
- Stock: quitada la línea "Con ese stock se pueden hacer N rollos · ≈ N unidades" de cada producto.
- Iconos: el botón "Rollos hechos" y los items del menú lateral (Pedidos, Usuarios, Respaldo, Cerrar sesión) usan iconos SVG de línea, igual que la barra de abajo. Están en el objeto ICO de app.js (se crean con ic()). Regla: no usar emojis para botones ni menús; usar ic() con trazo.

## Cambios parche12
- Sin emojis en toda la app: los mensajes cortos van en texto y los lugares con icono usan ICO (hora, persona, nota, alerta, check). Regla: no usar emojis; usar ic() con trazo.
- Stock: la tarjeta de cada producto ahora son filas con título claro (Rollos listos para vender, Rollos hechos hoy / este mes, Cada rollo, De la materia salen, Precio de venta, Costo, Ganancia). La burbuja de la derecha dice "En bodega" con los gramos y para cuántos rollos alcanza.

## Cambios parche13
- Stock: la tarjeta de cada producto es más compacta: cuadritos de 3 columnas (Listos para vender, Hechos hoy, Hechos este mes, Cada rollo, Unidades por rollo, Rollos por kilo, Rollos por libra, Precio de venta, Costo) y debajo una barra de color con la ganancia (verde) o la pérdida (roja) por rollo y su % sobre el costo.
- Arreglado: la ganancia y la pérdida volvieron a verse en color (en parche12 el CSS de .kv las pintaba de gris).

## Cambios parche14
- Stock: la tarjeta del producto vuelve a ser simple. Se ve siempre: nombre, categoría, "En bodega" (gramos y para cuántos rollos alcanza), "Listos para vender" y la barra de ganancia (verde) o pérdida (roja) por rollo. El resto va escondido en el botón "Ver más datos" como filas con título (hechos hoy y este mes, peso de cada rollo, unidades por rollo, rollos por kilo, rollos por libra, precio de venta, costo). Los cuadritos de parche13 ya no se usan.
