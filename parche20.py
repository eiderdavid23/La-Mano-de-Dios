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

# ---- Cuenta del rollo de salsa: por peso (rollo y litro) o por rollos que salen de 1 caneca ----
parchar(A, "const costoForm = () => costoKiloForm() * num($('#f-gpr').value) / 1000;",
r"""// ml que lleva 1 rollo: si dices cuántos rollos salen de 1 caneca, sale de ahí; si no, del peso del rollo y del peso de 1 litro
const mlRollo = (gr, gl, litros, rollos) => rollos > 0 && litros > 0 ? litros * 1000 / rollos : (gr > 0 && gl > 0 ? gr / gl * 1000 : 0);
const gprForm = () => esSalsa($('#f-cat').value) ? mlRollo(num($('#f-gpr').value), num($('#f-gl').value), num($('#f-kc').value), num($('#f-rc').value)) : num($('#f-gpr').value);
const costoForm = () => costoKiloForm() * gprForm() / 1000;""")
parchar(A, "  $('#f-l-gpr').textContent = s ? 'Mililitros que lleva 1 rollo' : 'Gramos que pesa 1 rollo';\n", "")
parchar(A, """value="' + p.gramosPorRollo + '" placeholder="Ej: 33\"""", """value="' + (unidS(p) ? (p.pesoRolloG || '') : p.gramosPorRollo) + '" placeholder="Ej: 33\"""")
parchar(A, """placeholder="Lo que pagas por 1 caneca" oninput="desdePrecio()"></div>'""",
r"""placeholder="Lo que pagas por 1 caneca" oninput="desdePrecio()"><label>Gramos que pesa 1 litro de salsa</label><input id="f-gl" type="number" inputmode="decimal" value="' + (p.gramosLitro || '') + '" placeholder="Pesa 1 litro en la balanza" oninput="desdePrecio()"><label>O: rollos que salen de 1 caneca</label><input id="f-rc" type="number" inputmode="decimal" value="' + (p.rollosCaneca || '') + '" placeholder="Si lo sabes, sin pesar nada" oninput="desdePrecio()"></div>'""")
parchar(A, "function desdePrecio() {\n", "function desdePrecio() {\n  hintGr();\n")
parchar(A, "  if (esSalsa($('#f-cat').value)) { $('#f-hint').textContent = g > 0 ? '1 litro ≈ ' + fmt(1000 / g) + ' rollos' : 'Escribe cuántos mililitros lleva un rollo. Así sabes cuántos rollos salen por litro.'; return; }\n",
r"""  if (esSalsa($('#f-cat').value)) {
    const ml = gprForm(), kc = num($('#f-kc').value);
    $('#f-hint').textContent = ml > 0 ? '1 rollo ≈ ' + fmt(ml) + ' ml · 1 litro ≈ ' + fmt(1000 / ml) + ' rollos' + (kc > 0 ? ' · 1 caneca ≈ ' + fmt(kc * 1000 / ml) + ' rollos' : '') : 'Escribe cuánto pesa 1 rollo y 1 litro de salsa, o cuántos rollos salen de 1 caneca.';
    return;
  }
""")
parchar(A, "gramosPorRollo: num($('#f-gpr').value), precio:", "gramosPorRollo: gprForm() || (fx === 1000 && id ? (prod(id).gramosPorRollo || 0) : 0), pesoRolloG: fx === 1000 ? num($('#f-gpr').value) : 0, gramosLitro: num($('#f-gl').value), rollosCaneca: num($('#f-rc').value), precio:")

