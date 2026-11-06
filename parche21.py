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

A = 'js/app.js'

JS = r"""
// ===== Borrar datos de prueba =====
ICO.borrar = ic('<path d="M4 7h16M10 11v6M14 11v6M6 7l1 12h10l1-12M9 7V4h6v3"/>');
LBL.pruebas_borradas = 'Borró datos de prueba';
const plu = (n, a, b) => n + ' ' + (n === 1 ? a : b);
function selLimpieza() {
  let d1 = $('#lp-d1').value || hoy(), d2 = $('#lp-d2').value || hoy();
  if (d1 > d2) { const t = d1; d1 = d2; d2 = t; }
  const en = f => !!f && f >= d1 && f <= d2;
  const ven = $('#lp-ven').checked, rol = $('#lp-rol').checked, ing = $('#lp-ing').checked;
  const peds = ven ? db.pedidos.filter(x => en(x.fecha) || (x.estado === 'entregado' && en(x.entregadoEn))) : [];
  const idP = {}; peds.forEach(x => { idP[x.id] = 1; });
  const vts = ven ? db.ventas.filter(v => v.pedidoId ? idP[v.pedidoId] : en(v.fecha)) : [];
  return { d1, d2, peds, vts, rols: rol ? db.produccion.filter(x => en(x.fecha)) : [], ings: ing ? db.entradas.filter(x => en(x.fecha)) : [] };
}
function resumenLimpieza(s) {
  const t = [];
  if (s.vts.length) t.push(plu(s.vts.length, 'venta', 'ventas'));
  if (s.peds.length) t.push(plu(s.peds.length, 'pedido', 'pedidos'));
  if (s.rols.length) t.push(plu(s.rols.length, 'registro de rollos hechos', 'registros de rollos hechos'));
  if (s.ings.length) t.push(plu(s.ings.length, 'ingreso de materia', 'ingresos de materia'));
  return t.join(', ');
}
function prevLimpieza() {
  const r = resumenLimpieza(selLimpieza());
  $('#lp-prev').textContent = r ? 'Se borran: ' + r : 'No hay nada en esas fechas';
}
function formLimpieza() {
  if (espera()) return;
  const ck = (id, t) => '<label style="display:flex;align-items:center;gap:10px;margin:10px 0 0;font-weight:600"><input type="checkbox" id="' + id + '" checked onchange="prevLimpieza()" style="width:auto;margin:0">' + t + '</label>';
  modal('<h3>Borrar datos de prueba</h3><div class="sub" style="margin:2px 0 4px">Borra lo que se registró en esos días y el stock vuelve a como estaba. Ya no cuenta en las ganancias del mes.</div>' +
    '<label>Desde el día</label><input id="lp-d1" type="date" value="' + hoy() + '" max="' + hoy() + '" onchange="prevLimpieza()">' +
    '<label>Hasta el día</label><input id="lp-d2" type="date" value="' + hoy() + '" max="' + hoy() + '" onchange="prevLimpieza()">' +
    ck('lp-ven', 'Ventas y pedidos') + ck('lp-rol', 'Rollos hechos') + ck('lp-ing', 'Ingresos de materia') +
    '<div class="preview" id="lp-prev"></div>' +
    '<div class="hint">El costo y el peso del rollo se quedan como los dejó el último ingreso; si hiciste pruebas con otros valores, corrígelos en Editar.</div>' +
    '<button class="btn del full" onclick="limpiarPruebas()">Borrar</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
  prevLimpieza();
}
function limpiarPruebas() {
  if (espera()) return;
  const s = selLimpieza(), res = resumenLimpieza(s);
  if (!res) return toast('No hay nada en esas fechas');
  if (!confirm('¿Borrar datos de prueba del ' + s.d1 + ' al ' + s.d2 + '?\n\n' + res + '\n\nEl stock vuelve a como estaba. Esto NO se puede deshacer.')) return;
  // 1) Ventas y pedidos: los rollos hechos vuelven
  s.vts.forEach(v => {
    const p = prod(v.productoId); if (!p) return;
    if (v.modo === 'hechos') p.hechos = r2((p.hechos || 0) + v.rollos); else p.stockG = r2(p.stockG + (v.gramos != null ? v.gramos : v.rollos * gpr(p)));
  });
  const idV = {}, idP = {}, idR = {}, idI = {};
  s.vts.forEach(v => { idV[v.id] = 1; }); s.peds.forEach(x => { idP[x.id] = 1; });
  db.ventas = db.ventas.filter(v => !idV[v.id]); db.pedidos = db.pedidos.filter(x => !idP[x.id]);
  // 2) Rollos hechos: la materia vuelve al stock (si ya se vendieron fuera de esas fechas, se dejan)
  let rolNo = 0;
  s.rols.forEach(x => {
    const p = prod(x.productoId);
    if (p && (p.hechos || 0) < x.rollos - 1e-6) { rolNo++; return; }
    if (p) { p.stockG = r2(p.stockG + x.gramos - (x.excesoG || 0)); p.hechos = r2((p.hechos || 0) - x.rollos); }
    idR[x.id] = 1;
  });
  db.produccion = db.produccion.filter(x => !idR[x.id]);
  // 3) Ingresos de materia: se resta del stock
  s.ings.forEach(x => { const p = prod(x.productoId); if (p) p.stockG = Math.max(0, r2(p.stockG - x.gramos)); idI[x.id] = 1; });
  db.entradas = db.entradas.filter(x => !idI[x.id]);
  anotar('pruebas_borradas', 'Borró datos de prueba del ' + s.d1 + ' al ' + s.d2 + ': ' + res);
  guardar(); cerrarModal(); render();
  toast(rolNo ? 'Listo. ' + plu(rolNo, 'registro de rollos hechos se dejó', 'registros de rollos hechos se dejaron') + ' porque ya se vendieron' : 'Datos de prueba borrados');
}
"""

parchar(A, "\niniciar();\n", JS + "\niniciar();\n")
parchar(A, "    it(ICO.historial, 'Historial', 'menuHistorial()') +\n",
"    it(ICO.historial, 'Historial', 'menuHistorial()') +\n    (!NUBE || adm ? it(ICO.borrar, 'Borrar pruebas', 'menuModal(formLimpieza)') : '') +\n")

I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche21
- Menú lateral > Borrar pruebas (solo el administrador en modo nube; en modo local, cualquiera). Pide Desde y Hasta (por defecto hoy) y tres casillas: Ventas y pedidos, Rollos hechos, Ingresos de materia. Muestra cuántos registros se borran y pide confirmar. Funciones en app.js: formLimpieza, selLimpieza, prevLimpieza, limpiarPruebas.
- Al borrar, el stock vuelve a como estaba: las ventas devuelven rollos hechos (las viejas sin modo devuelven gramos), los rollos hechos devuelven la materia al stock y quitan los rollos listos (si esos rollos ya se vendieron fuera de las fechas, ese registro se deja), los ingresos restan la materia (el stock no baja de 0). Un pedido cuenta si se anotó o se entregó en las fechas; al borrarlo se borran también sus ventas.
- No restaura el costo por kilo ni el peso del rollo que cambió un ingreso de prueba (se corrigen en Editar). Se anota en el registro de cambios (tipo pruebas_borradas). Lo borrado no se puede recuperar.
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche21 aplicado (Borrar pruebas en el menú)')
