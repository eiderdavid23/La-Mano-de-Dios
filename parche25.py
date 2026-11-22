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

# ---- 1. Tipo nuevo en el registro de cambios ----
parchar(A, "rollos_deshechos: 'Rollos hechos deshechos' };",
 "rollos_deshechos: 'Rollos hechos deshechos', rollos_editados: 'Rollos hechos editados' };")

# ---- 2. Funciones para editar rollos hechos ----
parchar(A, "function lineaProd(x, vol) {", r"""function formEditarProd(id) {
  if (espera()) return;
  const x = db.produccion.find(y => y.id === id); if (!x) return;
  const ops = db.productos.map(p => '<option value="' + p.id + '"' + (p.id === x.productoId ? ' selected' : '') + '>' + esc(p.nombre) + '</option>').join('');
  modal('<h3>Editar rollos hechos</h3><div class="sub" style="margin:2px 0 0">Corrige el producto, la cantidad o el día. El cambio queda anotado en el Historial.</div>' +
    '<label>Producto</label><select id="e-prod">' + ops + '</select>' +
    '<label>Rollos hechos</label><input id="e-cant" type="number" inputmode="decimal" value="' + x.rollos + '">' +
    '<label>Día</label><input id="e-fec" type="date" value="' + x.fecha + '" max="' + hoy() + '">' +
    '<button class="btn main full" onclick="guardarEdicionProd(\'' + id + '\')">Guardar cambios</button><button class="btn full" onclick="cerrarModal()">Cancelar</button>');
}
function guardarEdicionProd(id) {
  if (espera()) return;
  const x = db.produccion.find(y => y.id === id); if (!x) return;
  const nid = $('#e-prod').value, q = num($('#e-cant').value), f = $('#e-fec').value || x.fecha;
  const pOld = prod(x.productoId), pNew = prod(nid);
  if (!pNew) return toast('Escoge el producto');
  if (q <= 0) return toast('Escribe cuántos rollos fueron');
  const mismo = x.productoId === nid;
  if (mismo && (pNew.hechos || 0) - x.rollos + q < -1e-6) return toast('Con ese número quedarían rollos en negativo: ya se vendieron');
  if (!mismo && pOld && (pOld.hechos || 0) < x.rollos - 1e-6) return toast('Esos rollos ya se vendieron de ' + pOld.nombre + '; no se pueden pasar a otro producto');
  const cb = [];
  if (!mismo) cb.push('Producto: ' + x.nombre + ' → ' + pNew.nombre);
  if (x.rollos !== q) cb.push('Rollos hechos: ' + fmt(x.rollos) + ' → ' + fmt(q));
  if (x.fecha !== f) cb.push('Día: ' + diaLargo(x.fecha) + ' → ' + diaLargo(f));
  if (!cb.length) { cerrarModal(); return toast('No cambiaste nada'); }
  const antes = x.nombre;
  if (pOld) pOld.hechos = r2((pOld.hechos || 0) - x.rollos);
  pNew.hechos = r2((pNew.hechos || 0) + q);
  Object.assign(x, { productoId: nid, nombre: pNew.nombre, rollos: q, fecha: f, precio: pNew.precio, quedaron: pNew.hechos, editado: { fecha: hoy(), hora: ahora(), por: quien() } });
  anotar('rollos_editados', mismo ? 'Editó los rollos hechos de ' + pNew.nombre : 'Pasó ' + fmt(q) + ' rollos hechos de ' + antes + ' a ' + pNew.nombre, cb);
  guardar(); cerrarModal(); render(); toast('Rollos hechos actualizados');
}
function lineaProd(x, vol) {""")

# ---- 3. Boton Editar y dato "Editado" en el detalle ----
parchar(A, "    filaD('Registrado por', x.por ? esc(x.por) : '') +\n    '<button class=\"btn del full\" onclick=\"' + dsp('borrarProduccion', x.id) + '\">Deshacer rollos hechos</button>' +",
 "    filaD('Registrado por', x.por ? esc(x.por) : '') +\n    (x.editado ? filaD('Editado', diaLargo(x.editado.fecha) + (x.editado.hora ? ' · ' + fmtHora(x.editado.hora) : '') + (x.editado.por ? ' · ' + esc(x.editado.por) : ''), 1) : '') +\n    '<button class=\"btn main full\" style=\"margin-top:14px\" onclick=\"' + dsp('formEditarProd', x.id) + '\">Editar rollos hechos</button>' +\n    '<button class=\"btn del full\" onclick=\"' + dsp('borrarProduccion', x.id) + '\">Deshacer rollos hechos</button>' +")

# ---- Version nueva + contexto ----
I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))
X = 'CONTEXTO.md'
leer(X)
parchar(X, "\n\n## Pendiente", "\n- [x] Editar rollos hechos (producto, cantidad, día) y anotarlo en el Historial (parche25)\n\n## Pendiente")
F[X] += """
## Cambios parche25 (editar rollos hechos)
- En el detalle de un registro de Rollos hechos hay un botón "Editar rollos hechos" (formEditarProd / guardarEdicionProd en app.js). Se puede cambiar producto, cantidad y día. Sirve para corregir cuando se registraron en el producto equivocado.
- Al guardar se ajusta p.hechos: se quitan los rollos viejos del producto anterior y se suman los nuevos al producto nuevo. Si esos rollos ya se vendieron (el stock quedaría en negativo) no deja.
- El registro de producción guarda x.editado {fecha, hora, por}; el detalle lo muestra.
- Se anota en el registro de cambios con tipo rollos_editados ("Rollos hechos editados"), con el antes y el después. Sale en Historial > Cambios y en Todo.
- Sigue sin poder editarse: ventas, pedidos entregados.
"""
for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche25 aplicado (editar rollos hechos + historial)')
