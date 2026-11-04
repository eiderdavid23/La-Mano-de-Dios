import sys

def parchar(archivo, viejo, nuevo):
    s = open(archivo, encoding='utf-8').read()
    n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces):', viejo[:60])
        sys.exit(1)
    open(archivo, 'w', encoding='utf-8').write(s.replace(viejo, nuevo))

A = 'js/app.js'

parchar(A, r'''if (!listo && firebase.auth().currentUser) mostrarError();''', r'''if (!listo) mostrarError();''')

parchar(A, r'''  firebase.initializeApp(firebaseConfig);''', r'''  firebase.initializeApp(firebaseConfig);
  paso = 'esperando sesión'; vigilar();''')

parchar(A, r'''<div class="empty">Cargando…</div>'; return; }''', r'''<div class="empty">Cargando… [v4 ' + paso + ']</div>'; return; }''')

parchar(A, '\niniciar();', r'''
window.addEventListener('error', e => { if (!listo) { paso = 'error JS: ' + e.message; mostrarError(); } });
window.addEventListener('unhandledrejection', e => { if (!listo) { paso = 'promesa: ' + (e.reason && (e.reason.code || e.reason.message) || e.reason); mostrarError(); } });
iniciar();''')

parchar('index.html', 'js/app.js"', 'js/app.js?v=4"')
parchar('index.html', 'js/firebase-config.js"', 'js/firebase-config.js?v=4"')
print('Parche 4 aplicado ✅')
