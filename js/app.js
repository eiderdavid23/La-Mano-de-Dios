// ===== Pantalla de carga =====
const splashT0 = Date.now();
function quitarSplash() {
  const s = document.getElementById('splash');
  if (!s || s.dataset.salio) return;
  s.dataset.salio = '1';
  setTimeout(() => { s.classList.add('out'); setTimeout(() => s.remove(), 600); }, Math.max(0, 250 - (Date.now() - splashT0)));
}
setTimeout(quitarSplash, 10000);

// ===== Datos =====
function p2(n) { return String(n).padStart(2, '0'); }
const r2 = n => Math.round(n * 100) / 100;
const KEY = 'control_rollos_v1';
let db = cargar();
let vista = 'inicio';
let mesSel = hoy().slice(0, 7);
let fCat = 'Todas', fBus = '';
const NUBE = typeof firebaseConfig !== 'undefined' && !!firebaseConfig.apiKey;
let local = null, fbRef = null, listo = !NUBE;
const remoto = { productos: {}, entradas: {}, ventas: {}, pedidos: {}, produccion: {}, registro: {} };
const COLS = ['productos', 'entradas', 'ventas', 'pedidos', 'produccion'];
const ord = x => Array.isArray(x) ? x.map(ord) : (x && typeof x === 'object') ? Object.keys(x).sort().reduce((a, k) => (a[k] = ord(x[k]), a), {}) : x;
const est = o => o ? JSON.stringify(ord(o)) : 'null';
const KEYC = 'lmd_cache_v1';
function guardarCache() { try { localStorage.setItem(KEYC, JSON.stringify(db)); } catch (e) {} }
let cacheActiva = false, saltarPop = false, enLogin = false, sinRed = false, menuOn = false;
const espera = () => { if (cacheActiva && !listo) { toast(sinRed ? 'Sin conexión: por ahora solo puedes consultar' : 'Sincronizando… espera un momento'); return true; } return false; };

function cargar() {
  try { const d = JSON.parse(localStorage.getItem(KEY)); if (d && d.productos) return migrar(d); } catch (e) {}
  return { productos: [], entradas: [], ventas: [], pedidos: [], produccion: [], registro: [] };
}
// Datos viejos (stock en rollos) -> stock en gramos
function migrar(d) {
  d.pedidos = d.pedidos || [];
  d.produccion = d.produccion || [];
  d.registro = d.registro || [];
  (d.productos || []).forEach(p => { if (p.hechos === undefined) p.hechos = 0; });
  (d.productos || []).forEach(p => {
    if (p.gramosPorRollo !== undefined) return;
    const g = p.rollosPorKilo > 0 ? 1000 / p.rollosPorKilo : 0;
    p.gramosPorRollo = r2(g);
    p.stockG = r2((p.stock || 0) * g);
    p.minimoG = r2((p.minimo || 0) * g);
    delete p.rollosPorKilo; delete p.stock; delete p.minimo;
  });
  return d;
}
function guardar() {
  if (!NUBE) { localStorage.setItem(KEY, JSON.stringify(db)); return; }
  if (!listo || !fbRef) return;
  guardarCache();
  const upd = {};
  COLS.forEach(c => {
    const actual = {};
    db[c].forEach(x => { actual[x.id] = x; });
    Object.keys(actual).forEach(id => {
      if (est(actual[id]) !== est(remoto[c][id])) upd[c + '/' + id] = JSON.parse(JSON.stringify(actual[id]));
    });
    Object.keys(remoto[c]).forEach(id => { if (!actual[id]) upd[c + '/' + id] = null; });
  });
  if (Object.keys(upd).length) fbRef.update(upd).catch(e => toast('No se pudo guardar: ' + e.message));
  const upR = {};
  (db.registro || []).forEach(x => { if (!remoto.registro[x.id]) upR['registro/' + x.id] = JSON.parse(JSON.stringify(x)); });
  if (Object.keys(upR).length) fbRef.update(upR).catch(() => {});
}

// ===== Utilidades =====
function hoy() { const d = new Date(); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); }
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const num = v => { const n = parseFloat(String(v).replace(',', '.')); return isNaN(n) ? 0 : n; };
const money = n => (n < 0 ? '-' : '') + '$' + Math.round(Math.abs(n)).toLocaleString('es-CO');
const fmt = n => (Math.round(n * 10) / 10).toLocaleString('es-CO');
const prod = id => db.productos.find(p => p.id === id);
const gpr = p => p.gramosPorRollo || 0;
const fmtG = g => fmt(g) + ' g';
const ahora = () => { const d = new Date(); return p2(d.getHours()) + ':' + p2(d.getMinutes()); };
const fmtHora = h => { if (!h) return ''; const [H, M] = h.split(':').map(Number); return ((H % 12) || 12) + ':' + p2(M) + (H < 12 ? ' a. m.' : ' p. m.'); };
const quien = () => { try { return NUBE ? usuarioActual() : ''; } catch (e) { return ''; } };
function diaLargo(f) { if (!f) return ''; const [y, m, d] = f.split('-').map(Number); return new Date(y, m - 1, d).toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }); }
const filaD = (k, v, c) => v ? '<div class="dt"><span>' + k + '</span><b' + (c ? ' class="cap"' : '') + '>' + v + '</b></div>' : '';
const btnVolver = (f, v) => (v ? '<button class="btn full" onclick="' + f + '(\'' + v + '\')">← Volver al día</button>' : '') + '<button class="btn full" onclick="cerrarModal()">Cerrar</button>';
const itemsDe = x => Array.isArray(x.items) ? x.items : Object.values(x.items || {});
const apartadoR = p => (db.pedidos || []).filter(x => x.estado === 'pendiente').reduce((a, x) => a + itemsDe(x).filter(i => i.productoId === p.id).reduce((b, i) => b + i.rollos, 0), 0);
const hechosLibres = p => Math.max(0, r2((p.hechos || 0) - apartadoR(p)));
const hechosEn = (pid, f) => (db.produccion || []).filter(x => x.productoId === pid && x.fecha === f).reduce((a, x) => a + x.rollos, 0);
const hechosMes = (pid, ym) => (db.produccion || []).filter(x => x.productoId === pid && x.fecha.slice(0, 7) === ym).reduce((a, x) => a + x.rollos, 0);
const dispG = p => p.stockG;
const rollosDisp = p => gpr(p) > 0 ? Math.floor(dispG(p) / gpr(p) + 1e-9) : 0;
const bajo = p => dispG(p) <= p.minimoG;
const costoRollo = p => gpr(p) > 0 ? p.costoKilo * gpr(p) / 1000 : 0;
const gananciaRollo = p => p.precio - costoRollo(p);
const gLbl = n => n < 0 ? 'Pérdida' : 'Ganancia';
const gCls = n => n < 0 ? 'neg' : 'pos';
const gHero = n => n < 0 ? 'loss' : n > 0 ? 'gain' : '';
function nombreMes(ym) {
  const [y, m] = ym.split('-').map(Number);
  return new Date(y, m - 1, 1).toLocaleDateString('es-CO', { month: 'long', year: 'numeric' });
}
function nombreDia(f) {
  const [y, m, d] = f.split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'short' });
}
function toast(t) {
  const el = $('#toast'); el.textContent = t; el.classList.add('show');
  clearTimeout(toast.t); toast.t = setTimeout(() => el.classList.remove('show'), 2200);
}
function modal(html) { if (!enHist('m')) hist({ m: 1 }); const m = $('#modal'); m.innerHTML = '<div class="sheet">' + html + '</div>'; m.classList.remove('closing'); m.classList.add('show'); }
function cerrarModal() {
  const m = $('#modal');
  if (!m.classList.contains('show') || m.classList.contains('closing')) return;
  if (enHist('m')) { saltarPop = true; history.back(); }
  cierraModal();
}
function cierraModal() {
  const m = $('#modal');
  m.classList.add('closing');
  setTimeout(() => { if (m.classList.contains('closing')) m.classList.remove('show', 'closing'); }, 220);
}

// ===== Filas de historial =====
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
const ventasDia = f => db.ventas.filter(v => v.fecha === f);
const ventasMes = ym => db.ventas.filter(v => v.fecha.slice(0, 7) === ym);
const suma = (arr, k) => arr.reduce((a, v) => a + v[k], 0);

// ===== Categorías y filtro =====
const catDe = p => p.categoria || 'Sin categoría';
function categorias() {
  return Array.from(new Set(db.productos.map(catDe))).sort((a, b) => a.localeCompare(b, 'es'));
}
function filtrados() {
  const b = fBus.trim().toLowerCase();
  return db.productos
    .filter(p => (fCat === 'Todas' || catDe(p) === fCat) && (!b || p.nombre.toLowerCase().includes(b)))
    .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));
}
function barraFiltro() {
  const cats = ['Todas'].concat(categorias());
  if (!cats.includes(fCat)) fCat = 'Todas';
  return '<input id="bus" type="search" placeholder="Buscar producto…" value="' + esc(fBus) + '" oninput="setBus(this.value)" style="margin-bottom:10px">' +
    '<div class="chips">' + cats.map((c, i) => '<button class="chip ' + (c === fCat ? 'on' : '') + '" onclick="setCat(' + i + ')">' + esc(c) + '</button>').join('') + '</div>';
}
function setCat(i) { fCat = ['Todas'].concat(categorias())[i]; render(); }
function setBus(v) { fBus = v; $('#lista').innerHTML = vista === 'stock' ? listaStock() : listaVender(); }

