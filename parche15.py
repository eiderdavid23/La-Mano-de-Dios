import sys, re, time

F = {}
def leer(a):
    if a not in F:
        F[a] = open(a, encoding='utf-8').read()
    return F[a]

def parchar(a, viejo, nuevo):
    s = leer(a); n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces) en ' + a + ':', viejo[:80]); sys.exit(1)
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

# ===== ayudas para filas, días y registro de cambios =====
parchar(A, "// ===== Cálculos =====\n", r"""// ===== Filas de historial =====
const mayus = s => s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
function restaDias(f, n) { const [y, m, d] = f.split('-').map(Number), t = new Date(y, m - 1, d - n); return t.getFullYear() + '-' + p2(t.getMonth() + 1) + '-' + p2(t.getDate()); }
function etiquetaDia(f) { if (!f) return 'Sin fecha'; if (f === hoy()) return 'Hoy'; if (f === restaDias(hoy(), 1)) return 'Ayer'; return mayus(nombreDia(f)); }
const hfila = o => '<div class="hrow" onclick="' + o.on + '">' + (o.ic ? '<span class="hic t-' + o.k + '">' + o.ic + '</span>' : '') + '<div class="hm"><div class="ht">' + o.t + '</div><div class="hs">' + o.s + '</div></div>' + (o.r ? '<div class="hv ' + (o.rc || '') + '"><b>' + o.r + '</b>' + (o.rs ? '<small>' + o.rs + '</small>' : '') + '</div>' : '') + '</div>';
function agrupaDia(arr, ff, fn) {
  const g = [];
  arr.forEach(x => { const f = ff(x) || ''; let d = g[g.length - 1]; if (!d || d.f !== f) g.push(d = { f, l: [] }); d.l.push(x); });
  return g.map(d => '<div class="hday"><span>' + etiquetaDia(d.f) + '</span><small>' + d.l.length + (d.l.length === 1 ? ' movimiento' : ' movimientos') + '</small></div><div class="hcard">' + d.l.map(fn).join('') + '</div>').join('');
}
const dsp = (f, id) => 'cerrarModal();setTimeout(function(){' + f + '(\'' + id + '\')},300)';
const LBL = { producto_nuevo: 'Producto nuevo', producto_editado: 'Producto editado', producto_borrado: 'Producto borrado', venta_deshecha: 'Venta deshecha', pedido_cancelado: 'Pedido cancelado', entrega_deshecha: 'Entrega deshecha', rollos_deshechos: 'Rollos hechos deshechos' };
function anotar(tipo, texto, cambios) { db.registro.push(Object.assign({ id: uid(), fecha: hoy(), hora: ahora(), por: quien(), tipo, texto }, cambios && cambios.length ? { cambios } : {})); }

// ===== Cálculos =====
""")

# ===== iconos nuevos =====
parchar(A, """  check: ic('<path d="m5 12.5 4.5 4.5L19 7.5"/>')\n};""", r"""  check: ic('<path d="m5 12.5 4.5 4.5L19 7.5"/>'),
  deshacer: ic('<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>'),
  historial: ic('<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/>'),
  venta: TABS[2][1]
};""")

# ===== datos: registro de cambios (se guarda aparte para no frenar ventas ni stock) =====
parchar(A, "const remoto = { productos: {}, entradas: {}, ventas: {}, pedidos: {}, produccion: {} };", "const remoto = { productos: {}, entradas: {}, ventas: {}, pedidos: {}, produccion: {}, registro: {} };")
parchar(A, "return { productos: [], entradas: [], ventas: [], pedidos: [], produccion: [] };", "return { productos: [], entradas: [], ventas: [], pedidos: [], produccion: [], registro: [] };")
parchar(A, "  d.produccion = d.produccion || [];\n", "  d.produccion = d.produccion || [];\n  d.registro = d.registro || [];\n")
parchar(A, "  if (Object.keys(upd).length) fbRef.update(upd).catch(e => toast('No se pudo guardar: ' + e.message));\n", r"""  if (Object.keys(upd).length) fbRef.update(upd).catch(e => toast('No se pudo guardar: ' + e.message));
  const upR = {};
  (db.registro || []).forEach(x => { if (!remoto.registro[x.id]) upR['registro/' + x.id] = JSON.parse(JSON.stringify(x)); });
  if (Object.keys(upR).length) fbRef.update(upR).catch(() => {});
""")
parchar(A, "    COLS.forEach(c => { remoto[c] = v[c] || {}; });\n", "    COLS.forEach(c => { remoto[c] = v[c] || {}; });\n    remoto.registro = v.registro || {};\n")
parchar(A, "      produccion: Object.values(remoto.produccion).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1)\n    });", "      produccion: Object.values(remoto.produccion).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1),\n      registro: Object.values(remoto.registro).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1)\n    });")
parchar(A, "produccion: d.produccion || [] });", "produccion: d.produccion || [], registro: d.registro || [] });")

