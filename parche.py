import sys

def parchar(archivo, viejo, nuevo):
    s = open(archivo, encoding='utf-8').read()
    n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces):', viejo[:60])
        sys.exit(1)
    open(archivo, 'w', encoding='utf-8').write(s.replace(viejo, nuevo))

A = 'js/app.js'
parchar(A, r'''function formProducto(id) {''', r'''function opcionesCat(sel) {
  const lista = ['Aliños', 'Salsas', 'Otro'];
  if (sel && !lista.includes(sel)) lista.splice(2, 0, sel);
  return lista.map(c => '<option value="' + esc(c) + '"' + (c === sel ? ' selected' : '') + '>' + esc(c) + '</option>').join('');
}
function formProducto(id) {''')
parchar(A, r'''<input id="f-cat" list="cats" value="' + esc(p.categoria || '') + '" placeholder="Ej: Aliños, Salsas"><datalist id="cats">' + categorias().map(c => '<option value="' + esc(c) + '">').join('') + '</datalist>''', r'''<select id="f-cat">' + opcionesCat(p.categoria || (id ? 'Otro' : 'Aliños')) + '</select>''')
parchar('CONTEXTO.md', '- [x] Nombre de la plataforma: Condimentos la Mano de Dios', '- [x] Nombre de la plataforma: Condimentos la Mano de Dios\n- [x] Categoría con desplegable: Aliños, Salsas, Otro')
print('OK: desplegable de categoría listo')
