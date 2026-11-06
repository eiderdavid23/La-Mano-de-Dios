import sys

def parchar(archivo, viejo, nuevo):
    s = open(archivo, encoding='utf-8').read()
    n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces) en ' + archivo + ':', viejo[:70]); sys.exit(1)
    open(archivo, 'w', encoding='utf-8').write(s.replace(viejo, nuevo))

def bloque(archivo, ini, fin, nuevo):
    s = open(archivo, encoding='utf-8').read()
    a = s.find(ini)
    if a < 0 or s.count(ini) != 1:
        print('ERROR: no encuentro (o se repite) el inicio:', ini[:60]); sys.exit(1)
    b = s.find(fin, a + 1)
    if b < 0:
        print('ERROR: no encuentro el final:', fin[:60]); sys.exit(1)
    open(archivo, 'w', encoding='utf-8').write(s[:a] + nuevo + s[b:])

A = 'js/app.js'

# ===== datos: produccion + rollos hechos =====
parchar(A, "const remoto = { productos: {}, entradas: {}, ventas: {}, pedidos: {} };", "const remoto = { productos: {}, entradas: {}, ventas: {}, pedidos: {}, produccion: {} };")
parchar(A, "const COLS = ['productos', 'entradas', 'ventas', 'pedidos'];", "const COLS = ['productos', 'entradas', 'ventas', 'pedidos', 'produccion'];")
parchar(A, "return { productos: [], entradas: [], ventas: [], pedidos: [] };", "return { productos: [], entradas: [], ventas: [], pedidos: [], produccion: [] };")
parchar(A, "db = { productos: [], entradas: [], ventas: [], pedidos: [] };", "db = { productos: [], entradas: [], ventas: [], pedidos: [], produccion: [] };")
parchar(A, "  d.pedidos = d.pedidos || [];\n", "  d.pedidos = d.pedidos || [];\n  d.produccion = d.produccion || [];\n  (d.productos || []).forEach(p => { if (p.hechos === undefined) p.hechos = 0; });\n")
parchar(A, "      pedidos: Object.values(remoto.pedidos).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1)\n    });",
"      pedidos: Object.values(remoto.pedidos).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1),\n      produccion: Object.values(remoto.produccion).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1)\n    });")
parchar(A, "ventas: d.ventas, pedidos: d.pedidos || [] });", "ventas: d.ventas, pedidos: d.pedidos || [], produccion: d.produccion || [] });")

# ===== los pedidos ahora apartan ROLLOS HECHOS (no gramos) =====
parchar(A, "const apartadoG = p => (db.pedidos || []).filter(x => x.estado === 'pendiente').reduce((a, x) => a + itemsDe(x).filter(i => i.productoId === p.id).reduce((b, i) => b + i.gramos, 0), 0);",
r"""const apartadoR = p => (db.pedidos || []).filter(x => x.estado === 'pendiente').reduce((a, x) => a + itemsDe(x).filter(i => i.productoId === p.id).reduce((b, i) => b + i.rollos, 0), 0);
const hechosLibres = p => Math.max(0, r2((p.hechos || 0) - apartadoR(p)));
const hechosEn = (pid, f) => (db.produccion || []).filter(x => x.productoId === pid && x.fecha === f).reduce((a, x) => a + x.rollos, 0);
const hechosMes = (pid, ym) => (db.produccion || []).filter(x => x.productoId === pid && x.fecha.slice(0, 7) === ym).reduce((a, x) => a + x.rollos, 0);""")
parchar(A, "const dispG = p => Math.max(0, r2(p.stockG - apartadoG(p)));", "const dispG = p => p.stockG;")
parchar(A, "apartadoG(pp) > 0", "apartadoR(pp) > 0")
parchar(A, "(apartadoG(p) > 0 ? '<b>Apartado en pedidos: ' + fmtG(apartadoG(p)) + '</b> (stock físico ' + fmtG(p.stockG) + ')<br>' : '')",
"'<b>Rollos hechos: ' + fmt(p.hechos || 0) + '</b>' + (apartadoR(p) > 0 ? ' (' + fmt(apartadoR(p)) + ' apartados en pedidos)' : '') + ' · hoy ' + fmt(hechosEn(p.id, hoy())) + ' · este mes ' + fmt(hechosMes(p.id, hoy().slice(0, 7))) + '<br>'")
parchar(A, "'<br>Alcanza para '", "'<br>Con ese stock se pueden hacer '")
parchar(A, "＋ Ingresar kilos/libras</button>", "＋ Ingresar kilos/libras</button><button class=\"btn main\" onclick=\"formProduccion(\\'' + p.id + '\\')\">🧆 Rollos hechos</button>")

