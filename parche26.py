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

# ---- 1. La etiqueta ahora depende de si es kilo o libra ----
parchar(A, "const lblCosto = c => esSalsa(c) ? 'Precio de la caneca' : 'Precio del kilo';",
 "const lblCosto = (c, u) => esSalsa(c) ? 'Precio de la caneca' : (u === 'lb' ? 'Precio de la libra' : 'Precio del kilo');")

# ---- 2. Donde se muestra el precio en la tarjeta del producto y en el resumen ----
parchar(A, "'<div class=\"lis\"><span>' + lblCosto(catDe(p)) + '</span>",
 "'<div class=\"lis\"><span>' + lblCosto(catDe(p), p.unidadCosto) + '</span>")
parchar(A, "lblCosto(catDe(x.p))", "lblCosto(catDe(x.p), x.p.unidadCosto)", 2)

# ---- 3. Formulario: selector Kilo / Libra (no sale en Salsas) ----
parchar(A, "    '<label id=\"f-costo-l\">' + lblCosto(p.categoria || 'Aliños') + ' ($)</label>",
 "    '<div id=\"f-uc-w\"' + (esSalsa(p.categoria || 'Aliños') ? ' style=\"display:none\"' : '') + '><label>Se compra por</label><select id=\"f-ucosto\" onchange=\"etiquetaCosto()\"><option value=\"kg\"' + (p.unidadCosto !== 'lb' ? ' selected' : '') + '>Kilo</option><option value=\"lb\"' + (p.unidadCosto === 'lb' ? ' selected' : '') + '>Libra</option></select></div>' +\n    '<label id=\"f-costo-l\">' + lblCosto(p.categoria || 'Aliños', p.unidadCosto) + ' ($)</label>")

parchar(A, "  $('#f-costo-l').textContent = lblCosto(c) + ' ($)';",
 "  $('#f-uc-w').style.display = esSalsa(c) ? 'none' : '';\n  $('#f-costo-l').textContent = lblCosto(c, $('#f-ucosto').value) + ' ($)';")

# ---- 4. Guardar la unidad y anotarla si cambia ----
parchar(A, "costoKilo: num($('#f-costo').value), hechos: r2(num($('#f-stock').value)) };",
 "costoKilo: num($('#f-costo').value), unidadCosto: esSalsa($('#f-cat').value) ? 'kg' : $('#f-ucosto').value, hechos: r2(num($('#f-stock').value)) };")
parchar(A, "const o = Object.assign({}, prod(id)), CP = [",
 "const o = Object.assign({}, prod(id)), CP = [['unidadCosto', 'Se compra por', x => x === 'lb' ? 'Libra' : 'Kilo'], ")
parchar(A, "['costoKilo', lblCosto($('#f-cat').value), money]",
 "['costoKilo', lblCosto($('#f-cat').value, d.unidadCosto), money]")
parchar(A, "const cb = CP.filter(c => (o[c[0]] || 0) !== (d[c[0]] || 0))",
 "o.unidadCosto = o.unidadCosto || 'kg';\n    const cb = CP.filter(c => !(c[0] === 'unidadCosto' && esSalsa(d.categoria)) && (o[c[0]] || 0) !== (d[c[0]] || 0))")

# ---- Version nueva + contexto ----
I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))
X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche26 (kilo o libra en el producto)
- En Nuevo producto / Editar producto hay un selector "Se compra por" (Kilo o Libra) justo arriba del precio. La etiqueta del precio cambia a "Precio del kilo" o "Precio de la libra". Se guarda en p.unidadCosto ('kg' o 'lb'; si no existe se toma como kg).
- En Salsas no sale el selector: sigue siendo "Precio de la caneca".
- El precio se guarda tal cual lo escribes (no se convierte): el gasto del mes sigue siendo ese precio. El cambio de unidad se anota en el Historial como cualquier otra edicion del producto.
"""
for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche26 aplicado (kilo o libra en el producto)')
