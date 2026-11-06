import sys, re, time

F = {}
def leer(a):
    if a not in F:
        F[a] = open(a, encoding='utf-8').read()
    return F[a]

def parchar(a, viejo, nuevo):
    s = leer(a); n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces) en ' + a + ':', viejo[:70]); sys.exit(1)
    F[a] = s.replace(viejo, nuevo)

def bloque(a, ini, fin, nuevo):
    s = leer(a); i = s.find(ini)
    if i < 0 or s.count(ini) != 1:
        print('ERROR: no encuentro (o se repite) el inicio:', ini[:60]); sys.exit(1)
    j = s.find(fin, i + 1)
    if j < 0:
        print('ERROR: no encuentro el final:', fin[:60]); sys.exit(1)
    F[a] = s[:i] + nuevo + s[j:]

A = 'js/app.js'

# ===== ayudas: hora, quien, fechas largas, filas de detalle =====
parchar(A, "const fmtG = g => fmt(g) + ' g';\n", r"""const fmtG = g => fmt(g) + ' g';
const ahora = () => { const d = new Date(); return p2(d.getHours()) + ':' + p2(d.getMinutes()); };
const fmtHora = h => { if (!h) return ''; const [H, M] = h.split(':').map(Number); return ((H % 12) || 12) + ':' + p2(M) + (H < 12 ? ' a. m.' : ' p. m.'); };
const quien = () => { try { return NUBE ? usuarioActual() : ''; } catch (e) { return ''; } };
function diaLargo(f) { if (!f) return ''; const [y, m, d] = f.split('-').map(Number); return new Date(y, m - 1, d).toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }); }
const filaD = (k, v, c) => v ? '<div class="dt"><span>' + k + '</span><b' + (c ? ' class="cap"' : '') + '>' + v + '</b></div>' : '';
const btnVolver = (f, v) => (v ? '<button class="btn full" onclick="' + f + '(\'' + v + '\')">← Volver al día</button>' : '') + '<button class="btn full" onclick="cerrarModal()">Cerrar</button>';
""")

# ===== Stock: historiales de rollos hechos e ingresos =====
bloque(A, "function vStock() {", "function listaStock() {", r"""function vStock() {
  const rec = db.produccion.slice().sort((a, b) => a.id < b.id ? 1 : -1).slice(0, 8);
  const ing = db.entradas.slice().sort((a, b) => a.id < b.id ? 1 : -1).slice(0, 8);
  const hint = '<div class="hint" style="margin:0 0 10px">Toca uno para ver el detalle completo</div>';
  return '<h2>Inventario</h2><button class="add" onclick="formProducto()">＋ Nuevo producto</button>' +
    (db.productos.length ? barraFiltro() + '<div id="lista">' + listaStock() + '</div>' : '<div class="empty">Aún no hay productos</div>') +
    (rec.length ? '<h2 style="margin-top:22px">Últimos rollos hechos</h2>' + hint + rec.map(x => lineaProd(x)).join('') : '') +
    (ing.length ? '<h2 style="margin-top:22px">Últimos ingresos de materia</h2>' + hint + ing.map(x => lineaIngreso(x)).join('') : '');
}
""")

# ===== Ingreso de materia: guarda hora y quien =====
parchar(A, "cantidad: cant, unidad: $('#i-uni').value, gramos: g, costoKilo: p.costoKilo });",
"hora: ahora(), por: quien(), cantidad: cant, unidad: $('#i-uni').value, gramos: g, costoKilo: p.costoKilo, gramosRollo: gp, stockDespuesG: p.stockG });")

