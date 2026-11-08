import sys, re, time

F = {}
def leer(a):
    if a not in F:
        F[a] = open(a, encoding='utf-8').read()
    return F[a]

def parchar(a, viejo, nuevo, n=1, opc=False):
    s = leer(a); c = s.count(viejo)
    if c == 0 and opc:
        return
    if c != n:
        print('ERROR (' + str(c) + ' veces, se esperaban ' + str(n) + ') en ' + a + ':', viejo[:80]); sys.exit(1)
    F[a] = s.replace(viejo, nuevo)

def linea(a, prefijo, nuevo, opc=False):
    ls = leer(a).split('\n')
    idx = [i for i, l in enumerate(ls) if l.startswith(prefijo)]
    if len(idx) == 0 and opc:
        return
    if len(idx) != 1:
        print('ERROR (' + str(len(idx)) + ' lineas) en ' + a + ':', prefijo[:80]); sys.exit(1)
    if nuevo == '':
        del ls[idx[0]]
    else:
        ls[idx[0]] = nuevo
    F[a] = '\n'.join(ls)

def func(a, nombre, nuevo, opc=False):
    s = leer(a)
    m = re.search(r'^function ' + re.escape(nombre) + r'\(.*?^}\n', s, re.S | re.M)
    if not m:
        if opc:
            return
        print('ERROR: no encontre la funcion ' + nombre); sys.exit(1)
    F[a] = s[:m.start()] + (nuevo.strip('\n') + '\n' if nuevo else '') + s[m.end():]

A = 'js/app.js'

# ---- Cuentas del mes: rollos hechos x precio - costo ----
linea(A, 'const rollosKilo = ', '', True)
linea(A, 'const costoRollo = ', """const costoRollo = p => 0;
const valorHecho = (p, ym) => db.produccion.filter(x => x.productoId === p.id && x.fecha.slice(0, 7) === ym).reduce((a, x) => a + x.rollos * (x.precio != null ? x.precio : (p.precio || 0)), 0);
const costoMes = (p, ym) => hechosMes(p.id, ym) > 0 ? (p.costoKilo || 0) : 0;
const gananciaMes = (p, ym) => valorHecho(p, ym) - costoMes(p, ym);""")
linea(A, 'const bajo = ', 'const bajo = p => (p.hechos || 0) <= 0;')

# ---- Inicio ----
func(A, 'vInicio', r"""
function vInicio() {
  const ym = hoy().slice(0, 7), vh = ventasDia(hoy()), bajos = db.productos.filter(p => bajo(p));
  const g = db.productos.reduce((a, p) => a + gananciaMes(p, ym), 0);
  return '<div class="hero"><small>Vendido hoy</small><b data-n="' + suma(vh, 'total') + '">' + money(suma(vh, 'total')) + '</b><span>' + fmt(suma(vh, 'rollos')) + ' rollos vendidos</span></div>' +
    '<div class="grid">' +
    '<div class="bubble wide"><small>' + gLbl(g) + ' del mes (' + nombreMes(ym) + ')</small><b class="' + gCls(g) + '" data-n="' + Math.abs(g) + '">' + money(Math.abs(g)) + '</b></div>' +
    '<div class="bubble"><small>Productos</small><b>' + db.productos.length + '</b></div>' +
    '<div class="bubble"><small>Sin rollos</small><b class="' + (bajos.length ? 'neg' : '') + '">' + bajos.length + '</b></div>' +
    '</div>' +
    (bajos.length ? '<h2>Por hacer</h2>' + bajos.map(p => '<div class="item low"><div class="row"><div class="name">' + esc(p.nombre) + '</div><span class="pill low">' + fmt(p.hechos || 0) + '<br><small>rollos</small></span></div></div>').join('') : '') +
    (!db.productos.length ? '<div class="empty">Empieza creando tu primer producto en Stock</div>' : '');
}
""")

# ---- Stock ----
func(A, 'vStock', r"""
function vStock() {
  const rec = db.produccion.slice().sort((a, b) => a.fecha < b.fecha ? 1 : a.fecha > b.fecha ? -1 : (a.id < b.id ? 1 : -1)).slice(0, 8);
  const hint = '<div class="hint" style="margin:0 0 10px">Toca uno para ver el detalle completo</div>';
  return '<h2>Inventario</h2><button class="add" onclick="formProducto()">＋ Nuevo producto</button>' +
    (db.productos.length ? barraFiltro() + '<div id="lista">' + listaStock() + '</div>' : '<div class="empty">Aún no hay productos</div>') +
    (rec.length ? '<h2 style="margin-top:22px">Últimos rollos hechos</h2>' + hint + agrupaDia(rec, x => x.fecha, x => lineaProd(x)) : '');
}
""")

