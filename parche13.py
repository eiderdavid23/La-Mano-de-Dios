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

# ===== Stock: tarjeta más compacta, en cuadritos, con ganancia/pérdida en color =====
bloque(A, "function listaStock() {", "function opcionesCat(", r"""function listaStock() {
  const l = filtrados();
  if (!l.length) return '<div class="empty">No hay productos con ese filtro</div>';
  const tl = (k, v) => '<div class="tile"><span>' + k + '</span><b>' + v + '</b></div>';
  return l.map(p => {
    const g = gpr(p), ga = gananciaRollo(p), cr = costoRollo(p), ap = apartadoR(p);
    return '<div class="item ' + (bajo(p) ? 'low' : '') + '"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div><div class="meta"><span class="tag">' + esc(catDe(p)) + '</span></div></div>' +
      '<span class="pill ' + (bajo(p) ? 'low' : '') + '"><small>En bodega</small>' + fmtG(dispG(p)) + (g > 0 ? '<small>para ' + rollosDisp(p).toLocaleString('es-CO') + ' rollos</small>' : '') + '</span></div>' +
      '<div class="tiles">' +
      tl('Listos para vender', fmt(p.hechos || 0) + (ap > 0 ? ' <small>(' + fmt(ap) + ' apartados)</small>' : '')) +
      tl('Hechos hoy', fmt(hechosEn(p.id, hoy()))) +
      tl('Hechos este mes', fmt(hechosMes(p.id, hoy().slice(0, 7)))) +
      (g > 0
        ? tl('Cada rollo', fmtG(g)) + tl('Unidades por rollo', fmt(p.unidadesRollo)) + tl('Rollos por kilo', fmt(1000 / g)) + tl('Rollos por libra', fmt(500 / g)) +
          tl('Precio de venta', money(p.precio)) + tl('Costo', money(cr))
        : tl('Precio de venta', money(p.precio))) +
      '</div>' +
      (g > 0
        ? '<div class="gan ' + gCls(ga) + '"><span>' + gLbl(ga) + ' por rollo</span><b>' + money(Math.abs(ga)) + ' <small>(' + fmt(cr > 0 ? ga / cr * 100 : 0) + ' % sobre el costo)</small></b></div>'
        : '<div class="gan neg"><span>Falta definir los gramos por rollo. Toca Editar.</span></div>') +
      '<div class="actions"><button class="btn main" onclick="formIngreso(\'' + p.id + '\')">＋ Ingresar kilos/libras</button><button class="btn main" onclick="formProduccion(\'' + p.id + '\')">' + ICO.rollos + ' Rollos hechos</button><button class="btn" onclick="formProducto(\'' + p.id + '\')">Editar</button><button class="btn del" onclick="borrarProducto(\'' + p.id + '\')">Borrar</button></div></div>';
  }).join('');
}

""")

# ===== estilos =====
C = 'css/styles.css'
leer(C)
F[C] += r"""
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:10px}
.tile{background:var(--soft);border-radius:12px;padding:7px 9px;min-width:0}
.tile span{display:block;font-size:.66rem;color:var(--mut);line-height:1.2;font-weight:600}
.tile b{display:block;font:800 .92rem var(--f-d);margin-top:2px}
.tile b small,.gan b small{font:600 .68rem system-ui,sans-serif;opacity:.8}
.gan{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:6px;padding:9px 12px;border-radius:12px;background:var(--okbg);color:var(--ok);font-size:.8rem;font-weight:700}
.gan.neg{background:var(--badbg);color:var(--bad)}
.gan b{font:800 .95rem var(--f-d);text-align:right}
.item .actions{margin-top:10px}
"""

I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche13
- Stock: la tarjeta de cada producto es más compacta: cuadritos de 3 columnas (Listos para vender, Hechos hoy, Hechos este mes, Cada rollo, Unidades por rollo, Rollos por kilo, Rollos por libra, Precio de venta, Costo) y debajo una barra de color con la ganancia (verde) o la pérdida (roja) por rollo y su % sobre el costo.
- Arreglado: la ganancia y la pérdida volvieron a verse en color (en parche12 el CSS de .kv las pintaba de gris).
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche13 aplicado (tarjeta compacta + ganancia en color)')
