// ===== Datos =====
function p2(n) { return String(n).padStart(2, '0'); }
const r2 = n => Math.round(n * 100) / 100;
const KEY = 'control_rollos_v1';
let db = cargar();
let vista = 'inicio';
let mesSel = hoy().slice(0, 7);
let fCat = 'Todas', fBus = '';
const NUBE = typeof firebase !== 'undefined' && typeof firebaseConfig !== 'undefined' && !!firebaseConfig.apiKey;
let local = null, fbRef = null, listo = !NUBE;
const remoto = { productos: {}, entradas: {}, ventas: {} };
const COLS = ['productos', 'entradas', 'ventas'];
const est = o => o ? JSON.stringify(o, Object.keys(o).sort()) : 'null';

function cargar() {
  try { const d = JSON.parse(localStorage.getItem(KEY)); if (d && d.productos) return migrar(d); } catch (e) {}
  return { productos: [], entradas: [], ventas: [] };
}
// Datos viejos (stock en rollos) -> stock en gramos
function migrar(d) {
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
const rollosDisp = p => gpr(p) > 0 ? Math.floor(p.stockG / gpr(p) + 1e-9) : 0;
const bajo = p => p.stockG <= p.minimoG;
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
function modal(html) { const m = $('#modal'); m.innerHTML = '<div class="sheet">' + html + '</div>'; m.classList.add('show'); }
function cerrarModal() { $('#modal').classList.remove('show'); }

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
  return '<input id="bus" type="search" placeholder="🔍 Buscar producto..." value="' + esc(fBus) + '" oninput="setBus(this.value)" style="margin-bottom:10px">' +
    '<div class="chips">' + cats.map((c, i) => '<button class="chip ' + (c === fCat ? 'on' : '') + '" onclick="setCat(' + i + ')">' + esc(c) + '</button>').join('') + '</div>';
}
function setCat(i) { fCat = ['Todas'].concat(categorias())[i]; render(); }
function setBus(v) { fBus = v; $('#lista').innerHTML = vista === 'stock' ? listaStock() : listaVender(); }

// ===== Navegación =====
const TABS = [['inicio', '🏠', 'Inicio'], ['stock', '📦', 'Stock'], ['vender', '🛒', 'Vender'], ['ganancias', '💰', 'Ganancias']];
function ir(v) { vista = v; fCat = 'Todas'; fBus = ''; render(); window.scrollTo(0, 0); }
function render() {
  if (NUBE && !listo) { $('#app').innerHTML = '<div class="empty">Cargando…</div>'; return; }
  $('#fecha').textContent = new Date().toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' });
  $('#nav').innerHTML = TABS.map(t => '<button class="' + (vista === t[0] ? 'on' : '') + '" onclick="ir(\'' + t[0] + '\')"><span>' + t[1] + '</span>' + t[2] + '</button>').join('');
  const v = { inicio: vInicio, stock: vStock, vender: vVender, ganancias: vGanancias }[vista];
  $('#app').innerHTML = '<div class="fade">' + v() + '</div>';
}

// ===== Inicio =====
function vInicio() {
  const vh = ventasDia(hoy()), vm = ventasMes(hoy().slice(0, 7));
  const bajos = db.productos.filter(p => bajo(p));
  return '<div class="hero ' + gHero(suma(vh, 'ganancia')) + '"><small>' + gLbl(suma(vh, 'ganancia')) + ' de hoy</small><b>' + money(Math.abs(suma(vh, 'ganancia'))) + '</b><span>' + fmt(suma(vh, 'rollos')) + ' rollos vendidos · ' + money(suma(vh, 'total')) + ' en ventas</span></div>' +
    '<div class="grid">' +
    '<div class="bubble wide"><small>' + gLbl(suma(vm, 'ganancia')) + ' del mes (' + nombreMes(hoy().slice(0, 7)) + ')</small><b class="' + gCls(suma(vm, 'ganancia')) + '">' + money(Math.abs(suma(vm, 'ganancia'))) + '</b></div>' +
    '<div class="bubble"><small>Productos</small><b>' + db.productos.length + '</b></div>' +
    '<div class="bubble"><small>Stock bajo</small><b class="' + (bajos.length ? 'neg' : '') + '">' + bajos.length + '</b></div>' +
    '</div>' +
    (bajos.length ? '<h2>⚠️ Por reponer</h2>' + bajos.map(p => '<div class="item low"><div class="row"><div class="name">' + esc(p.nombre) + '</div><span class="pill low">' + fmtG(p.stockG) + '<br><small>' + rollosDisp(p).toLocaleString('es-CO') + ' rollos</small></span></div></div>').join('') : '') +
    (!db.productos.length ? '<div class="empty">Empieza creando tu primer producto en 📦 Stock</div>' : '');
}

