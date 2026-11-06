import sys, re, time

F = {}
def leer(a):
    if a not in F:
        F[a] = open(a, encoding='utf-8').read()
    return F[a]

def parchar(a, viejo, nuevo, opcional=False):
    s = leer(a); n = s.count(viejo)
    if n == 0 and opcional:
        return
    if n != 1:
        print('ERROR (' + str(n) + ' veces) en ' + a + ':', viejo[:70]); sys.exit(1)
    F[a] = s.replace(viejo, nuevo)

A = 'js/app.js'

# ===== iconos de línea (mismo estilo de la barra de abajo) =====
parchar(A, "let vistaPrev = null;\n", r"""const ICO = {
  rollos: ic('<path d="M6 5l1.5-2L9 5l1.5-2L12 5l1.5-2L15 5l1.5-2L18 5v14l-1.5 2-1.5-2-1.5 2-1.5-2-1.5 2L9 19l-1.5 2L6 19z"/><path d="M9.5 10h5M10.5 14h3"/>'),
  pedidos: ic('<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4h6v3H9z"/><path d="M9 12h6M9 16h4"/>'),
  usuarios: ic('<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M17 14c2.4 0 4 1.9 4 4.5"/>'),
  respaldo: ic('<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5"/><path d="M4 19h16"/>'),
  salir: ic('<path d="M10 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h5"/><path d="M15 8l4 4-4 4M19 12H9"/>')
};
let vistaPrev = null;
""")

# ===== menú lateral sin emojis =====
parchar(A, "it('📋',", "it(ICO.pedidos,")
parchar(A, "it('👥',", "it(ICO.usuarios,")
parchar(A, "it('💾',", "it(ICO.respaldo,")
parchar(A, "it('🚪',", "it(ICO.salir,")

# ===== botón Rollos hechos con icono =====
parchar(A, ">🧆 Rollos hechos</button>", ">' + ICO.rollos + ' Rollos hechos</button>")
parchar(A, "4px\">🧆 Rollos hechos' + (exc", "4px\">Rollos hechos' + (exc", True)
parchar(A, ">👥 Usuarios' +", ">' + ICO.usuarios + ' Usuarios' +", True)

# ===== quitar "Con ese stock se pueden hacer N rollos · ≈ N unidades" =====
parchar(A, "'<br>Con ese stock se pueden hacer ' + rollosDisp(p).toLocaleString('es-CO') + ' rollos · ≈ ' + Math.floor(rollosDisp(p) * p.unidadesRollo).toLocaleString('es-CO') + ' unidades<br>' : '')", "'<br>' : '')")

# ===== estilos =====
C = 'css/styles.css'
leer(C)
F[C] += r"""
.mi span{display:grid;place-items:center;font-size:1rem}
.btn .ic{width:18px;height:18px;vertical-align:-4px;margin-right:4px}
"""

I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
parchar(X, "- [x] Rollos hechos puede pasarse del stock: se registra y avisa que salieron más de lo calculado\n",
"""- [x] Rollos hechos puede pasarse del stock: se registra y avisa que salieron más de lo calculado
- [x] Sin emojis en el menú lateral ni en el botón Rollos hechos: ahora son iconos de línea (ICO en app.js)
- [x] Quitada la línea "Con ese stock se pueden hacer N rollos · ≈ N unidades" de cada producto en Stock
""", True)
F[X] += """
## Cambios parche11
- Stock: quitada la línea "Con ese stock se pueden hacer N rollos · ≈ N unidades" de cada producto.
- Iconos: el botón "Rollos hechos" y los items del menú lateral (Pedidos, Usuarios, Respaldo, Cerrar sesión) usan iconos SVG de línea, igual que la barra de abajo. Están en el objeto ICO de app.js (se crean con ic()). Regla: no usar emojis para botones ni menús; usar ic() con trazo.
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche11 aplicado (sin línea de stock, iconos en vez de emojis)')
