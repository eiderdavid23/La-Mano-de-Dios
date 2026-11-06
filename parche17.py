import sys, re, time

F = {}
def leer(a):
    if a not in F:
        F[a] = open(a, encoding='utf-8').read()
    return F[a]

def parchar(a, viejo, nuevo):
    s = leer(a); n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces) en ' + a + ':', viejo[:80]); sys.exit(1)
    F[a] = s.replace(viejo, nuevo)

A = 'js/app.js'

# ---- Ayudas ----
parchar(A, "const costoForm = () => num($('#f-costo').value) * num($('#f-gpr').value) / 1000;",
r"""const esSalsa = c => String(c || '').trim().toLowerCase() === 'salsas';
const uniTxt = u => u === 'ca' ? 'canecas' : (u || 'kg');
const costoKiloForm = () => {
  if (esSalsa($('#f-cat').value)) { const kc = num($('#f-kc').value); return kc > 0 ? num($('#f-costoc').value) / kc : 0; }
  return num($('#f-costo').value);
};
function cambiarCatForm() {
  const s = esSalsa($('#f-cat').value);
  $('#f-b-sal').style.display = s ? '' : 'none'; $('#f-b-ali').style.display = s ? 'none' : '';
  desdePrecio();
}
const costoForm = () => costoKiloForm() * num($('#f-gpr').value) / 1000;""")

# ---- Formulario de producto: aliños por kilo, salsas por caneca ----
parchar(A, """'<label>Categoría</label><select id="f-cat">'""", """'<label>Categoría</label><select id="f-cat" onchange="cambiarCatForm()">'""")
parchar(A, r"""'<label>Costo por kilo ($)</label><input id="f-costo" type="number" inputmode="decimal" value="' + p.costoKilo + '" placeholder="Lo que pagas por 1 kilo" oninput="desdePrecio()">' +""",
r"""'<div id="f-b-ali"' + (esSalsa(p.categoria || (id ? 'Otro' : 'Aliños')) ? ' style="display:none"' : '') + '><label>Costo por kilo ($)</label><input id="f-costo" type="number" inputmode="decimal" value="' + p.costoKilo + '" placeholder="Lo que pagas por 1 kilo" oninput="desdePrecio()"></div>' +
    '<div id="f-b-sal"' + (esSalsa(p.categoria || (id ? 'Otro' : 'Aliños')) ? '' : ' style="display:none"') + '><label>Kilos que trae cada caneca</label><input id="f-kc" type="number" inputmode="decimal" value="' + (p.kilosCaneca || '') + '" placeholder="Ej: 20" oninput="desdePrecio()"><label>Costo por caneca ($)</label><input id="f-costoc" type="number" inputmode="decimal" value="' + (p.kilosCaneca && p.costoKilo ? r2(p.costoKilo * p.kilosCaneca) : '') + '" placeholder="Lo que pagas por 1 caneca" oninput="desdePrecio()"></div>' +""")
parchar(A, "'Escribe el costo por kilo y los gramos por rollo para calcular.'", "'Escribe el costo y los gramos por rollo para calcular.'")
parchar(A, "if (!nombre) return toast('Escribe el nombre');",
"""if (!nombre) return toast('Escribe el nombre');
  if (esSalsa($('#f-cat').value) && num($('#f-costoc').value) > 0 && num($('#f-kc').value) <= 0) return toast('Escribe cuántos kilos trae la caneca');""")
parchar(A, "costoKilo: num($('#f-costo').value),", "costoKilo: costoKiloForm(), kilosCaneca: num($('#f-kc').value),")
parchar(A, "['gramosPorRollo', 'Gramos por rollo', fmtG],", "['gramosPorRollo', 'Gramos por rollo', fmtG], ['kilosCaneca', 'Kilos por caneca', fmt],")

