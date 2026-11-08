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

def entre(a, ini, fin, nuevo):
    s = leer(a)
    if s.count(ini) != 1 or s.count(fin) != 1:
        print('ERROR marcadores en ' + a + ':', ini[:60]); sys.exit(1)
    i = s.index(ini); j = s.index(fin)
    if j < i:
        print('ERROR orden de marcadores:', ini[:60]); sys.exit(1)
    F[a] = s[:i] + nuevo + s[j:]

def linea(a, inicio, nuevo):
    s = leer(a)
    if s.count(inicio) != 1:
        print('ERROR linea en ' + a + ':', inicio[:60]); sys.exit(1)
    i = s.index(inicio); j = s.index('\n', i)
    F[a] = s[:i] + nuevo + s[j:]

A = 'js/app.js'

# ---- 1. Nombre del costo segun categoria ----
parchar(A, "const gLbl = n => n < 0 ? 'Pérdida' : 'Ganancia';",
 "const gLbl = n => n < 0 ? 'Pérdida' : 'Ganancia';\nconst lblCosto = c => esSalsa(c) ? 'Precio de la caneca' : 'Precio del kilo';")

# Stock: etiqueta segun categoria
parchar(A, "<span>Precio del kilo</span><b>' + money(p.costoKilo)",
 "<span>' + lblCosto(catDe(p)) + '</span><b>' + money(p.costoKilo)")

# Formulario: etiqueta cambia al escoger categoria
parchar(A, "'<label>Categoría</label><select id=\"f-cat\">'",
 "'<label>Categoría</label><select id=\"f-cat\" onchange=\"etiquetaCosto()\">'")
parchar(A, "'<label>Precio del kilo ($; si es salsa, del litro)</label><input id=\"f-costo\"",
 "'<label id=\"f-costo-l\">' + lblCosto(p.categoria || 'Aliños') + ' ($)</label><input id=\"f-costo\"")
parchar(A, "const esSalsa = c => String(c || '').trim().toLowerCase() === 'salsas';",
 "const esSalsa = c => String(c || '').trim().toLowerCase() === 'salsas';\n" + r"""function etiquetaCosto() {
  const c = $('#f-cat').value;
  $('#f-costo-l').textContent = lblCosto(c) + ' ($)';
  $('#f-costo').placeholder = esSalsa(c) ? 'Ej: 120000' : 'Ej: 34000';
}""")

# Registro de cambios
parchar(A, "['costoKilo', 'Precio del kilo', money]", "['costoKilo', lblCosto($('#f-cat').value), money]")

# ---- 2. Aviso al registrar rollos hechos, mas claro ----
linea(A, "  $('#h-prev').textContent = 'Quedan '",
 r"""  $('#h-prev').textContent = 'Quedarán ' + fmt((p.hechos || 0) + q) + ' rollos listos. ' + nombreMes(ym) + ': ' + fmt(hechosMes(id, ym) + q) + ' rollos = ' + money(v) + (c > 0 ? ' − gasto ' + money(c) + ' = ' + gLbl(v - c).toLowerCase() + ' ' + money(Math.abs(v - c)) : '');""")