# ===== Stock: ultimos rollos hechos =====
bloque(A, "function vStock() {", "function listaStock() {",
r"""function vStock() {
  const rec = db.produccion.slice().sort((a, b) => a.id < b.id ? 1 : -1).slice(0, 8);
  return '<h2>Inventario</h2><button class="add" onclick="formProducto()">＋ Nuevo producto</button>' +
    (db.productos.length ? barraFiltro() + '<div id="lista">' + listaStock() + '</div>' : '<div class="empty">Aún no hay productos</div>') +
    (rec.length ? '<h2 style="margin-top:22px">Últimos rollos hechos</h2>' + rec.map(x => '<div class="item"><div class="row"><div><div class="name">' + esc(x.nombre) + '</div><div class="meta">' + fmt(x.rollos) + ' rollos · ' + nombreDia(x.fecha) + ' · ' + fmtG(x.gramos) + '</div></div><button class="btn del" onclick="borrarProduccion(\'' + x.id + '\')">Deshacer</button></div></div>').join('') : '');
}
""")

# ===== Registrar rollos hechos =====
parchar(A, "// ===== Vender =====",
r"""// ===== Rollos hechos (producción) =====
function formProduccion(id) {
  if (espera()) return;
  const p = prod(id);
  if (!(gpr(p) > 0)) return toast('Primero define los gramos por rollo (Editar)');
  modal('<h3>Rollos hechos · ' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Descuenta los gramos del stock y suma rollos listos para vender</div>' +
    '<label>¿Cuántos rollos hiciste?</label><input id="h-cant" type="number" inputmode="decimal" placeholder="Ej: 20" oninput="prevProd(\'' + id + '\')">' +
    '<label>Día en que los hiciste</label><input id="h-fec" type="date" value="' + hoy() + '" max="' + hoy() + '">' +
    '<div class="preview" id="h-prev"></div>' +
    '<button class="btn main full" onclick="confirmarProd(\'' + id + '\')">Registrar rollos hechos</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
  prevProd(id);
}
function prevProd(id) {
  const p = prod(id), q = num($('#h-cant').value), resto = p.stockG - q * gpr(p);
  $('#h-prev').textContent = q > 0
    ? 'Se descuentan ' + fmtG(q * gpr(p)) + ' · quedan ' + fmtG(Math.max(0, resto)) + ' · se podrán hacer ' + fmt(Math.max(0, Math.floor(resto / gpr(p) + 1e-9))) + ' rollos más'
    : 'Ahora hay ' + fmtG(p.stockG) + ': se pueden hacer ' + rollosDisp(p) + ' rollos';
}
function confirmarProd(id) {
  const p = prod(id), q = num($('#h-cant').value), f = $('#h-fec').value || hoy();
  if (q <= 0) return toast('Escribe cuántos rollos hiciste');
  const g = r2(q * gpr(p));
  if (g > p.stockG + 1e-6) return toast('No alcanza: solo hay para ' + rollosDisp(p) + ' rollos (' + fmtG(p.stockG) + ')');
  p.stockG = r2(p.stockG - g); p.hechos = r2((p.hechos || 0) + q);
  db.produccion.push({ id: uid(), fecha: f, productoId: id, nombre: p.nombre, rollos: q, gramos: g });
  guardar(); cerrarModal(); render(); toast('+' + fmt(q) + ' rollos hechos ✅');
}
function borrarProduccion(id) {
  if (espera()) return;
  const x = db.produccion.find(y => y.id === id); if (!x) return;
  const p = prod(x.productoId);
  if (p && (p.hechos || 0) < x.rollos - 1e-6) return toast('Esos rollos ya se vendieron; no se puede deshacer');
  if (!confirm('¿Deshacer esta producción? Los gramos vuelven al stock.')) return;
  if (p) { p.stockG = r2(p.stockG + x.gramos); p.hechos = r2((p.hechos || 0) - x.rollos); }
  db.produccion = db.produccion.filter(y => y.id !== id);
  guardar(); render();
}

// ===== Vender =====""")