# ---- Ingreso de stock ----
parchar(A, "const gUni = () => { const u = $('#i-uni').value;",
"const enCaneca = () => !$('#i-uni');\nconst gUni = () => { if (enCaneca()) return num($('#i-kc').value) * 1000; const u = $('#i-uni').value;")
parchar(A, "  const p = prod(id);\n  modal('<h3>Ingresar ' + esc(p.nombre) + '</h3>",
r"""  const p = prod(id);
  if (esSalsa(catDe(p))) {
    modal('<h3>Ingresar ' + esc(p.nombre) + '</h3><div class="sub" style="margin:2px 0 0">Las salsas se compran por caneca. Se suma al stock en gramos (1 kilo = 1000 g)</div>' +
      '<label>Canecas que llegaron</label><input id="i-cant" type="number" inputmode="decimal" placeholder="Ej: 1" oninput="prevIngreso(\'' + id + '\')">' +
      '<label>Kilos que trae cada caneca</label><input id="i-kc" type="number" inputmode="decimal" value="' + (p.kilosCaneca || '') + '" placeholder="Ej: 20" oninput="prevIngreso(\'' + id + '\')">' +
      '<label>Gramos que pesa 1 rollo</label><input id="i-gpr" type="number" inputmode="decimal" value="' + (gpr(p) || '') + '" placeholder="Ej: 33" oninput="prevIngreso(\'' + id + '\')">' +
      '<label>Costo por caneca ($)</label><input id="i-costo" type="number" inputmode="decimal" value="' + (p.kilosCaneca && p.costoKilo ? r2(p.costoKilo * p.kilosCaneca) : '') + '" placeholder="Lo que pagas por 1 caneca">' +
      '<div class="preview" id="i-prev"></div>' +
      '<button class="btn main full" onclick="confirmarIngreso(\'' + id + '\')">Agregar al stock</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
    return prevIngreso(id);
  }
  modal('<h3>Ingresar ' + esc(p.nombre) + '</h3>""")
parchar(A, "if (gp <= 0) return toast('Escribe cuántos gramos pesa 1 rollo');",
"""if (gp <= 0) return toast('Escribe cuántos gramos pesa 1 rollo');
  if (enCaneca() && num($('#i-kc').value) <= 0) return toast('Escribe cuántos kilos trae la caneca');""")
parchar(A, "costoKilo = num($('#i-costo').value) * 1000 / gCosto();",
"costoKilo = enCaneca() ? num($('#i-costo').value) / num($('#i-kc').value) : num($('#i-costo').value) * 1000 / gCosto();")
parchar(A, "p.costoKilo = r2(costoKilo); p.gramosPorRollo = gp;",
"p.costoKilo = r2(costoKilo); p.gramosPorRollo = gp; if (enCaneca()) p.kilosCaneca = num($('#i-kc').value);")
parchar(A, "unidad: $('#i-uni').value,", "unidad: enCaneca() ? 'ca' : $('#i-uni').value, kilosCaneca: enCaneca() ? num($('#i-kc').value) : 0,")

# ---- Mostrar canecas en listas y detalle ----
s = leer(A)
if s.count("(x.unidad || 'kg')") != 2:
    print('ERROR: unidad en listas'); sys.exit(1)
F[A] = s.replace("(x.unidad || 'kg')", "uniTxt(x.unidad)")
parchar(A, "{ kg: 'kilos', lb: 'libras', g: 'gramos' }", "{ kg: 'kilos', lb: 'libras', g: 'gramos', ca: 'canecas' }")
parchar(A, "filaD('Llegó', fmt(x.cantidad) + ' ' + u) +", "filaD('Llegó', fmt(x.cantidad) + ' ' + u) + (x.kilosCaneca ? filaD('Kilos por caneca', fmt(x.kilosCaneca)) : '') +")

# ---- Botón del stock ----
parchar(A, "＋ Ingresar kilos/libras</button>", "＋ Ingresar ' + (esSalsa(catDe(p)) ? 'canecas' : 'kilos/libras') + '</button>")

# ---- Versión y contexto ----
I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
leer(X)
F[X] = F[X].replace("- [ ] Confirmar cómo se venden las salsas (¿también por rollos o por otra unidad?)", "- [x] Salsas: se venden igual, por rollo de 14 unidades; solo se compran por caneca (parche17)")
F[X] += """
## Cambios parche17
- Salsas se compran por CANECA, aliños por kilo. El stock sigue guardándose en gramos y las ventas por rollo no cambian; solo cambia cómo se ingresa.
- Producto nuevo/editar: al escoger la categoría Salsas, el costo por kilo se cambia por \"Kilos que trae cada caneca\" y \"Costo por caneca ($)\" (costoKilo = costo de caneca / kilos). Aliños y Otro siguen con \"Costo por kilo\". Se guarda p.kilosCaneca. Funciones: esSalsa, costoKiloForm, cambiarCatForm.
- Stock > Ingresar: en productos de Salsas el botón dice \"Ingresar canecas\" y el formulario pide canecas que llegaron, kilos por caneca, gramos por rollo y costo por caneca; suma al stock (canecas x kilos x 1000 g). Los ingresos guardan unidad 'ca' y kilosCaneca; las listas y el detalle dicen \"canecas\". La capacidad de la caneca se recuerda en el producto. enCaneca() indica el modo.
- Supuesto: la caneca se mide en kilos (si viene en litros, se escribe lo que pesa).
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche17 aplicado (salsas por caneca)')