// ===== Navegación =====
const ic = d => '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">' + d + '</svg>';
const TABS = [
  ['inicio', ic('<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>'), 'Inicio'],
  ['stock', ic('<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>'), 'Stock'],
  ['vender', ic('<circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.6 11.5a1 1 0 0 0 1 .8h9.2a1 1 0 0 0 1-.8L21 7H6"/>'), 'Vender'],
  ['ganancias', ic('<path d="m3 17 6-6 4 4 8-8"/><path d="M15 7h6v6"/>'), 'Ganancias']
];
const ICO = {
  rollos: ic('<path d="M6 5l1.5-2L9 5l1.5-2L12 5l1.5-2L15 5l1.5-2L18 5v14l-1.5 2-1.5-2-1.5 2-1.5-2-1.5 2L9 19l-1.5 2L6 19z"/><path d="M9.5 10h5M10.5 14h3"/>'),
  pedidos: ic('<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4h6v3H9z"/><path d="M9 12h6M9 16h4"/>'),
  usuarios: ic('<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M17 14c2.4 0 4 1.9 4 4.5"/>'),
  respaldo: ic('<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5"/><path d="M4 19h16"/>'),
  salir: ic('<path d="M10 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h5"/><path d="M15 8l4 4-4 4M19 12H9"/>'),
  hora: ic('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
  persona: ic('<circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.9 3.1-7 7-7s7 3.1 7 7"/>'),
  nota: ic('<path d="M6 3h9l4 4v14H6z"/><path d="M9 12h7M9 16h5"/>'),
  alerta: ic('<path d="M12 3 2.5 20h19z"/><path d="M12 10v5M12 17.5v.5"/>'),
  check: ic('<path d="m5 12.5 4.5 4.5L19 7.5"/>'),
  deshacer: ic('<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>'),
  historial: ic('<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/>'),
  venta: TABS[2][1]
};
let vistaPrev = null;
// Los números grandes cuentan hacia arriba al cambiar de pantalla
function animarNumeros(cambio) {
  if (!cambio || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('[data-n]').forEach(el => {
    const fin = Number(el.dataset.n), t0 = performance.now();
    const paso = t => {
      const k = Math.min(1, (t - t0) / 800);
      el.textContent = money(fin * (1 - Math.pow(1 - k, 3)));
      if (k < 1) requestAnimationFrame(paso);
    };
    requestAnimationFrame(paso);
  });
}
const enHist = k => !!(history.state && history.state[k]);
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
  return '<div class="dh"><b>Condimentos la Mano de Dios</b><small>' + (NUBE ? esc(usuarioActual()) + (adm ? ' · administrador' : '') : 'Datos en este teléfono') + '</small></div>' +
    it(ICO.pedidos, 'Pedidos', 'menuPedidos()', pend ? '<em>' + pend + '</em>' : '') +
    it(ICO.historial, 'Historial', 'menuHistorial()') +
    (adm ? it(ICO.usuarios, 'Usuarios' + esp, 'menuModal(abrirUsuarios)') : '') +
    (!NUBE ? it(ICO.respaldo, 'Respaldo', 'menuModal(abrirAjustes)') : '') +
    (NUBE ? it(ICO.salir, 'Cerrar sesión', 'menuSalir()') : '');
}
function menuPedidos() {
  if (vista === 'pedidos') { cerrarMenu(); return; }
  cierraMenu();
  try { history.replaceState({ v: 'pedidos' }, ''); } catch (e) {}
  vista = 'pedidos'; fCat = 'Todas'; fBus = ''; render(); window.scrollTo(0, 0);
}
function menuHistorial() {
  if (vista === 'historial') { cerrarMenu(); return; }
  cierraMenu();
  hf = { tipo: 'todo', per: 'todo', q: '', n: 30 };
  try { history.replaceState({ v: 'historial' }, ''); } catch (e) {}
  vista = 'historial'; fCat = 'Todas'; fBus = ''; render(); window.scrollTo(0, 0);
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
}
function render() {
  if (NUBE && !listo && !cacheActiva) { $('#app').innerHTML = '<div class="empty">Cargando… [v4 ' + paso + ']</div>'; return; }
  $('#fecha').textContent = new Date().toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' });
  $('#nav').innerHTML = TABS.map(t => '<button class="' + (vista === t[0] ? 'on' : '') + '" onclick="ir(\'' + t[0] + '\')"><span>' + t[1] + '</span>' + t[2] + '</button>').join('');
  if (cacheActiva && !listo) $('#fecha').textContent += ' · sincronizando…';
  const v = { inicio: vInicio, stock: vStock, vender: vVender, ganancias: vGanancias, pedidos: vPedidos, historial: vHistorial }[vista];
  const cambio = vista !== vistaPrev; vistaPrev = vista;
  $('#app').innerHTML = '<div class="fade' + (cambio ? '' : ' quiet') + '">' + v() + '</div>';
  const idx = TABS.findIndex(t => t[0] === vista);
  $('#nav').style.setProperty('--i', Math.max(0, idx)); $('#nav').classList.toggle('fuera', idx < 0);
  animarNumeros(cambio);
}

// ===== Inicio =====
function vInicio() {
  const vh = ventasDia(hoy()), vm = ventasMes(hoy().slice(0, 7));
  const bajos = db.productos.filter(p => bajo(p));
  return '<div class="hero ' + gHero(suma(vh, 'ganancia')) + '"><small>' + gLbl(suma(vh, 'ganancia')) + ' de hoy</small><b data-n="' + Math.abs(suma(vh, 'ganancia')) + '">' + money(Math.abs(suma(vh, 'ganancia'))) + '</b><span>' + fmt(suma(vh, 'rollos')) + ' rollos vendidos · ' + money(suma(vh, 'total')) + ' en ventas</span></div>' +
    '<div class="grid">' +
    '<div class="bubble wide"><small>' + gLbl(suma(vm, 'ganancia')) + ' del mes (' + nombreMes(hoy().slice(0, 7)) + ')</small><b class="' + gCls(suma(vm, 'ganancia')) + '" data-n="' + Math.abs(suma(vm, 'ganancia')) + '">' + money(Math.abs(suma(vm, 'ganancia'))) + '</b></div>' +
    '<div class="bubble"><small>Productos</small><b>' + db.productos.length + '</b></div>' +
    '<div class="bubble"><small>Stock bajo</small><b class="' + (bajos.length ? 'neg' : '') + '">' + bajos.length + '</b></div>' +
    '</div>' +
    (bajos.length ? '<h2>Por reponer</h2>' + bajos.map(p => '<div class="item low"><div class="row"><div class="name">' + esc(p.nombre) + '</div><span class="pill low">' + fmtG(dispG(p)) + '<br><small>' + rollosDisp(p).toLocaleString('es-CO') + ' rollos</small></span></div></div>').join('') : '') +
    (!db.productos.length ? '<div class="empty">Empieza creando tu primer producto en Stock</div>' : '');
}

// ===== Stock =====
function vStock() {
  const rec = db.produccion.slice().sort((a, b) => a.fecha < b.fecha ? 1 : a.fecha > b.fecha ? -1 : (a.id < b.id ? 1 : -1)).slice(0, 8);
  const ing = db.entradas.slice().sort((a, b) => a.fecha < b.fecha ? 1 : a.fecha > b.fecha ? -1 : (a.id < b.id ? 1 : -1)).slice(0, 8);
  const hint = '<div class="hint" style="margin:0 0 10px">Toca uno para ver el detalle completo</div>';
  return '<h2>Inventario</h2><button class="add" onclick="formProducto()">＋ Nuevo producto</button>' +
    (db.productos.length ? barraFiltro() + '<div id="lista">' + listaStock() + '</div>' : '<div class="empty">Aún no hay productos</div>') +
    (rec.length ? '<h2 style="margin-top:22px">Últimos rollos hechos</h2>' + hint + agrupaDia(rec, x => x.fecha, x => lineaProd(x)) : '') +
    (ing.length ? '<h2 style="margin-top:22px">Últimos ingresos de materia</h2>' + hint + agrupaDia(ing, x => x.fecha, x => lineaIngreso(x)) : '');
}
const stkAb = {};
function listaStock() {
  const l = filtrados();
  if (!l.length) return '<div class="empty">No hay productos con ese filtro</div>';
  const kv = (k, v) => '<div class="kv"><span>' + k + '</span><b>' + v + '</b></div>';
  return l.map(p => {
    const g = gpr(p), ga = gananciaRollo(p), cr = costoRollo(p), ap = apartadoR(p);
    const mas = kv('Rollos hechos hoy', fmt(hechosEn(p.id, hoy()))) + kv('Rollos hechos este mes', fmt(hechosMes(p.id, hoy().slice(0, 7)))) +
      (g > 0 ? kv('Peso de cada rollo', fmtG(g)) + kv('Unidades por rollo', fmt(p.unidadesRollo)) + kv('Rollos por kilo', fmt(1000 / g)) + kv('Rollos por libra', fmt(500 / g)) + kv('Precio de venta por rollo', money(p.precio)) + kv('Costo por rollo', money(cr)) : kv('Precio de venta por rollo', money(p.precio)));
    return '<div class="item ' + (bajo(p) ? 'low' : '') + '"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div><div class="meta"><span class="tag">' + esc(catDe(p)) + '</span></div></div>' +
      '<span class="pill ' + (bajo(p) ? 'low' : '') + '"><small>En bodega</small>' + fmtG(dispG(p)) + (g > 0 ? '<small>para ' + rollosDisp(p).toLocaleString('es-CO') + ' rollos</small>' : '') + '</span></div>' +
      '<div class="lis"><span>Listos para vender</span><b>' + fmt(p.hechos || 0) + ' rollos' + (ap > 0 ? ' <small>(' + fmt(ap) + ' apartados en pedidos)</small>' : '') + '</b></div>' +
      (g > 0
        ? '<div class="gan ' + gCls(ga) + '"><span>' + gLbl(ga) + ' por rollo</span><b>' + money(Math.abs(ga)) + ' <small>(' + fmt(cr > 0 ? ga / cr * 100 : 0) + ' % sobre el costo)</small></b></div>'
        : '<div class="gan neg"><span>Falta definir los gramos por rollo. Toca Editar.</span></div>') +
      '<details class="mas"' + (stkAb[p.id] ? ' open' : '') + ' ontoggle="stkAb[\'' + p.id + '\']=this.open"><summary>Ver más datos</summary>' + mas + '</details>' +
      '<div class="actions"><button class="btn main" onclick="formIngreso(\'' + p.id + '\')">＋ Ingresar kilos/libras</button><button class="btn main" onclick="formProduccion(\'' + p.id + '\')">' + ICO.rollos + ' Rollos hechos</button><button class="btn" onclick="formProducto(\'' + p.id + '\')">Editar</button><button class="btn del" onclick="borrarProducto(\'' + p.id + '\')">Borrar</button></div></div>';
  }).join('');
}

function opcionesCat(sel) {
  const lista = ['Aliños', 'Salsas', 'Otro'];
  if (sel && !lista.includes(sel)) lista.splice(2, 0, sel);
  return lista.map(c => '<option value="' + esc(c) + '"' + (c === sel ? ' selected' : '') + '>' + esc(c) + '</option>').join('');
}
function formProducto(id) {
  if (espera()) return;
  const p = id ? prod(id) : { nombre: '', categoria: '', unidadesRollo: 14, gramosPorRollo: '', precio: 2000, costoKilo: '', minimoG: 500, stockG: 0 };
  modal('<h3>' + (id ? 'Editar producto' : 'Nuevo producto') + '</h3>' +
    '<label>Nombre</label><input id="f-nombre" value="' + esc(p.nombre) + '" placeholder="Ej: Clavitos">' +
    '<label>Categoría</label><select id="f-cat">' + opcionesCat(p.categoria || (id ? 'Otro' : 'Aliños')) + '</select>' +
    '<label>Unidades por rollo</label><input id="f-unid" type="number" inputmode="decimal" value="' + p.unidadesRollo + '">' +
    '<label>Gramos que pesa 1 rollo</label><input id="f-gpr" type="number" inputmode="decimal" value="' + p.gramosPorRollo + '" placeholder="Ej: 33" oninput="hintGr();desdePrecio()"><div class="hint" id="f-hint"></div>' +
    '<label>Precio de venta por rollo ($)</label><input id="f-precio" type="number" inputmode="decimal" value="' + p.precio + '" oninput="desdePrecio()">' +
    '<label>Costo por kilo ($)</label><input id="f-costo" type="number" inputmode="decimal" value="' + p.costoKilo + '" placeholder="Lo que pagas por 1 kilo" oninput="desdePrecio()">' +
    '<label>% de ganancia sobre el costo</label><input id="f-pct" type="number" inputmode="decimal" placeholder="Ej: 40" oninput="desdePct()"><div class="hint" id="f-pcthint"></div>' +
    '<label>Avisar cuando queden (gramos)</label><input id="f-min" type="number" inputmode="decimal" value="' + p.minimoG + '">' +
    '<label>' + (id ? 'Stock actual' : 'Stock inicial') + ' (gramos)</label><input id="f-stock" type="number" inputmode="decimal" value="' + (p.stockG || 0) + '">' +
    '<button class="btn main full" onclick="guardarProducto(\'' + (id || '') + '\')">Guardar</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
  hintGr(); desdePrecio();
}
const costoForm = () => num($('#f-costo').value) * num($('#f-gpr').value) / 1000;
function desdePct() {
  const c = costoForm(), t = $('#f-pct').value;
  if (c > 0 && t !== '') $('#f-precio').value = Math.round(c * (1 + num(t) / 100) / 50) * 50;
  infoPct();
}
function desdePrecio() {
  const c = costoForm(), pr = num($('#f-precio').value);
  $('#f-pct').value = c > 0 ? Math.round((pr - c) / c * 1000) / 10 : '';
  infoPct();
}
function infoPct() {
  const c = costoForm(), pr = num($('#f-precio').value);
  $('#f-pcthint').textContent = c > 0 ? 'Te cuesta ' + money(c) + ' por rollo · con este precio ganas ' + money(pr - c) + ' por rollo (precio redondeado a $50)' : 'Escribe el costo por kilo y los gramos por rollo para calcular.';
}
function hintGr() {
  const g = num($('#f-gpr').value);
  $('#f-hint').textContent = g > 0 ? '1 kilo ≈ ' + fmt(1000 / g) + ' rollos · 1 libra (500 g) ≈ ' + fmt(500 / g) + ' rollos' : 'Pesa un rollo y escribe cuántos gramos tiene. Así sabes cuántos rollos salen por kilo.';
}
function guardarProducto(id) {
  const nombre = $('#f-nombre').value.trim();
  if (!nombre) return toast('Escribe el nombre');
  const d = { nombre, categoria: $('#f-cat').value.trim(), unidadesRollo: num($('#f-unid').value) || 1, gramosPorRollo: num($('#f-gpr').value), precio: num($('#f-precio').value), costoKilo: num($('#f-costo').value), minimoG: num($('#f-min').value), stockG: r2(num($('#f-stock').value)) };
  if (id) {
    const o = Object.assign({}, prod(id)), CP = [['nombre', 'Nombre', x => x], ['categoria', 'Categoría', x => x || 'Sin categoría'], ['unidadesRollo', 'Unidades por rollo', fmt], ['gramosPorRollo', 'Gramos por rollo', fmtG], ['precio', 'Precio de venta', money], ['costoKilo', 'Costo por kilo', money], ['minimoG', 'Mínimo en bodega', fmtG], ['stockG', 'Gramos en bodega', fmtG]];
    const cb = CP.filter(c => (o[c[0]] || 0) !== (d[c[0]] || 0)).map(c => c[1] + ': ' + c[2](o[c[0]] || 0) + ' → ' + c[2](d[c[0]] || 0));
    Object.assign(prod(id), d);
    if (cb.length) anotar('producto_editado', 'Editó el producto ' + nombre, cb);
  } else {
    db.productos.push(Object.assign({ id: uid(), stockG: num($('#f-stock').value) }, d));
    anotar('producto_nuevo', 'Creó el producto ' + nombre);
  }
  guardar(); cerrarModal(); render(); toast('Producto guardado');
}
function borrarProducto(id) {
  if (espera()) return;
  const pp = prod(id); if (pp && apartadoR(pp) > 0) return toast('Tiene pedidos pendientes: entrégalos o cancélalos primero');
  if (!confirm('¿Borrar este producto? Sus ventas ya registradas se conservan.')) return;
  anotar('producto_borrado', 'Borró el producto ' + (pp ? pp.nombre : ''));
  db.productos = db.productos.filter(p => p.id !== id);
  guardar(); render();
}

// ===== Ingreso por kilos / libras =====
const gUni = () => { const u = $('#i-uni').value; return u === 'lb' ? 500 : u === 'g' ? 1 : 1000; };
const gCosto = () => $('#i-uni').value === 'lb' ? 500 : 1000;
function formIngreso(id) {
  if (espera()) return;
  const p = prod(id);
  modal('<h3>Ingresar ' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Se suma al stock en gramos. Puedes cambiar estos datos en cada ingreso</div>' +
    '<label>Unidad</label><select id="i-uni" onchange="cambiarUnidad(\'' + id + '\')"><option value="kg">Kilos (1 kilo = 1000 g)</option><option value="lb">Libras (1 libra = 500 g)</option><option value="g">Gramos</option></select>' +
    '<label>Cantidad que llegó</label><input id="i-cant" type="number" inputmode="decimal" placeholder="Ej: 1" oninput="prevIngreso(\'' + id + '\')">' +
    '<label>Gramos que pesa 1 rollo</label><input id="i-gpr" type="number" inputmode="decimal" value="' + (gpr(p) || '') + '" placeholder="Ej: 33" oninput="prevIngreso(\'' + id + '\')">' +
    '<label id="i-lblc">Costo por kilo ($)</label><input id="i-costo" type="number" inputmode="decimal" value="' + p.costoKilo + '">' +
    '<div class="preview" id="i-prev"></div>' +
    '<button class="btn main full" onclick="confirmarIngreso(\'' + id + '\')">Agregar al stock</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
  prevIngreso(id);
}
function cambiarUnidad(id) {
  const p = prod(id), u = $('#i-uni').value, b = gCosto();
  $('#i-lblc').textContent = 'Costo por ' + (b === 500 ? 'libra' : 'kilo') + ' ($)';
  $('#i-costo').value = p.costoKilo ? r2(p.costoKilo * b / 1000) : '';
  $('#i-cant').placeholder = u === 'g' ? 'Ej: 1000' : 'Ej: 1';
  prevIngreso(id);
}
function prevIngreso(id) {
  const p = prod(id), g = num($('#i-cant').value) * gUni(), gp = num($('#i-gpr').value);
  $('#i-prev').textContent = '= ' + fmt(g) + ' g' + (gp > 0 ? ' · ≈ ' + fmt(Math.floor(g / gp)) + ' rollos' : '') + ' · stock queda en ' + fmtG(dispG(p) + g);
}
function confirmarIngreso(id) {
  const p = prod(id), cant = num($('#i-cant').value), gp = num($('#i-gpr').value);
  if (cant <= 0) return toast('Escribe la cantidad');
  if (gp <= 0) return toast('Escribe cuántos gramos pesa 1 rollo');
  const g = r2(cant * gUni()), costoKilo = num($('#i-costo').value) * 1000 / gCosto();
  if (g >= 100000 && !confirm('¿Seguro? Vas a ingresar ' + fmt(g) + ' g (' + fmt(g / 1000) + ' kilos).')) return;
  p.stockG = r2(p.stockG + g); p.costoKilo = r2(costoKilo); p.gramosPorRollo = gp;
  db.entradas.push({ id: uid(), fecha: hoy(), productoId: id, nombre: p.nombre, hora: ahora(), por: quien(), cantidad: cant, unidad: $('#i-uni').value, gramos: g, costoKilo: p.costoKilo, gramosRollo: gp, stockDespuesG: p.stockG });
  guardar(); cerrarModal(); render(); toast('+' + fmt(g) + ' g');
}

// ===== Rollos hechos (producción) =====
function formProduccion(id) {
  if (espera()) return;
  const p = prod(id);
  if (!(gpr(p) > 0)) return toast('Primero define los gramos por rollo (Editar)');
  modal('<h3>Rollos hechos · ' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Descuenta los gramos del stock y suma rollos listos para vender. Si salen más rollos de los que daba el stock, igual los puedes registrar.</div>' +
    '<label>¿Cuántos rollos hiciste?</label><input id="h-cant" type="number" inputmode="decimal" placeholder="Ej: 20" oninput="prevProd(\'' + id + '\')">' +
    '<label>Día en que los hiciste</label><input id="h-fec" type="date" value="' + hoy() + '" max="' + hoy() + '">' +
    '<div class="preview" id="h-prev"></div>' +
    '<button class="btn main full" onclick="confirmarProd(\'' + id + '\')">Registrar rollos hechos</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
  prevProd(id);
}
function prevProd(id) {
  const p = prod(id), q = num($('#h-cant').value), resto = p.stockG - q * gpr(p), el = $('#h-prev');
  if (q > 0 && resto < -1e-6) {
    el.classList.add('warn');
    el.innerHTML = '' + ICO.alerta + ' Salieron más de lo calculado<small>Con el stock alcanzaba para ' + rollosDisp(p) + ' rollos y estás registrando ' + fmt(q) + ' (' + fmt(r2(q - rollosDisp(p))) + ' de más, ≈ ' + fmtG(-resto) + ' que no estaban en el stock). El stock queda en 0 g.</small>';
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
  toast(exc > 0 ? '+' + fmt(q) + ' rollos · salieron ' + fmt(excR) + ' más de lo calculado' : '+' + fmt(q) + ' rollos hechos');
}
function borrarProduccion(id) {
  if (espera()) return;
  const x = db.produccion.find(y => y.id === id); if (!x) return;
  const p = prod(x.productoId);
  if (p && (p.hechos || 0) < x.rollos - 1e-6) return toast('Esos rollos ya se vendieron; no se puede deshacer');
  if (!confirm('¿Deshacer esta producción? Los gramos vuelven al stock.')) return;
  if (p) { p.stockG = r2(p.stockG + x.gramos - (x.excesoG || 0)); p.hechos = r2((p.hechos || 0) - x.rollos); }
  anotar('rollos_deshechos', 'Deshizo ' + fmt(x.rollos) + ' rollos hechos de ' + x.nombre);
  db.produccion = db.produccion.filter(y => y.id !== id);
  guardar(); render();
}
function lineaProd(x, vol) {
  return hfila({ t: esc(x.nombre) + (x.excesoG > 0 ? ' <span class="tag warn">Salieron de más</span>' : ''), s: 'Rollos hechos' + (x.hora ? ' · ' + fmtHora(x.hora) : ''), r: '+' + fmt(x.rollos), rs: 'rollos', on: "detalleProd('" + x.id + "'" + (vol ? ",'" + vol + "'" : '') + ")" });
}
function lineaIngreso(x) {
  return hfila({ t: esc(x.nombre), s: 'Ingreso de materia' + (x.hora ? ' · ' + fmtHora(x.hora) : ''), r: '+' + fmt(x.cantidad) + ' ' + (x.unidad || 'kg'), on: "detalleIngreso('" + x.id + "')" });
}
function detalleProd(id, vol) {
  const x = db.produccion.find(y => y.id === id); if (!x) return;
  const p = prod(x.productoId), exc = x.excesoG || 0, und = p && p.unidadesRollo ? r2(x.rollos * p.unidadesRollo) : null;
  const gr = x.gramosRollo || (x.rollos ? r2(x.gramos / x.rollos) : 0);
  modal('<h3>' + esc(x.nombre) + '</h3><div class="sub" style="margin:2px 0 4px">Rollos hechos' + (exc > 0 ? ' · ' + ICO.alerta + ' salieron más de lo calculado' : '') + '</div>' +
    '<div class="dsec">Producción</div>' +
    filaD('Rollos hechos', fmt(x.rollos)) + filaD('Unidades', und != null ? fmt(und) : '') +
    filaD('Día en que se hicieron', diaLargo(x.fecha), 1) +
    filaD('Registrado el', x.reg ? diaLargo(x.reg) : '', 1) +
    filaD('Hora del registro', x.hora ? fmtHora(x.hora) : 'No se registró (registro antiguo)') +
    filaD('Registrado por', x.por ? esc(x.por) : '') +
    '<div class="dsec">Materia</div>' +
    filaD('Gramos por rollo', gr ? fmtG(gr) : '') + filaD('Materia usada', fmtG(x.gramos)) +
    (x.quedaronG != null ? filaD('Quedó en el stock', fmtG(x.quedaronG)) : '') +
    (exc > 0 ? '<div class="dsec warn">' + ICO.alerta + ' Salieron más de lo calculado</div>' + filaD('El stock alcanzaba para', fmt(x.alcanzaba || 0) + ' rollos') + filaD('Salieron de más', fmt(x.excesoR || 0) + ' rollos') + filaD('Materia que no estaba en el stock', fmtG(exc)) : '') +
    '<button class="btn del full" onclick="' + dsp('borrarProduccion', x.id) + '">Deshacer rollos hechos</button>' +
    btnVolver('detalleDiaProd', vol));
}
function detalleIngreso(id) {
  const x = db.entradas.find(y => y.id === id); if (!x) return;
  const u = { kg: 'kilos', lb: 'libras', g: 'gramos' }[x.unidad] || '', p = prod(x.productoId);
  const costo = x.costoKilo ? x.gramos / 1000 * x.costoKilo : 0, gr = x.gramosRollo || (p ? gpr(p) : 0);
  modal('<h3>' + esc(x.nombre) + '</h3><div class="sub" style="margin:2px 0 4px">Ingreso de materia</div>' +
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

// ===== Vender =====
function vVender() {
  if (!db.productos.length) return '<div class="empty">Primero crea un producto en Stock</div>';
  const hoyV = ventasDia(hoy());
  return '<h2>¿Qué vendiste?</h2>' + barraFiltro() + '<div id="lista">' + listaVender() + '</div>' +
    '<h2 style="margin-top:22px">Ventas de hoy</h2>' +
    (hoyV.length ? '<div class="hint" style="margin:0 0 10px">Toca una venta para ver el detalle o deshacerla</div><div class="hcard">' + hoyV.slice().reverse().map(v => lineaVenta(v)).join('') + '</div>' : '<div class="empty">Sin ventas hoy</div>');
}
function lineaVenta(v, vol) {
  return hfila({ t: esc(v.nombre) + (v.pedidoId ? ' <span class="tag">Pedido</span>' : ''), s: fmt(v.rollos) + ' rollos' + (v.cliente ? ' · ' + esc(v.cliente) : '') + (v.hora ? ' · ' + fmtHora(v.hora) : ''), r: money(v.total), on: "detalleVenta('" + v.id + "'" + (vol ? ",'" + vol + "'" : '') + ")" });
}
function listaVender() {
  const l = filtrados();
  if (!l.length) return '<div class="empty">No hay productos con ese filtro</div>';
  return l.map(p => '<div class="item tap" onclick="formVenta(\'' + p.id + '\')"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div><div class="meta"><span class="tag">' + esc(catDe(p)) + '</span> ' + money(p.precio) + ' c/u</div></div><span class="pill ' + (hechosLibres(p) <= 0 ? 'low' : '') + '">' + fmt(hechosLibres(p)) + '<br><small>rollos hechos</small></span></div></div>').join('');
}
function formVenta(id) {
  if (espera()) return;
  const p = prod(id);
  modal('<h3>' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Rollos hechos para vender: ' + fmt(hechosLibres(p)) + (apartadoR(p) > 0 ? ' (' + fmt(apartadoR(p)) + ' apartados en pedidos)' : '') + ' · ' + money(p.precio) + ' c/u</div>' +
    '<label>Rollos</label><div class="step"><button onclick="ajustarQty(-1,\'' + id + '\')">−</button><input id="v-qty" type="number" inputmode="decimal" value="1" oninput="calcVenta(\'' + id + '\')"><button onclick="ajustarQty(1,\'' + id + '\')">+</button></div>' +
    '<label>Cliente (opcional)</label><input id="v-cli" placeholder="¿A quién se lo vendes?">' +
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
  const cli = ($('#v-cli').value || '').trim();
  p.hechos = r2((p.hechos || 0) - q);
  db.ventas.push({ id: uid(), fecha: hoy(), hora: ahora(), por: quien(), cliente: cli, productoId: p.id, nombre: p.nombre, categoria: catDe(p), rollos: q, unidades: r2(q * (p.unidadesRollo || 0)), gramos: 0, modo: 'hechos', precio: p.precio, costo, total: q * p.precio, ganancia: q * (p.precio - costo), quedaron: p.hechos });
  guardar(); cerrarModal(); render(); toast('Venta registrada'); if (navigator.vibrate) navigator.vibrate(15);
}
function borrarVenta(id) {
  if (espera()) return;
  const v = db.ventas.find(x => x.id === id);
  if (v && v.pedidoId) return toast('Viene de un pedido: deshaz la entrega en Pedidos');
  if (!v || !confirm('¿Deshacer esta venta? Los rollos vuelven al stock.')) return;
  const p = prod(v.productoId);
  if (p) { if (v.modo === 'hechos') p.hechos = r2((p.hechos || 0) + v.rollos); else p.stockG = r2(p.stockG + (v.gramos != null ? v.gramos : v.rollos * gpr(p))); }
  anotar('venta_deshecha', 'Deshizo la venta de ' + fmt(v.rollos) + ' rollos de ' + v.nombre + ' (' + money(v.total) + ')' + (v.cliente ? ' a ' + v.cliente : ''));
  db.ventas = db.ventas.filter(x => x.id !== id);
  guardar(); render();
}

// ===== Pedidos =====
let pedFiltro = 'pendiente', ped = null;
const pendPed = () => (db.pedidos || []).filter(x => x.estado === 'pendiente');
function setPedFiltro(f) { pedFiltro = f; render(); }
function vPedidos() {
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
function cardPedido(x) {
  const its = itemsDe(x), total = its.reduce((a, i) => a + i.rollos * i.precio, 0), pen = x.estado === 'pendiente';
  const hecho = 'Pedido hecho: ' + (x.fecha ? nombreDia(x.fecha) : '—') + (x.hora ? ' · ' + fmtHora(x.hora) : '');
  return '<div class="item"><div class="row"><div class="tap" onclick="detallePedido(\'' + x.id + '\')"><div class="name">' + esc(x.cliente || 'Sin nombre') + '</div><div class="meta">' +
    (pen ? (x.entrega ? 'Entrega: ' + nombreDia(x.entrega) : 'Sin fecha de entrega') : 'Entregado: ' + nombreDia(x.entregadoEn) + (x.entregadoHora ? ' · ' + ICO.hora + ' ' + fmtHora(x.entregadoHora) : '')) + '<br>' + hecho + '<br>' +
    its.map(i => fmt(i.rollos) + ' × ' + esc(i.nombre)).join(' · ') + (x.nota ? '<br>' + ICO.nota + ' ' + esc(x.nota) : '') + '</div></div>' +
    '<span class="pill">' + money(total) + '</span></div>' +
    '<div class="actions"><button class="btn" onclick="detallePedido(\'' + x.id + '\')">Ver detalle</button>' + (pen
      ? '<button class="btn main" onclick="entregarPedido(\'' + x.id + '\')">' + ICO.check + ' Entregar</button><button class="btn del" onclick="cancelarPedido(\'' + x.id + '\')">Cancelar pedido</button>'
      : '<button class="btn" onclick="deshacerEntrega(\'' + x.id + '\')">Deshacer entrega</button>') + '</div></div>';
}
function formPedido() {
  if (espera()) return;
  if (!db.productos.length) return toast('Primero crea un producto en Stock');
  ped = { items: [] };
  const ops = db.productos.slice().sort((a, b) => a.nombre.localeCompare(b.nombre, 'es')).map(p => '<option value="' + p.id + '">' + esc(p.nombre) + ' (' + fmt(hechosLibres(p)) + ' hechos libres)</option>').join('');
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
  const ex = ped.items.find(i => i.productoId === p.id);
  if (ex) ex.rollos = r2(ex.rollos + q);
  else ped.items.push({ productoId: p.id, nombre: p.nombre, rollos: q, gramos: 0, precio: p.precio });
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
  db.pedidos.push({ id: uid(), fecha: hoy(), hora: ahora(), por: quien(), cliente, entrega: $('#p-fec').value || '', nota: $('#p-nota').value.trim(), estado: 'pendiente', items: ped.items });
  ped = null; pedFiltro = 'pendiente';
  guardar(); cerrarModal(); render(); toast('Pedido guardado, producto apartado');
}
function entregarPedido(id) {
  if (espera()) return;
  const x = db.pedidos.find(y => y.id === id); if (!x || x.estado !== 'pendiente') return;
  const its = itemsDe(x);
  for (const i of its) {
    const p = prod(i.productoId);
    if (!p) return toast(i.nombre + ' ya no existe en el stock');
    if (i.rollos > (p.hechos || 0) + 1e-6) return toast('Faltan rollos hechos de ' + p.nombre + ': tienes ' + fmt(p.hechos || 0) + ' y el pedido pide ' + fmt(i.rollos));
  }
  if (!confirm('¿Entregar el pedido de ' + x.cliente + '? Se registra como venta de hoy.')) return;
  const hr = ahora(), por = quien();
  its.forEach(i => {
    const p = prod(i.productoId), costo = costoRollo(p);
    p.hechos = r2((p.hechos || 0) - i.rollos);
    db.ventas.push({ id: uid(), fecha: hoy(), hora: hr, por, cliente: x.cliente || '', productoId: p.id, nombre: p.nombre, categoria: catDe(p), rollos: i.rollos, unidades: r2(i.rollos * (p.unidadesRollo || 0)), gramos: 0, modo: 'hechos', precio: i.precio, costo, total: i.rollos * i.precio, ganancia: i.rollos * (i.precio - costo), quedaron: p.hechos, pedidoId: x.id });
  });
  x.estado = 'entregado'; x.entregadoEn = hoy(); x.entregadoHora = hr; x.entregadoPor = por;
  guardar(); render(); toast('Entregado y registrado como venta'); if (navigator.vibrate) navigator.vibrate(15);
}
function cancelarPedido(id) {
  if (espera()) return;
  if (!confirm('¿Cancelar este pedido? El producto apartado vuelve a estar disponible.')) return;
  const pc = db.pedidos.find(x => x.id === id);
  if (pc) anotar('pedido_cancelado', 'Canceló el pedido de ' + (pc.cliente || 'Sin nombre') + ' (' + money(itemsDe(pc).reduce((a, i) => a + i.rollos * i.precio, 0)) + ')');
  db.pedidos = db.pedidos.filter(x => x.id !== id);
  guardar(); render();
}
function deshacerEntrega(id) {
  if (espera()) return;
  const x = db.pedidos.find(y => y.id === id); if (!x) return;
  if (!confirm('¿Deshacer la entrega? Se borran sus ventas y el pedido vuelve a por entregar.')) return;
  db.ventas.filter(v => v.pedidoId === id).forEach(v => {
    const p = prod(v.productoId); if (!p) return;
    if (v.modo === 'hechos') p.hechos = r2((p.hechos || 0) + v.rollos); else p.stockG = r2(p.stockG + (v.gramos || 0));
  });
  db.ventas = db.ventas.filter(v => v.pedidoId !== id);
  x.estado = 'pendiente'; delete x.entregadoEn; delete x.entregadoHora; delete x.entregadoPor;
  anotar('entrega_deshecha', 'Deshizo la entrega del pedido de ' + (x.cliente || 'Sin nombre'));
  guardar(); render();
}

function detalleVenta(id, vol) {
  const v = db.ventas.find(x => x.id === id); if (!v) return;
  const x = v.pedidoId ? db.pedidos.find(y => y.id === v.pedidoId) : null, p = prod(v.productoId);
  const cli = v.cliente || (x && x.cliente) || '';
  const und = v.unidades != null ? v.unidades : (p && p.unidadesRollo ? r2(v.rollos * p.unidadesRollo) : null);
  const gr = v.rollos ? v.ganancia / v.rollos : 0;
  modal('<h3>' + esc(v.nombre) + '</h3><div class="sub" style="margin:2px 0 4px">' + (x ? 'Venta por pedido' : 'Venta directa') + '</div>' +
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
    (!x && v.fecha === hoy() ? '<button class="btn del full" onclick="' + dsp('borrarVenta', v.id) + '">Deshacer venta</button>' : '') +
    btnVolver('detalleDia', vol));
}
function detalleDia(f) {
  const vs = ventasDia(f).slice().reverse(), g = suma(vs, 'ganancia');
  modal('<h3 class="cap">' + diaLargo(f) + '</h3><div class="sub" style="margin:2px 0 10px">' + vs.length + (vs.length === 1 ? ' venta' : ' ventas') + ' · ' + fmt(suma(vs, 'rollos')) + ' rollos · ' + money(suma(vs, 'total')) + ' vendido · ' + gLbl(g).toLowerCase() + ' ' + money(Math.abs(g)) + '</div>' +
    (vs.length ? '<div class="hint" style="margin:0 0 10px">Toca una venta para ver el detalle</div>' + '<div class="hcard">' + vs.map(v => lineaVenta(v, f)).join('') + '</div>' : '<div class="empty">Sin ventas ese día</div>') +
    '<button class="btn full" onclick="cerrarModal()">Cerrar</button>');
}
function detalleDiaProd(f) {
  const l = db.produccion.filter(x => x.fecha === f).slice().reverse();
  modal('<h3 class="cap">' + diaLargo(f) + '</h3><div class="sub" style="margin:2px 0 10px">' + fmt(suma(l, 'rollos')) + ' rollos hechos · ' + l.length + (l.length === 1 ? ' registro' : ' registros') + '</div>' +
    (l.length ? '<div class="hint" style="margin:0 0 10px">Toca uno para ver el detalle</div>' + '<div class="hcard">' + l.map(x => lineaProd(x, f)).join('') + '</div>' : '<div class="empty">Sin rollos hechos ese día</div>') +
    '<button class="btn full" onclick="cerrarModal()">Cerrar</button>');
}
function detallePedido(id) {
  const x = db.pedidos.find(y => y.id === id); if (!x) return;
  const its = itemsDe(x), total = its.reduce((a, i) => a + i.rollos * i.precio, 0), ent = x.estado === 'entregado';
  const vs = db.ventas.filter(v => v.pedidoId === id), dias = f => { const a = f.split('-').map(Number); return Math.round(Date.UTC(a[0], a[1] - 1, a[2]) / 864e5); };
  let punt = '';
  if (ent && x.entrega && x.entregadoEn) { const d = dias(x.entregadoEn) - dias(x.entrega); punt = d === 0 ? 'A tiempo (el día prometido)' : d < 0 ? 'Adelantado ' + (-d) + (d === -1 ? ' día' : ' días') : 'Tarde ' + d + (d === 1 ? ' día' : ' días'); }
  modal('<h3>' + esc(x.cliente || 'Sin nombre') + '</h3><div class="sub" style="margin:2px 0 4px">' + (ent ? 'Pedido entregado' : 'Pedido por entregar') + '</div>' +
    '<div class="dsec">Pedido</div>' +
    filaD('Pedido hecho el', diaLargo(x.fecha), 1) + filaD('Hora del pedido', x.hora ? fmtHora(x.hora) : 'No se registró (pedido antiguo)') +
    filaD('Anotado por', x.por ? esc(x.por) : '') + filaD('Entrega prometida', x.entrega ? diaLargo(x.entrega) : 'Sin fecha', 1) +
    (ent ? '<div class="dsec">Entrega</div>' + filaD('Entregado el', diaLargo(x.entregadoEn), 1) + filaD('Hora de la entrega', x.entregadoHora ? fmtHora(x.entregadoHora) : 'No se registró (entrega antigua)') + filaD('Entregado por', x.entregadoPor ? esc(x.entregadoPor) : '') + filaD('Puntualidad', punt) : '') +
    '<div class="dsec">Productos</div>' + its.map(i => filaD(fmt(i.rollos) + ' × ' + esc(i.nombre), money(i.rollos * i.precio))).join('') +
    filaD('Total del pedido', money(total)) + (ent && vs.length ? filaD(gLbl(suma(vs, 'ganancia')) + ' del pedido', money(suma(vs, 'ganancia'))) : '') +
    (x.nota ? '<div class="dsec">Nota</div><div class="sub" style="margin:4px 0">' + esc(x.nota) + '</div>' : '') +
    (ent ? '<button class="btn del full" onclick="' + dsp('deshacerEntrega', x.id) + '">Deshacer entrega</button>' : '<button class="btn main full" onclick="' + dsp('entregarPedido', x.id) + '">Entregar pedido</button><button class="btn del full" onclick="' + dsp('cancelarPedido', x.id) + '">Cancelar pedido</button>') +
    '<button class="btn full" onclick="cerrarModal()">Cerrar</button>');
}

// ===== Historial =====
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
function cambiarMes(d) {
  const [y, m] = mesSel.split('-').map(Number), n = new Date(y, m - 1 + d, 1);
  mesSel = n.getFullYear() + '-' + p2(n.getMonth() + 1); render();
}
function resumenMes(ym) {
  const pr = db.produccion.filter(x => x.fecha.slice(0, 7) === ym), en = db.entradas.filter(x => x.fecha.slice(0, 7) === ym);
  const porProd = {}, dias = {}, P = x => (porProd[x.productoId] = porProd[x.productoId] || { n: x.nombre, h: 0, g: 0 });
  pr.forEach(x => { P(x).h += x.rollos; dias[x.fecha] = dias[x.fecha] || {}; dias[x.fecha][x.nombre] = (dias[x.fecha][x.nombre] || 0) + x.rollos; });
  en.forEach(x => { P(x).g += x.gramos; });
  const lista = Object.values(porProd).sort((a, b) => a.n.localeCompare(b.n, 'es'));
  return '<div class="grid"><div class="bubble"><small>Rollos hechos</small><b>' + fmt(suma(pr, 'rollos')) + '</b></div><div class="bubble"><small>Materia ingresada</small><b>' + fmt(suma(en, 'gramos') / 1000) + ' kg</b></div></div>' +
    '<div class="sub" style="margin:0 0 6px">Cada mes empieza de cero; lo que queda en stock pasa al mes siguiente.</div>' +
    '<h2>Producción y materia del mes</h2>' + (lista.length ? lista.map(x => '<div class="item"><div class="row"><div><div class="name">' + esc(x.n) + '</div><div class="meta">Hizo ' + fmt(x.h) + ' rollos · ingresó ' + fmtG(x.g) + '</div></div></div></div>').join('') : '<div class="empty">Sin producción ni ingresos este mes</div>') +
    '<h2>Rollos hechos por día</h2><div class="hint" style="margin:0 0 10px">Toca un día para ver el detalle</div>' + (Object.keys(dias).length ? '<div class="hcard">' + Object.keys(dias).sort().reverse().map(f => hfila({ t: '<span class="cap">' + nombreDia(f) + '</span>', s: Object.keys(dias[f]).map(n => fmt(dias[f][n]) + ' × ' + esc(n)).join(' · '), r: '+' + fmt(Object.values(dias[f]).reduce((a, b) => a + b, 0)), rs: 'rollos', on: "detalleDiaProd('" + f + "')" })).join('') + '</div>' : '<div class="empty">Sin rollos hechos este mes</div>');
}
function vGanancias() {
  const vm = ventasMes(mesSel), dias = {}, prods = {};
  vm.forEach(v => {
    (dias[v.fecha] = dias[v.fecha] || { r: 0, t: 0, g: 0 });
    dias[v.fecha].r += v.rollos; dias[v.fecha].t += v.total; dias[v.fecha].g += v.ganancia;
    const k = v.productoId || v.nombre;
    (prods[k] = prods[k] || { n: v.nombre, r: 0, t: 0, g: 0 });
    prods[k].r += v.rollos; prods[k].t += v.total; prods[k].g += v.ganancia;
  });
  const lista = Object.values(prods).sort((a, b) => b.g - a.g);
  const g = suma(vm, 'ganancia');
  return '<div class="month"><button onclick="cambiarMes(-1)">‹</button><b>' + nombreMes(mesSel) + '</b><button onclick="cambiarMes(1)">›</button></div>' +
    '<div class="hero ' + gHero(g) + '"><small>' + gLbl(g) + ' total del mes (todos los productos)</small><b data-n="' + Math.abs(g) + '">' + money(Math.abs(g)) + '</b><span>' + money(suma(vm, 'total')) + ' vendido · ' + fmt(suma(vm, 'rollos')) + ' rollos</span></div>' +
    resumenMes(mesSel) +
    '<h2>Ganancia por producto</h2>' +
    (lista.length ? lista.map(x => '<div class="item"><div class="row"><div><div class="name">' + esc(x.n) + '</div><div class="meta">' + fmt(x.r) + ' rollos · ' + money(x.t) + ' vendido</div></div><span class="pill ' + (x.g < 0 ? 'low' : '') + '">' + money(x.g) + '</span></div></div>').join('') +
      '<div class="item" style="border-color:var(--ac)"><div class="row"><div class="name">Total de todos los productos</div><span class="pill ' + (g < 0 ? 'low' : '') + '">' + money(g) + '</span></div></div>' : '<div class="empty">Sin ventas este mes</div>') +
    '<h2 style="margin-top:22px">Día por día</h2><div class="hint" style="margin:0 0 10px">Toca un día para ver cada venta, a quién y a qué hora</div>' +
    (Object.keys(dias).length ? '<div class="hcard">' + Object.keys(dias).sort().reverse().map(f => hfila({ t: '<span class="cap">' + nombreDia(f) + '</span>', s: fmt(dias[f].r) + ' rollos · ' + money(dias[f].t) + ' vendido', r: money(dias[f].g), rs: dias[f].g < 0 ? 'pérdida' : 'ganancia', rc: dias[f].g < 0 ? 'neg' : 'pos', on: "detalleDia('" + f + "')" })).join('') + '</div>' : '<div class="empty">Sin ventas este mes</div>');
}

// ===== Ajustes / respaldo =====
function abrirAjustes() {
  if (!NUBE) {
    modal('<h3>Respaldo</h3><div class="sub" style="margin:2px 0 10px">Los datos viven en este teléfono. Guarda una copia de vez en cuando.</div>' +
      '<button class="btn main full" onclick="exportar()">' + ICO.respaldo + ' Descargar copia</button>' +
      '<label>Restaurar copia</label><input type="file" accept=".json" onchange="importar(this)">' +
      '<button class="btn full" style="margin-top:14px" onclick="cerrarModal()">Cerrar</button>');
    return;
  }
  const adm = miPerfil && miPerfil.admin;
  modal('<h3>Ajustes</h3><div class="sub" style="margin:2px 0 10px">Sesión: ' + esc(usuarioActual()) + (adm ? ' · administrador' : '') + '<br>Tus datos se guardan en la nube automáticamente.</div>' +
    (adm ? '<button class="btn main full" onclick="abrirUsuarios()">' + ICO.usuarios + ' Usuarios' + (pendientes() ? ' (' + pendientes() + ' en espera)' : '') + '</button>' : '') +
    '<button class="btn del full" style="margin-top:14px" onclick="salir()">Cerrar sesión</button>' +
    '<button class="btn full" style="margin-top:14px" onclick="cerrarModal()">Cerrar</button>');
}
function exportar() {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(db)], { type: 'application/json' }));
  a.download = 'respaldo-rollos-' + hoy() + '.json'; a.click();
}
function importar(inp) {
  const f = inp.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = () => {
    try {
      const d = JSON.parse(r.result);
      if (!d.productos || !d.ventas) throw 0;
      if (!confirm('Esto reemplaza los datos actuales. ¿Continuar?')) return;
      db = migrar({ productos: d.productos, entradas: d.entradas || [], ventas: d.ventas, pedidos: d.pedidos || [], produccion: d.produccion || [], registro: d.registro || [] });
      guardar(); cerrarModal(); render(); toast('Copia restaurada');
    } catch (e) { toast('Archivo no válido'); }
  };
  r.readAsText(f);
}

// ===== Nube (Firebase) =====
let usrRef = null, usrAdminRef = null, miPerfil = null, listaUsr = {}, modoCrear = false;
const usuarioActual = () => { const u = firebase.auth().currentUser; return u && u.email ? u.email.replace('@manodedios.app', '') : ''; };
function iniciarNube() {
  try { firebase.database.INTERNAL.forceLongPolling(); } catch (e) {}
  firebase.initializeApp(firebaseConfig);
  paso = 'esperando sesión'; vigilar();
  try { firebase.auth().setPersistence(firebase.auth.Auth.Persistence.LOCAL); } catch (e) {}
  firebase.auth().onAuthStateChanged(u => {
    desuscribir();
    if (u) { enLogin = false; paso = 'leyendo perfil'; vigilar(); perfil(u); }
    else { clearTimeout(timer); cacheActiva = false; try { localStorage.removeItem(KEYC); } catch (e) {} if (!enLogin) mostrarLogin(); }
  });
}
let paso = '', timer = null;
function vigilar() {
  clearTimeout(timer);
  timer = setTimeout(() => { if (!listo) mostrarError(); }, 8000);
}
function mostrarError() {
  quitarSplash();
  if (cacheActiva) { sinRed = true; toast('Sin conexión: mostrando lo último guardado'); render(); return; }
  $('#nav').style.display = 'none';
  $('#app').innerHTML = '<div class="fade"><h2>No carga</h2><div class="bubble"><div class="sub" style="margin:0 0 14px">Se quedó en: ' + esc(paso || 'inicio') + '</div><button class="btn main full" onclick="reintentar()">Reintentar</button><button class="btn full" style="margin-top:10px" onclick="salir()">Cerrar sesión</button></div></div>';
}
function reintentar() {
  desuscribir();
  $('#app').innerHTML = '<div class="sk"></div><div class="sk"></div><div class="sk"></div>';
  const u = firebase.auth().currentUser;
  if (u) { paso = 'leyendo perfil'; vigilar(); perfil(u); } else mostrarLogin();
}
function desuscribir() {
  if (fbRef) fbRef.off();
  if (usrRef) usrRef.off();
  if (usrAdminRef) usrAdminRef.off();
  fbRef = usrRef = usrAdminRef = null; listo = false; miPerfil = null; listaUsr = {};
}
// El primer usuario queda como administrador; los demás quedan en espera
function perfil(u) {
  const nombre = usuarioActual();
  usrRef = firebase.database().ref('usuarios/' + u.uid);
  usrRef.once('value')
    .then(s => s.exists() ? null : usrRef.set({ nombre, aprobado: true, admin: true }).catch(() => usrRef.set({ nombre, aprobado: false })))
    .catch(() => {})
    .then(() => {
      if (!usrRef) return;
      usrRef.on('value', s => {
        miPerfil = s.val();
        if (miPerfil && miPerfil.aprobado === true) {
          paso = 'leyendo datos del negocio';
          if (!fbRef) escuchar();
          if (miPerfil.admin === true) vigilarUsuarios();
          else if (usrAdminRef) { usrAdminRef.off(); usrAdminRef = null; listaUsr = {}; }
        } else {
          if (fbRef) fbRef.off();
          fbRef = null; listo = false; mostrarPendiente();
        }
      }, e => { paso = 'perfil: ' + (e && e.code ? e.code : 'error'); mostrarError(); });
    });
}
function mostrarPendiente() {
  quitarSplash(); cacheActiva = false; enLogin = false; try { localStorage.removeItem(KEYC); } catch (e) {}  $('#nav').style.display = 'none';
  $('#app').innerHTML = '<div class="fade"><h2>Cuenta en espera</h2><div class="bubble"><div class="sub" style="margin:0 0 14px">Tu cuenta (' + esc(usuarioActual()) + ') ya está creada. Pídele al administrador que te apruebe; esta pantalla se abre sola cuando lo haga.</div><button class="btn del full" onclick="salir()">Cerrar sesión</button></div></div>';
}
// ===== Usuarios (solo administrador) =====
function vigilarUsuarios() {
  if (usrAdminRef) return;
  usrAdminRef = firebase.database().ref('usuarios');
  usrAdminRef.on('value', s => {
    listaUsr = s.val() || {};
    const el = $('#usr-lista');
    if (el && $('#modal').classList.contains('show')) el.innerHTML = htmlUsuarios();
  }, () => {});
}
const pendientes = () => Object.values(listaUsr).filter(x => x && x.aprobado !== true).length;
function htmlUsuarios() {
  const ids = Object.keys(listaUsr).sort((a, b) => (listaUsr[a].aprobado ? 1 : 0) - (listaUsr[b].aprobado ? 1 : 0));
  if (!ids.length) return '<div class="empty">Sin usuarios</div>';
  return ids.map(id => {
    const x = listaUsr[id];
    return '<div class="item"><div class="row"><div><div class="name">' + esc(x.nombre || '(sin nombre)') + (x.admin ? ' <span class="tag">Administrador</span>' : '') + '</div><div class="meta">' + (x.aprobado ? 'Con acceso' : 'Esperando aprobación') + '</div></div>' +
      botonesUsr(id, x) + '</div></div>';
  }).join('');
}
function botonesUsr(id, x) {
  if (firebase.auth().currentUser.uid === id) return '';
  const b = (t, cls, f, v) => '<button class="btn ' + cls + '" onclick="' + f + '(\'' + id + '\',' + v + ')">' + t + '</button>';
  let h;
  if (!x.aprobado) h = b('Aprobar', 'main', 'aprobar', true);
  else if (x.admin) h = b('Quitar admin', '', 'hacerAdmin', false);
  else h = b('Hacer admin', 'main', 'hacerAdmin', true) + b('Quitar', 'del', 'aprobar', false);
  return '<div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end">' + h + '</div>';
}
function hacerAdmin(id, si) {
  if (!confirm(si ? '¿Dar administrador a este usuario? Podrá aprobar y quitar usuarios.' : '¿Quitar administrador a este usuario?')) return;
  firebase.database().ref('usuarios/' + id + '/admin').set(si).catch(e => toast('No se pudo: ' + e.message));
}
function abrirUsuarios() {
  modal('<h3>Usuarios</h3><div class="sub" style="margin:2px 0 10px">Quien crea una cuenta nueva queda en espera. Apruébala para que vea el negocio.</div><div id="usr-lista">' + htmlUsuarios() + '</div><button class="btn full" style="margin-top:14px" onclick="cerrarModal()">Cerrar</button>');
}
function aprobar(id, si) {
  firebase.database().ref('usuarios/' + id + '/aprobado').set(si).catch(e => toast('No se pudo: ' + e.message));
}

// ===== Datos en la nube =====
function escuchar() {
  if (fbRef) fbRef.off();
  listo = false;
  fbRef = firebase.database().ref('negocio');
  fbRef.on('value', snap => {
    const v = snap.val() || {};
    COLS.forEach(c => { remoto[c] = v[c] || {}; });
    remoto.registro = v.registro || {};
    const vacio = !Object.keys(remoto.productos).length;
    if (!listo && vacio && local && local.productos.length && !localStorage.getItem(KEY + '_subido') &&
        confirm('La nube está vacía. ¿Subir los datos guardados en este teléfono?')) {
      db = local; listo = true; guardar();
      localStorage.setItem(KEY + '_subido', '1'); $('#nav').style.display = ''; render(); return;
    }
    db = migrar({
      productos: Object.values(remoto.productos).map(x => Object.assign({}, x)),
      entradas: Object.values(remoto.entradas).map(x => Object.assign({}, x)),
      ventas: Object.values(remoto.ventas).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1),
      pedidos: Object.values(remoto.pedidos).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1),
      produccion: Object.values(remoto.produccion).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1),
      registro: Object.values(remoto.registro).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1)
    });
    listo = true; cacheActiva = false; sinRed = false; guardarCache(); quitarSplash(); clearTimeout(timer); $('#nav').style.display = ''; render();
  }, e => { fbRef = null; listo = false; paso = 'negocio: ' + (e && e.code ? e.code : 'error'); mostrarError(); });
}

// ===== Login y cuenta =====
function mostrarLogin() {
  quitarSplash(); enLogin = true; cacheActiva = false;  $('#nav').style.display = 'none';
  const c = modoCrear, enter = ' onkeydown="if(event.key===\'Enter\')entrar()"';
  $('#app').innerHTML = '<div class="fade"><h2>' + (c ? 'Crear cuenta' : 'Iniciar sesión') + '</h2><div class="bubble">' +
    '<label>Usuario</label><input id="l-mail" type="text" autocapitalize="none" autocorrect="off" autocomplete="username" placeholder="Ej: rodrigo">' +
    '<label>Contraseña</label><input id="l-pass" type="password" autocomplete="' + (c ? 'new-password' : 'current-password') + '"' + (c ? '' : enter) + '>' +
    (c ? '<label>Repetir contraseña</label><input id="l-pass2" type="password" autocomplete="new-password"' + enter + '>' : '') +
    '<button class="btn main full" style="margin-top:16px" onclick="entrar()">' + (c ? 'Crear cuenta' : 'Entrar') + '</button>' +
    '<button class="btn full" style="margin-top:10px" onclick="cambiarModo()">' + (c ? 'Ya tengo cuenta' : 'Crear cuenta nueva') + '</button></div></div>';
}
function cambiarModo() { modoCrear = !modoCrear; mostrarLogin(); }
function entrar() {
  const u = $('#l-mail').value.trim().toLowerCase().replace(/\s+/g, ''), c = $('#l-pass').value;
  if (!u || !c) return toast('Escribe usuario y contraseña');
  if (!/^[a-z0-9._-]+$/.test(u)) return toast('El usuario solo puede tener letras y números');
  if (typeof firebase === 'undefined' || !firebase.auth) return toast('Conectando… intenta de nuevo en un momento');
  const m = u + '@manodedios.app';
  if (!modoCrear) return firebase.auth().signInWithEmailAndPassword(m, c).catch(() => toast('Usuario o contraseña incorrectos'));
  if (c.length < 6) return toast('La contraseña debe tener mínimo 6 caracteres');
  if (c !== $('#l-pass2').value) return toast('Las contraseñas no coinciden');
  firebase.auth().createUserWithEmailAndPassword(m, c).catch(e => toast(e.code === 'auth/email-already-in-use' ? 'Ese usuario ya existe, elige otro' : 'No se pudo crear: ' + e.message));
}
function salir() { modoCrear = false; cacheActiva = false; try { localStorage.removeItem(KEYC); } catch (e) {} cerrarModal(); firebase.auth().signOut(); }

function cargarScript(src) {
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
  local = db; db = { productos: [], entradas: [], ventas: [], pedidos: [], produccion: [] };
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
}
window.addEventListener('error', e => { if (!listo) { paso = 'error JS: ' + e.message; mostrarError(); } });
window.addEventListener('unhandledrejection', e => { if (!listo) { paso = 'promesa: ' + (e.reason && (e.reason.code || e.reason.message) || e.reason); mostrarError(); } });
// ===== Aviso de actualización =====
// La versión de esta app es el ?v= con que index.html cargó app.js.
// Cada parche cambia ese número en index.html; si el index publicado trae uno mayor, hay actualización.
const VER_APP = (() => {
  const s = document.querySelector('script[src*="js/app.js"]');
  const m = s && /[?&]v=(\d+)/.exec(s.src);
  return m ? Number(m[1]) : 0;
})();
let verCerrada = 0;
function avisarActualizacion(v) {
  let el = document.getElementById('upd');
  if (!el) {
    el = document.createElement('div'); el.id = 'upd'; el.className = 'upd';
    el.innerHTML = '<span>Se hizo una actualización reciente</span>' +
      '<button class="go" onclick="recargarApp()">' + ic('<path d="M20 12a8 8 0 1 1-2.4-5.7"/><path d="M20 4v5h-5"/>') + 'Recargar</button>' +
      '<button class="x" aria-label="Cerrar" onclick="cerrarAvisoUpd()">' + ic('<path d="M6 6l12 12M18 6 6 18"/>') + '</button>';
    document.body.appendChild(el);
  }
  el.dataset.v = v;
  requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('show')));
}
function cerrarAvisoUpd() {
  const el = document.getElementById('upd'); if (!el) return;
  verCerrada = Number(el.dataset.v) || 0; el.classList.remove('show');
}
function revisarVersion() {
  if (!VER_APP || navigator.onLine === false) return;
  fetch('index.html?c=' + Date.now(), { cache: 'no-store' })
    .then(r => r.ok ? r.text() : '')
    .then(t => {
      const m = /js\/app\.js\?v=(\d+)/.exec(t); const v = m ? Number(m[1]) : 0;
      if (v > VER_APP && v !== verCerrada) avisarActualizacion(v);
    })
    .catch(() => {});
}
function recargarApp() {
  const b = document.querySelector('#upd .go');
  if (b) { b.disabled = true; b.textContent = 'Actualizando…'; }
  let hecho = false;
  const fin = () => { if (hecho) return; hecho = true; location.reload(); };
  setTimeout(fin, 4000);
  // Pide el index nuevo saltándose la copia guardada y luego recarga
  fetch(location.href.split('#')[0], { cache: 'reload' }).catch(() => {}).then(fin);
}
setTimeout(revisarVersion, 4000);
setInterval(revisarVersion, 5 * 60 * 1000);
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') revisarVersion(); });
window.addEventListener('online', revisarVersion);

iniciar();