# ===== Rollos hechos: se puede pasar del stock (avisa que salieron de más) =====
parchar(A, "suma rollos listos para vender</div>'", "suma rollos listos para vender. Si salen más rollos de los que daba el stock, igual los puedes registrar.</div>'")
bloque(A, "function prevProd(id) {", "// ===== Vender =====", r"""function prevProd(id) {
  const p = prod(id), q = num($('#h-cant').value), resto = p.stockG - q * gpr(p), el = $('#h-prev');
  if (q > 0 && resto < -1e-6) {
    el.classList.add('warn');
    el.innerHTML = '⚠️ Salieron más de lo calculado<small>Con el stock alcanzaba para ' + rollosDisp(p) + ' rollos y estás registrando ' + fmt(q) + ' (' + fmt(r2(q - rollosDisp(p))) + ' de más, ≈ ' + fmtG(-resto) + ' que no estaban en el stock). El stock queda en 0 g.</small>';
    return;
  }
  el.classList.remove('warn');
  el.textContent = q > 0
    ? 'Se descuentan ' + fmtG(q * gpr(p)) + ' · quedan ' + fmtG(Math.max(0, resto)) + ' · se podrán hacer ' + fmt(Math.max(0, Math.floor(resto / gpr(p) + 1e-9))) + ' rollos más'
    : 'Ahora hay ' + fmtG(p.stockG) + ': se pueden hacer ' + rollosDisp(p) + ' rollos';
}
function confirmarProd(id) {
  const p = prod(id), q = num($('#h-cant').value), f = $('#h-fec').value || hoy();
  if (q <= 0) return toast('Escribe cuántos rollos hiciste');
  const g = r2(q * gpr(p)), alc = rollosDisp(p), exc = g > p.stockG + 1e-6 ? r2(g - p.stockG) : 0, excR = exc > 0 ? r2(q - alc) : 0;
  p.stockG = exc > 0 ? 0 : r2(p.stockG - g); p.hechos = r2((p.hechos || 0) + q);
  db.produccion.push({ id: uid(), fecha: f, reg: hoy(), hora: ahora(), por: quien(), productoId: id, nombre: p.nombre, rollos: q, gramos: g, gramosRollo: gpr(p), excesoG: exc, excesoR: excR, alcanzaba: alc, quedaronG: p.stockG });
  guardar(); cerrarModal(); render();
  toast(exc > 0 ? '+' + fmt(q) + ' rollos · ⚠️ salieron ' + fmt(excR) + ' más de lo calculado' : '+' + fmt(q) + ' rollos hechos ✅');
}
function borrarProduccion(id) {
  if (espera()) return;
  const x = db.produccion.find(y => y.id === id); if (!x) return;
  const p = prod(x.productoId);
  if (p && (p.hechos || 0) < x.rollos - 1e-6) return toast('Esos rollos ya se vendieron; no se puede deshacer');
  if (!confirm('¿Deshacer esta producción? Los gramos vuelven al stock.')) return;
  if (p) { p.stockG = r2(p.stockG + x.gramos - (x.excesoG || 0)); p.hechos = r2((p.hechos || 0) - x.rollos); }
  db.produccion = db.produccion.filter(y => y.id !== id);
  guardar(); render();
}
function lineaProd(x, vol) {
  const a = vol ? ",'" + vol + "'" : '', exc = x.excesoG > 0;
  return '<div class="item tap" onclick="detalleProd(\'' + x.id + '\'' + a + ')"><div class="row"><div><div class="name">' + esc(x.nombre) + (exc ? ' <span class="tag warn">Salieron de más</span>' : '') + '</div><div class="meta">' + fmt(x.rollos) + ' rollos · ' + nombreDia(x.fecha) + (x.hora ? ' · 🕒 ' + fmtHora(x.hora) : '') + (exc ? '<br>⚠️ Salieron ' + fmt(x.excesoR || 0) + ' rollos más de lo calculado' : '') + '</div></div>' + (vol ? '' : '<button class="btn del" onclick="event.stopPropagation();borrarProduccion(\'' + x.id + '\')">Deshacer</button>') + '</div></div>';
}
function lineaIngreso(x) {
  const u = { kg: 'kilos', lb: 'libras', g: 'gramos' }[x.unidad] || '';
  return '<div class="item tap" onclick="detalleIngreso(\'' + x.id + '\')"><div class="row"><div><div class="name">' + esc(x.nombre) + '</div><div class="meta">+' + fmt(x.cantidad) + ' ' + u + ' · ' + nombreDia(x.fecha) + (x.hora ? ' · 🕒 ' + fmtHora(x.hora) : '') + '<br>' + fmtG(x.gramos) + ' al stock</div></div></div></div>';
}
function detalleProd(id, vol) {
  const x = db.produccion.find(y => y.id === id); if (!x) return;
  const p = prod(x.productoId), exc = x.excesoG || 0, und = p && p.unidadesRollo ? r2(x.rollos * p.unidadesRollo) : null;
  const gr = x.gramosRollo || (x.rollos ? r2(x.gramos / x.rollos) : 0);
  modal('<h3>' + esc(x.nombre) + '</h3><div class="sub" style="margin:2px 0 4px">🧆 Rollos hechos' + (exc > 0 ? ' · ⚠️ salieron más de lo calculado' : '') + '</div>' +
    '<div class="dsec">Producción</div>' +
    filaD('Rollos hechos', fmt(x.rollos)) + filaD('Unidades', und != null ? fmt(und) : '') +
    filaD('Día en que se hicieron', diaLargo(x.fecha), 1) +
    filaD('Registrado el', x.reg ? diaLargo(x.reg) : '', 1) +
    filaD('Hora del registro', x.hora ? fmtHora(x.hora) : 'No se registró (registro antiguo)') +
    filaD('Registrado por', x.por ? esc(x.por) : '') +
    '<div class="dsec">Materia</div>' +
    filaD('Gramos por rollo', gr ? fmtG(gr) : '') + filaD('Materia usada', fmtG(x.gramos)) +
    (x.quedaronG != null ? filaD('Quedó en el stock', fmtG(x.quedaronG)) : '') +
    (exc > 0 ? '<div class="dsec warn">⚠️ Salieron más de lo calculado</div>' + filaD('El stock alcanzaba para', fmt(x.alcanzaba || 0) + ' rollos') + filaD('Salieron de más', fmt(x.excesoR || 0) + ' rollos') + filaD('Materia que no estaba en el stock', fmtG(exc)) : '') +
    btnVolver('detalleDiaProd', vol));
}
function detalleIngreso(id) {
  const x = db.entradas.find(y => y.id === id); if (!x) return;
  const u = { kg: 'kilos', lb: 'libras', g: 'gramos' }[x.unidad] || '', p = prod(x.productoId);
  const costo = x.costoKilo ? x.gramos / 1000 * x.costoKilo : 0, gr = x.gramosRollo || (p ? gpr(p) : 0);
  modal('<h3>' + esc(x.nombre) + '</h3><div class="sub" style="margin:2px 0 4px">📦 Ingreso de materia</div>' +
    '<div class="dsec">Ingreso</div>' +
    filaD('Llegó', fmt(x.cantidad) + ' ' + u) + filaD('Equivale a', fmtG(x.gramos) + ' (' + fmt(x.gramos / 1000) + ' kg)') +
    filaD('Día', diaLargo(x.fecha), 1) + filaD('Hora', x.hora ? fmtHora(x.hora) : 'No se registró (ingreso antiguo)') +
    filaD('Registrado por', x.por ? esc(x.por) : '') +
    '<div class="dsec">Cuentas</div>' +
    filaD('Costo por kilo', x.costoKilo ? money(x.costoKilo) : '') + filaD('Costo de este ingreso', costo ? money(costo) : '') +
    (gr > 0 ? filaD('Rollos que salen (≈)', fmt(Math.floor(x.gramos / gr + 1e-9))) : '') +
    (x.stockDespuesG != null ? filaD('Stock después del ingreso', fmtG(x.stockDespuesG)) : '') +
    btnVolver('', ''));
}

""")

