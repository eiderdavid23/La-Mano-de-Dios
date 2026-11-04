// ===== Datos =====
function p2(n) { return String(n).padStart(2, '0'); }
const KEY = 'control_rollos_v1';
let db = cargar();
let vista = 'inicio';
let mesSel = hoy().slice(0, 7);
let fCat = 'Todas', fBus = '';

function cargar() {
  try { const d = JSON.parse(localStorage.getItem(KEY)); if (d && d.productos) return d; } catch (e) {}
  return { productos: [], entradas: [], ventas: [] };
}
function guardar() { localStorage.setItem(KEY, JSON.stringify(db)); }

// ===== Utilidades =====
function hoy() { const d = new Date(); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); }
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const num = v => { const n = parseFloat(String(v).replace(',', '.')); return isNaN(n) ? 0 : n; };
const money = n => (n < 0 ? '-' : '') + '$' + Math.round(Math.abs(n)).toLocaleString('es-CO');
const fmt = n => (Math.round(n * 10) / 10).toLocaleString('es-CO');
const prod = id => db.productos.find(p => p.id === id);
const costoRollo = p => p.rollosPorKilo > 0 ? p.costoKilo / p.rollosPorKilo : 0;
const gananciaRollo = p => p.precio - costoRollo(p);
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
  $('#fecha').textContent = new Date().toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' });
  $('#nav').innerHTML = TABS.map(t => '<button class="' + (vista === t[0] ? 'on' : '') + '" onclick="ir(\'' + t[0] + '\')"><span>' + t[1] + '</span>' + t[2] + '</button>').join('');
  const v = { inicio: vInicio, stock: vStock, vender: vVender, ganancias: vGanancias }[vista];
  $('#app').innerHTML = '<div class="fade">' + v() + '</div>';
}

// ===== Inicio =====
function vInicio() {
  const vh = ventasDia(hoy()), vm = ventasMes(hoy().slice(0, 7));
  const bajos = db.productos.filter(p => p.stock <= p.minimo);
  return '<div class="hero"><small>Ganancia de hoy</small><b>' + money(suma(vh, 'ganancia')) + '</b><span>' + fmt(suma(vh, 'rollos')) + ' rollos vendidos · ' + money(suma(vh, 'total')) + ' en ventas</span></div>' +
    '<div class="grid">' +
    '<div class="bubble wide"><small>Ganancia del mes (' + nombreMes(hoy().slice(0, 7)) + ')</small><b class="pos">' + money(suma(vm, 'ganancia')) + '</b></div>' +
    '<div class="bubble"><small>Productos</small><b>' + db.productos.length + '</b></div>' +
    '<div class="bubble"><small>Stock bajo</small><b class="' + (bajos.length ? 'neg' : '') + '">' + bajos.length + '</b></div>' +
    '</div>' +
    (bajos.length ? '<h2>⚠️ Por reponer</h2>' + bajos.map(p => '<div class="item low"><div class="row"><div class="name">' + esc(p.nombre) + '</div><span class="pill low">' + fmt(p.stock) + ' rollos</span></div></div>').join('') : '') +
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
    '<div class="item ' + (p.stock <= p.minimo ? 'low' : '') + '"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div>' +
    '<div class="meta"><span class="tag">' + esc(catDe(p)) + '</span><br>' + p.unidadesRollo + ' unid. por rollo · ≈ ' + Math.floor(p.stock * p.unidadesRollo).toLocaleString('es-CO') + ' unidades<br>' +
    (p.rollosPorKilo > 0 ? 'Venta ' + money(p.precio) + ' · Costo ' + money(costoRollo(p)) + ' · Gana <b class="' + (gananciaRollo(p) >= 0 ? 'pos' : 'neg') + '">' + money(gananciaRollo(p)) + '</b> por rollo' : 'Venta ' + money(p.precio) + ' · <b class="neg">Falta definir rollos por kilo</b>') + '</div></div>' +
    '<span class="pill ' + (p.stock <= p.minimo ? 'low' : '') + '">' + fmt(p.stock) + ' rollos</span></div>' +
    '<div class="actions"><button class="btn main" onclick="formIngreso(\'' + p.id + '\')">＋ Ingresar kilos</button><button class="btn" onclick="formProducto(\'' + p.id + '\')">Editar</button><button class="btn del" onclick="borrarProducto(\'' + p.id + '\')">Borrar</button></div></div>'
  ).join('');
}

