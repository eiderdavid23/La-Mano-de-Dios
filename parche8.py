import sys, re, time

def parchar(archivo, viejo, nuevo):
    s = open(archivo, encoding='utf-8').read()
    n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces) en ' + archivo + ':', viejo[:70]); sys.exit(1)
    open(archivo, 'w', encoding='utf-8').write(s.replace(viejo, nuevo))

def todo(archivo, viejo, nuevo):
    s = open(archivo, encoding='utf-8').read()
    if s.count(viejo) < 1:
        print('ERROR (0 veces) en ' + archivo + ':', viejo[:70]); sys.exit(1)
    open(archivo, 'w', encoding='utf-8').write(s.replace(viejo, nuevo))

A = 'js/app.js'
C = 'css/styles.css'
H = 'index.html'

# ===== COLORES: amarillo -> durazno =====
todo(C, '#F4B400', '#F5C6A0')
todo(C, 'rgba(244,180,0,', 'rgba(245,198,160,')
todo(C, '#7A5600', '#8A4B24')
todo(C, 'rgba(185,134,0,.75)', 'rgba(200,135,90,.55)')
todo(C, 'rgba(80,55,0,.3)', 'rgba(120,70,30,.25)')
todo(H, '#F4B400', '#F5C6A0')

# ===== INDEX: menu y firebase sin bloquear =====
s = open(H, encoding='utf-8').read()
s, n = re.subn(r'<button class="gear".*?</button>',
  '<button class="gear" onclick="abrirMenu()" aria-label="Menú"><svg class="ic" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>', s, flags=re.S)
if n != 1: print('ERROR: boton engranaje'); sys.exit(1)
for f in ['app', 'auth', 'database']:
    t = '<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-' + f + '-compat.js"></script>\n'
    if s.count(t) != 1: print('ERROR: script firebase ' + f); sys.exit(1)
    s = s.replace(t, '')
pre = ''.join('<link rel="preload" as="script" href="https://www.gstatic.com/firebasejs/10.12.2/firebase-' + f + '-compat.js">\n' for f in ['app', 'auth', 'database'])
if s.count('<link rel="stylesheet" href="css/styles.css') != 1: print('ERROR: css link'); sys.exit(1)
s = s.replace('<link rel="stylesheet" href="css/styles.css', pre + '<link rel="stylesheet" href="css/styles.css')
if s.count('<div id="modal"') != 1: print('ERROR: modal'); sys.exit(1)
s = s.replace('<div id="modal"', '<div id="scrim" onclick="cerrarMenu()"></div>\n<aside id="drawer"></aside>\n<div id="modal"')
v = str(int(time.time()))
s = re.sub(r'\?v=\d+', '?v=' + v, s)
open(H, 'w', encoding='utf-8').write(s)

# ===== APP.JS =====
parchar(A, 'Math.max(0, 900 - ', 'Math.max(0, 250 - ')

# --- datos, cache
parchar(A, "const remoto = { productos: {}, entradas: {}, ventas: {} };", "const remoto = { productos: {}, entradas: {}, ventas: {}, pedidos: {} };")
parchar(A, "const COLS = ['productos', 'entradas', 'ventas'];", "const COLS = ['productos', 'entradas', 'ventas', 'pedidos'];")
parchar(A, "const est = o => o ? JSON.stringify(o, Object.keys(o).sort()) : 'null';",
r"""const ord = x => Array.isArray(x) ? x.map(ord) : (x && typeof x === 'object') ? Object.keys(x).sort().reduce((a, k) => (a[k] = ord(x[k]), a), {}) : x;
const est = o => o ? JSON.stringify(ord(o)) : 'null';
const KEYC = 'lmd_cache_v1';
function guardarCache() { try { localStorage.setItem(KEYC, JSON.stringify(db)); } catch (e) {} }
let cacheActiva = false, saltarPop = false, enLogin = false, sinRed = false, menuOn = false;
const espera = () => { if (cacheActiva && !listo) { toast(sinRed ? 'Sin conexión: por ahora solo puedes consultar' : 'Sincronizando… espera un momento'); return true; } return false; };""")
parchar(A, "const NUBE = typeof firebase !== 'undefined' && typeof firebaseConfig", "const NUBE = typeof firebaseConfig")
parchar(A, "return { productos: [], entradas: [], ventas: [] };", "return { productos: [], entradas: [], ventas: [], pedidos: [] };")
parchar(A, "function migrar(d) {\n", "function migrar(d) {\n  d.pedidos = d.pedidos || [];\n")
parchar(A, "  if (!listo || !fbRef) return;\n  const upd = {};", "  if (!listo || !fbRef) return;\n  guardarCache();\n  const upd = {};")