# ===== Vender: cliente opcional, hora e historial detallado =====
bloque(A, "function vVender() {", "function listaVender() {", r"""function vVender() {
  if (!db.productos.length) return '<div class="empty">Primero crea un producto en 📦 Stock</div>';
  const hoyV = ventasDia(hoy());
  return '<h2>¿Qué vendiste?</h2>' + barraFiltro() + '<div id="lista">' + listaVender() + '</div>' +
    '<h2 style="margin-top:22px">Ventas de hoy</h2>' +
    (hoyV.length ? '<div class="hint" style="margin:0 0 10px">Toca una venta para ver el detalle completo</div>' + hoyV.slice().reverse().map(v => lineaVenta(v)).join('') : '<div class="empty">Sin ventas hoy</div>');
}
function lineaVenta(v, vol) {
  const a = vol ? ",'" + vol + "'" : '';
  const q2 = (v.cliente ? '👤 ' + esc(v.cliente) : '') + (v.cliente && v.hora ? ' · ' : '') + (v.hora ? '🕒 ' + fmtHora(v.hora) : '');
  return '<div class="item tap" onclick="detalleVenta(\'' + v.id + '\'' + a + ')"><div class="row"><div><div class="name">' + esc(v.nombre) + (v.pedidoId ? ' <span class="tag">Pedido</span>' : '') + '</div><div class="meta">' + fmt(v.rollos) + ' rollos · ' + money(v.total) + ' · ' + (v.ganancia < 0 ? 'pierde ' : 'gana ') + money(Math.abs(v.ganancia)) + (q2 ? '<br>' + q2 : '') + '</div></div>' + (v.pedidoId || vol ? '' : '<button class="btn del" onclick="event.stopPropagation();borrarVenta(\'' + v.id + '\')">Deshacer</button>') + '</div></div>';
}
""")
parchar(A, """    '<div class="total"><b id="v-total"></b>""", """    '<label>Cliente (opcional)</label><input id="v-cli" placeholder="¿A quién se lo vendes?">' +
    '<div class="total"><b id="v-total"></b>""")