func(A, 'listaStock', r"""
function listaStock() {
  const l = filtrados(), ym = hoy().slice(0, 7);
  if (!l.length) return '<div class="empty">No hay productos con ese filtro</div>';
  return l.map(p => {
    const ap = apartadoR(p), hm = hechosMes(p.id, ym), v = valorHecho(p, ym), g = v - costoMes(p, ym);
    return '<div class="item ' + (bajo(p) ? 'low' : '') + '"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div><div class="meta"><span class="tag">' + esc(catDe(p)) + '</span> ' + fmt(p.unidadesRollo || 0) + ' unidades · ' + money(p.precio) + '</div></div>' +
      '<span class="pill ' + (bajo(p) ? 'low' : '') + '"><small>Rollos listos</small>' + fmt(p.hechos || 0) + (ap > 0 ? '<small>' + fmt(ap) + ' apartados</small>' : '') + '</span></div>' +
      '<div class="lis"><span>Hechos este mes</span><b>' + fmt(hm) + ' rollos' + (hm > 0 ? ' <small>(' + money(v) + ')</small>' : '') + '</b></div>' +
      (p.costoKilo > 0 ? '<div class="lis"><span>Precio del kilo</span><b>' + money(p.costoKilo) + '</b></div>' : '') +
      (hm > 0 && p.costoKilo > 0 ? '<div class="gan ' + gCls(g) + '"><span>' + gLbl(g) + ' este mes</span><b>' + money(Math.abs(g)) + '</b></div>' : '') +
      '<div class="actions"><button class="btn main" onclick="formHechos(\'' + p.id + '\')">＋ Rollos hechos</button><button class="btn" onclick="formProducto(\'' + p.id + '\')">Editar</button><button class="btn del" onclick="borrarProducto(\'' + p.id + '\')">Borrar</button></div></div>';
  }).join('');
}
""")

# ---- Formulario del producto ----
func(A, 'formProducto', r"""
function formProducto(id) {
  if (espera()) return;
  const p = id ? prod(id) : { nombre: '', categoria: 'Aliños', unidadesRollo: 14, precio: 2000, costoKilo: '', hechos: 0 };
  modal('<h3>' + (id ? 'Editar producto' : 'Nuevo producto') + '</h3>' +
    '<label>Nombre</label><input id="f-nombre" value="' + esc(p.nombre) + '" placeholder="Ej: Canela">' +
    '<label>Categoría</label><select id="f-cat">' + opcionesCat(p.categoria || (id ? 'Otro' : 'Aliños')) + '</select>' +
    '<label>Unidades que trae el rollo</label><input id="f-unid" type="number" inputmode="decimal" value="' + (p.unidadesRollo || '') + '" placeholder="Ej: 14">' +
    '<label>Precio de venta del rollo ($)</label><input id="f-precio" type="number" inputmode="decimal" value="' + (p.precio || '') + '" placeholder="Ej: 2000">' +
    '<label>Precio del kilo ($; si es salsa, del litro)</label><input id="f-costo" type="number" inputmode="decimal" value="' + (p.costoKilo || '') + '" placeholder="Ej: 34000">' +
    '<label>' + (id ? 'Rollos listos que hay' : 'Rollos listos que tienes ahora (opcional)') + '</label><input id="f-stock" type="number" inputmode="decimal" value="' + (p.hechos || '') + '" placeholder="Ej: 20">' +
    '<button class="btn main full" onclick="guardarProducto(\'' + (id || '') + '\')">Guardar</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
}
""")