# --- stock disponible
parchar(A, "const rollosDisp = p => gpr(p) > 0 ? Math.floor(p.stockG / gpr(p) + 1e-9) : 0;\nconst bajo = p => p.stockG <= p.minimoG;",
r"""const itemsDe = x => Array.isArray(x.items) ? x.items : Object.values(x.items || {});
const apartadoG = p => (db.pedidos || []).filter(x => x.estado === 'pendiente').reduce((a, x) => a + itemsDe(x).filter(i => i.productoId === p.id).reduce((b, i) => b + i.gramos, 0), 0);
const dispG = p => Math.max(0, r2(p.stockG - apartadoG(p)));
const rollosDisp = p => gpr(p) > 0 ? Math.floor(dispG(p) / gpr(p) + 1e-9) : 0;
const bajo = p => dispG(p) <= p.minimoG;""")
todo(A, "fmtG(p.stockG)", "fmtG(dispG(p))")
parchar(A, "fmtG(p.stockG + g)", "fmtG(dispG(p) + g)")
parchar(A, "if (g > p.stockG + 1e-6) return toast('Solo alcanza", "if (g > dispG(p) + 1e-6) return toast('Solo alcanza")
parchar(A, "esc(catDe(p)) + '</span><br>' +\n    (gpr(p) > 0 ? fmtG(gpr(p)) + ' por rollo",
r"""esc(catDe(p)) + '</span><br>' + (apartadoG(p) > 0 ? '<b>Apartado en pedidos: ' + fmtG(apartadoG(p)) + '</b> (stock físico ' + fmtG(p.stockG) + ')<br>' : '') +
    (gpr(p) > 0 ? fmtG(gpr(p)) + ' por rollo""")