bloque(A, "  db.ventas.push({ id: uid(), fecha: hoy(), productoId: p.id, nombre: p.nombre, categoria: catDe(p), rollos: q,", "  guardar(); cerrarModal(); render(); toast('Venta registrada", r"""  const cli = ($('#v-cli').value || '').trim();
  p.hechos = r2((p.hechos || 0) - q);
  db.ventas.push({ id: uid(), fecha: hoy(), hora: ahora(), por: quien(), cliente: cli, productoId: p.id, nombre: p.nombre, categoria: catDe(p), rollos: q, unidades: r2(q * (p.unidadesRollo || 0)), gramos: 0, modo: 'hechos', precio: p.precio, costo, total: q * p.precio, ganancia: q * (p.precio - costo), quedaron: p.hechos });
""")

# ===== Pedidos: hora de pedido y de entrega =====
bloque(A, "function cardPedido(x) {", "function formPedido() {", r"""function cardPedido(x) {
  const its = itemsDe(x), total = its.reduce((a, i) => a + i.rollos * i.precio, 0), pen = x.estado === 'pendiente';
  const hecho = 'Pedido hecho: ' + (x.fecha ? nombreDia(x.fecha) : '—') + (x.hora ? ' · ' + fmtHora(x.hora) : '');
  return '<div class="item"><div class="row"><div class="tap" onclick="detallePedido(\'' + x.id + '\')"><div class="name">' + esc(x.cliente || 'Sin nombre') + '</div><div class="meta">' +
    (pen ? (x.entrega ? 'Entrega: ' + nombreDia(x.entrega) : 'Sin fecha de entrega') : '✅ Entregado: ' + nombreDia(x.entregadoEn) + (x.entregadoHora ? ' · 🕒 ' + fmtHora(x.entregadoHora) : '')) + '<br>' + hecho + '<br>' +
    its.map(i => fmt(i.rollos) + ' × ' + esc(i.nombre)).join(' · ') + (x.nota ? '<br>📝 ' + esc(x.nota) : '') + '</div></div>' +
    '<span class="pill">' + money(total) + '</span></div>' +
    '<div class="actions"><button class="btn" onclick="detallePedido(\'' + x.id + '\')">Ver detalle</button>' + (pen
      ? '<button class="btn main" onclick="entregarPedido(\'' + x.id + '\')">✅ Entregar</button><button class="btn del" onclick="cancelarPedido(\'' + x.id + '\')">Cancelar pedido</button>'
      : '<button class="btn" onclick="deshacerEntrega(\'' + x.id + '\')">Deshacer entrega</button>') + '</div></div>';
}
""")
parchar(A, "db.pedidos.push({ id: uid(), fecha: hoy(), cliente,", "db.pedidos.push({ id: uid(), fecha: hoy(), hora: ahora(), por: quien(), cliente,")
bloque(A, "  if (!confirm('¿Entregar el pedido de '", "  guardar(); render(); toast('Entregado", r"""  if (!confirm('¿Entregar el pedido de ' + x.cliente + '? Se registra como venta de hoy.')) return;
  const hr = ahora(), por = quien();
  its.forEach(i => {
    const p = prod(i.productoId), costo = costoRollo(p);
    p.hechos = r2((p.hechos || 0) - i.rollos);
    db.ventas.push({ id: uid(), fecha: hoy(), hora: hr, por, cliente: x.cliente || '', productoId: p.id, nombre: p.nombre, categoria: catDe(p), rollos: i.rollos, unidades: r2(i.rollos * (p.unidadesRollo || 0)), gramos: 0, modo: 'hechos', precio: i.precio, costo, total: i.rollos * i.precio, ganancia: i.rollos * (i.precio - costo), quedaron: p.hechos, pedidoId: x.id });
  });
  x.estado = 'entregado'; x.entregadoEn = hoy(); x.entregadoHora = hr; x.entregadoPor = por;
""")
parchar(A, "x.estado = 'pendiente'; delete x.entregadoEn;", "x.estado = 'pendiente'; delete x.entregadoEn; delete x.entregadoHora; delete x.entregadoPor;")