func(A, 'guardarProducto', r"""
function guardarProducto(id) {
  const nombre = $('#f-nombre').value.trim();
  if (!nombre) return toast('Escribe el nombre');
  const d = { nombre, categoria: $('#f-cat').value.trim(), unidadesRollo: num($('#f-unid').value) || 1, precio: num($('#f-precio').value), costoKilo: num($('#f-costo').value), hechos: r2(num($('#f-stock').value)) };
  if (id) {
    const o = Object.assign({}, prod(id)), CP = [['nombre', 'Nombre', x => x], ['categoria', 'Categoría', x => x || 'Sin categoría'], ['unidadesRollo', 'Unidades por rollo', fmt], ['precio', 'Precio de venta', money], ['costoKilo', 'Precio del kilo', money], ['hechos', 'Rollos listos', fmt]];
    const cb = CP.filter(c => (o[c[0]] || 0) !== (d[c[0]] || 0)).map(c => c[1] + ': ' + c[2](o[c[0]] || 0) + ' → ' + c[2](d[c[0]] || 0));
    Object.assign(prod(id), d);
    if (cb.length) anotar('producto_editado', 'Editó el producto ' + nombre, cb);
  } else {
    db.productos.push(Object.assign({ id: uid(), stockG: 0, minimoG: 0, gramosPorRollo: 0 }, d));
    anotar('producto_nuevo', 'Creó el producto ' + nombre);
  }
  guardar(); cerrarModal(); render(); toast('Producto guardado');
}
""")

for n in ['formIngreso', 'cambiarUnidad', 'prevIngreso', 'confirmarIngreso', 'formProduccion', 'prevProd', 'confirmarProd',
          'etiquetasForm', 'cambiarCatForm', 'desdePct', 'desdePrecio', 'infoPct', 'hintGr', 'formHechos', 'prevHechos', 'confirmarHechos', 'resumenMes']:
    func(A, n, '', True)

# ---- Rollos hechos: solo la cantidad y el dia ----
NUEVO = r"""
// ===== Rollos hechos: solo la cantidad (y el día) =====
function formHechos(id) {
  if (espera()) return;
  const p = prod(id);
  modal('<h3>Rollos hechos · ' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Hay ' + fmt(p.hechos || 0) + ' rollos listos</div>' +
    '<label>¿Cuántos rollos hiciste?</label><input id="h-cant" type="number" inputmode="decimal" placeholder="Ej: 30" oninput="prevHechos(\'' + id + '\')">' +
    '<label>Día</label><input id="h-fec" type="date" value="' + hoy() + '" max="' + hoy() + '" onchange="prevHechos(\'' + id + '\')">' +
    '<div class="preview" id="h-prev"></div>' +
    '<button class="btn main full" onclick="confirmarHechos(\'' + id + '\')">Registrar rollos hechos</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
}
function prevHechos(id) {
  const p = prod(id), q = num($('#h-cant').value), ym = ($('#h-fec').value || hoy()).slice(0, 7);
  if (q <= 0) { $('#h-prev').textContent = ''; return; }
  const v = valorHecho(p, ym) + q * (p.precio || 0), c = p.costoKilo || 0;
  $('#h-prev').textContent = 'Quedan ' + fmt((p.hechos || 0) + q) + ' rollos listos · ' + nombreMes(ym) + ': ' + fmt(hechosMes(id, ym) + q) + ' rollos = ' + money(v) + (c > 0 ? ' · ' + gLbl(v - c).toLowerCase() + ' ' + money(Math.abs(v - c)) : '');
}
function confirmarHechos(id) {
  const p = prod(id), q = num($('#h-cant').value), f = $('#h-fec').value || hoy();
  if (q <= 0) return toast('Escribe cuántos rollos hiciste');
  p.hechos = r2((p.hechos || 0) + q);
  db.produccion.push({ id: uid(), fecha: f, reg: hoy(), hora: ahora(), por: quien(), productoId: id, nombre: p.nombre, rollos: q, precio: p.precio, gramos: 0, gramosRollo: 0, excesoG: 0, excesoR: 0, alcanzaba: 0, quedaronG: 0, quedaron: p.hechos });
  guardar(); cerrarModal(); render(); toast('+' + fmt(q) + ' rollos hechos');
}
"""
parchar(A, "function borrarProduccion(id) {", NUEVO.strip('\n') + "\nfunction borrarProduccion(id) {")

func(A, 'borrarProduccion', r"""
function borrarProduccion(id) {
  if (espera()) return;
  const x = db.produccion.find(y => y.id === id); if (!x) return;
  const p = prod(x.productoId);
  if (p && (p.hechos || 0) < x.rollos - 1e-6) return toast('Esos rollos ya se vendieron; no se puede deshacer');
  if (!confirm('¿Deshacer estos rollos hechos?')) return;
  if (p) { p.stockG = r2((p.stockG || 0) + (x.gramos || 0) - (x.excesoG || 0)); p.hechos = r2((p.hechos || 0) - x.rollos); }
  anotar('rollos_deshechos', 'Deshizo ' + fmt(x.rollos) + ' rollos hechos de ' + x.nombre);
  db.produccion = db.produccion.filter(y => y.id !== id);
  guardar(); render();
}
""")