# ===== Vender: ahora descuenta ROLLOS HECHOS =====
bloque(A, "function listaVender() {", "// ===== Pedidos =====",
r"""function listaVender() {
  const l = filtrados();
  if (!l.length) return '<div class="empty">No hay productos con ese filtro</div>';
  return l.map(p => '<div class="item tap" onclick="formVenta(\'' + p.id + '\')"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div><div class="meta"><span class="tag">' + esc(catDe(p)) + '</span> ' + money(p.precio) + ' c/u</div></div><span class="pill ' + (hechosLibres(p) <= 0 ? 'low' : '') + '">' + fmt(hechosLibres(p)) + '<br><small>rollos hechos</small></span></div></div>').join('');
}
function formVenta(id) {
  if (espera()) return;
  const p = prod(id);
  modal('<h3>' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Rollos hechos para vender: ' + fmt(hechosLibres(p)) + (apartadoR(p) > 0 ? ' (' + fmt(apartadoR(p)) + ' apartados en pedidos)' : '') + ' · ' + money(p.precio) + ' c/u</div>' +
    '<label>Rollos</label><div class="step"><button onclick="ajustarQty(-1,\'' + id + '\')">−</button><input id="v-qty" type="number" inputmode="decimal" value="1" oninput="calcVenta(\'' + id + '\')"><button onclick="ajustarQty(1,\'' + id + '\')">+</button></div>' +
    '<div class="total"><b id="v-total"></b><span class="pos" id="v-gan"></span></div>' +
    '<button class="btn main full" onclick="registrarVenta(\'' + id + '\')">Registrar venta</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
  calcVenta(id);
}
const qtyVenta = () => Math.max(0, num($('#v-qty').value));
function ajustarQty(d, id) { $('#v-qty').value = Math.max(1, Math.round((qtyVenta() + d) * 100) / 100); calcVenta(id); }
function calcVenta(id) {
  const p = prod(id), q = qtyVenta();
  $('#v-total').textContent = money(q * p.precio);
  $('#v-gan').className = q * gananciaRollo(p) < 0 ? 'neg' : 'pos';
  $('#v-gan').textContent = gpr(p) > 0 ? 'Ganancia: ' + money(q * gananciaRollo(p)) : 'Falta definir gramos por rollo';
}
function registrarVenta(id) {
  const p = prod(id), q = qtyVenta();
  if (q <= 0) return toast('Escribe la cantidad');
  if (q > hechosLibres(p) + 1e-6) return toast('Solo tienes ' + fmt(hechosLibres(p)) + ' rollos hechos. Registra los rollos hechos en Stock primero');
  const costo = costoRollo(p);
  db.ventas.push({ id: uid(), fecha: hoy(), productoId: p.id, nombre: p.nombre, categoria: catDe(p), rollos: q, gramos: 0, modo: 'hechos', precio: p.precio, costo, total: q * p.precio, ganancia: q * (p.precio - costo) });
  p.hechos = r2((p.hechos || 0) - q);
  guardar(); cerrarModal(); render(); toast('Venta registrada ✅'); if (navigator.vibrate) navigator.vibrate(15);
}
function borrarVenta(id) {
  if (espera()) return;
  const v = db.ventas.find(x => x.id === id);
  if (v && v.pedidoId) return toast('Viene de un pedido: deshaz la entrega en Pedidos');
  if (!v || !confirm('¿Deshacer esta venta? Los rollos vuelven al stock.')) return;
  const p = prod(v.productoId);
  if (p) { if (v.modo === 'hechos') p.hechos = r2((p.hechos || 0) + v.rollos); else p.stockG = r2(p.stockG + (v.gramos != null ? v.gramos : v.rollos * gpr(p))); }
  db.ventas = db.ventas.filter(x => x.id !== id);
  guardar(); render();
}

""")