# --- 1) BOTON ATRAS + MENU LATERAL
parchar(A, "function ir(v) { vista = v; fCat = 'Todas'; fBus = ''; render(); window.scrollTo(0, 0); }",
r"""const enHist = k => !!(history.state && history.state[k]);
function hist(x) { try { history.pushState(Object.assign({ v: vista }, x || {}), ''); } catch (e) {} }
function hist0(v) { try { history.pushState({ v }, ''); } catch (e) {} }
function ir(v) {
  if (v !== vista) hist0(v);
  vista = v; fCat = 'Todas'; fBus = ''; render(); window.scrollTo(0, 0);
}
window.addEventListener('popstate', e => {
  if (saltarPop) { saltarPop = false; return; }
  if (menuOn) { cierraMenu(); return; }
  const m = $('#modal');
  if (m.classList.contains('show') && !m.classList.contains('closing')) { cierraModal(); return; }
  if (NUBE && !listo && !cacheActiva) return;
  const v = e.state && e.state.v;
  if (v && v !== vista) { vista = v; fCat = 'Todas'; fBus = ''; render(); window.scrollTo(0, 0); }
});
function abrirMenu() {
  if (menuOn || (NUBE && !listo && !cacheActiva)) return;
  $('#drawer').innerHTML = htmlMenu();
  hist({ d: 1 }); menuOn = true; document.body.classList.add('menu-on');
}
function cierraMenu() { menuOn = false; document.body.classList.remove('menu-on'); }
function cerrarMenu() {
  if (!menuOn) return;
  if (enHist('d')) { saltarPop = true; history.back(); }
  cierraMenu();
}
function htmlMenu() {
  const adm = NUBE && miPerfil && miPerfil.admin;
  const pend = pendPed().length, esp = adm && pendientes() ? ' (' + pendientes() + ' en espera)' : '';
  const it = (ico, t, f, extra) => '<button class="mi" onclick="' + f + '"><span>' + ico + '</span>' + t + (extra || '') + '</button>';
  return '<div class="dh"><b>Condimentos la Mano de Dios</b><small>' + (NUBE ? esc(usuarioActual()) + (adm ? ' 👑 administrador' : '') : 'Datos en este teléfono') + '</small></div>' +
    it('📋', 'Pedidos', 'menuPedidos()', pend ? '<em>' + pend + '</em>' : '') +
    (adm ? it('👥', 'Usuarios' + esp, 'menuModal(abrirUsuarios)') : '') +
    (!NUBE ? it('💾', 'Respaldo', 'menuModal(abrirAjustes)') : '') +
    (NUBE ? it('🚪', 'Cerrar sesión', 'menuSalir()') : '');
}
function menuPedidos() {
  if (vista === 'pedidos') { cerrarMenu(); return; }
  cierraMenu();
  try { history.replaceState({ v: 'pedidos' }, ''); } catch (e) {}
  vista = 'pedidos'; fCat = 'Todas'; fBus = ''; render(); window.scrollTo(0, 0);
}
function menuModal(f) {
  cierraMenu();
  try { history.replaceState({ v: vista, m: 1 }, ''); } catch (e) {}
  f();
}
function menuSalir() {
  cierraMenu();
  try { history.replaceState({ v: vista }, ''); } catch (e) {}
  salir();
}""")
parchar(A, "function modal(html) { const m = $('#modal');", "function modal(html) { if (!enHist('m')) hist({ m: 1 }); const m = $('#modal');")
parchar(A, "  m.classList.add('closing');\n  setTimeout(() => { if (m.classList.contains('closing')) m.classList.remove('show', 'closing'); }, 220);\n}",
r"""  if (enHist('m')) { saltarPop = true; history.back(); }
  cierraModal();
}
function cierraModal() {
  const m = $('#modal');
  m.classList.add('closing');
  setTimeout(() => { if (m.classList.contains('closing')) m.classList.remove('show', 'closing'); }, 220);
}""")

# --- render, bloqueos mientras sincroniza
parchar(A, "if (NUBE && !listo) { $('#app').innerHTML", "if (NUBE && !listo && !cacheActiva) { $('#app').innerHTML")
parchar(A, "  const v = { inicio: vInicio, stock: vStock, vender: vVender, ganancias: vGanancias }[vista];",
"  if (cacheActiva && !listo) $('#fecha').textContent += ' · sincronizando…';\n  const v = { inicio: vInicio, stock: vStock, vender: vVender, ganancias: vGanancias, pedidos: vPedidos }[vista];")
parchar(A, "  $('#nav').style.setProperty('--i', Math.max(0, TABS.findIndex(t => t[0] === vista)));",
"  const idx = TABS.findIndex(t => t[0] === vista);\n  $('#nav').style.setProperty('--i', Math.max(0, idx)); $('#nav').classList.toggle('fuera', idx < 0);")
parchar(A, "function formProducto(id) {\n", "function formProducto(id) {\n  if (espera()) return;\n")
parchar(A, "function borrarProducto(id) {\n", "function borrarProducto(id) {\n  if (espera()) return;\n  const pp = prod(id); if (pp && apartadoG(pp) > 0) return toast('Tiene pedidos pendientes: entrégalos o cancélalos primero');\n")
parchar(A, "function formIngreso(id) {\n", "function formIngreso(id) {\n  if (espera()) return;\n")
parchar(A, "function formVenta(id) {\n", "function formVenta(id) {\n  if (espera()) return;\n")
parchar(A, "function borrarVenta(id) {\n  const v = db.ventas.find(x => x.id === id);\n",
"function borrarVenta(id) {\n  if (espera()) return;\n  const v = db.ventas.find(x => x.id === id);\n  if (v && v.pedidoId) return toast('Viene de un pedido: deshaz la entrega en Pedidos');\n")
parchar(A, """'</div></div><button class="btn del" onclick="borrarVenta(\\'' + v.id + '\\')">Deshacer</button></div></div>'""",
"""'</div></div>' + (v.pedidoId ? '<span class="tag">Pedido</span>' : '<button class="btn del" onclick="borrarVenta(\\'' + v.id + '\\')">Deshacer</button>') + '</div></div>'""")
parchar(A, "db = migrar({ productos: d.productos, entradas: d.entradas || [], ventas: d.ventas });", "db = migrar({ productos: d.productos, entradas: d.entradas || [], ventas: d.ventas, pedidos: d.pedidos || [] });")

