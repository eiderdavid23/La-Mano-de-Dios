import sys, re, time

F = {}
def leer(a):
    if a not in F:
        F[a] = open(a, encoding='utf-8').read()
    return F[a]

def parchar(a, viejo, nuevo):
    s = leer(a); n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces) en ' + a + ':', viejo[:70]); sys.exit(1)
    F[a] = s.replace(viejo, nuevo)

def bloque(a, ini, fin, nuevo):
    s = leer(a); i = s.find(ini)
    if i < 0 or s.count(ini) != 1:
        print('ERROR: no encuentro (o se repite) el inicio:', ini[:60]); sys.exit(1)
    j = s.find(fin, i + 1)
    if j < 0:
        print('ERROR: no encuentro el final:', fin[:60]); sys.exit(1)
    F[a] = s[:i] + nuevo + s[j:]

A = 'js/app.js'

# ===== iconos que faltaban =====
parchar(A, "\n};\nlet vistaPrev = null;\n", r""",
  hora: ic('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
  persona: ic('<circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.9 3.1-7 7-7s7 3.1 7 7"/>'),
  nota: ic('<path d="M6 3h9l4 4v14H6z"/><path d="M9 12h7M9 16h5"/>'),
  alerta: ic('<path d="M12 3 2.5 20h19z"/><path d="M12 10v5M12 17.5v.5"/>'),
  check: ic('<path d="m5 12.5 4.5 4.5L19 7.5"/>')
};
let vistaPrev = null;
""")

# ===== quitar TODOS los emojis que quedan =====
s = leer(A)
s = s.replace(">✅ Entregar</button>", ">' + ICO.check + ' Entregar</button>")
# mensajes cortos (toast): sin emoji
def toast_limpio(m):
    t = m.group(0)
    t = re.sub(r'\s?✅', '', t)
    t = re.sub(r'⚠️\s?', '', t)
    return t
s = '\n'.join(toast_limpio(re.match(r'.*', l)) if 'toast(' in l else l for l in s.split('\n'))
# solo texto
for e in ['📦 ', '📋 ', '🛒 ', '✅ ', '⏳ ']:
    s = s.replace(e, '')
s = s.replace(' ⚠️</h2>', '</h2>').replace(' ⏳</h2>', '</h2>')
s = s.replace(" 👑 administrador", " · administrador")
s = s.replace("(x.admin ? ' 👑' : '')", "(x.admin ? ' <span class=\"tag\">Administrador</span>' : '')")
# iconos en línea
for e, n in [('🕒', 'hora'), ('👤', 'persona'), ('📝', 'nota'), ('⚠️', 'alerta')]:
    s = re.sub(e + ' ?', "' + ICO." + n + " + ' ", s)
F[A] = s
quedan = re.findall(r'[\U0001F300-\U0001FAFF\u2600-\u27BF\u23F3\u2705]\ufe0f?', s)
if quedan:
    print('AVISO: quedan emojis sin cambiar:', ''.join(quedan))

# ===== Stock: tarjeta de producto más clara =====
bloque(A, "function listaStock() {", "function opcionesCat(", r"""function listaStock() {
  const l = filtrados();
  if (!l.length) return '<div class="empty">No hay productos con ese filtro</div>';
  const kv = (k, v) => '<div class="kv"><span>' + k + '</span><b>' + v + '</b></div>';
  return l.map(p => {
    const g = gpr(p), ga = gananciaRollo(p), cr = costoRollo(p);
    return '<div class="item ' + (bajo(p) ? 'low' : '') + '"><div class="row"><div><div class="name">' + esc(p.nombre) + '</div><div class="meta"><span class="tag">' + esc(catDe(p)) + '</span></div></div>' +
      '<span class="pill ' + (bajo(p) ? 'low' : '') + '"><small>En bodega</small>' + fmtG(dispG(p)) + (g > 0 ? '<small>para ' + rollosDisp(p).toLocaleString('es-CO') + ' rollos</small>' : '') + '</span></div>' +
      '<div class="kvs">' +
      kv('Rollos listos para vender', fmt(p.hechos || 0) + (apartadoR(p) > 0 ? '<small>' + fmt(apartadoR(p)) + ' apartados en pedidos</small>' : '')) +
      kv('Rollos hechos', 'hoy ' + fmt(hechosEn(p.id, hoy())) + ' · este mes ' + fmt(hechosMes(p.id, hoy().slice(0, 7)))) +
      (g > 0
        ? kv('Cada rollo', fmtG(g) + ' · ' + fmt(p.unidadesRollo) + ' unidades') +
          kv('De la materia salen', '1 kilo = ' + fmt(1000 / g) + ' rollos<small>1 libra = ' + fmt(500 / g) + ' rollos</small>') +
          kv('Precio de venta', money(p.precio) + ' por rollo') +
          kv('Costo', money(cr) + ' por rollo') +
          kv('Ganancia', '<span class="' + gCls(ga) + '">' + money(ga) + '</span> por rollo<small>' + fmt(cr > 0 ? ga / cr * 100 : 0) + ' % sobre el costo</small>')
        : kv('Precio de venta', money(p.precio) + ' por rollo') + '<div class="kv"><span class="neg">Falta definir los gramos por rollo. Toca Editar.</span></div>') +
      '</div>' +
      '<div class="actions"><button class="btn main" onclick="formIngreso(\'' + p.id + '\')">＋ Ingresar kilos/libras</button><button class="btn main" onclick="formProduccion(\'' + p.id + '\')">' + ICO.rollos + ' Rollos hechos</button><button class="btn" onclick="formProducto(\'' + p.id + '\')">Editar</button><button class="btn del" onclick="borrarProducto(\'' + p.id + '\')">Borrar</button></div></div>';
  }).join('');
}

""")

# ===== estilos =====
C = 'css/styles.css'
leer(C)
F[C] += r"""
.kvs{margin-top:12px;border-top:1px solid var(--line)}
.kv{display:flex;justify-content:space-between;align-items:baseline;gap:14px;padding:8px 0;border-bottom:1px solid var(--line);font-size:.86rem}
.kv:last-child{border-bottom:none}
.kv span{color:var(--mut)}
.kv b{text-align:right;font-weight:700}
.kv b small{display:block;font-weight:600;color:var(--mut);font-size:.74rem;margin-top:1px}
.meta .ic,.sub .ic,.hint .ic,.dsec .ic,.dt .ic,.tag .ic{width:14px;height:14px;vertical-align:-2px}
.preview .ic{width:17px;height:17px;vertical-align:-3px}
"""

I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche12
- Sin emojis en toda la app: los mensajes cortos van en texto y los lugares con icono usan ICO (hora, persona, nota, alerta, check). Regla: no usar emojis; usar ic() con trazo.
- Stock: la tarjeta de cada producto ahora son filas con título claro (Rollos listos para vender, Rollos hechos hoy / este mes, Cada rollo, De la materia salen, Precio de venta, Costo, Ganancia). La burbuja de la derecha dice "En bodega" con los gramos y para cuántos rollos alcanza.
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche12 aplicado (sin emojis + tarjeta de stock clara)')