# ===== anotar los cambios (editar, borrar, deshacer, cancelar) =====
parchar(A, """  if (id) Object.assign(prod(id), d);
  else db.productos.push(Object.assign({ id: uid(), stockG: num($('#f-stock').value) }, d));
""", r"""  if (id) {
    const o = Object.assign({}, prod(id)), CP = [['nombre', 'Nombre', x => x], ['categoria', 'Categoría', x => x || 'Sin categoría'], ['unidadesRollo', 'Unidades por rollo', fmt], ['gramosPorRollo', 'Gramos por rollo', fmtG], ['precio', 'Precio de venta', money], ['costoKilo', 'Costo por kilo', money], ['minimoG', 'Mínimo en bodega', fmtG], ['stockG', 'Gramos en bodega', fmtG]];
    const cb = CP.filter(c => (o[c[0]] || 0) !== (d[c[0]] || 0)).map(c => c[1] + ': ' + c[2](o[c[0]] || 0) + ' → ' + c[2](d[c[0]] || 0));
    Object.assign(prod(id), d);
    if (cb.length) anotar('producto_editado', 'Editó el producto ' + nombre, cb);
  } else {
    db.productos.push(Object.assign({ id: uid(), stockG: num($('#f-stock').value) }, d));
    anotar('producto_nuevo', 'Creó el producto ' + nombre);
  }
""")
parchar(A, "  db.productos = db.productos.filter(p => p.id !== id);\n", "  anotar('producto_borrado', 'Borró el producto ' + (pp ? pp.nombre : ''));\n  db.productos = db.productos.filter(p => p.id !== id);\n")
parchar(A, "  db.ventas = db.ventas.filter(x => x.id !== id);\n", "  anotar('venta_deshecha', 'Deshizo la venta de ' + fmt(v.rollos) + ' rollos de ' + v.nombre + ' (' + money(v.total) + ')' + (v.cliente ? ' a ' + v.cliente : ''));\n  db.ventas = db.ventas.filter(x => x.id !== id);\n")
parchar(A, "  db.pedidos = db.pedidos.filter(x => x.id !== id);\n", r"""  const pc = db.pedidos.find(x => x.id === id);
  if (pc) anotar('pedido_cancelado', 'Canceló el pedido de ' + (pc.cliente || 'Sin nombre') + ' (' + money(itemsDe(pc).reduce((a, i) => a + i.rollos * i.precio, 0)) + ')');
  db.pedidos = db.pedidos.filter(x => x.id !== id);
""")
parchar(A, "  x.estado = 'pendiente'; delete x.entregadoEn; delete x.entregadoHora; delete x.entregadoPor;\n", "  x.estado = 'pendiente'; delete x.entregadoEn; delete x.entregadoHora; delete x.entregadoPor;\n  anotar('entrega_deshecha', 'Deshizo la entrega del pedido de ' + (x.cliente || 'Sin nombre'));\n")
parchar(A, "  db.produccion = db.produccion.filter(y => y.id !== id);\n", "  anotar('rollos_deshechos', 'Deshizo ' + fmt(x.rollos) + ' rollos hechos de ' + x.nombre);\n  db.produccion = db.produccion.filter(y => y.id !== id);\n")