func(A, 'lineaProd', r"""
function lineaProd(x, vol) {
  return hfila({ t: esc(x.nombre), s: 'Rollos hechos' + (x.hora ? ' · ' + fmtHora(x.hora) : ''), r: '+' + fmt(x.rollos), rs: 'rollos', on: "detalleProd('" + x.id + "'" + (vol ? ",'" + vol + "'" : '') + ")" });
}
""")

func(A, 'detalleProd', r"""
function detalleProd(id, vol) {
  const x = db.produccion.find(y => y.id === id); if (!x) return;
  const p = prod(x.productoId), und = p && p.unidadesRollo ? r2(x.rollos * p.unidadesRollo) : null;
  modal('<h3>' + esc(x.nombre) + '</h3><div class="sub" style="margin:2px 0 4px">Rollos hechos</div>' +
    filaD('Rollos hechos', fmt(x.rollos)) + filaD('Unidades', und != null ? fmt(und) : '') +
    filaD('Valor a precio de venta', x.precio != null ? money(x.rollos * x.precio) : '') +
    filaD('Día', diaLargo(x.fecha), 1) +
    filaD('Registrado el', x.reg ? diaLargo(x.reg) : '', 1) +
    filaD('Hora del registro', x.hora ? fmtHora(x.hora) : 'No se registró (registro antiguo)') +
    filaD('Registrado por', x.por ? esc(x.por) : '') +
    '<button class="btn del full" onclick="' + dsp('borrarProduccion', x.id) + '">Deshacer rollos hechos</button>' +
    btnVolver('detalleDiaProd', vol));
}
""")

# ---- Vender y detalles: sin ganancia por venta ----
linea(A, "  $('#v-gan').className", "  $('#v-gan').className = 'pos';")
linea(A, "  $('#v-gan').textContent", "  $('#v-gan').textContent = '';")
parchar(A, "    '<div class=\"dsec\">Cuentas</div>' +\n    filaD('Costo por rollo', money(v.costo)) + filaD('Ganancia por rollo', money(gr)) + filaD(gLbl(v.ganancia) + ' total', money(v.ganancia)) +\n    (v.costo > 0 ? filaD('% sobre el costo', fmt(gr / v.costo * 100) + ' %') : '') +\n", "", 1, True)
parchar(A, " + ' vendido · ' + gLbl(g).toLowerCase() + ' ' + money(Math.abs(g)) + '</div>'", " + ' vendido</div>'")
parchar(A, " + (ent && vs.length ? filaD(gLbl(suma(vs, 'ganancia')) + ' del pedido', money(suma(vs, 'ganancia'))) : '')", "")

# ---- Historial ----
linea(A, "  db.produccion.forEach(x => add({ k: 'rollos'",
      "  db.produccion.forEach(x => add({ k: 'rollos', id: x.id, f: x.fecha, h: x.hora || '', t: esc(x.nombre), s: 'Rollos hechos', r: '+' + fmt(x.rollos), rs: 'rollos', b: x.nombre }));")
linea(A, "  db.entradas.forEach(x => add({ k: 'ingreso'", '', True)
parchar(A, "ch('tipo', 'rollos', 'Rollos hechos') + ch('tipo', 'materia', 'Materia') + ", "ch('tipo', 'rollos', 'Rollos hechos') + ", 1, True)

