import sys
def parchar(archivo, viejo, nuevo):
    s = open(archivo, encoding='utf-8').read()
    n = s.count(viejo)
    if n != 1:
        print('ERROR (' + str(n) + ' veces):', viejo[:60]); sys.exit(1)
    open(archivo, 'w', encoding='utf-8').write(s.replace(viejo, nuevo))

parchar('index.html', '<body>\n', '<body>\n<div id="splash"><div class="sp-logo">🤲</div><b>Condimentos la Mano de Dios</b><small>Cargando…</small></div>\n')

A = 'js/app.js'
parchar(A, "// ===== Datos =====",
"""// ===== Pantalla de carga =====
const splashT0 = Date.now();
function quitarSplash() {
  const s = document.getElementById('splash');
  if (!s || s.dataset.salio) return;
  s.dataset.salio = '1';
  setTimeout(() => { s.classList.add('out'); setTimeout(() => s.remove(), 600); }, Math.max(0, 900 - (Date.now() - splashT0)));
}
setTimeout(quitarSplash, 10000);

// ===== Datos =====""")
parchar(A, "if (!NUBE) { render(); return; }", "if (!NUBE) { render(); quitarSplash(); return; }")
parchar(A, "listo = true; $('#nav').style.display = ''; render();", "listo = true; $('#nav').style.display = ''; render(); quitarSplash();")
parchar(A, "$('#nav').style.display = ''; render(); return;", "$('#nav').style.display = ''; render(); quitarSplash(); return;")
parchar(A, "function mostrarLogin() {", "function mostrarLogin() {\n  quitarSplash();")
parchar(A, "function mostrarPendiente() {", "function mostrarPendiente() {\n  quitarSplash();")

open('css/styles.css', 'a', encoding='utf-8').write("""
#splash{position:fixed;inset:0;z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;background:radial-gradient(circle at 50% 38%,#1e1b4b 0%,#0b1220 65%);transition:opacity .45s ease,visibility .45s}
#splash.out{opacity:0;visibility:hidden}
#splash .sp-logo{position:relative;width:112px;height:112px;border-radius:50%;display:grid;place-items:center;font-size:56px;background:linear-gradient(135deg,#8b5cf6,#22d3ee);margin-bottom:18px;box-shadow:0 0 60px rgba(139,92,246,.45);animation:spLate 1.6s ease-in-out infinite}
#splash .sp-logo::after{content:"";position:absolute;inset:-14px;border-radius:50%;border:3px solid transparent;border-top-color:#22d3ee;border-right-color:#8b5cf6;animation:spGira 1.1s linear infinite}
#splash b{color:#eef2ff;font-size:1.15rem;text-align:center;padding:0 24px}
#splash small{color:#94a3b8;font-weight:600}
@keyframes spLate{0%,100%{transform:scale(1)}50%{transform:scale(1.07)}}
@keyframes spGira{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){#splash .sp-logo,#splash .sp-logo::after{animation:none}}
""")
print('OK: pantalla de carga con logo')