// ===== Stock =====
function vStock() {
  return '<h2>Inventario</h2><button class="add" onclick="formProducto()">＋ Nuevo producto</button>' +
    (db.productos.length ? barraFiltro() + '<div id="lista">' + listaStock() + '</div>' : '<div class="empty">Aún no hay productos</div>');
}
function listaStock() {
  const l = filtrados();
  if (!l.length) return '<div class="empty">No hay productos con ese filtro</div>';
  return l.map(p =>
    '<div class="item ' + (bajo(p) ? 'low' : '') + '"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div>' +
    '<div class="meta"><span class="tag">' + esc(catDe(p)) + '</span><br>' +
    (gpr(p) > 0 ? fmtG(gpr(p)) + ' por rollo · 1 kilo ≈ ' + fmt(1000 / gpr(p)) + ' rollos · 1 libra ≈ ' + fmt(500 / gpr(p)) + '<br>Alcanza para ' + rollosDisp(p).toLocaleString('es-CO') + ' rollos · ≈ ' + Math.floor(rollosDisp(p) * p.unidadesRollo).toLocaleString('es-CO') + ' unidades<br>' : '') +
    (gpr(p) > 0 ? 'Venta ' + money(p.precio) + ' · Costo ' + money(costoRollo(p)) + ' · Gana <b class="' + (gananciaRollo(p) >= 0 ? 'pos' : 'neg') + '">' + money(gananciaRollo(p)) + '</b> (' + fmt(costoRollo(p) > 0 ? gananciaRollo(p) / costoRollo(p) * 100 : 0) + '%) por rollo' : 'Venta ' + money(p.precio) + ' · <b class="neg">Falta definir los gramos por rollo</b>') + '</div></div>' +
    '<span class="pill ' + (bajo(p) ? 'low' : '') + '">' + fmtG(p.stockG) + '<br><small>' + rollosDisp(p).toLocaleString('es-CO') + ' rollos</small></span></div>' +
    '<div class="actions"><button class="btn main" onclick="formIngreso(\'' + p.id + '\')">＋ Ingresar kilos/libras</button><button class="btn" onclick="formProducto(\'' + p.id + '\')">Editar</button><button class="btn del" onclick="borrarProducto(\'' + p.id + '\')">Borrar</button></div></div>'
  ).join('');
}

function opcionesCat(sel) {
  const lista = ['Aliños', 'Salsas', 'Otro'];
  if (sel && !lista.includes(sel)) lista.splice(2, 0, sel);
  return lista.map(c => '<option value="' + esc(c) + '"' + (c === sel ? ' selected' : '') + '>' + esc(c) + '</option>').join('');
}
function formProducto(id) {
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
  if (id) Object.assign(prod(id), d);
  else db.productos.push(Object.assign({ id: uid(), stockG: num($('#f-stock').value) }, d));
  guardar(); cerrarModal(); render(); toast('Producto guardado ✅');
}
function borrarProducto(id) {
  if (!confirm('¿Borrar este producto? Sus ventas ya registradas se conservan.')) return;
  db.productos = db.productos.filter(p => p.id !== id);
  guardar(); render();
}