# ---- Ganancias: rollos hechos x precio - costo ----
func(A, 'vGanancias', r"""
function vGanancias() {
  const ym = mesSel, vm = ventasMes(ym), pr = db.produccion.filter(x => x.fecha.slice(0, 7) === ym), dv = {}, dp = {};
  vm.forEach(v => { const d = dv[v.fecha] = dv[v.fecha] || { r: 0, t: 0 }; d.r += v.rollos; d.t += v.total; });
  pr.forEach(x => { const d = dp[x.fecha] = dp[x.fecha] || {}; d[x.nombre] = (d[x.nombre] || 0) + x.rollos; });
  const lista = db.productos.filter(p => hechosMes(p.id, ym) > 0).map(p => ({ p, h: hechosMes(p.id, ym), v: valorHecho(p, ym), c: costoMes(p, ym), g: gananciaMes(p, ym) })).sort((a, b) => b.g - a.g);
  const g = lista.reduce((a, x) => a + x.g, 0);
  return '<div class="month"><button onclick="cambiarMes(-1)">‹</button><b>' + nombreMes(ym) + '</b><button onclick="cambiarMes(1)">›</button></div>' +
    '<div class="hero ' + gHero(g) + '"><small>' + gLbl(g) + ' del mes (todos los productos)</small><b data-n="' + Math.abs(g) + '">' + money(Math.abs(g)) + '</b><span>' + fmt(suma(pr, 'rollos')) + ' rollos hechos · ' + money(suma(vm, 'total')) + ' vendido</span></div>' +
    '<div class="sub" style="margin:0 0 6px">Ganancia = rollos hechos × precio de venta − precio del kilo. Cada mes empieza de cero.</div>' +
    '<h2>Ganancia por producto</h2>' + (lista.length ? lista.map(x => '<div class="item"><div class="row"><div><div class="name">' + esc(x.p.nombre) + '</div><div class="meta">' + fmt(x.h) + ' rollos · ' + money(x.v) + ' − costo ' + money(x.c) + '</div></div><span class="pill ' + (x.g < 0 ? 'low' : '') + '">' + money(x.g) + '</span></div></div>').join('') +
      '<div class="item" style="border-color:var(--ac)"><div class="row"><div class="name">Total de todos los productos</div><span class="pill ' + (g < 0 ? 'low' : '') + '">' + money(g) + '</span></div></div>' : '<div class="empty">Sin rollos hechos este mes</div>') +
    '<h2 style="margin-top:22px">Rollos hechos por día</h2><div class="hint" style="margin:0 0 10px">Toca un día para ver el detalle</div>' +
    (Object.keys(dp).length ? '<div class="hcard">' + Object.keys(dp).sort().reverse().map(f => hfila({ t: '<span class="cap">' + nombreDia(f) + '</span>', s: Object.keys(dp[f]).map(n => fmt(dp[f][n]) + ' × ' + esc(n)).join(' · '), r: '+' + fmt(Object.values(dp[f]).reduce((a, b) => a + b, 0)), rs: 'rollos', on: "detalleDiaProd('" + f + "')" })).join('') + '</div>' : '<div class="empty">Sin rollos hechos este mes</div>') +
    '<h2 style="margin-top:22px">Ventas día por día</h2><div class="hint" style="margin:0 0 10px">Toca un día para ver cada venta, a quién y a qué hora</div>' +
    (Object.keys(dv).length ? '<div class="hcard">' + Object.keys(dv).sort().reverse().map(f => hfila({ t: '<span class="cap">' + nombreDia(f) + '</span>', s: fmt(dv[f].r) + ' rollos', r: money(dv[f].t), rs: 'vendido', on: "detalleDia('" + f + "')" })).join('') + '</div>' : '<div class="empty">Sin ventas este mes</div>');
}
""")

# ---- Borrar pruebas ----
parchar(A, "ck('lp-rol', 'Rollos hechos') + ck('lp-ing', 'Ingresos de materia') +", "ck('lp-rol', 'Rollos hechos') +", 1, True)
parchar(A, "ing = $('#lp-ing').checked;", "ing = false;", 1, True)
linea(A, "    '<div class=\"hint\">El costo y el peso del rollo se quedan", '', True)
linea(A, "    if (p && x.kilos)", '', True)

# ---- Version nueva + contexto ----
I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))
X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche22 (productos simples, sin pesos ni conversiones)
- Esto REEMPLAZA las reglas de gramos, canecas, kilos y "ingreso de materia" de arriba. Un producto tiene: nombre, categoria, unidades que trae el rollo (unidadesRollo), precio de venta (precio), precio del kilo (costoKilo; en salsas, del litro) y rollos listos que hay (hechos = el stock).
- Rollos hechos (formHechos / confirmarHechos): solo la cantidad y el dia. Suma a p.hechos y guarda un registro en db.produccion con el precio de ese momento. No se piden kilos.
- Ganancia del mes de un producto = rollos hechos del mes x precio de venta - precio del kilo (el costo se cuenta una vez por mes, si hizo rollos). Se ve en tiempo real en Stock, Inicio y Ganancias. Funciones: valorHecho, costoMes, gananciaMes. Si se usa mas de un kilo en el mes, se escribe en "Precio del kilo" el costo total.
- Las ventas ya no calculan ganancia (costoRollo = 0); Vender y Pedidos siguen descontando p.hechos. Inicio muestra "Vendido hoy". Bajo = sin rollos (hechos <= 0).
- Se quitaron: kilos/libras/canecas, ingreso de materia, gramos por rollo. Datos viejos quedan guardados pero no se ven.
"""
for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche22 aplicado (productos simples)')