# ===== Detalle de venta, de un día y de un pedido =====
parchar(A, "// ===== Ganancias =====\n", r"""function detalleVenta(id, vol) {
  const v = db.ventas.find(x => x.id === id); if (!v) return;
  const x = v.pedidoId ? db.pedidos.find(y => y.id === v.pedidoId) : null, p = prod(v.productoId);
  const cli = v.cliente || (x && x.cliente) || '';
  const und = v.unidades != null ? v.unidades : (p && p.unidadesRollo ? r2(v.rollos * p.unidadesRollo) : null);
  const gr = v.rollos ? v.ganancia / v.rollos : 0;
  modal('<h3>' + esc(v.nombre) + '</h3><div class="sub" style="margin:2px 0 4px">' + (x ? '📋 Venta por pedido' : '🛒 Venta directa') + '</div>' +
    '<div class="dsec">Cliente y entrega</div>' +
    filaD('Se la vendimos a', cli ? esc(cli) : 'No se anotó el cliente') +
    filaD(x ? 'Entregado el' : 'Vendido el', diaLargo(v.fecha), 1) +
    filaD(x ? 'Hora de la entrega' : 'Hora de la venta', v.hora ? fmtHora(v.hora) : 'No se registró (venta antigua)') +
    filaD('Registrado por', v.por ? esc(v.por) : '') +
    (x ? filaD('Pedido hecho el', diaLargo(x.fecha), 1) + filaD('Hora del pedido', fmtHora(x.hora)) + filaD('Entrega prometida', x.entrega ? diaLargo(x.entrega) : 'Sin fecha', 1) : '') +
    '<div class="dsec">Producto</div>' +
    filaD('Categoría', v.categoria ? esc(v.categoria) : '') + filaD('Rollos', fmt(v.rollos)) + filaD('Unidades', und != null ? fmt(und) : '') +
    filaD('Precio por rollo', money(v.precio)) + filaD('Total vendido', money(v.total)) +
    '<div class="dsec">Cuentas</div>' +
    filaD('Costo por rollo', money(v.costo)) + filaD('Ganancia por rollo', money(gr)) + filaD(gLbl(v.ganancia) + ' total', money(v.ganancia)) +
    (v.costo > 0 ? filaD('% sobre el costo', fmt(gr / v.costo * 100) + ' %') : '') +
    (v.quedaron != null ? filaD('Rollos hechos que quedaron', fmt(v.quedaron)) : '') +
    (x && x.nota ? '<div class="dsec">Nota del pedido</div><div class="sub" style="margin:4px 0">' + esc(x.nota) + '</div>' : '') +
    btnVolver('detalleDia', vol));
}
function detalleDia(f) {
  const vs = ventasDia(f).slice().reverse(), g = suma(vs, 'ganancia');
  modal('<h3 class="cap">' + diaLargo(f) + '</h3><div class="sub" style="margin:2px 0 10px">' + vs.length + (vs.length === 1 ? ' venta' : ' ventas') + ' · ' + fmt(suma(vs, 'rollos')) + ' rollos · ' + money(suma(vs, 'total')) + ' vendido · ' + gLbl(g).toLowerCase() + ' ' + money(Math.abs(g)) + '</div>' +
    (vs.length ? '<div class="hint" style="margin:0 0 10px">Toca una venta para ver el detalle</div>' + vs.map(v => lineaVenta(v, f)).join('') : '<div class="empty">Sin ventas ese día</div>') +
    '<button class="btn full" onclick="cerrarModal()">Cerrar</button>');
}
function detalleDiaProd(f) {
  const l = db.produccion.filter(x => x.fecha === f).slice().reverse();
  modal('<h3 class="cap">' + diaLargo(f) + '</h3><div class="sub" style="margin:2px 0 10px">' + fmt(suma(l, 'rollos')) + ' rollos hechos · ' + l.length + (l.length === 1 ? ' registro' : ' registros') + '</div>' +
    (l.length ? '<div class="hint" style="margin:0 0 10px">Toca uno para ver el detalle</div>' + l.map(x => lineaProd(x, f)).join('') : '<div class="empty">Sin rollos hechos ese día</div>') +
    '<button class="btn full" onclick="cerrarModal()">Cerrar</button>');
}
function detallePedido(id) {
  const x = db.pedidos.find(y => y.id === id); if (!x) return;
  const its = itemsDe(x), total = its.reduce((a, i) => a + i.rollos * i.precio, 0), ent = x.estado === 'entregado';
  const vs = db.ventas.filter(v => v.pedidoId === id), dias = f => { const a = f.split('-').map(Number); return Math.round(Date.UTC(a[0], a[1] - 1, a[2]) / 864e5); };
  let punt = '';
  if (ent && x.entrega && x.entregadoEn) { const d = dias(x.entregadoEn) - dias(x.entrega); punt = d === 0 ? 'A tiempo (el día prometido)' : d < 0 ? 'Adelantado ' + (-d) + (d === -1 ? ' día' : ' días') : 'Tarde ' + d + (d === 1 ? ' día' : ' días'); }
  modal('<h3>' + esc(x.cliente || 'Sin nombre') + '</h3><div class="sub" style="margin:2px 0 4px">' + (ent ? '✅ Pedido entregado' : '⏳ Pedido por entregar') + '</div>' +
    '<div class="dsec">Pedido</div>' +
    filaD('Pedido hecho el', diaLargo(x.fecha), 1) + filaD('Hora del pedido', x.hora ? fmtHora(x.hora) : 'No se registró (pedido antiguo)') +
    filaD('Anotado por', x.por ? esc(x.por) : '') + filaD('Entrega prometida', x.entrega ? diaLargo(x.entrega) : 'Sin fecha', 1) +
    (ent ? '<div class="dsec">Entrega</div>' + filaD('Entregado el', diaLargo(x.entregadoEn), 1) + filaD('Hora de la entrega', x.entregadoHora ? fmtHora(x.entregadoHora) : 'No se registró (entrega antigua)') + filaD('Entregado por', x.entregadoPor ? esc(x.entregadoPor) : '') + filaD('Puntualidad', punt) : '') +
    '<div class="dsec">Productos</div>' + its.map(i => filaD(fmt(i.rollos) + ' × ' + esc(i.nombre), money(i.rollos * i.precio))).join('') +
    filaD('Total del pedido', money(total)) + (ent && vs.length ? filaD(gLbl(suma(vs, 'ganancia')) + ' del pedido', money(suma(vs, 'ganancia'))) : '') +
    (x.nota ? '<div class="dsec">Nota</div><div class="sub" style="margin:4px 0">' + esc(x.nota) + '</div>' : '') +
    '<button class="btn full" onclick="cerrarModal()">Cerrar</button>');
}

// ===== Ganancias =====
""")

