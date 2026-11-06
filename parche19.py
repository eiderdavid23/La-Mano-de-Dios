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

# ---- Ayudas: las salsas se muestran en litros / ml ----
parchar(A, "const uniTxt = u => u === 'ca' ? 'canecas' : (u || 'kg');",
r"""const uniTxt = u => u === 'ca' ? 'canecas' : (u || 'kg');
// Las salsas guardan el stock en mililitros (1 litro = 1000) pero se muestran en litros
const unidS = p => !!p && esSalsa(catDe(p));
const fmtV = (p, v) => unidS(p) ? (Math.abs(v) >= 1000 ? fmt(v / 1000) + ' L' : fmt(v) + ' ml') : fmtG(v);""")

# ---- Formulario de producto ----
parchar(A, """function cambiarCatForm() {
  const s = esSalsa($('#f-cat').value);
  $('#f-b-sal').style.display = s ? '' : 'none'; $('#f-b-ali').style.display = s ? 'none' : '';
  desdePrecio();
}""", r"""let catEsSalsa = false;
function etiquetasForm() {
  const s = esSalsa($('#f-cat').value);
  $('#f-l-gpr').textContent = s ? 'Mililitros que lleva 1 rollo' : 'Gramos que pesa 1 rollo';
  $('#f-l-min').textContent = s ? 'Avisar cuando queden (litros)' : 'Avisar cuando queden (gramos)';
  $('#f-l-stock').textContent = $('#f-l-stock').dataset.b + (s ? ' (litros)' : ' (gramos)');
}
function cambiarCatForm() {
  const s = esSalsa($('#f-cat').value);
  $('#f-b-sal').style.display = s ? '' : 'none'; $('#f-b-ali').style.display = s ? 'none' : '';
  if (s !== catEsSalsa) {
    ['#f-stock', '#f-min'].forEach(q => { const v = num($(q).value); if (v) $(q).value = r2(s ? v / 1000 : v * 1000); });
    catEsSalsa = s;
  }
  etiquetasForm(); hintGr(); desdePrecio();
}""")
parchar(A, """<label>Gramos que pesa 1 rollo</label><input id="f-gpr\"""", """<label id="f-l-gpr">Gramos que pesa 1 rollo</label><input id="f-gpr\"""")
parchar(A, r"""'<label>Avisar cuando queden (gramos)</label><input id="f-min" type="number" inputmode="decimal" value="' + p.minimoG + '">' +""",
r"""'<label id="f-l-min">Avisar cuando queden (gramos)</label><input id="f-min" type="number" inputmode="decimal" value="' + (unidS(p) ? r2(p.minimoG / 1000) : p.minimoG) + '">' +""")
parchar(A, r"""'<label>' + (id ? 'Stock actual' : 'Stock inicial') + ' (gramos)</label><input id="f-stock" type="number" inputmode="decimal" value="' + (p.stockG || 0) + '">' +""",
r"""'<label id="f-l-stock" data-b="' + (id ? 'Stock actual' : 'Stock inicial') + '">' + (id ? 'Stock actual' : 'Stock inicial') + ' (gramos)</label><input id="f-stock" type="number" inputmode="decimal" value="' + (unidS(p) ? r2((p.stockG || 0) / 1000) : (p.stockG || 0)) + '">' +""")
parchar(A, "  hintGr(); desdePrecio();\n}\nconst esSalsa", "  catEsSalsa = esSalsa($('#f-cat').value); etiquetasForm();\n  hintGr(); desdePrecio();\n}\nconst esSalsa")
parchar(A, "function hintGr() {\n  const g = num($('#f-gpr').value);\n",
r"""function hintGr() {
  const g = num($('#f-gpr').value);
  if (esSalsa($('#f-cat').value)) { $('#f-hint').textContent = g > 0 ? '1 litro ≈ ' + fmt(1000 / g) + ' rollos' : 'Escribe cuántos mililitros lleva un rollo. Así sabes cuántos rollos salen por litro.'; return; }
""")
parchar(A, "const d = { nombre, categoria:", "const fx = esSalsa($('#f-cat').value) ? 1000 : 1, fmtU = v => fmtV(fx === 1000 ? { categoria: 'Salsas' } : {}, v);\n  const d = { nombre, categoria:")
parchar(A, "minimoG: num($('#f-min').value), stockG: r2(num($('#f-stock').value)) };", "minimoG: r2(num($('#f-min').value) * fx), stockG: r2(num($('#f-stock').value) * fx) };")
parchar(A, "['gramosPorRollo', 'Gramos por rollo', fmtG]", "['gramosPorRollo', fx === 1000 ? 'Mililitros por rollo' : 'Gramos por rollo', fmtU]")
parchar(A, "['minimoG', 'Mínimo en bodega', fmtG]", "['minimoG', 'Mínimo en bodega', fmtU]")
parchar(A, "['stockG', 'Gramos en bodega', fmtG]", "['stockG', fx === 1000 ? 'Litros en bodega' : 'Gramos en bodega', fmtU]")