# ===== Pedidos: apartan rollos hechos =====
parchar(A, "rollosDisp(p).toLocaleString('es-CO') + ' disp.)</option>'", "fmt(hechosLibres(p)) + ' hechos libres)</option>'")
bloque(A, "function agregarItemPed() {", "function quitarItemPed(i)",
r"""function agregarItemPed() {
  const p = prod($('#p-prod').value), q = Math.max(0, num($('#p-qty').value));
  if (!p) return;
  if (q <= 0) return toast('Escribe los rollos');
  const ex = ped.items.find(i => i.productoId === p.id);
  if (ex) ex.rollos = r2(ex.rollos + q);
  else ped.items.push({ productoId: p.id, nombre: p.nombre, rollos: q, gramos: 0, precio: p.precio });
  $('#p-qty').value = 1; pintarItemsPed();
}
""")
bloque(A, "function entregarPedido(id) {", "function cancelarPedido(id) {",
r"""function entregarPedido(id) {
  if (espera()) return;
  const x = db.pedidos.find(y => y.id === id); if (!x || x.estado !== 'pendiente') return;
  const its = itemsDe(x);
  for (const i of its) {
    const p = prod(i.productoId);
    if (!p) return toast(i.nombre + ' ya no existe en el stock');
    if (i.rollos > (p.hechos || 0) + 1e-6) return toast('Faltan rollos hechos de ' + p.nombre + ': tienes ' + fmt(p.hechos || 0) + ' y el pedido pide ' + fmt(i.rollos));
  }
  if (!confirm('¿Entregar el pedido de ' + x.cliente + '? Se registra como venta de hoy.')) return;
  its.forEach(i => {
    const p = prod(i.productoId), costo = costoRollo(p);
    db.ventas.push({ id: uid(), fecha: hoy(), productoId: p.id, nombre: p.nombre, categoria: catDe(p), rollos: i.rollos, gramos: 0, modo: 'hechos', precio: i.precio, costo, total: i.rollos * i.precio, ganancia: i.rollos * (i.precio - costo), pedidoId: x.id });
    p.hechos = r2((p.hechos || 0) - i.rollos);
  });
  x.estado = 'entregado'; x.entregadoEn = hoy();
  guardar(); render(); toast('Entregado y registrado como venta ✅'); if (navigator.vibrate) navigator.vibrate(15);
}
""")
bloque(A, "function deshacerEntrega(id) {", "// ===== Ganancias =====",
r"""function deshacerEntrega(id) {
  if (espera()) return;
  const x = db.pedidos.find(y => y.id === id); if (!x) return;
  if (!confirm('¿Deshacer la entrega? Se borran sus ventas y el pedido vuelve a por entregar.')) return;
  db.ventas.filter(v => v.pedidoId === id).forEach(v => {
    const p = prod(v.productoId); if (!p) return;
    if (v.modo === 'hechos') p.hechos = r2((p.hechos || 0) + v.rollos); else p.stockG = r2(p.stockG + (v.gramos || 0));
  });
  db.ventas = db.ventas.filter(v => v.pedidoId !== id);
  x.estado = 'pendiente'; delete x.entregadoEn;
  guardar(); render();
}

""")

