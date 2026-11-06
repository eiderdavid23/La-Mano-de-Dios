import sys, re, time

F = {}
def leer(a):
    if a not in F:
        F[a] = open(a, encoding='utf-8').read()
    return F[a]

def parchar(a, viejo, nuevo):
    s = leer(a); n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces) en ' + a + ':', viejo[:80]); sys.exit(1)
    F[a] = s.replace(viejo, nuevo)

A = 'js/app.js'
C = 'css/styles.css'

JS = r"""
// ===== Aviso de actualización =====
// La versión de esta app es el ?v= con que index.html cargó app.js.
// Cada parche cambia ese número en index.html; si el index publicado trae uno mayor, hay actualización.
const VER_APP = (() => {
  const s = document.querySelector('script[src*="js/app.js"]');
  const m = s && /[?&]v=(\d+)/.exec(s.src);
  return m ? Number(m[1]) : 0;
})();
let verCerrada = 0;
function avisarActualizacion(v) {
  let el = document.getElementById('upd');
  if (!el) {
    el = document.createElement('div'); el.id = 'upd'; el.className = 'upd';
    el.innerHTML = '<span>Se hizo una actualización reciente</span>' +
      '<button class="go" onclick="recargarApp()">' + ic('<path d="M20 12a8 8 0 1 1-2.4-5.7"/><path d="M20 4v5h-5"/>') + 'Recargar</button>' +
      '<button class="x" aria-label="Cerrar" onclick="cerrarAvisoUpd()">' + ic('<path d="M6 6l12 12M18 6 6 18"/>') + '</button>';
    document.body.appendChild(el);
  }
  el.dataset.v = v;
  requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('show')));
}
function cerrarAvisoUpd() {
  const el = document.getElementById('upd'); if (!el) return;
  verCerrada = Number(el.dataset.v) || 0; el.classList.remove('show');
}
function revisarVersion() {
  if (!VER_APP || navigator.onLine === false) return;
  fetch('index.html?c=' + Date.now(), { cache: 'no-store' })
    .then(r => r.ok ? r.text() : '')
    .then(t => {
      const m = /js\/app\.js\?v=(\d+)/.exec(t); const v = m ? Number(m[1]) : 0;
      if (v > VER_APP && v !== verCerrada) avisarActualizacion(v);
    })
    .catch(() => {});
}
function recargarApp() {
  const b = document.querySelector('#upd .go');
  if (b) { b.disabled = true; b.textContent = 'Actualizando…'; }
  let hecho = false;
  const fin = () => { if (hecho) return; hecho = true; location.reload(); };
  setTimeout(fin, 4000);
  // Pide el index nuevo saltándose la copia guardada y luego recarga
  fetch(location.href.split('#')[0], { cache: 'reload' }).catch(() => {}).then(fin);
}
setTimeout(revisarVersion, 4000);
setInterval(revisarVersion, 5 * 60 * 1000);
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') revisarVersion(); });
window.addEventListener('online', revisarVersion);
"""

CSS = """
.upd{position:fixed;left:50%;bottom:calc(env(safe-area-inset-bottom) + 92px);transform:translate(-50%,220%);width:calc(100% - 28px);max-width:420px;display:flex;align-items:center;gap:8px;padding:10px 8px 10px 16px;border-radius:18px;background:var(--card);color:var(--txt);border:1px solid var(--sf);box-shadow:0 14px 30px -10px rgba(0,0,0,.45);z-index:60;transition:transform .55s var(--spring);font-size:.84rem;font-weight:600}
.upd.show{transform:translate(-50%,0)}
.upd span{flex:1;line-height:1.25}
.upd .go{flex:none;display:flex;align-items:center;gap:6px;border:none;border-radius:12px;padding:10px 14px;background:var(--sf);color:#1D1B16;font-family:inherit;font-weight:800;font-size:.82rem;cursor:pointer}
.upd .x{flex:none;width:32px;height:32px;display:grid;place-items:center;border:none;border-radius:10px;background:none;color:var(--mut);cursor:pointer}
.upd .ic{width:16px;height:16px}
"""

parchar(A, "\niniciar();\n", JS + "\niniciar();\n")
F[C] = leer(C).rstrip('\n') + '\n' + CSS

I = 'index.html'
F[I] = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
leer(X)
F[X] += """
## Cambios parche16
- Aviso de actualización: la app compara su versión (el ?v= con que index.html cargó app.js) con la del index.html publicado (se pide sin copia guardada). Si hay una mayor sale abajo, sobre la barra, "Se hizo una actualización reciente" con botón Recargar (y una X para cerrar). Recargar pide el index nuevo saltándose la copia guardada y recarga. Revisa a los 4 s de abrir, cada 5 min, al volver a la app y al recuperar internet. No hace falta tocar nada más: cada parche ya cambia el ?v= de index.html. Funciones en app.js: revisarVersion, avisarActualizacion, cerrarAvisoUpd, recargarApp. Los teléfonos con una versión anterior a parche16 necesitan una recarga manual la primera vez.
"""

for a in F:
    open(a, 'w', encoding='utf-8').write(F[a])
print('OK: parche16 aplicado (aviso de actualización con botón Recargar)')
