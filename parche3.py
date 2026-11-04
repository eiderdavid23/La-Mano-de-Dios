s = open('js/app.js', encoding='utf-8').read()
viejo = "firebase.initializeApp(firebaseConfig);"
nuevo = "try { firebase.database.INTERNAL.forceLongPolling(); } catch (e) {}\n  firebase.initializeApp(firebaseConfig);"
if s.count(viejo) != 1:
    print('ERROR', s.count(viejo)); raise SystemExit(1)
open('js/app.js', 'w', encoding='utf-8').write(s.replace(viejo, nuevo))
print('Parche 3 aplicado ✅')
