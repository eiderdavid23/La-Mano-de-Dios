import sys, re, time

F = {}
def leer(a):
    if a not in F:
        F[a] = open(a, encoding='utf-8').read()
    return F[a]

def parchar(a, viejo, nuevo, n=1):
    s = leer(a); c = s.count(viejo)
    if c != n:
        print('ERROR (' + str(c) + ' veces, se esperaban ' + str(n) + ') en ' + a + ':', viejo[:80]); sys.exit(1)
    F[a] = s.replace(viejo, nuevo)

def linea(a, prefijo, nuevo):
    ls = leer(a).split('\n')
    idx = [i for i, l in enumerate(ls) if l.startswith(prefijo)]
    if len(idx) != 1:
        print('ERROR (' + str(len(idx)) + ' lineas) en ' + a + ':', prefijo[:80]); sys.exit(1)
    if nuevo == '':
        del ls[idx[0]]
    else:
        ls[idx[0]] = nuevo
    F[a] = '\n'.join(ls)

def func(a, nombre, nuevo):
    s = leer(a)
    m = re.search(r'^function ' + re.escape(nombre) + r'\(.*?^}\n', s, re.S | re.M)
    if not m:
        print('ERROR: no encontre la funcion ' + nombre); sys.exit(1)
    F[a] = s[:m.start()] + (nuevo.strip('\n') + '\n' if nuevo else '') + s[m.end():]

A = 'js/app.js'

