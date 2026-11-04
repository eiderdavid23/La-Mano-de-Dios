import sys

def parchar(archivo, viejo, nuevo):
    s = open(archivo, encoding='utf-8').read()
    n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces):', viejo[:60])
        sys.exit(1)
    open(archivo, 'w', encoding='utf-8').write(s.replace(viejo, nuevo))

A = 'js/app.js'

parchar(A, r'''function desuscribir() {''', r'''let paso = '', timer = null;
function vigilar() {
  clearTimeout(timer);
  timer = setTimeout(() => { if (!listo && firebase.auth().currentUser) mostrarError(); }, 8000);
}
function mostrarError() {
  $('#nav').style.display = 'none';
  $('#app').innerHTML = '<div class="fade"><h2>No carga ⚠️</h2><div class="bubble"><div class="sub" style="margin:0 0 14px">Se quedó en: ' + esc(paso || 'inicio') + '</div><button class="btn main full" onclick="reintentar()">Reintentar</button><button class="btn full" style="margin-top:10px" onclick="salir()">Cerrar sesión</button></div></div>';
}
function reintentar() {
  desuscribir();
  $('#app').innerHTML = '<div class="empty">Cargando…</div>';
  const u = firebase.auth().currentUser;
  if (u) { paso = 'leyendo perfil'; vigilar(); perfil(u); } else mostrarLogin();
}
function desuscribir() {''')

parchar(A, r'''if (u) perfil(u); else mostrarLogin();''', r'''if (u) { paso = 'leyendo perfil'; vigilar(); perfil(u); } else { clearTimeout(timer); mostrarLogin(); }''')

parchar(A, r'''        miPerfil = s.val();
        if (miPerfil && miPerfil.aprobado === true) {
          if (!fbRef) escuchar();''', r'''        miPerfil = s.val();
        if (miPerfil && miPerfil.aprobado === true) {
          paso = 'leyendo datos del negocio';
          if (!fbRef) escuchar();''')

parchar(A, r'''      }, () => mostrarPendiente());
    });''', r'''      }, e => { paso = 'perfil: ' + (e && e.code ? e.code : 'error'); mostrarError(); });
    });''')

parchar(A, r'''    listo = true; $('#nav').style.display = ''; render();
  }, () => { fbRef = null; listo = false; mostrarPendiente(); });''', r'''    listo = true; clearTimeout(timer); $('#nav').style.display = ''; render();
  }, e => { fbRef = null; listo = false; paso = 'negocio: ' + (e && e.code ? e.code : 'error'); mostrarError(); });''')
print('Parche aplicado ✅')