# ---- Ingreso de salsa: pide el peso del litro y el del rollo, o los rollos que salieron ----
parchar(A, "const enCaneca = () => !$('#i-uni');",
"""const enCaneca = () => !$('#i-uni');
const gpIngreso = () => enCaneca() ? mlRollo(num($('#i-gpr').value), num($('#i-gl').value), num($('#i-kc').value), num($('#i-rc').value)) : num($('#i-gpr').value);""")
parchar(A, "\n      '<label>Mililitros que lleva 1 rollo</label><input id=\"i-gpr\" type=\"number\" inputmode=\"decimal\" value=\"' + (gpr(p) || '') + '\" placeholder=\"Ej: 33\" oninput=\"prevIngreso(\\'' + id + '\\')\">' +",
r"""
      '<label>Gramos que pesa 1 litro de salsa</label><input id="i-gl" type="number" inputmode="decimal" value="' + (p.gramosLitro || '') + '" placeholder="Pesa 1 litro en la balanza" oninput="prevIngreso(\'' + id + '\')">' +
      '<label>Gramos que pesa 1 rollo</label><input id="i-gpr" type="number" inputmode="decimal" value="' + (p.pesoRolloG || '') + '" placeholder="Ej: 370" oninput="prevIngreso(\'' + id + '\')">' +
      '<label>O: rollos que salen de 1 caneca</label><input id="i-rc" type="number" inputmode="decimal" value="' + (p.rollosCaneca || '') + '" placeholder="Si lo sabes, sin pesar nada" oninput="prevIngreso(\'' + id + '\')">' +""")
parchar(A, "gp = num($('#i-gpr').value)", "gp = gpIngreso()", 2)
parchar(A, "' · ≈ ' + fmt(Math.floor(g / gp)) + ' rollos'", "' · ≈ ' + fmt(Math.floor(g / gp)) + ' rollos' + (enCaneca() ? ' (cada rollo ≈ ' + fmt(gp) + ' ml)' : '')")
parchar(A, "enCaneca() ? 'Escribe cuántos mililitros lleva 1 rollo' :", "enCaneca() ? 'Escribe el peso del litro y del rollo, o cuántos rollos salen de 1 caneca' :")
parchar(A, "if (enCaneca()) p.kilosCaneca = num($('#i-kc').value);",
"if (enCaneca()) { p.kilosCaneca = num($('#i-kc').value); p.gramosLitro = num($('#i-gl').value); p.pesoRolloG = num($('#i-gpr').value); p.rollosCaneca = num($('#i-rc').value); }")

# ---- Textos ----
parchar(A, "Falta definir los mililitros por rollo. Toca Editar.", "Falta definir el peso del rollo y del litro (o los rollos por caneca). Toca Editar.")
parchar(A, "'Falta definir mililitros por rollo'", "'Falta definir el tamaño del rollo'")
parchar(A, "'Primero define los mililitros por rollo (Editar)'", "'Primero define el peso del rollo y del litro (Editar)'")
parchar(A, "kv(unidS(p) ? 'Lo que lleva cada rollo' : 'Peso de cada rollo', fmtV(p, g))",
"kv(unidS(p) ? 'Lo que lleva cada rollo' : 'Peso de cada rollo', fmtV(p, g)) + (unidS(p) && p.pesoRolloG ? kv('Peso de cada rollo', fmtG(p.pesoRolloG)) : '')")

# ---- Versión y contexto ----
I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche20
- Salsas: el tamaño del rollo se saca de dos formas (mlRollo en app.js). (1) Por peso: gramos que pesa 1 rollo y gramos que pesa 1 litro de salsa -> ml por rollo = gramos del rollo / gramos del litro x 1000. (2) Por rollos que salen de 1 caneca: ml por rollo = litros de la caneca x 1000 / rollos. Si se escriben los rollos por caneca, manda esa; si no, el peso.
- Se pide en Producto (nuevo/editar) y en Stock > Ingresar canecas. Se guardan en el producto: p.pesoRolloG (gramos del rollo), p.gramosLitro, p.rollosCaneca, p.kilosCaneca (litros de la caneca). p.gramosPorRollo sigue guardando los ML por rollo para que el resto de la app no cambie.
- El formulario muestra al vuelo \"1 rollo ≈ X ml · 1 litro ≈ N rollos · 1 caneca ≈ N rollos\". gprForm y gpIngreso dan los ml por rollo en cada formulario.
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche20 aplicado (salsas: peso del litro o rollos por caneca)')