# ===== Ganancias: resumen del mes =====
parchar(A, "    '<h2>Ganancia por producto</h2>' +\n", "    resumenMes(mesSel) +\n    '<h2>Ganancia por producto</h2>' +\n")
parchar(A, "function vGanancias() {",
r"""function resumenMes(ym) {
  const pr = db.produccion.filter(x => x.fecha.slice(0, 7) === ym), en = db.entradas.filter(x => x.fecha.slice(0, 7) === ym);
  const porProd = {}, dias = {}, P = x => (porProd[x.productoId] = porProd[x.productoId] || { n: x.nombre, h: 0, g: 0 });
  pr.forEach(x => { P(x).h += x.rollos; dias[x.fecha] = dias[x.fecha] || {}; dias[x.fecha][x.nombre] = (dias[x.fecha][x.nombre] || 0) + x.rollos; });
  en.forEach(x => { P(x).g += x.gramos; });
  const lista = Object.values(porProd).sort((a, b) => a.n.localeCompare(b.n, 'es'));
  return '<div class="grid"><div class="bubble"><small>Rollos hechos</small><b>' + fmt(suma(pr, 'rollos')) + '</b></div><div class="bubble"><small>Materia ingresada</small><b>' + fmt(suma(en, 'gramos') / 1000) + ' kg</b></div></div>' +
    '<div class="sub" style="margin:0 0 6px">Cada mes empieza de cero; lo que queda en stock pasa al mes siguiente.</div>' +
    '<h2>Producción y materia del mes</h2>' + (lista.length ? lista.map(x => '<div class="item"><div class="row"><div><div class="name">' + esc(x.n) + '</div><div class="meta">Hizo ' + fmt(x.h) + ' rollos · ingresó ' + fmtG(x.g) + '</div></div></div></div>').join('') : '<div class="empty">Sin producción ni ingresos este mes</div>') +
    '<h2>Rollos hechos por día</h2>' + (Object.keys(dias).length ? Object.keys(dias).sort().reverse().map(f => '<div class="item"><div class="row"><div><div class="name cap">' + nombreDia(f) + '</div><div class="meta">' + Object.keys(dias[f]).map(n => fmt(dias[f][n]) + ' × ' + esc(n)).join(' · ') + '</div></div><span class="pill">' + fmt(Object.values(dias[f]).reduce((a, b) => a + b, 0)) + '</span></div></div>').join('') : '<div class="empty">Sin rollos hechos este mes</div>');
}
function vGanancias() {""")

# ===== Ingreso: gramos / libras / kilos =====
parchar(A, "const gUni = () => $('#i-uni').value === 'lb' ? 500 : 1000;",
"const gUni = () => { const u = $('#i-uni').value; return u === 'lb' ? 500 : u === 'g' ? 1 : 1000; };\nconst gCosto = () => $('#i-uni').value === 'lb' ? 500 : 1000;")
parchar(A, '<option value="kg">Kilos (1000 g)</option><option value="lb">Libras (500 g)</option>',
'<option value="kg">Kilos (1 kilo = 1000 g)</option><option value="lb">Libras (1 libra = 500 g)</option><option value="g">Gramos</option>')
bloque(A, "function cambiarUnidad(id) {", "function prevIngreso(id) {",
r"""function cambiarUnidad(id) {
  const p = prod(id), u = $('#i-uni').value, b = gCosto();
  $('#i-lblc').textContent = 'Costo por ' + (b === 500 ? 'libra' : 'kilo') + ' ($)';
  $('#i-costo').value = p.costoKilo ? r2(p.costoKilo * b / 1000) : '';
  $('#i-cant').placeholder = u === 'g' ? 'Ej: 1000' : 'Ej: 1';
  prevIngreso(id);
}
""")
parchar(A, "const g = r2(cant * gUni()), costoKilo = num($('#i-costo').value) * 1000 / gUni();",
"const g = r2(cant * gUni()), costoKilo = num($('#i-costo').value) * 1000 / gCosto();\n  if (g >= 100000 && !confirm('¿Seguro? Vas a ingresar ' + fmt(g) + ' g (' + fmt(g / 1000) + ' kilos).')) return;")

open('CONTEXTO.md', 'a', encoding='utf-8').write("""
## Cambios parche9
- Rollos hechos (producción): en Stock, botón "Rollos hechos" por producto. Se escribe cuántos rollos se hicieron y el día; descuenta gramos del stock (rollos x gramos por rollo) y suma a p.hechos. Se guarda en el nodo "produccion". El stock muestra los gramos que quedan y los rollos que aún se pueden hacer.
- Vender y pedidos ahora descuentan ROLLOS HECHOS (p.hechos), no gramos. Las ventas nuevas llevan modo:'hechos'; las viejas (sin modo) devolvían gramos al deshacer. Los pedidos pendientes apartan rollos hechos; se pueden crear sin rollos hechos, pero entregar exige tenerlos.
- Ganancias (por mes): resumen con rollos hechos, materia ingresada, producción por producto y por día. Cada mes empieza de cero; el stock que queda pasa al mes siguiente.
- Ingreso de materia: unidades Kilos, Libras o Gramos; pregunta si se ingresan 100 kilos o más.
""")
print('OK: parche9 aplicado (rollos hechos, resumen del mes, ingreso en gramos)')