# --- nube, login rapido, arranque
parchar(A, "    if (u) { paso = 'leyendo perfil'; vigilar(); perfil(u); } else { clearTimeout(timer); mostrarLogin(); }",
r"""    if (u) { enLogin = false; paso = 'leyendo perfil'; vigilar(); perfil(u); }
    else { clearTimeout(timer); cacheActiva = false; try { localStorage.removeItem(KEYC); } catch (e) {} if (!enLogin) mostrarLogin(); }""")
parchar(A, "function mostrarError() {\n", "function mostrarError() {\n  quitarSplash();\n  if (cacheActiva) { sinRed = true; toast('Sin conexión: mostrando lo último guardado'); render(); return; }\n")
parchar(A, "function mostrarPendiente() {\n", "function mostrarPendiente() {\n  quitarSplash(); cacheActiva = false; enLogin = false; try { localStorage.removeItem(KEYC); } catch (e) {}")
parchar(A, "function mostrarLogin() {\n", "function mostrarLogin() {\n  quitarSplash(); enLogin = true; cacheActiva = false;")
parchar(A, "      ventas: Object.values(remoto.ventas).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1)\n    });",
"      ventas: Object.values(remoto.ventas).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1),\n      pedidos: Object.values(remoto.pedidos).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1)\n    });")
parchar(A, "    listo = true; clearTimeout(timer); $('#nav').style.display = ''; render();\n  }, e => {", "    listo = true; cacheActiva = false; sinRed = false; guardarCache(); quitarSplash(); clearTimeout(timer); $('#nav').style.display = ''; render();\n  }, e => {")
parchar(A, "  const m = u + '@manodedios.app';\n", "  if (typeof firebase === 'undefined' || !firebase.auth) return toast('Conectando… intenta de nuevo en un momento');\n  const m = u + '@manodedios.app';\n")
parchar(A, "function salir() { modoCrear = false; cerrarModal(); firebase.auth().signOut(); }",
"function salir() { modoCrear = false; cacheActiva = false; try { localStorage.removeItem(KEYC); } catch (e) {} cerrarModal(); firebase.auth().signOut(); }")
parchar(A, "function iniciar() {\n  if (!NUBE) { render(); quitarSplash(); return; }\n  local = db; db = { productos: [], entradas: [], ventas: [] };\n  render(); iniciarNube();\n}",
r"""function cargarScript(src) {
  return new Promise((ok, mal) => {
    const s = document.createElement('script'); s.src = src; s.onload = ok;
    s.onerror = () => mal(new Error('No cargó ' + src)); document.head.appendChild(s);
  });
}
function cargarFirebase() {
  const b = 'https://www.gstatic.com/firebasejs/10.12.2/firebase-';
  return cargarScript(b + 'app-compat.js').then(() => Promise.all([cargarScript(b + 'auth-compat.js'), cargarScript(b + 'database-compat.js')]));
}
function iniciar() {
  try { history.replaceState({ v: vista }, ''); } catch (e) {}
  if (!NUBE) { render(); quitarSplash(); return; }
  local = db; db = { productos: [], entradas: [], ventas: [], pedidos: [] };
  let c = null;
  try { c = JSON.parse(localStorage.getItem(KEYC)); } catch (e) {}
  if (c && c.productos) { db = migrar(c); cacheActiva = true; $('#nav').style.display = ''; render(); quitarSplash(); }
  else mostrarLogin();
  cargarFirebase().then(iniciarNube).catch(() => {
    sinRed = true; paso = 'sin conexión';
    if (cacheActiva) toast('Sin conexión: mostrando lo último guardado');
    else if (!enLogin) mostrarError();
    else toast('Sin conexión a internet');
  });
}""")