// ===== Ingreso por kilos / libras =====
const gUni = () => $('#i-uni').value === 'lb' ? 500 : 1000;
function formIngreso(id) {
  const p = prod(id);
  modal('<h3>Ingresar ' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Se suma al stock en gramos. Puedes cambiar estos datos en cada ingreso</div>' +
    '<label>Unidad</label><select id="i-uni" onchange="cambiarUnidad(\'' + id + '\')"><option value="kg">Kilos (1000 g)</option><option value="lb">Libras (500 g)</option></select>' +
    '<label>Cantidad que llegó</label><input id="i-cant" type="number" inputmode="decimal" placeholder="Ej: 1" oninput="prevIngreso(\'' + id + '\')">' +
    '<label>Gramos que pesa 1 rollo</label><input id="i-gpr" type="number" inputmode="decimal" value="' + (gpr(p) || '') + '" placeholder="Ej: 33" oninput="prevIngreso(\'' + id + '\')">' +
    '<label id="i-lblc">Costo por kilo ($)</label><input id="i-costo" type="number" inputmode="decimal" value="' + p.costoKilo + '">' +
    '<div class="preview" id="i-prev"></div>' +
    '<button class="btn main full" onclick="confirmarIngreso(\'' + id + '\')">Agregar al stock</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
  prevIngreso(id);
}
function cambiarUnidad(id) {
  const p = prod(id), lb = gUni() === 500;
  $('#i-lblc').textContent = 'Costo por ' + (lb ? 'libra' : 'kilo') + ' ($)';
  $('#i-costo').value = p.costoKilo ? r2(p.costoKilo * gUni() / 1000) : '';
  prevIngreso(id);
}
function prevIngreso(id) {
  const p = prod(id), g = num($('#i-cant').value) * gUni(), gp = num($('#i-gpr').value);
  $('#i-prev').textContent = '= ' + fmt(g) + ' g' + (gp > 0 ? ' · ≈ ' + fmt(Math.floor(g / gp)) + ' rollos' : '') + ' · stock queda en ' + fmtG(p.stockG + g);
}
function confirmarIngreso(id) {
  const p = prod(id), cant = num($('#i-cant').value), gp = num($('#i-gpr').value);
  if (cant <= 0) return toast('Escribe la cantidad');
  if (gp <= 0) return toast('Escribe cuántos gramos pesa 1 rollo');
  const g = r2(cant * gUni()), costoKilo = num($('#i-costo').value) * 1000 / gUni();
  p.stockG = r2(p.stockG + g); p.costoKilo = r2(costoKilo); p.gramosPorRollo = gp;
  db.entradas.push({ id: uid(), fecha: hoy(), productoId: id, nombre: p.nombre, cantidad: cant, unidad: $('#i-uni').value, gramos: g, costoKilo: p.costoKilo });
  guardar(); cerrarModal(); render(); toast('+' + fmt(g) + ' g ✅');
}

// ===== Vender =====
function vVender() {
  if (!db.productos.length) return '<div class="empty">Primero crea un producto en 📦 Stock</div>';
  const hoyV = ventasDia(hoy());
  return '<h2>¿Qué vendiste?</h2>' + barraFiltro() + '<div id="lista">' + listaVender() + '</div>' +
    '<h2 style="margin-top:22px">Ventas de hoy</h2>' +
    (hoyV.length ? hoyV.slice().reverse().map(v => '<div class="item"><div class="row"><div><div class="name">' + esc(v.nombre) + '</div><div class="meta">' + fmt(v.rollos) + ' rollos · ' + money(v.total) + ' · ' + (v.ganancia < 0 ? 'pierde ' : 'gana ') + money(Math.abs(v.ganancia)) + '</div></div><button class="btn del" onclick="borrarVenta(\'' + v.id + '\')">Deshacer</button></div></div>').join('') : '<div class="empty">Sin ventas hoy</div>');
}
function listaVender() {
  const l = filtrados();
  if (!l.length) return '<div class="empty">No hay productos con ese filtro</div>';
  return l.map(p => '<div class="item tap" onclick="formVenta(\'' + p.id + '\')"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div><div class="meta"><span class="tag">' + esc(catDe(p)) + '</span> ' + money(p.precio) + ' c/u · ' + rollosDisp(p).toLocaleString('es-CO') + ' rollos</div></div><span class="pill ' + (bajo(p) ? 'low' : '') + '">' + fmtG(p.stockG) + '<br><small>' + rollosDisp(p).toLocaleString('es-CO') + ' rollos</small></span></div></div>').join('');
}
function formVenta(id) {
  const p = prod(id);
  modal('<h3>' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Stock: ' + fmtG(p.stockG) + ' (≈ ' + rollosDisp(p).toLocaleString('es-CO') + ' rollos) · ' + money(p.precio) + ' c/u</div>' +
    '<label>Rollos</label><div class="step"><button onclick="ajustarQty(-1,\'' + id + '\')">−</button><input id="v-qty" type="number" inputmode="decimal" value="1" oninput="calcVenta(\'' + id + '\')"><button onclick="ajustarQty(1,\'' + id + '\')">+</button></div>' +
    '<div class="hint" id="v-g"></div>' +
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
  $('#v-g').textContent = gpr(p) > 0 ? q + ' rollos × ' + fmtG(gpr(p)) + ' = se descuentan ' + fmtG(q * gpr(p)) + ' del stock' : '';
  $('#v-gan').textContent = gpr(p) > 0 ? 'Ganancia: ' + money(q * gananciaRollo(p)) : 'Falta definir gramos por rollo';
}
function registrarVenta(id) {
  const p = prod(id), q = qtyVenta();
  if (q <= 0) return toast('Escribe la cantidad');
  if (!(gpr(p) > 0)) return toast('Primero define los gramos por rollo (Stock → Editar)');
  const g = r2(q * gpr(p));
  if (g > p.stockG + 1e-6) return toast('Solo alcanza para ' + rollosDisp(p) + ' rollos (' + fmtG(p.stockG) + ')');
  const costo = costoRollo(p);
  db.ventas.push({ id: uid(), fecha: hoy(), productoId: p.id, nombre: p.nombre, categoria: catDe(p), rollos: q, gramos: g, precio: p.precio, costo, total: q * p.precio, ganancia: q * (p.precio - costo) });
  p.stockG = Math.max(0, r2(p.stockG - g));
  guardar(); cerrarModal(); render(); toast('Venta registrada ✅');
}
function borrarVenta(id) {
  const v = db.ventas.find(x => x.id === id);
  if (!v || !confirm('¿Deshacer esta venta? El stock se devuelve.')) return;
  const p = prod(v.productoId); if (p) p.stockG = r2(p.stockG + (v.gramos != null ? v.gramos : v.rollos * gpr(p)));
  db.ventas = db.ventas.filter(x => x.id !== id);
  guardar(); render();
}

// ===== Ganancias =====
function cambiarMes(d) {
  const [y, m] = mesSel.split('-').map(Number), n = new Date(y, m - 1 + d, 1);
  mesSel = n.getFullYear() + '-' + p2(n.getMonth() + 1); render();
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
    '<div class="hero ' + gHero(g) + '"><small>' + gLbl(g) + ' total del mes (todos los productos)</small><b>' + money(Math.abs(g)) + '</b><span>' + money(suma(vm, 'total')) + ' vendido · ' + fmt(suma(vm, 'rollos')) + ' rollos</span></div>' +
    '<h2>Ganancia por producto</h2>' +
    (lista.length ? lista.map(x => '<div class="item"><div class="row"><div><div class="name">' + esc(x.n) + '</div><div class="meta">' + fmt(x.r) + ' rollos · ' + money(x.t) + ' vendido</div></div><span class="pill ' + (x.g < 0 ? 'low' : '') + '">' + money(x.g) + '</span></div></div>').join('') +
      '<div class="item" style="border-color:var(--ac)"><div class="row"><div class="name">Total de todos los productos</div><span class="pill ' + (g < 0 ? 'low' : '') + '">' + money(g) + '</span></div></div>' : '<div class="empty">Sin ventas este mes</div>') +
    '<h2 style="margin-top:22px">Día por día</h2>' +
    (Object.keys(dias).length ? Object.keys(dias).sort().reverse().map(f => '<div class="item"><div class="row"><div><div class="name" style="text-transform:capitalize">' + nombreDia(f) + '</div><div class="meta">' + fmt(dias[f].r) + ' rollos · ' + money(dias[f].t) + ' vendido</div></div><span class="pill ' + (dias[f].g < 0 ? 'low' : '') + '">' + money(dias[f].g) + '</span></div></div>').join('') : '<div class="empty">Sin ventas este mes</div>');
}

// ===== Ajustes / respaldo =====
function abrirAjustes() {
  if (!NUBE) {
    modal('<h3>Respaldo</h3><div class="sub" style="margin:2px 0 10px">Los datos viven en este teléfono. Guarda una copia de vez en cuando.</div>' +
      '<button class="btn main full" onclick="exportar()">⬇️ Descargar copia</button>' +
      '<label>Restaurar copia</label><input type="file" accept=".json" onchange="importar(this)">' +
      '<button class="btn full" style="margin-top:14px" onclick="cerrarModal()">Cerrar</button>');
    return;
  }
  const adm = miPerfil && miPerfil.admin;
  modal('<h3>Ajustes</h3><div class="sub" style="margin:2px 0 10px">Sesión: ' + esc(usuarioActual()) + (adm ? ' 👑 administrador' : '') + '<br>Tus datos se guardan en la nube automáticamente.</div>' +
    (adm ? '<button class="btn main full" onclick="abrirUsuarios()">👥 Usuarios' + (pendientes() ? ' (' + pendientes() + ' en espera)' : '') + '</button>' : '') +
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
      db = migrar({ productos: d.productos, entradas: d.entradas || [], ventas: d.ventas });
      guardar(); cerrarModal(); render(); toast('Copia restaurada ✅');
    } catch (e) { toast('Archivo no válido'); }
  };
  r.readAsText(f);
}

// ===== Nube (Firebase) =====
let usrRef = null, usrAdminRef = null, miPerfil = null, listaUsr = {}, modoCrear = false;
const usuarioActual = () => { const u = firebase.auth().currentUser; return u && u.email ? u.email.replace('@manodedios.app', '') : ''; };
function iniciarNube() {
  firebase.initializeApp(firebaseConfig);
  try { firebase.auth().setPersistence(firebase.auth.Auth.Persistence.LOCAL); } catch (e) {}
  firebase.auth().onAuthStateChanged(u => {
    desuscribir();
    if (u) perfil(u); else mostrarLogin();
  });
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
          if (!fbRef) escuchar();
          if (miPerfil.admin === true) vigilarUsuarios();
          else if (usrAdminRef) { usrAdminRef.off(); usrAdminRef = null; listaUsr = {}; }
        } else {
          if (fbRef) fbRef.off();
          fbRef = null; listo = false; mostrarPendiente();
        }
      }, () => mostrarPendiente());
    });
}
function mostrarPendiente() {
  $('#nav').style.display = 'none';
  $('#app').innerHTML = '<div class="fade"><h2>Cuenta en espera ⏳</h2><div class="bubble"><div class="sub" style="margin:0 0 14px">Tu cuenta (' + esc(usuarioActual()) + ') ya está creada. Pídele al administrador que te apruebe; esta pantalla se abre sola cuando lo haga.</div><button class="btn del full" onclick="salir()">Cerrar sesión</button></div></div>';
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
    return '<div class="item"><div class="row"><div><div class="name">' + esc(x.nombre || '(sin nombre)') + (x.admin ? ' 👑' : '') + '</div><div class="meta">' + (x.aprobado ? 'Con acceso' : '⏳ Esperando aprobación') + '</div></div>' +
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
    const vacio = !Object.keys(remoto.productos).length;
    if (!listo && vacio && local && local.productos.length && !localStorage.getItem(KEY + '_subido') &&
        confirm('La nube está vacía. ¿Subir los datos guardados en este teléfono?')) {
      db = local; listo = true; guardar();
      localStorage.setItem(KEY + '_subido', '1'); $('#nav').style.display = ''; render(); return;
    }
    db = migrar({
      productos: Object.values(remoto.productos).map(x => Object.assign({}, x)),
      entradas: Object.values(remoto.entradas).map(x => Object.assign({}, x)),
      ventas: Object.values(remoto.ventas).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1)
    });
    listo = true; $('#nav').style.display = ''; render();
  }, () => { fbRef = null; listo = false; mostrarPendiente(); });
}

// ===== Login y cuenta =====
function mostrarLogin() {
  $('#nav').style.display = 'none';
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
  const m = u + '@manodedios.app';
  if (!modoCrear) return firebase.auth().signInWithEmailAndPassword(m, c).catch(() => toast('Usuario o contraseña incorrectos'));
  if (c.length < 6) return toast('La contraseña debe tener mínimo 6 caracteres');
  if (c !== $('#l-pass2').value) return toast('Las contraseñas no coinciden');
  firebase.auth().createUserWithEmailAndPassword(m, c).catch(e => toast(e.code === 'auth/email-already-in-use' ? 'Ese usuario ya existe, elige otro' : 'No se pudo crear: ' + e.message));
}
function salir() { modoCrear = false; cerrarModal(); firebase.auth().signOut(); }

function iniciar() {
  if (!NUBE) { render(); return; }
  local = db; db = { productos: [], entradas: [], ventas: [] };
  render(); iniciarNube();
}
iniciar();