# ===== Ganancias: días tocables =====
parchar(A, """'<div class="item"><div class="row"><div><div class="name cap">' + nombreDia(f) + '</div><div class="meta">' + fmt(dias[f].r)""",
"""'<div class="item tap" onclick="detalleDia(\\'' + f + '\\')"><div class="row"><div><div class="name cap">' + nombreDia(f) + '</div><div class="meta">' + fmt(dias[f].r)""")
parchar(A, """'<div class="item"><div class="row"><div><div class="name cap">' + nombreDia(f) + '</div><div class="meta">' + Object.keys(dias[f])""",
"""'<div class="item tap" onclick="detalleDiaProd(\\'' + f + '\\')"><div class="row"><div><div class="name cap">' + nombreDia(f) + '</div><div class="meta">' + Object.keys(dias[f])""")
parchar(A, "Día por día</h2>' +", """Día por día</h2><div class="hint" style="margin:0 0 10px">Toca un día para ver cada venta, a quién y a qué hora</div>' +""")
parchar(A, "'<h2>Rollos hechos por día</h2>' + (", """'<h2>Rollos hechos por día</h2><div class="hint" style="margin:0 0 10px">Toca un día para ver el detalle</div>' + (""")

# ===== Estilos =====
C = 'css/styles.css'
leer(C)
F[C] += r"""
.dsec{margin:18px 0 2px;font:800 .72rem var(--f-d);color:var(--mut);text-transform:uppercase;letter-spacing:.08em}
.dsec.warn{color:var(--bad)}
.dt{display:flex;justify-content:space-between;align-items:baseline;gap:16px;padding:9px 0;border-bottom:1px solid var(--line);font-size:.88rem}
.dt span{color:var(--mut);flex:0 0 auto}
.dt b{text-align:right;font-weight:700;min-width:0;overflow-wrap:anywhere}
.tag.warn{background:var(--badbg);color:var(--bad)}
.preview.warn{background:var(--badbg);color:var(--bad)}
.preview small{display:block;font:600 .8rem system-ui,sans-serif;margin-top:6px;line-height:1.45}
"""

