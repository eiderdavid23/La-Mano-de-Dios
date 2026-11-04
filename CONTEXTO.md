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
- Login con USUARIO y contraseña (sin correo real): la app agrega @manodedios.app al usuario para Firebase Authentication (correo/contraseña). La sesión queda guardada en el teléfono, no vuelve a pedir login hasta cerrar sesión. Los usuarios se crean a mano en la consola de Firebase con el correo usuario@manodedios.app.
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

## Pendiente
- [ ] Definir los gramos por rollo reales de cada producto
- [ ] Base de datos: se deja para después. El cliente pidió cambios, revisarlos antes de conectar Firebase
- [ ] Confirmar con el cliente si "se hicieron N rollos" debe ser un paso aparte de la venta (producción) o si descontar al vender está bien
- [ ] Confirmar cómo se venden las salsas (¿también por rollos o por otra unidad?)
- [ ] Login y usuarios (empleados)
- [ ] Guardar datos en la nube (Firebase) para usar en varios celulares
- [ ] Gastos del mes (restar a la ganancia)
- [ ] Iconos propios de la app y modo sin internet