function formProducto(id) {
  const p = id ? prod(id) : { nombre: '', categoria: '', unidadesRollo: 14, rollosPorKilo: '', precio: 2000, costoKilo: '', minimo: 5, stock: 0 };
  modal('<h3>' + (id ? 'Editar producto' : 'Nuevo producto') + '</h3>' +
    '<label>Nombre</label><input id="f-nombre" value="' + esc(p.nombre) + '" placeholder="Ej: Clavitos">' +
    '<label>Categoría</label><input id="f-cat" list="cats" value="' + esc(p.categoria || '') + '" placeholder="Ej: Aliños, Salsas"><datalist id="cats">' + categorias().map(c => '<option value="' + esc(c) + '">').join('') + '</datalist>' +
    '<label>Unidades por rollo</label><input id="f-unid" type="number" inputmode="decimal" value="' + p.unidadesRollo + '">' +
    '<label>Rollos que salen de 1 kilo</label><input id="f-rpk" type="number" inputmode="decimal" value="' + p.rollosPorKilo + '" placeholder="Ej: 30"><div class="hint">Con esto se convierten los kilos a rollos. Si aún no lo sabes, déjalo vacío y lo defines después con Editar.</div>' +
    '<label>Precio de venta por rollo ($)</label><input id="f-precio" type="number" inputmode="decimal" value="' + p.precio + '">' +
    '<label>Costo por kilo ($)</label><input id="f-costo" type="number" inputmode="decimal" value="' + p.costoKilo + '" placeholder="Lo que pagas por 1 kilo">' +
    '<label>Avisar cuando queden (rollos)</label><input id="f-min" type="number" inputmode="decimal" value="' + p.minimo + '">' +
    (id ? '' : '<label>Stock inicial (rollos)</label><input id="f-stock" type="number" inputmode="decimal" value="0">') +
    '<button class="btn main full" onclick="guardarProducto(\'' + (id || '') + '\')">Guardar</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
}
function guardarProducto(id) {
  const nombre = $('#f-nombre').value.trim();
  const rpk = num($('#f-rpk').value);
  if (!nombre) return toast('Escribe el nombre');
  const d = { nombre, categoria: $('#f-cat').value.trim(), unidadesRollo: num($('#f-unid').value) || 1, rollosPorKilo: rpk, precio: num($('#f-precio').value), costoKilo: num($('#f-costo').value), minimo: num($('#f-min').value) };
  if (id) Object.assign(prod(id), d);
  else db.productos.push(Object.assign({ id: uid(), stock: num($('#f-stock').value) }, d));
  guardar(); cerrarModal(); render(); toast('Producto guardado ✅');
}
function borrarProducto(id) {
  if (!confirm('¿Borrar este producto? Sus ventas ya registradas se conservan.')) return;
  db.productos = db.productos.filter(p => p.id !== id);
  guardar(); render();
}

// ===== Ingreso por kilos =====
function formIngreso(id) {
  const p = prod(id);
  modal('<h3>Ingresar ' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Puedes cambiar estos datos en cada ingreso</div>' +
    '<label>Kilos que llegaron</label><input id="i-kilos" type="number" inputmode="decimal" placeholder="Ej: 1" oninput="prevIngreso(\'' + id + '\')">' +
    '<label>Rollos que salen de 1 kilo</label><input id="i-rpk" type="number" inputmode="decimal" value="' + (p.rollosPorKilo || '') + '" placeholder="Ej: 30" oninput="prevIngreso(\'' + id + '\')">' +
    '<label>Costo por kilo ($)</label><input id="i-costo" type="number" inputmode="decimal" value="' + p.costoKilo + '">' +
    '<div class="preview" id="i-prev">= 0 rollos</div>' +
    '<button class="btn main full" onclick="confirmarIngreso(\'' + id + '\')">Agregar al stock</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
}
function prevIngreso(id) {
  const r = num($('#i-kilos').value) * num($('#i-rpk').value);
  $('#i-prev').textContent = '= ' + fmt(r) + ' rollos';
}
function confirmarIngreso(id) {
  const p = prod(id), kilos = num($('#i-kilos').value);
  const rpk = num($('#i-rpk').value);
  if (kilos <= 0) return toast('Escribe los kilos');
  if (rpk <= 0) return toast('Escribe cuántos rollos salen de 1 kilo');
  const rollos = kilos * rpk, costo = num($('#i-costo').value);
  p.stock += rollos; p.costoKilo = costo; p.rollosPorKilo = rpk;
  db.entradas.push({ id: uid(), fecha: hoy(), productoId: id, nombre: p.nombre, kilos, rollos, costoKilo: costo });
  guardar(); cerrarModal(); render(); toast('+' + fmt(rollos) + ' rollos ✅');
}

// ===== Vender =====
function vVender() {
  if (!db.productos.length) return '<div class="empty">Primero crea un producto en 📦 Stock</div>';
  const hoyV = ventasDia(hoy());
  return '<h2>¿Qué vendiste?</h2>' + barraFiltro() + '<div id="lista">' + listaVender() + '</div>' +
    '<h2 style="margin-top:22px">Ventas de hoy</h2>' +
    (hoyV.length ? hoyV.slice().reverse().map(v => '<div class="item"><div class="row"><div><div class="name">' + esc(v.nombre) + '</div><div class="meta">' + fmt(v.rollos) + ' rollos · ' + money(v.total) + ' · gana ' + money(v.ganancia) + '</div></div><button class="btn del" onclick="borrarVenta(\'' + v.id + '\')">Deshacer</button></div></div>').join('') : '<div class="empty">Sin ventas hoy</div>');
}
function listaVender() {
  const l = filtrados();
  if (!l.length) return '<div class="empty">No hay productos con ese filtro</div>';
  return l.map(p => '<div class="item tap" onclick="formVenta(\'' + p.id + '\')"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div><div class="meta"><span class="tag">' + esc(catDe(p)) + '</span> ' + money(p.precio) + ' c/u</div></div><span class="pill ' + (p.stock <= p.minimo ? 'low' : '') + '">' + fmt(p.stock) + ' rollos</span></div></div>').join('');
}
function formVenta(id) {
  const p = prod(id);
  modal('<h3>' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Disponible: ' + fmt(p.stock) + ' rollos · ' + money(p.precio) + ' c/u</div>' +
    '<div class="step"><button onclick="ajustarQty(-1,\'' + id + '\')">−</button><input id="v-qty" type="number" inputmode="decimal" value="1" oninput="calcVenta(\'' + id + '\')"><button onclick="ajustarQty(1,\'' + id + '\')">+</button></div>' +
    '<div class="total"><b id="v-total"></b><span class="pos" id="v-gan"></span></div>' +
    '<button class="btn main full" onclick="registrarVenta(\'' + id + '\')">Registrar venta</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
  calcVenta(id);
}
const qtyVenta = () => Math.max(0, num($('#v-qty').value));
function ajustarQty(d, id) { $('#v-qty').value = Math.max(1, Math.round((qtyVenta() + d) * 100) / 100); calcVenta(id); }
function calcVenta(id) {
  const p = prod(id), q = qtyVenta();
  $('#v-total').textContent = money(q * p.precio);
  $('#v-gan').textContent = p.rollosPorKilo > 0 ? 'Ganancia: ' + money(q * gananciaRollo(p)) : 'Falta definir rollos por kilo';
}
function registrarVenta(id) {
  const p = prod(id), q = qtyVenta();
  if (q <= 0) return toast('Escribe la cantidad');
  if (!(p.rollosPorKilo > 0)) return toast('Primero define los rollos por kilo (Stock → Editar)');
  if (q > p.stock) return toast('Solo hay ' + fmt(p.stock) + ' rollos en stock');
  const costo = costoRollo(p);
  db.ventas.push({ id: uid(), fecha: hoy(), productoId: p.id, nombre: p.nombre, categoria: catDe(p), rollos: q, precio: p.precio, costo, total: q * p.precio, ganancia: q * (p.precio - costo) });
  p.stock -= q;
  guardar(); cerrarModal(); render(); toast('Venta registrada ✅');
}
function borrarVenta(id) {
  const v = db.ventas.find(x => x.id === id);
  if (!v || !confirm('¿Deshacer esta venta? El stock se devuelve.')) return;
  const p = prod(v.productoId); if (p) p.stock += v.rollos;
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
    '<div class="hero"><small>Ganancia total del mes (todos los productos)</small><b>' + money(g) + '</b><span>' + money(suma(vm, 'total')) + ' vendido · ' + fmt(suma(vm, 'rollos')) + ' rollos</span></div>' +
    '<h2>Ganancia por producto</h2>' +
    (lista.length ? lista.map(x => '<div class="item"><div class="row"><div><div class="name">' + esc(x.n) + '</div><div class="meta">' + fmt(x.r) + ' rollos · ' + money(x.t) + ' vendido</div></div><span class="pill ' + (x.g < 0 ? 'low' : '') + '">' + money(x.g) + '</span></div></div>').join('') +
      '<div class="item" style="border-color:var(--ac)"><div class="row"><div class="name">Total de todos los productos</div><span class="pill ' + (g < 0 ? 'low' : '') + '">' + money(g) + '</span></div></div>' : '<div class="empty">Sin ventas este mes</div>') +
    '<h2 style="margin-top:22px">Día por día</h2>' +
    (Object.keys(dias).length ? Object.keys(dias).sort().reverse().map(f => '<div class="item"><div class="row"><div><div class="name" style="text-transform:capitalize">' + nombreDia(f) + '</div><div class="meta">' + fmt(dias[f].r) + ' rollos · ' + money(dias[f].t) + ' vendido</div></div><span class="pill">' + money(dias[f].g) + '</span></div></div>').join('') : '<div class="empty">Sin ventas este mes</div>');
}

// ===== Ajustes / respaldo =====
function abrirAjustes() {
  modal('<h3>Respaldo</h3><div class="sub" style="margin:2px 0 10px">Los datos viven en este teléfono. Guarda una copia de vez en cuando.</div>' +
    '<button class="btn main full" onclick="exportar()">⬇️ Descargar copia</button>' +
    '<label>Restaurar copia</label><input type="file" accept=".json" onchange="importar(this)">' +
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
      db = { productos: d.productos, entradas: d.entradas || [], ventas: d.ventas };
      guardar(); cerrarModal(); render(); toast('Copia restaurada ✅');
    } catch (e) { toast('Archivo no válido'); }
  };
  r.readAsText(f);
}

render();