# ===== Vender: ventas de hoy en una sola tarjeta =====
bloque(A, "function vVender() {", "function listaVender() {", r"""function vVender() {
  if (!db.productos.length) return '<div class="empty">Primero crea un producto en Stock</div>';
  const hoyV = ventasDia(hoy());
  return '<h2>¿Qué vendiste?</h2>' + barraFiltro() + '<div id="lista">' + listaVender() + '</div>' +
    '<h2 style="margin-top:22px">Ventas de hoy</h2>' +
    (hoyV.length ? '<div class="hint" style="margin:0 0 10px">Toca una venta para ver el detalle o deshacerla</div><div class="hcard">' + hoyV.slice().reverse().map(v => lineaVenta(v)).join('') + '</div>' : '<div class="empty">Sin ventas hoy</div>');
}
function lineaVenta(v, vol) {
  return hfila({ t: esc(v.nombre) + (v.pedidoId ? ' <span class="tag">Pedido</span>' : ''), s: fmt(v.rollos) + ' rollos' + (v.cliente ? ' · ' + esc(v.cliente) : '') + (v.hora ? ' · ' + fmtHora(v.hora) : ''), r: money(v.total), on: "detalleVenta('" + v.id + "'" + (vol ? ",'" + vol + "'" : '') + ")" });
}
""")

# ===== Stock: rollos hechos e ingresos agrupados por día =====
bloque(A, "function lineaProd(x, vol) {", "function detalleProd(id, vol) {", r"""function lineaProd(x, vol) {
  return hfila({ t: esc(x.nombre) + (x.excesoG > 0 ? ' <span class="tag warn">Salieron de más</span>' : ''), s: 'Rollos hechos' + (x.hora ? ' · ' + fmtHora(x.hora) : ''), r: '+' + fmt(x.rollos), rs: 'rollos', on: "detalleProd('" + x.id + "'" + (vol ? ",'" + vol + "'" : '') + ")" });
}
function lineaIngreso(x) {
  return hfila({ t: esc(x.nombre), s: 'Ingreso de materia' + (x.hora ? ' · ' + fmtHora(x.hora) : ''), r: '+' + fmt(x.cantidad) + ' ' + (x.unidad || 'kg'), on: "detalleIngreso('" + x.id + "')" });
}
""")
parchar(A, "const rec = db.produccion.slice().sort((a, b) => a.id < b.id ? 1 : -1).slice(0, 8);", "const rec = db.produccion.slice().sort((a, b) => a.fecha < b.fecha ? 1 : a.fecha > b.fecha ? -1 : (a.id < b.id ? 1 : -1)).slice(0, 8);")
parchar(A, "const ing = db.entradas.slice().sort((a, b) => a.id < b.id ? 1 : -1).slice(0, 8);", "const ing = db.entradas.slice().sort((a, b) => a.fecha < b.fecha ? 1 : a.fecha > b.fecha ? -1 : (a.id < b.id ? 1 : -1)).slice(0, 8);")
parchar(A, "hint + rec.map(x => lineaProd(x)).join('')", "hint + agrupaDia(rec, x => x.fecha, x => lineaProd(x))")
parchar(A, "hint + ing.map(x => lineaIngreso(x)).join('')", "hint + agrupaDia(ing, x => x.fecha, x => lineaIngreso(x))")

# ===== Pedidos: entregados en filas por día =====
bloque(A, "function vPedidos() {", "function cardPedido(x) {", r"""function vPedidos() {
  const pend = pendPed().length, ent = db.pedidos.length - pend, K = x => x.entrega || '9999';
  const tot = x => itemsDe(x).reduce((a, i) => a + i.rollos * i.precio, 0), nro = x => itemsDe(x).reduce((a, i) => a + i.rollos, 0);
  let l = db.pedidos.filter(x => x.estado === pedFiltro), cuerpo;
  if (pedFiltro === 'pendiente') {
    l = l.sort((a, b) => K(a) < K(b) ? -1 : K(a) > K(b) ? 1 : (a.id < b.id ? -1 : 1));
    cuerpo = l.length ? l.map(cardPedido).join('') : '<div class="empty">No hay pedidos por entregar</div>';
  } else {
    l = l.sort((a, b) => { const fa = a.entregadoEn || '', fb = b.entregadoEn || ''; return fa !== fb ? (fa < fb ? 1 : -1) : ((a.entregadoHora || '') < (b.entregadoHora || '') ? 1 : -1); }).slice(0, 40);
    cuerpo = l.length ? '<div class="hint" style="margin:0 0 10px">Toca un pedido para ver el detalle o deshacer la entrega</div>' + agrupaDia(l, x => x.entregadoEn, x => hfila({ t: esc(x.cliente || 'Sin nombre'), s: fmt(nro(x)) + ' rollos' + (x.entregadoHora ? ' · ' + fmtHora(x.entregadoHora) : ''), r: money(tot(x)), on: "detallePedido('" + x.id + "')" })) : '<div class="empty">Aún no hay pedidos entregados</div>';
  }
  return '<h2>Pedidos</h2><button class="add" onclick="formPedido()">＋ Nuevo pedido</button>' +
    '<div class="chips"><button class="chip ' + (pedFiltro === 'pendiente' ? 'on' : '') + '" onclick="setPedFiltro(\'pendiente\')">Por entregar (' + pend + ')</button>' +
    '<button class="chip ' + (pedFiltro === 'entregado' ? 'on' : '') + '" onclick="setPedFiltro(\'entregado\')">Entregados (' + ent + ')</button></div>' + cuerpo;
}
""")