# --- 4) PEDIDOS
parchar(A, "// ===== Ganancias =====",
r"""// ===== Pedidos =====
let pedFiltro = 'pendiente', ped = null;
const pendPed = () => (db.pedidos || []).filter(x => x.estado === 'pendiente');
function setPedFiltro(f) { pedFiltro = f; render(); }
function vPedidos() {
  const pend = pendPed().length, ent = db.pedidos.length - pend, K = x => x.entrega || '9999';
  let l = db.pedidos.filter(x => x.estado === pedFiltro);
  l = pedFiltro === 'pendiente'
    ? l.sort((a, b) => K(a) < K(b) ? -1 : K(a) > K(b) ? 1 : (a.id < b.id ? -1 : 1))
    : l.sort((a, b) => (a.entregadoEn || '') < (b.entregadoEn || '') ? 1 : -1).slice(0, 30);
  return '<h2>Pedidos</h2><button class="add" onclick="formPedido()">＋ Nuevo pedido</button>' +
    '<div class="chips"><button class="chip ' + (pedFiltro === 'pendiente' ? 'on' : '') + '" onclick="setPedFiltro(\'pendiente\')">Por entregar (' + pend + ')</button>' +
    '<button class="chip ' + (pedFiltro === 'entregado' ? 'on' : '') + '" onclick="setPedFiltro(\'entregado\')">Entregados (' + ent + ')</button></div>' +
    (l.length ? l.map(cardPedido).join('') : '<div class="empty">' + (pedFiltro === 'pendiente' ? 'No hay pedidos por entregar' : 'Aún no hay pedidos entregados') + '</div>');
}
function cardPedido(x) {
  const its = itemsDe(x), total = its.reduce((a, i) => a + i.rollos * i.precio, 0), pen = x.estado === 'pendiente';
  return '<div class="item"><div class="row"><div><div class="name">' + esc(x.cliente || 'Sin nombre') + '</div><div class="meta">' +
    (pen ? (x.entrega ? 'Entrega: ' + nombreDia(x.entrega) : 'Sin fecha de entrega') : 'Entregado: ' + nombreDia(x.entregadoEn)) + '<br>' +
    its.map(i => fmt(i.rollos) + ' × ' + esc(i.nombre)).join(' · ') + (x.nota ? '<br>📝 ' + esc(x.nota) : '') + '</div></div>' +
    '<span class="pill">' + money(total) + '</span></div>' +
    '<div class="actions">' + (pen
      ? '<button class="btn main" onclick="entregarPedido(\'' + x.id + '\')">✅ Entregar</button><button class="btn del" onclick="cancelarPedido(\'' + x.id + '\')">Cancelar pedido</button>'
      : '<button class="btn" onclick="deshacerEntrega(\'' + x.id + '\')">Deshacer entrega</button>') + '</div></div>';
}
function formPedido() {
  if (espera()) return;
  if (!db.productos.length) return toast('Primero crea un producto en Stock');
  ped = { items: [] };
  const ops = db.productos.slice().sort((a, b) => a.nombre.localeCompare(b.nombre, 'es')).map(p => '<option value="' + p.id + '">' + esc(p.nombre) + ' (' + rollosDisp(p).toLocaleString('es-CO') + ' disp.)</option>').join('');
  modal('<h3>Nuevo pedido</h3><div class="sub" style="margin:2px 0 0">Aparta el producto del stock hasta que lo entregues</div>' +
    '<label>Cliente</label><input id="p-cli" placeholder="Nombre del cliente">' +
    '<label>Fecha de entrega (opcional)</label><input id="p-fec" type="date">' +
    '<label>Producto</label><select id="p-prod">' + ops + '</select>' +
    '<label>Rollos</label><div class="step"><button onclick="ajustarPed(-1)">−</button><input id="p-qty" type="number" inputmode="decimal" value="1"><button onclick="ajustarPed(1)">+</button></div>' +
    '<button class="btn full" onclick="agregarItemPed()">＋ Agregar al pedido</button>' +
    '<div id="p-items"></div>' +
    '<label>Nota (opcional)</label><input id="p-nota" placeholder="Ej: lo recoge en la tienda">' +
    '<button class="btn main full" onclick="guardarPedido()">Guardar pedido</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
  pintarItemsPed();
}
function ajustarPed(d) { $('#p-qty').value = Math.max(1, Math.round((Math.max(0, num($('#p-qty').value)) + d) * 100) / 100); }
function agregarItemPed() {
  const p = prod($('#p-prod').value), q = Math.max(0, num($('#p-qty').value));
  if (!p) return;
  if (q <= 0) return toast('Escribe los rollos');
  if (!(gpr(p) > 0)) return toast('Primero define los gramos por rollo (Stock → Editar)');
  const ex = ped.items.find(i => i.productoId === p.id), g = r2(q * gpr(p)), libre = dispG(p) - (ex ? ex.gramos : 0);
  if (g > libre + 1e-6) return toast('Solo quedan ' + Math.max(0, Math.floor(libre / gpr(p) + 1e-9)) + ' rollos disponibles de ' + p.nombre);
  if (ex) { ex.rollos = r2(ex.rollos + q); ex.gramos = r2(ex.gramos + g); }
  else ped.items.push({ productoId: p.id, nombre: p.nombre, rollos: q, gramos: g, precio: p.precio });
  $('#p-qty').value = 1; pintarItemsPed();
}
function quitarItemPed(i) { ped.items.splice(i, 1); pintarItemsPed(); }
function pintarItemsPed() {
  const t = ped.items.reduce((a, i) => a + i.rollos * i.precio, 0);
  $('#p-items').innerHTML = ped.items.length
    ? ped.items.map((i, k) => '<div class="item"><div class="row"><div><div class="name">' + esc(i.nombre) + '</div><div class="meta">' + fmt(i.rollos) + ' rollos · ' + money(i.rollos * i.precio) + '</div></div><button class="btn del" onclick="quitarItemPed(' + k + ')">Quitar</button></div></div>').join('') + '<div class="total"><b>' + money(t) + '</b></div>'
    : '<div class="empty">Aún no agregas productos</div>';
}
function guardarPedido() {
  const cliente = $('#p-cli').value.trim();
  if (!cliente) return toast('Escribe el nombre del cliente');
  if (!ped.items.length) return toast('Agrega al menos un producto');
  db.pedidos.push({ id: uid(), fecha: hoy(), cliente, entrega: $('#p-fec').value || '', nota: $('#p-nota').value.trim(), estado: 'pendiente', items: ped.items });
  ped = null; pedFiltro = 'pendiente';
  guardar(); cerrarModal(); render(); toast('Pedido guardado, producto apartado ✅');
}
function entregarPedido(id) {
  if (espera()) return;
  const x = db.pedidos.find(y => y.id === id); if (!x || x.estado !== 'pendiente') return;
  const its = itemsDe(x);
  for (const i of its) {
    const p = prod(i.productoId);
    if (!p) return toast(i.nombre + ' ya no existe en el stock');
    if (i.gramos > p.stockG + 1e-6) return toast('No alcanza el stock de ' + p.nombre + ' (' + fmtG(p.stockG) + ')');
  }
  if (!confirm('¿Entregar el pedido de ' + x.cliente + '? Se registra como venta de hoy.')) return;
  its.forEach(i => {
    const p = prod(i.productoId), costo = costoRollo(p);
    db.ventas.push({ id: uid(), fecha: hoy(), productoId: p.id, nombre: p.nombre, categoria: catDe(p), rollos: i.rollos, gramos: i.gramos, precio: i.precio, costo, total: i.rollos * i.precio, ganancia: i.rollos * (i.precio - costo), pedidoId: x.id });
    p.stockG = Math.max(0, r2(p.stockG - i.gramos));
  });
  x.estado = 'entregado'; x.entregadoEn = hoy();
  guardar(); render(); toast('Entregado y registrado como venta ✅'); if (navigator.vibrate) navigator.vibrate(15);
}
function cancelarPedido(id) {
  if (espera()) return;
  if (!confirm('¿Cancelar este pedido? El producto apartado vuelve a estar disponible.')) return;
  db.pedidos = db.pedidos.filter(x => x.id !== id);
  guardar(); render();
}
function deshacerEntrega(id) {
  if (espera()) return;
  const x = db.pedidos.find(y => y.id === id); if (!x) return;
  if (!confirm('¿Deshacer la entrega? Se borran sus ventas y el pedido vuelve a por entregar.')) return;
  db.ventas.filter(v => v.pedidoId === id).forEach(v => { const p = prod(v.productoId); if (p) p.stockG = r2(p.stockG + (v.gramos || 0)); });
  db.ventas = db.ventas.filter(v => v.pedidoId !== id);
  x.estado = 'pendiente'; delete x.entregadoEn;
  guardar(); render();
}

// ===== Ganancias =====""")

