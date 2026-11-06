import sys, re, time

F = {}
def leer(a):
    if a not in F:
        F[a] = open(a, encoding='utf-8').read()
    return F[a]

def bloque(a, ini, fin, nuevo):
    s = leer(a); i = s.find(ini)
    if i < 0 or s.count(ini) != 1:
        print('ERROR: no encuentro (o se repite) el inicio:', ini[:60]); sys.exit(1)
    j = s.find(fin, i + 1)
    if j < 0:
        print('ERROR: no encuentro el final:', fin[:60]); sys.exit(1)
    F[a] = s[:i] + nuevo + s[j:]

A = 'js/app.js'

# ===== Stock: tarjeta simple (lo importante arriba, el resto en "Ver más datos") =====
bloque(A, "function listaStock() {", "function opcionesCat(", r"""const stkAb = {};
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

""")

# ===== estilos =====
C = 'css/styles.css'
leer(C)
F[C] += r"""
.lis{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin-top:12px;font-size:.86rem;font-weight:600;color:var(--mut)}
.lis b{font:800 1.05rem var(--f-d);color:var(--txt);text-align:right}
.lis b small{font:600 .7rem system-ui,sans-serif;color:var(--mut)}
.mas{margin-top:8px}
.mas summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:8px;border-radius:12px;background:var(--soft);font-size:.8rem;font-weight:700;color:var(--txt)}
.mas summary::-webkit-details-marker{display:none}
.mas summary::after{content:"";width:7px;height:7px;margin:-3px 0 0 9px;border:solid currentColor;border-width:0 2px 2px 0;transform:rotate(45deg);transition:transform .2s}
.mas[open] summary::after{margin-top:3px;transform:rotate(-135deg)}
.mas[open] .kv:first-of-type{margin-top:6px}
"""

I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche14
- Stock: la tarjeta del producto vuelve a ser simple. Se ve siempre: nombre, categoría, "En bodega" (gramos y para cuántos rollos alcanza), "Listos para vender" y la barra de ganancia (verde) o pérdida (roja) por rollo. El resto va escondido en el botón "Ver más datos" como filas con título (hechos hoy y este mes, peso de cada rollo, unidades por rollo, rollos por kilo, rollos por libra, precio de venta, costo). Los cuadritos de parche13 ya no se usan.
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche14 aplicado (tarjeta simple + Ver más datos)')
