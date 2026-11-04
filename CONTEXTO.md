# CONTEXTO DEL PROYECTO — Control de Rollos

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
- Se compra por kilos y se vende por rollos.
- Cada producto tiene: unidades por rollo (Clavitos = 14), rollos por kilo (conversión), precio de venta por rollo (Clavitos = 2000), costo por kilo y stock mínimo.
- Ingresar kilos: rollos = kilos × rollos por kilo, se suman al stock.
- Costo por rollo = costo por kilo ÷ rollos por kilo. Ganancia por rollo = precio − costo por rollo.
- Cada venta guarda su costo y ganancia en ese momento, así los cambios de precio no alteran el historial.
- Ganancia del día y del mes = suma de las ganancias de las ventas.

## Cómo trabajo (para la IA)
- Programo desde el celular con Termux. Dar el código en bloques para copiar y pegar con cat > archivo << 'EOF'.
- Después de cada cambio: git add -A && git commit -m "mensaje" && git push
- Respuestas cortas, en español.

## Hecho
- [x] Diseño base oscuro con burbujas y barra inferior
- [x] Productos: crear, editar, borrar
- [x] Ingreso por kilos con conversión automática a rollos
- [x] Registro de ventas con stock descontado y opción de deshacer
- [x] Ganancia del día (Inicio) y del mes (Ganancias, con día por día y por producto)
- [x] Alerta de stock bajo
- [x] Respaldo: descargar y restaurar JSON

## Pendiente
- [ ] Definir los rollos por kilo reales de cada producto
- [ ] Login y usuarios (empleados)
- [ ] Guardar datos en la nube (Firebase) para usar en varios celulares
- [ ] Gastos del mes (restar a la ganancia)
- [ ] Iconos propios de la app y modo sin internet