# ---- Tarjeta de stock y alertas ----
parchar(A, "kv('Peso de cada rollo', fmtG(g)) + kv('Unidades por rollo', fmt(p.unidadesRollo)) + kv('Rollos por kilo', fmt(1000 / g)) + kv('Rollos por libra', fmt(500 / g))",
"kv(unidS(p) ? 'Lo que lleva cada rollo' : 'Peso de cada rollo', fmtV(p, g)) + kv('Unidades por rollo', fmt(p.unidadesRollo)) + (unidS(p) ? kv('Rollos por litro', fmt(1000 / g)) : kv('Rollos por kilo', fmt(1000 / g)) + kv('Rollos por libra', fmt(500 / g)))")
parchar(A, "fmtG(dispG(p))", "fmtV(p, dispG(p))", 2)
parchar(A, "Falta definir los gramos por rollo. Toca Editar.", "' + (unidS(p) ? 'Falta definir los mililitros por rollo. Toca Editar.' : 'Falta definir los gramos por rollo. Toca Editar.') + '")
parchar(A, "'Falta definir gramos por rollo'", "(unidS(p) ? 'Falta definir mililitros por rollo' : 'Falta definir gramos por rollo')")

# ---- Ingreso de stock ----
parchar(A, "Las salsas se compran por caneca. Para el stock se cuenta 1 litro = 1000 g", "Las salsas se compran por caneca. Se suma al stock en litros")
parchar(A, "\n      '<label>Gramos que pesa 1 rollo</label>", "\n      '<label>Mililitros que lleva 1 rollo</label>")
parchar(A, "'= ' + fmt(g) + ' g'", "'= ' + fmtV(p, g)")
parchar(A, "fmtG(dispG(p) + g)", "fmtV(p, dispG(p) + g)")
parchar(A, "return toast('Escribe cuántos gramos pesa 1 rollo');", "return toast(enCaneca() ? 'Escribe cuántos mililitros lleva 1 rollo' : 'Escribe cuántos gramos pesa 1 rollo');")
parchar(A, "fmt(g) + ' g (' + fmt(g / 1000) + ' kilos).'", "(enCaneca() ? fmt(g / 1000) + ' litros.' : fmt(g) + ' g (' + fmt(g / 1000) + ' kilos).')")
parchar(A, "toast('+' + fmt(g) + ' g');", "toast('+' + fmtV(p, g));")

