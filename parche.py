import sys

def parchar(archivo, viejo, nuevo):
    s = open(archivo, encoding='utf-8').read()
    n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces):', viejo[:60])
        sys.exit(1)
    open(archivo, 'w', encoding='utf-8').write(s.replace(viejo, nuevo))

A = 'js/app.js'

parchar(A, r'''let fCat = 'Todas', fBus = '';''', r'''let fCat = 'Todas', fBus = '';
const NUBE = typeof firebase !== 'undefined' && typeof firebaseConfig !== 'undefined' && !!firebaseConfig.apiKey;
let local = null, fbRef = null, listo = !NUBE;
const remoto = { productos: {}, entradas: {}, ventas: {} };
const COLS = ['productos', 'entradas', 'ventas'];
const est = o => o ? JSON.stringify(o, Object.keys(o).sort()) : 'null';''')

parchar(A, r'''function guardar() { localStorage.setItem(KEY, JSON.stringify(db)); }''', r'''function guardar() {
  if (!NUBE) { localStorage.setItem(KEY, JSON.stringify(db)); return; }
  if (!listo || !fbRef) return;
  const upd = {};
  COLS.forEach(c => {
    const actual = {};
    db[c].forEach(x => { actual[x.id] = x; });
    Object.keys(actual).forEach(id => {
      if (est(actual[id]) !== est(remoto[c][id])) upd[c + '/' + id] = JSON.parse(JSON.stringify(actual[id]));
    });
    Object.keys(remoto[c]).forEach(id => { if (!actual[id]) upd[c + '/' + id] = null; });
  });
  if (Object.keys(upd).length) fbRef.update(upd).catch(e => toast('No se pudo guardar: ' + e.message));
}''')

parchar(A, r'''function render() {''', r'''function render() {
  if (NUBE && !listo) { $('#app').innerHTML = '<div class="empty">Cargando…</div>'; return; }''')

parchar(A, r'''<div class="sub" style="margin:2px 0 10px">Los datos viven en este teléfono. Guarda una copia de vez en cuando.</div>' +''',
r'''<div class="sub" style="margin:2px 0 10px">' + (NUBE ? 'Tus datos se guardan en la nube. Igual puedes bajar una copia.' : 'Los datos viven en este teléfono. Guarda una copia de vez en cuando.') + '</div>' +''')

parchar(A, r''''<button class="btn full" style="margin-top:14px" onclick="cerrarModal()">Cerrar</button>');''',
r'''(NUBE ? '<button class="btn del full" style="margin-top:14px" onclick="salir()">Cerrar sesión</button>' : '') +
    '<button class="btn full" style="margin-top:14px" onclick="cerrarModal()">Cerrar</button>');''')

parchar(A, '''  r.readAsText(f);
}

render();''', r'''  r.readAsText(f);
}

// ===== Nube (Firebase) =====
function iniciarNube() {
  firebase.initializeApp(firebaseConfig);
  firebase.auth().onAuthStateChanged(u => {
    if (u) { $('#nav').style.display = ''; escuchar(); }
    else { desuscribir(); mostrarLogin(); }
  });
}
function desuscribir() { if (fbRef) fbRef.off(); fbRef = null; listo = false; }
function escuchar() {
  desuscribir();
  fbRef = firebase.database().ref('negocio');
  fbRef.on('value', snap => {
    const v = snap.val() || {};
    COLS.forEach(c => { remoto[c] = v[c] || {}; });
    const vacio = !Object.keys(remoto.productos).length;
    if (!listo && vacio && local && local.productos.length && !localStorage.getItem(KEY + '_subido') &&
        confirm('La nube está vacía. ¿Subir los datos guardados en este teléfono?')) {
      db = local; listo = true; guardar();
      localStorage.setItem(KEY + '_subido', '1'); render(); return;
    }
    db = {
      productos: Object.values(remoto.productos).map(x => Object.assign({}, x)),
      entradas: Object.values(remoto.entradas).map(x => Object.assign({}, x)),
      ventas: Object.values(remoto.ventas).map(x => Object.assign({}, x)).sort((a, b) => a.id < b.id ? -1 : 1)
    };
    listo = true; render();
  }, () => { toast('Este usuario no tiene permiso'); firebase.auth().signOut(); });
}
function mostrarLogin() {
  $('#nav').style.display = 'none';
  $('#app').innerHTML = '<div class="fade"><h2>Iniciar sesión</h2><div class="bubble">' +
    '<label>Correo</label><input id="l-mail" type="email" autocomplete="username">' +
    '<label>Contraseña</label><input id="l-pass" type="password" autocomplete="current-password" onkeydown="if(event.key===\'Enter\')entrar()">' +
    '<button class="btn main full" style="margin-top:16px" onclick="entrar()">Entrar</button></div></div>';
}
function entrar() {
  const m = $('#l-mail').value.trim(), c = $('#l-pass').value;
  if (!m || !c) return toast('Escribe correo y contraseña');
  firebase.auth().signInWithEmailAndPassword(m, c).catch(() => toast('Correo o contraseña incorrectos'));
}
function salir() { cerrarModal(); firebase.auth().signOut(); }

function iniciar() {
  if (!NUBE) { render(); return; }
  local = db; db = { productos: [], entradas: [], ventas: [] };
  render(); iniciarNube();
}
iniciar();''')

parchar('index.html', '<script src="js/app.js"></script>', '''<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-auth-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-database-compat.js"></script>
<script src="js/firebase-config.js"></script>
<script src="js/app.js"></script>''')

C = 'CONTEXTO.md'
parchar(C, '## Cómo trabajo (para la IA)', '''## Firebase
- Realtime Database, nodo "negocio" con productos, entradas y ventas (cada registro guardado por su id).
- Login con correo y contraseña (Authentication). Los usuarios se crean a mano en la consola de Firebase.
- Reglas: solo los UID autorizados leen y escriben (el repo es público, no se deja abierto a cualquiera con sesión).
- La configuración (pública) va en js/firebase-config.js. Si ese archivo está vacío, la app funciona solo en el teléfono (localStorage).
- Con la nube vacía, al primer ingreso ofrece subir los datos guardados en el teléfono.

## Cómo trabajo (para la IA)''')
parchar(C, '## Hecho\n', '## Hecho\n- [x] Código de Firebase (Realtime Database + login por correo) listo\n')
parchar(C, '- [ ] Guardar datos en la nube para usar en varios celulares', '- [ ] Conectar Firebase: crear el proyecto y llenar js/firebase-config.js')
print('OK: código de Firebase agregado')
