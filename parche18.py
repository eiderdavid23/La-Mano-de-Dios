import sys, re, time

def leer(a):
    return open(a, encoding='utf-8').read()

def cambiar(s, viejo, nuevo, n):
    c = s.count(viejo)
    if c != n:
        print('ERROR (' + str(c) + ' veces, se esperaban ' + str(n) + '):', viejo[:70]); sys.exit(1)
    return s.replace(viejo, nuevo)

A = 'js/app.js'
s = leer(A)
s = cambiar(s, 'Kilos que trae cada caneca', 'Litros que trae cada caneca', 2)
s = cambiar(s, 'Escribe cuántos kilos trae la caneca', 'Escribe cuántos litros trae la caneca', 2)
s = cambiar(s, 'Kilos por caneca', 'Litros por caneca', 2)
s = cambiar(s, 'Las salsas se compran por caneca. Se suma al stock en gramos (1 kilo = 1000 g)', 'Las salsas se compran por caneca. Para el stock se cuenta 1 litro = 1000 g', 1)

I = 'index.html'
i = re.sub(r'\?v=\d+', '?v=' + str(int(time.time())), leer(I))

X = 'CONTEXTO.md'
x = leer(X)
x = cambiar(x, 'Kilos que trae cada caneca', 'Litros que trae cada caneca', 1)
x = cambiar(x, "- Supuesto: la caneca se mide en kilos (si viene en litros, se escribe lo que pesa).",
 "- Las canecas vienen en LITROS (parche18): se pide \"Litros que trae cada caneca\" y para el stock se cuenta 1 litro = 1000 g. Por dentro el dato sigue llamándose kilosCaneca (p.kilosCaneca y x.kilosCaneca en los ingresos) y guarda los litros.", 1)

open(A, 'w', encoding='utf-8').write(s)
open(I, 'w', encoding='utf-8').write(i)
open(X, 'w', encoding='utf-8').write(x)
print('OK: parche18 aplicado (canecas en litros)')