# ===== listas dentro de los detalles de un día =====
parchar(A, "vs.map(v => lineaVenta(v, f)).join('')", "'<div class=\"hcard\">' + vs.map(v => lineaVenta(v, f)).join('') + '</div>'")
parchar(A, "l.map(x => lineaProd(x, f)).join('')", "'<div class=\"hcard\">' + l.map(x => lineaProd(x, f)).join('') + '</div>'")

# ===== Ganancias: día por día y rollos por día en filas limpias =====
parchar(A, r"""Object.keys(dias).sort().reverse().map(f => '<div class="item tap" onclick="detalleDiaProd(\'' + f + '\')"><div class="row"><div><div class="name cap">' + nombreDia(f) + '</div><div class="meta">' + Object.keys(dias[f]).map(n => fmt(dias[f][n]) + ' × ' + esc(n)).join(' · ') + '</div></div><span class="pill">' + fmt(Object.values(dias[f]).reduce((a, b) => a + b, 0)) + '</span></div></div>').join('')""",
r"""'<div class="hcard">' + Object.keys(dias).sort().reverse().map(f => hfila({ t: '<span class="cap">' + nombreDia(f) + '</span>', s: Object.keys(dias[f]).map(n => fmt(dias[f][n]) + ' × ' + esc(n)).join(' · '), r: '+' + fmt(Object.values(dias[f]).reduce((a, b) => a + b, 0)), rs: 'rollos', on: "detalleDiaProd('" + f + "')" })).join('') + '</div>'""")
parchar(A, r"""Object.keys(dias).sort().reverse().map(f => '<div class="item tap" onclick="detalleDia(\'' + f + '\')"><div class="row"><div><div class="name cap">' + nombreDia(f) + '</div><div class="meta">' + fmt(dias[f].r) + ' rollos · ' + money(dias[f].t) + ' vendido</div></div><span class="pill ' + (dias[f].g < 0 ? 'low' : '') + '">' + money(dias[f].g) + '</span></div></div>').join('')""",
r"""'<div class="hcard">' + Object.keys(dias).sort().reverse().map(f => hfila({ t: '<span class="cap">' + nombreDia(f) + '</span>', s: fmt(dias[f].r) + ' rollos · ' + money(dias[f].t) + ' vendido', r: money(dias[f].g), rs: dias[f].g < 0 ? 'pérdida' : 'ganancia', rc: dias[f].g < 0 ? 'neg' : 'pos', on: "detalleDia('" + f + "')" })).join('') + '</div>'""")

# ===== botones de acción dentro de los detalles =====
parchar(A, "    btnVolver('detalleDia', vol));", r"""    (!x && v.fecha === hoy() ? '<button class="btn del full" onclick="' + dsp('borrarVenta', v.id) + '">Deshacer venta</button>' : '') +
    btnVolver('detalleDia', vol));""")
parchar(A, "    btnVolver('detalleDiaProd', vol));", r"""    '<button class="btn del full" onclick="' + dsp('borrarProduccion', x.id) + '">Deshacer rollos hechos</button>' +
    btnVolver('detalleDiaProd', vol));""")
parchar(A, """    (x.nota ? '<div class="dsec">Nota</div><div class="sub" style="margin:4px 0">' + esc(x.nota) + '</div>' : '') +
    '<button class="btn full" onclick="cerrarModal()">Cerrar</button>');""", r"""    (x.nota ? '<div class="dsec">Nota</div><div class="sub" style="margin:4px 0">' + esc(x.nota) + '</div>' : '') +
    (ent ? '<button class="btn del full" onclick="' + dsp('deshacerEntrega', x.id) + '">Deshacer entrega</button>' : '<button class="btn main full" onclick="' + dsp('entregarPedido', x.id) + '">Entregar pedido</button><button class="btn del full" onclick="' + dsp('cancelarPedido', x.id) + '">Cancelar pedido</button>') +
    '<button class="btn full" onclick="cerrarModal()">Cerrar</button>');""")