# --- CSS menu lateral
open(C, 'a', encoding='utf-8').write("""
.nav.fuera::before{opacity:0}
#scrim{position:fixed;inset:0;background:rgba(24,18,6,.42);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);opacity:0;visibility:hidden;transition:opacity .25s,visibility .25s;z-index:110}
#drawer{position:fixed;top:0;bottom:0;left:0;width:min(82vw,320px);background:var(--card);z-index:120;transform:translateX(-104%);transition:transform .32s var(--ease);padding:calc(env(safe-area-inset-top) + 24px) 14px 24px;box-shadow:12px 0 40px rgba(0,0,0,.25);overflow-y:auto}
body.menu-on #scrim{opacity:1;visibility:visible}
body.menu-on #drawer{transform:none}
.dh{padding:4px 8px 18px;border-bottom:1px solid var(--line);margin-bottom:10px}
.dh b{display:block;font:800 1.1rem/1.15 var(--f-d);letter-spacing:-.02em}
.dh small{color:var(--mut);font-weight:600;font-size:.82rem}
.mi{width:100%;display:flex;align-items:center;gap:12px;padding:14px 10px;border:none;background:none;border-radius:14px;color:var(--txt);font-family:inherit;font-weight:700;font-size:.98rem;text-align:left;cursor:pointer}
.mi:active{background:var(--soft)}
.mi span{font-size:1.2rem;width:26px;text-align:center}
.mi em{margin-left:auto;font-style:normal;background:var(--sf);color:#1D1B16;border-radius:10px;padding:2px 10px;font-size:.8rem}
""")

open('CONTEXTO.md', 'a', encoding='utf-8').write("""
## Cambios parche8
- Botón atrás: cada pantalla, ventana y el menú lateral quedan en el historial. Atrás cierra ventana/menú y luego vuelve a la pantalla anterior.
- Login rápido: copia de datos en el teléfono (lmd_cache_v1) que se muestra al instante mientras sincroniza con Firebase por detrás (solo consulta mientras tanto). Sin sesión, el login sale de inmediato. Firebase se carga por detrás (cargarFirebase en app.js).
- Colores: el amarillo pasó a durazno suave (#F5C6A0).
- Menú lateral (hamburguesa) reemplaza al engranaje: Pedidos, Usuarios (admin), Respaldo (modo local), Cerrar sesión.
- Pedidos: nodo "pedidos" dentro de "negocio". Un pedido pendiente aparta gramos del stock (disponible = stockG - apartado). Al entregar se crean las ventas (con pedidoId) y se descuenta el stock; la ganancia cuenta el día de la entrega. Deshacer entrega borra esas ventas. Cancelar libera lo apartado.
""")
print('OK: parche8 aplicado (atrás, login rápido, durazno, pedidos con menú lateral)')