# ---- Cuentas: rollos por kilo sale de lo que vas sumando ----
parchar(A, "const costoRollo = p => gpr(p) > 0 ? p.costoKilo * gpr(p) / 1000 : 0;",
"const rollosKilo = p => p.kilosUsados > 0 && p.rollosSalidos > 0 ? p.rollosSalidos / p.kilosUsados : (gpr(p) > 0 ? 1000 / gpr(p) : 0);\nconst costoRollo = p => rollosKilo(p) > 0 && p.costoKilo > 0 ? p.costoKilo / rollosKilo(p) : 0;")
parchar(A, "const bajo = p => dispG(p) <= p.minimoG;", "const bajo = p => (p.hechos || 0) <= 0;")
parchar(A, "fmtV(p, dispG(p)) + '<br><small>' + rollosDisp(p).toLocaleString('es-CO') + ' rollos</small>",
           "fmt(p.hechos || 0) + '<br><small>rollos</small>")

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
  const l = filtrados();
  if (!l.length) return '<div class="empty">No hay productos con ese filtro</div>';
  return l.map(p => {
    const ga = gananciaRollo(p), cr = costoRollo(p), ap = apartadoR(p), rk = rollosKilo(p), sab = p.kilosUsados > 0 && p.rollosSalidos > 0;
    return '<div class="item ' + (bajo(p) ? 'low' : '') + '"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div><div class="meta"><span class="tag">' + esc(catDe(p)) + '</span> ' + fmt(p.unidadesRollo || 0) + ' unidades · ' + money(p.precio) + '</div></div>' +
      '<span class="pill ' + (bajo(p) ? 'low' : '') + '"><small>Rollos hechos</small>' + fmt(p.hechos || 0) + (ap > 0 ? '<small>' + fmt(ap) + ' apartados</small>' : '') + '</span></div>' +
      '<div class="lis"><span>Del kilo salen</span><b>' + (rk > 0 ? '≈ ' + fmt(rk) + ' rollos' + (sab ? ' <small>(' + fmt(p.rollosSalidos) + ' rollos de ' + fmt(p.kilosUsados) + ' kilos)</small>' : '') : 'Aún no se sabe') + '</b></div>' +
      (p.costoKilo > 0 ? '<div class="lis"><span>Precio del kilo</span><b>' + money(p.costoKilo) + '</b></div>' : '') +
      (cr > 0 ? '<div class="gan ' + gCls(ga) + '"><span>' + gLbl(ga) + ' por rollo</span><b>' + money(Math.abs(ga)) + '</b></div>' : '') +
      '<div class="actions"><button class="btn main" onclick="formHechos(\'' + p.id + '\')">＋ Rollos hechos</button><button class="btn" onclick="formProducto(\'' + p.id + '\')">Editar</button><button class="btn del" onclick="borrarProducto(\'' + p.id + '\')">Borrar</button></div></div>';
  }).join('');
}
""")

func(A, 'formProducto', r"""
function formProducto(id) {
  if (espera()) return;
  const p = id ? prod(id) : { nombre: '', categoria: 'Aliños', unidadesRollo: 14, precio: 2000, costoKilo: '', hechos: 0 };
  modal('<h3>' + (id ? 'Editar producto' : 'Nuevo producto') + '</h3>' +
    '<label>Nombre</label><input id="f-nombre" value="' + esc(p.nombre) + '" placeholder="Ej: Canela">' +
    '<label>Categoría</label><select id="f-cat">' + opcionesCat(p.categoria || (id ? 'Otro' : 'Aliños')) + '</select>' +
    '<label>Unidades que trae el rollo</label><input id="f-unid" type="number" inputmode="decimal" value="' + (p.unidadesRollo || '') + '" placeholder="Ej: 14">' +
    '<label>Precio de venta del rollo ($)</label><input id="f-precio" type="number" inputmode="decimal" value="' + (p.precio || '') + '" placeholder="Ej: 2000">' +
    '<label>Precio del kilo ($; si es salsa, del litro)</label><input id="f-costo" type="number" inputmode="decimal" value="' + (p.costoKilo || '') + '" placeholder="Lo que pagas por 1 kilo">' +
    '<label>' + (id ? 'Rollos hechos que hay' : 'Rollos hechos que tienes ahora (opcional)') + '</label><input id="f-stock" type="number" inputmode="decimal" value="' + (p.hechos || '') + '" placeholder="Ej: 20">' +
    '<button class="btn main full" onclick="guardarProducto(\'' + (id || '') + '\')">Guardar</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
}
""")

func(A, 'guardarProducto', r"""
function guardarProducto(id) {
  const nombre = $('#f-nombre').value.trim();
  if (!nombre) return toast('Escribe el nombre');
  const d = { nombre, categoria: $('#f-cat').value.trim(), unidadesRollo: num($('#f-unid').value) || 1, precio: num($('#f-precio').value), costoKilo: num($('#f-costo').value), hechos: r2(num($('#f-stock').value)) };
  if (id) {
    const o = Object.assign({}, prod(id)), CP = [['nombre', 'Nombre', x => x], ['categoria', 'Categoría', x => x || 'Sin categoría'], ['unidadesRollo', 'Unidades por rollo', fmt], ['precio', 'Precio de venta', money], ['costoKilo', 'Precio del kilo', money], ['hechos', 'Rollos hechos', fmt]];
    const cb = CP.filter(c => (o[c[0]] || 0) !== (d[c[0]] || 0)).map(c => c[1] + ': ' + c[2](o[c[0]] || 0) + ' → ' + c[2](d[c[0]] || 0));
    Object.assign(prod(id), d);
    if (cb.length) anotar('producto_editado', 'Editó el producto ' + nombre, cb);
  } else {
    db.productos.push(Object.assign({ id: uid(), stockG: 0, minimoG: 0, gramosPorRollo: 0, kilosUsados: 0, rollosSalidos: 0 }, d));
    anotar('producto_nuevo', 'Creó el producto ' + nombre);
  }
  guardar(); cerrarModal(); render(); toast('Producto guardado');
}
""")

for n in ['formIngreso', 'cambiarUnidad', 'prevIngreso', 'confirmarIngreso', 'formProduccion', 'prevProd', 'confirmarProd',
          'etiquetasForm', 'cambiarCatForm', 'desdePct', 'desdePrecio', 'infoPct', 'hintGr']:
    func(A, n, '')

# ---- Rollos hechos: suma kilos y rollos para saber cuantos salen por kilo ----
NUEVO = r"""
// ===== Rollos hechos (suma kilos y rollos: así se sabe cuántos salen por kilo) =====
function formHechos(id) {
  if (espera()) return;
  const p = prod(id), rk = rollosKilo(p);
  modal('<h3>Rollos hechos · ' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Hay ' + fmt(p.hechos || 0) + ' rollos' + (rk > 0 ? ' · del kilo salen ≈ ' + fmt(rk) : '') + '</div>' +
    '<label>Kilos que usaste</label><input id="h-kg" type="number" inputmode="decimal" value="1" oninput="prevHechos(\'' + id + '\')">' +
    '<label>¿Cuántos rollos salieron?</label><input id="h-cant" type="number" inputmode="decimal" placeholder="Ej: 30" oninput="prevHechos(\'' + id + '\')">' +
    '<div class="preview" id="h-prev"></div>' +
    '<button class="btn main full" onclick="confirmarHechos(\'' + id + '\')">Registrar rollos hechos</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
}
function prevHechos(id) {
  const p = prod(id), q = num($('#h-cant').value), k = num($('#h-kg').value);
  if (q <= 0) { $('#h-prev').textContent = ''; return; }
  const tk = (p.kilosUsados || 0) + k, tr = (p.rollosSalidos || 0) + q;
  $('#h-prev').textContent = 'Quedan ' + fmt((p.hechos || 0) + q) + ' rollos' + (k > 0 ? ' · esta vez 1 kilo = ' + fmt(q / k) + ' rollos · con todo lo sumado 1 kilo = ' + fmt(tr / tk) : '');
}
function confirmarHechos(id) {
  const p = prod(id), q = num($('#h-cant').value), k = num($('#h-kg').value);
  if (q <= 0) return toast('Escribe cuántos rollos salieron');
  p.hechos = r2((p.hechos || 0) + q);
  if (k > 0) { p.kilosUsados = r2((p.kilosUsados || 0) + k); p.rollosSalidos = r2((p.rollosSalidos || 0) + q); }
  db.produccion.push({ id: uid(), fecha: hoy(), reg: hoy(), hora: ahora(), por: quien(), productoId: id, nombre: p.nombre, rollos: q, kilos: k > 0 ? k : 0, gramos: 0, gramosRollo: 0, excesoG: 0, excesoR: 0, alcanzaba: 0, quedaronG: 0, quedaron: p.hechos });
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
  if (p) {
    p.stockG = r2((p.stockG || 0) + (x.gramos || 0) - (x.excesoG || 0)); p.hechos = r2((p.hechos || 0) - x.rollos);
    if (x.kilos) { p.kilosUsados = Math.max(0, r2((p.kilosUsados || 0) - x.kilos)); p.rollosSalidos = Math.max(0, r2((p.rollosSalidos || 0) - x.rollos)); }
  }
  anotar('rollos_deshechos', 'Deshizo ' + fmt(x.rollos) + ' rollos hechos de ' + x.nombre);
  db.produccion = db.produccion.filter(y => y.id !== id);
  guardar(); render();
}
""")

func(A, 'lineaProd', r"""
function lineaProd(x, vol) {
  return hfila({ t: esc(x.nombre), s: 'Rollos hechos' + (x.kilos ? ' · ' + fmt(x.kilos) + ' kg' : '') + (x.hora ? ' · ' + fmtHora(x.hora) : ''), r: '+' + fmt(x.rollos), rs: 'rollos', on: "detalleProd('" + x.id + "'" + (vol ? ",'" + vol + "'" : '') + ")" });
}
""")

func(A, 'detalleProd', r"""
function detalleProd(id, vol) {
  const x = db.produccion.find(y => y.id === id); if (!x) return;
  const p = prod(x.productoId), und = p && p.unidadesRollo ? r2(x.rollos * p.unidadesRollo) : null;
  modal('<h3>' + esc(x.nombre) + '</h3><div class="sub" style="margin:2px 0 4px">Rollos hechos</div>' +
    filaD('Rollos hechos', fmt(x.rollos)) + filaD('Unidades', und != null ? fmt(und) : '') +
    filaD('Kilos que usaste', x.kilos ? fmt(x.kilos) : '') + filaD('Salieron por kilo', x.kilos ? fmt(x.rollos / x.kilos) + ' rollos' : '') +
    filaD('Día', diaLargo(x.fecha), 1) +
    filaD('Hora del registro', x.hora ? fmtHora(x.hora) : 'No se registró (registro antiguo)') +
    filaD('Registrado por', x.por ? esc(x.por) : '') +
    (x.gramos > 0 ? filaD('Materia usada (registro antiguo)', fmtV(p, x.gramos)) : '') +
    '<button class="btn del full" onclick="' + dsp('borrarProduccion', x.id) + '">Deshacer rollos hechos</button>' +
    btnVolver('detalleDiaProd', vol));
}
""")

# ---- Vender ----
linea(A, "  $('#v-gan').textContent = gpr(p) > 0 ?",
      "  $('#v-gan').textContent = costoRollo(p) > 0 ? 'Ganancia: ' + money(q * gananciaRollo(p)) : '';")

# ---- Historial ----
linea(A, "  db.produccion.forEach(x => add({ k: 'rollos'",
      "  db.produccion.forEach(x => add({ k: 'rollos', id: x.id, f: x.fecha, h: x.hora || '', t: esc(x.nombre), s: 'Rollos hechos' + (x.kilos ? ' · ' + fmt(x.kilos) + ' kg' : ''), r: '+' + fmt(x.rollos), rs: 'rollos', b: x.nombre }));")
linea(A, "  db.entradas.forEach(x => add({ k: 'ingreso'", '')
parchar(A, "ch('tipo', 'rollos', 'Rollos hechos') + ch('tipo', 'materia', 'Materia') + ", "ch('tipo', 'rollos', 'Rollos hechos') + ")

# ---- Ganancias ----
func(A, 'resumenMes', r"""
function resumenMes(ym) {
  const pr = db.produccion.filter(x => x.fecha.slice(0, 7) === ym), porProd = {}, dias = {};
  pr.forEach(x => {
    const k = x.productoId || x.nombre, P = porProd[k] = porProd[k] || { n: x.nombre, h: 0, k: 0 };
    P.h += x.rollos; P.k += x.kilos || 0;
    dias[x.fecha] = dias[x.fecha] || {}; dias[x.fecha][x.nombre] = (dias[x.fecha][x.nombre] || 0) + x.rollos;
  });
  const lista = Object.values(porProd).sort((a, b) => a.n.localeCompare(b.n, 'es'));
  return '<div class="grid"><div class="bubble"><small>Rollos hechos</small><b>' + fmt(suma(pr, 'rollos')) + '</b></div><div class="bubble"><small>Kilos usados</small><b>' + fmt(pr.reduce((a, x) => a + (x.kilos || 0), 0)) + '</b></div></div>' +
    '<h2>Rollos hechos por producto</h2>' + (lista.length ? lista.map(x => '<div class="item"><div class="row"><div><div class="name">' + esc(x.n) + '</div><div class="meta">Hizo ' + fmt(x.h) + ' rollos' + (x.k > 0 ? ' · usó ' + fmt(x.k) + ' kilos · salen ' + fmt(x.h / x.k) + ' por kilo' : '') + '</div></div></div></div>').join('') : '<div class="empty">Sin rollos hechos este mes</div>') +
    '<h2>Rollos hechos por día</h2><div class="hint" style="margin:0 0 10px">Toca un día para ver el detalle</div>' + (Object.keys(dias).length ? '<div class="hcard">' + Object.keys(dias).sort().reverse().map(f => hfila({ t: '<span class="cap">' + nombreDia(f) + '</span>', s: Object.keys(dias[f]).map(n => fmt(dias[f][n]) + ' × ' + esc(n)).join(' · '), r: '+' + fmt(Object.values(dias[f]).reduce((a, b) => a + b, 0)), rs: 'rollos', on: "detalleDiaProd('" + f + "')" })).join('') + '</div>' : '<div class="empty">Sin rollos hechos este mes</div>');
}
""")

# ---- Borrar pruebas ----
parchar(A, "ck('lp-rol', 'Rollos hechos') + ck('lp-ing', 'Ingresos de materia') +", "ck('lp-rol', 'Rollos hechos') +")
parchar(A, "ing = $('#lp-ing').checked;", "ing = false;")
linea(A, "    '<div class=\"hint\">El costo y el peso del rollo se quedan", '')
parchar(A, "    idR[x.id] = 1;", "    if (p && x.kilos) { p.kilosUsados = Math.max(0, r2((p.kilosUsados || 0) - x.kilos)); p.rollosSalidos = Math.max(0, r2((p.rollosSalidos || 0) - x.rollos)); }\n    idR[x.id] = 1;")

# ---- Version nueva + contexto ----
I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))
X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche22 (productos simples, sin pesos ni conversiones)
- Esto REEMPLAZA las reglas de gramos, canecas y "ingreso de materia" de arriba. Un producto tiene: nombre, categoria, unidades que trae el rollo (unidadesRollo), precio de venta (precio), precio del kilo (costoKilo; en salsas, del litro) y rollos hechos que hay (hechos = el stock).
- Rollos hechos (formHechos / confirmarHechos): se escribe kilos usados y rollos que salieron. Suma a p.hechos y acumula p.kilosUsados y p.rollosSalidos. Rollos por kilo = rollosSalidos / kilosUsados (rollosKilo en app.js); si aun no hay datos usa 1000 / gramosPorRollo del producto viejo. Costo por rollo = costoKilo / rollos por kilo; sin eso no se muestra ganancia.
- Vender y Pedidos descuentan p.hechos como antes. Bajo = sin rollos (hechos <= 0).
- Se quitaron: kilos/libras/canecas, ingreso de materia, gramos por rollo en el formulario. Datos viejos (stockG, entradas) quedan guardados pero no se ven.
"""
for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche22 aplicado (productos simples)')