# ---- Rollos hechos ----
parchar(A, "return toast('Primero define los gramos por rollo (Editar)');", "return toast(unidS(p) ? 'Primero define los mililitros por rollo (Editar)' : 'Primero define los gramos por rollo (Editar)');")
parchar(A, "Descuenta los gramos del stock", "Descuenta ' + (unidS(p) ? 'los litros' : 'los gramos') + ' del stock")
parchar(A, "fmtG(-resto)", "fmtV(p, -resto)")
parchar(A, "El stock queda en 0 g.</small>", "El stock queda en ' + (unidS(p) ? '0 L' : '0 g') + '.</small>")
parchar(A, "fmtG(q * gpr(p))", "fmtV(p, q * gpr(p))")
parchar(A, "fmtG(Math.max(0, resto))", "fmtV(p, Math.max(0, resto))")
parchar(A, "'Ahora hay ' + fmtG(p.stockG)", "'Ahora hay ' + fmtV(p, p.stockG)")
parchar(A, "Los gramos vuelven al stock.", "Lo que se gastó vuelve al stock.")

parchar(A, "filaD('Gramos por rollo', gr ? fmtG(gr) : '') + filaD('Materia usada', fmtG(x.gramos))",
"filaD(unidS(p) ? 'Mililitros por rollo' : 'Gramos por rollo', gr ? fmtV(p, gr) : '') + filaD('Materia usada', fmtV(p, x.gramos))")
parchar(A, "fmtG(x.quedaronG)", "fmtV(p, x.quedaronG)")
parchar(A, "fmtG(exc)", "fmtV(p, exc)")

# ---- Detalle del ingreso y resumen del mes ----
parchar(A, "filaD('Equivale a', fmtG(x.gramos) + ' (' + fmt(x.gramos / 1000) + ' kg)')",
"(x.unidad === 'ca' ? filaD('Total', fmt(x.gramos / 1000) + ' litros') : filaD('Equivale a', fmtG(x.gramos) + ' (' + fmt(x.gramos / 1000) + ' kg)'))")
parchar(A, "filaD('Costo por kilo', x.costoKilo ? money(x.costoKilo) : '')", "filaD(x.unidad === 'ca' ? 'Costo por litro' : 'Costo por kilo', x.costoKilo ? money(x.costoKilo) : '')")
parchar(A, "fmtG(x.stockDespuesG)", "fmtV(p, x.stockDespuesG)")
parchar(A, "{ n: x.nombre, h: 0, g: 0 }", "{ n: x.nombre, h: 0, g: 0, s: unidS(prod(x.productoId)) }")
parchar(A, "fmtG(x.g)", "fmtV(x.s ? { categoria: 'Salsas' } : {}, x.g)")
parchar(A, "fmt(suma(en, 'gramos') / 1000) + ' kg</b>",
"fmt(suma(en.filter(x => x.unidad !== 'ca'), 'gramos') / 1000) + ' kg' + (en.some(x => x.unidad === 'ca') ? ' · ' + fmt(suma(en.filter(x => x.unidad === 'ca'), 'gramos') / 1000) + ' L' : '') + '</b>")

# ---- Versión y contexto ----
I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche19
- Las salsas se ven SOLO en litros y mililitros (nada de gramos ni kilos). Por dentro el stock de una salsa sigue guardado en el mismo campo (stockG, minimoG, gramosPorRollo) pero en MILILITROS (1 litro = 1000); la pantalla lo muestra como \"20 L\" o \"30 ml\". Los aliños siguen en gramos/kilos.
- Ayudas en app.js: unidS(p) (es salsa), fmtV(p, valor) (muestra en L/ml o en g), esSalsa(categoria).
- Producto de salsa: \"Mililitros que lleva 1 rollo\", \"Avisar cuando queden (litros)\", \"Stock (litros)\". Al cambiar la categoría en el formulario, los campos de stock y aviso se convierten solos y las etiquetas cambian (etiquetasForm, cambiarCatForm).
- Ingreso de salsa: canecas x litros por caneca = litros que se suman. Costo por caneca; el costo por litro queda en p.costoKilo. Tarjeta de stock: \"Lo que lleva cada rollo\" y \"Rollos por litro\".
- Historial/detalles de salsas dicen litros y mililitros; en Ganancias, \"Materia ingresada\" muestra los kg de aliños y aparte los litros de salsas.
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche19 aplicado (salsas solo en litros)')