# ===== emoji que faltaba en Respaldo =====
parchar(A, "⬇️ ", "' + ICO.respaldo + ' ")

# ===== Pantalla nueva: Historial =====
parchar(A, "// ===== Ganancias =====\n", r"""// ===== Historial =====
let hf = { tipo: 'todo', per: 'todo', q: '', n: 30 };
function eventosHist() {
  const ev = [], nro = x => itemsDe(x).reduce((a, i) => a + i.rollos, 0), tot = x => itemsDe(x).reduce((a, i) => a + i.rollos * i.precio, 0), ts = id => parseInt(String(id).slice(0, 8), 36) || 0;
  const add = o => { if (o.f) { o.ts = o.ts || ts(o.id); ev.push(o); } };
  db.ventas.filter(v => !v.pedidoId).forEach(v => add({ k: 'venta', id: v.id, f: v.fecha, h: v.hora || '', t: esc(v.nombre), s: fmt(v.rollos) + ' rollos' + (v.cliente ? ' · ' + esc(v.cliente) : ''), r: money(v.total), m: v.total, b: v.nombre + ' ' + (v.cliente || '') }));
  db.pedidos.forEach(x => {
    const cli = x.cliente || 'Sin nombre', nom = itemsDe(x).map(i => i.nombre).join(' ');
    add({ k: 'pedido', id: x.id, f: x.fecha, h: x.hora || '', t: 'Pedido de ' + esc(cli), s: 'Anotado' + (x.estado === 'pendiente' ? ' · por entregar' : '') + ' · ' + fmt(nro(x)) + ' rollos', r: money(tot(x)), b: cli + ' ' + nom });
    const vv = db.ventas.find(v => v.pedidoId === x.id);
    if (x.estado === 'entregado') add({ k: 'entrega', id: x.id, ts: (vv ? ts(vv.id) : ts(x.id)) + 0.5, f: x.entregadoEn, h: x.entregadoHora || '', t: 'Entrega a ' + esc(cli), s: 'Pedido entregado · ' + fmt(nro(x)) + ' rollos', r: money(tot(x)), m: tot(x), b: cli + ' ' + nom });
  });
  db.produccion.forEach(x => add({ k: 'rollos', id: x.id, f: x.fecha, h: x.hora || '', t: esc(x.nombre), s: 'Rollos hechos' + (x.excesoG > 0 ? ' · salieron de más' : ''), r: '+' + fmt(x.rollos), rs: 'rollos', b: x.nombre }));
  db.entradas.forEach(x => add({ k: 'ingreso', id: x.id, f: x.fecha, h: x.hora || '', t: esc(x.nombre), s: 'Ingreso de materia', r: '+' + fmt(x.cantidad) + ' ' + (x.unidad || 'kg'), b: x.nombre }));
  (db.registro || []).forEach(x => add({ k: 'cambio', id: x.id, f: x.fecha, h: x.hora || '', t: LBL[x.tipo] || 'Cambio', s: esc(x.texto || ''), b: (LBL[x.tipo] || '') + ' ' + (x.texto || '') }));
  return ev.sort((a, b) => a.f !== b.f ? (a.f < b.f ? 1 : -1) : a.h !== b.h ? (a.h < b.h ? 1 : -1) : b.ts - a.ts);
}
function evFiltrados() {
  const tp = { todo: null, ventas: ['venta', 'entrega'], pedidos: ['pedido', 'entrega'], rollos: ['rollos'], materia: ['ingreso'], cambios: ['cambio'] }[hf.tipo];
  const h = hoy(), desde = hf.per === 'hoy' ? h : hf.per === '7' ? restaDias(h, 6) : hf.per === 'mes' ? h.slice(0, 7) + '-01' : '', q = hf.q.trim().toLowerCase();
  return eventosHist().filter(e => (!tp || tp.indexOf(e.k) >= 0) && (!desde || e.f >= desde) && (!q || e.b.toLowerCase().indexOf(q) >= 0));
}
function hLista() {
  const l = evFiltrados(), ver = l.slice(0, hf.n), dias = [];
  if (!l.length) return '<div class="empty">No hay movimientos con ese filtro</div>';
  const HI = { venta: ICO.venta, entrega: ICO.check, pedido: ICO.pedidos, rollos: ICO.rollos, ingreso: ICO.respaldo, cambio: ICO.deshacer };
  ver.forEach(e => { let d = dias[dias.length - 1]; if (!d || d.f !== e.f) dias.push(d = { f: e.f, l: [] }); d.l.push(e); });
  return '<div class="hint" style="margin:0 0 4px">' + l.length + (l.length === 1 ? ' movimiento' : ' movimientos') + '</div>' +
    dias.map(d => {
      const v = d.l.reduce((a, e) => a + (e.m || 0), 0);
      return '<div class="hday"><span>' + etiquetaDia(d.f) + '</span><small>' + d.l.length + (d.l.length === 1 ? ' movimiento' : ' movimientos') + (v ? ' · ' + money(v) + ' vendido' : '') + '</small></div><div class="hcard">' +
        d.l.map(e => hfila({ k: e.k, ic: HI[e.k], t: e.t, s: e.s + (e.h ? ' · ' + fmtHora(e.h) : ''), r: e.r, rs: e.rs, on: "abrirEv('" + e.k + "','" + e.id + "')" })).join('') + '</div>';
    }).join('') +
    (l.length > ver.length ? '<button class="btn full" style="margin-top:12px" onclick="hMas()">Ver más (' + (l.length - ver.length) + ')</button>' : '');
}
function vHistorial() {
  const ch = (g, v, t) => '<button class="chip ' + (hf[g] === v ? 'on' : '') + '" onclick="hSet(\'' + g + '\',\'' + v + '\')">' + t + '</button>';
  return '<h2>Historial</h2><div class="sub" style="margin:0 0 10px">Todo lo que se hace en la plataforma, ordenado por día. Toca un movimiento para ver el detalle.</div>' +
    '<input id="h-q" type="search" placeholder="Buscar cliente o producto…" value="' + esc(hf.q) + '" oninput="hBus(this.value)" style="margin-bottom:10px">' +
    '<div class="chips">' + ch('tipo', 'todo', 'Todo') + ch('tipo', 'ventas', 'Ventas') + ch('tipo', 'pedidos', 'Pedidos') + ch('tipo', 'rollos', 'Rollos hechos') + ch('tipo', 'materia', 'Materia') + ch('tipo', 'cambios', 'Cambios') + '</div>' +
    '<div class="chips">' + ch('per', 'hoy', 'Hoy') + ch('per', '7', 'Últimos 7 días') + ch('per', 'mes', 'Este mes') + ch('per', 'todo', 'Todo el tiempo') + '</div>' +
    '<div id="hlista">' + hLista() + '</div>';
}
function hSet(g, v) { hf[g] = v; hf.n = 30; render(); }
function hBus(v) { hf.q = v; hf.n = 30; $('#hlista').innerHTML = hLista(); }
function hMas() { hf.n += 30; $('#hlista').innerHTML = hLista(); }
function abrirEv(k, id) { ({ venta: detalleVenta, entrega: detallePedido, pedido: detallePedido, rollos: detalleProd, ingreso: detalleIngreso, cambio: detalleCambio })[k](id); }
function detalleCambio(id) {
  const x = (db.registro || []).find(y => y.id === id); if (!x) return;
  const cb = Array.isArray(x.cambios) ? x.cambios : Object.values(x.cambios || {});
  modal('<h3>' + (LBL[x.tipo] || 'Cambio') + '</h3><div class="sub" style="margin:2px 0 4px">' + esc(x.texto || '') + '</div>' +
    '<div class="dsec">Cuándo y quién</div>' + filaD('Día', diaLargo(x.fecha), 1) + filaD('Hora', x.hora ? fmtHora(x.hora) : '') + filaD('Hecho por', x.por ? esc(x.por) : '') +
    (cb.length ? '<div class="dsec">Qué cambió</div>' + cb.map(c => '<div class="dt"><b style="text-align:left">' + esc(c) + '</b></div>').join('') : '') +
    '<button class="btn full" style="margin-top:14px" onclick="cerrarModal()">Cerrar</button>');
}

// ===== Ganancias =====
""")