# ---- 3. Pantalla Ganancias clara ----
entre(A, "  const lista = db.productos.filter(p => hechosMes(p.id, ym) > 0)", "    '<h2 style=\"margin-top:22px\">Rollos hechos por día</h2>", r"""  const lista = db.productos.filter(p => hechosMes(p.id, ym) > 0).map(p => ({ p, h: hechosMes(p.id, ym), v: valorHecho(p, ym), c: costoMes(p, ym), g: gananciaMes(p, ym) })).sort((a, b) => b.g - a.g);
  const g = lista.reduce((a, x) => a + x.g, 0), vT = lista.reduce((a, x) => a + x.v, 0), cT = lista.reduce((a, x) => a + x.c, 0);
  const fila = (k, v) => '<div class="lis"><span>' + k + '</span><b>' + v + '</b></div>';
  const barra = n => '<div class="gan ' + gCls(n) + '"><span>' + gLbl(n) + '</span><b>' + money(Math.abs(n)) + '</b></div>';
  return '<div class="month"><button onclick="cambiarMes(-1)">‹</button><b>' + nombreMes(ym) + '</b><button onclick="cambiarMes(1)">›</button></div>' +
    '<div class="hero ' + gHero(g) + '"><small>' + gLbl(g) + ' del mes</small><b data-n="' + Math.abs(g) + '">' + money(Math.abs(g)) + '</b><span>' + fmt(suma(pr, 'rollos')) + ' rollos hechos en ' + nombreMes(ym) + '</span></div>' +
    '<h2>Resumen del mes</h2>' + (lista.length ? '<div class="item">' + fila('Rollos hechos', fmt(suma(pr, 'rollos'))) + fila('Valen (rollos × precio de venta)', money(vT)) + fila('Gastos de materia', '−' + money(cT)) + barra(g) + '</div>' +
      '<div class="sub" style="margin:0 0 6px">Ganancia = lo que valen los rollos hechos − lo que gastaste en la materia. Cada mes empieza de cero.</div>' : '<div class="empty">Sin rollos hechos este mes</div>') +
    (lista.length ? '<h2 style="margin-top:22px">Ganancia por producto</h2>' + lista.map(x => '<div class="item"><div class="row"><div><div class="name">' + esc(x.p.nombre) + '</div><div class="meta">' + fmt(x.h) + ' rollos hechos</div></div></div>' +
      fila('Valen', money(x.v)) + fila('Gasto · ' + lblCosto(catDe(x.p)).toLowerCase(), '−' + money(x.c)) + barra(x.g) +
      (x.c <= 0 ? '<div class="hint">Falta el ' + lblCosto(catDe(x.p)).toLowerCase() + ': ponlo en Editar para ver la ganancia real.</div>' : '') + '</div>').join('') : '') +
""")

# Total vendido pasa a la seccion de ventas (ya no confunde con la ganancia)
parchar(A, "margin:0 0 10px\">Toca un día para ver cada venta", "margin:0 0 10px\">Vendido en el mes: ' + money(suma(vm, 'total')) + '. Toca un día para ver cada venta")

# ---- Version nueva + contexto ----
I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))
X = 'CONTEXTO.md'
leer(X)
parchar(X, "\n\n## Pendiente", "\n- [x] Ganancias más claras (parche23): resumen del mes (rollos hechos, valen, gastos, ganancia) y tarjeta por producto\n- [x] Precio del kilo en aliños y Precio de la caneca en salsas (parche23)\n\n## Pendiente")
F[X] += """
## Cambios parche23 (Ganancias más claras y precio de la caneca)
- Producto: la etiqueta del costo depende de la categoría (lblCosto en app.js): Aliños y Otro = \"Precio del kilo\"; Salsas = \"Precio de la caneca\". Cambia sola al escoger la categoría en el formulario (etiquetaCosto). Se sigue guardando en p.costoKilo y el cálculo no cambió: es el gasto de la materia del mes. En salsas ahora se escribe lo que cuesta la caneca (antes era el litro): hay que reeditar las salsas que ya tenían precio por litro.
- Ganancias (vGanancias): arriba la Ganancia o Pérdida del mes; \"Resumen del mes\" con Rollos hechos, Valen (rollos x precio), Gastos de materia y Ganancia; luego una tarjeta por producto (Valen, Gasto, Ganancia). Si falta el precio del kilo/caneca avisa en rojo. El total vendido se pasó a \"Ventas día por día\".
- Al registrar rollos hechos, el aviso muestra: rollos = valor - gasto = ganancia.
- Sigue pendiente: las ventas guardan ganancia = total vendido (costoRollo = 0); revisar detalleVenta/detalleDia. Gastos del mes aparte (luz, transporte, etc.) sin hacer.
"""
for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche23 aplicado (ganancias claras + precio de la caneca)')