# ===== Versión (para que el teléfono cargue lo nuevo) =====
I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

# ===== CONTEXTO.md =====
X = 'CONTEXTO.md'
parchar(X, "- [x] Stock en gramos: ingreso en kilos/libras, gramos por rollo, la venta descuenta gramos\n",
"""- [x] Stock en gramos: ingreso en kilos/libras, gramos por rollo, la venta descuenta gramos
- [x] Historiales detallados (ventas, pedidos, rollos hechos, ingresos de materia): al tocar uno se ve cliente, fecha, hora, quién lo registró y más
- [x] Rollos hechos puede pasarse del stock: se registra y avisa que salieron más de lo calculado
""")
F[X] += """
## Cambios parche10
- Historiales detallados. Ventas, pedidos, rollos hechos e ingresos de materia guardan ahora hora (hora), quién lo registró (por: usuario de la nube, vacío en modo local) y datos extra. Los registros viejos no tienen hora: el detalle dice "No se registró".
- Tocar un registro abre su detalle (funciones detalleVenta, detallePedido, detalleProd, detalleIngreso). En Ganancias, tocar un día (Día por día o Rollos hechos por día) lista las ventas o la producción de ese día, y desde ahí se abre cada detalle con "Volver al día".
- Venta: campo opcional Cliente en Vender (v.cliente). Venta por pedido guarda cliente, hora de entrega, unidades y rollos hechos que quedaron; el detalle también muestra cuándo se hizo el pedido, la entrega prometida y la nota.
- Pedido: guarda hora (cuándo se anotó) y por; al entregar guarda entregadoHora y entregadoPor. El detalle muestra puntualidad (a tiempo, adelantado o tarde) y la ganancia del pedido.
- Stock: nueva lista "Últimos ingresos de materia" (sin deshacer).
- Rollos hechos: se pueden registrar más rollos de los que da el stock. El stock queda en 0 g y se guarda excesoG (gramos que faltaban), excesoR (rollos de más) y alcanzaba (rollos que alcanzaban). Sale aviso rojo "Salieron más de lo calculado" al escribir, en el aviso al registrar, en la lista y en el detalle. Deshacer devuelve solo los gramos que sí habían salido del stock (gramos - excesoG).
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche10 aplicado (historiales detallados + rollos hechos que pasan del stock)')