# ===== menú lateral y pantallas =====
parchar(A, "    it(ICO.pedidos, 'Pedidos', 'menuPedidos()', pend ? '<em>' + pend + '</em>' : '') +\n", "    it(ICO.pedidos, 'Pedidos', 'menuPedidos()', pend ? '<em>' + pend + '</em>' : '') +\n    it(ICO.historial, 'Historial', 'menuHistorial()') +\n")
parchar(A, "function menuModal(f) {", r"""function menuHistorial() {
  if (vista === 'historial') { cerrarMenu(); return; }
  cierraMenu();
  hf = { tipo: 'todo', per: 'todo', q: '', n: 30 };
  try { history.replaceState({ v: 'historial' }, ''); } catch (e) {}
  vista = 'historial'; fCat = 'Todas'; fBus = ''; render(); window.scrollTo(0, 0);
}
function menuModal(f) {""")
parchar(A, "ganancias: vGanancias, pedidos: vPedidos }[vista]", "ganancias: vGanancias, pedidos: vPedidos, historial: vHistorial }[vista]")

# ===== estilos =====
C = 'css/styles.css'
leer(C)
F[C] += r"""
.hday{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin:18px 4px 7px}
.hday span{font:800 .82rem var(--f-d);color:var(--txt)}
.hday small{font-size:.72rem;font-weight:600;color:var(--mut);text-align:right}
.hcard{background:var(--card);border:1px solid var(--line);border-radius:18px;box-shadow:var(--sh);overflow:hidden;margin-bottom:4px}
.hrow{display:flex;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid var(--line);cursor:pointer;transition:background .15s}
.hrow:last-child{border-bottom:none}
.hrow:active{background:var(--soft)}
.hic{flex:none;width:38px;height:38px;border-radius:12px;display:grid;place-items:center;background:var(--soft);color:var(--txt)}
.hic .ic{width:20px;height:20px}
.hic.t-venta,.hic.t-entrega{background:var(--okbg);color:var(--ok)}
.hic.t-pedido,.hic.t-rollos{background:var(--tagbg);color:var(--tagfg)}
.hic.t-cambio{background:var(--badbg);color:var(--bad)}
.hm{flex:1;min-width:0}
.ht{font-weight:700;font-size:.94rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.hs{font-size:.78rem;color:var(--mut);margin-top:2px;line-height:1.3}
.hv{flex:none;text-align:right}
.hv b{display:block;font:800 .95rem var(--f-d)}
.hv small{display:block;font-size:.7rem;color:var(--mut);font-weight:600}
.hv.pos b{color:var(--ok)}
.hv.neg b{color:var(--bad)}
"""

I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche15
- Historiales con filas limpias: cada movimiento es una fila de 2 líneas (arriba el producto o cliente y el total; abajo en gris los rollos, el cliente y la hora). Van en una sola tarjeta con líneas finas y agrupadas por día (Hoy, Ayer, fecha). El botón Deshacer ya no está en cada fila: está dentro del detalle (Deshacer venta, Deshacer rollos hechos, Deshacer entrega, Entregar pedido, Cancelar pedido). Ayudas en app.js: hfila(), agrupaDia(), dsp().
- Pantalla nueva Historial (menú lateral, debajo de Pedidos): junta ventas, pedidos anotados, entregas, rollos hechos, ingresos de materia y cambios. Filtros por tipo (Todo, Ventas, Pedidos, Rollos hechos, Materia, Cambios), por periodo (Hoy, Últimos 7 días, Este mes, Todo el tiempo) y buscador por cliente o producto. Muestra 30 y botón Ver más. Tocar un movimiento abre su detalle. Funciones: eventosHist, evFiltrados, hLista, vHistorial, abrirEv, detalleCambio.
- Registro de cambios (db.registro, función anotar): guarda quién y cuándo creó o editó un producto (con el antes y el después de cada dato), borró un producto, deshizo una venta, canceló un pedido, deshizo una entrega o deshizo rollos hechos. Se guarda en Firebase en negocio/registro con un envío aparte para no frenar el guardado de ventas y stock; si las reglas de Firebase no permiten esa carpeta, los cambios se ven solo en ese teléfono hasta recargar.
- Quitado el último emoji (Respaldo > Descargar copia).
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche15 aplicado (historiales limpios + pantalla Historial + registro de cambios)')
