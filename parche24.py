s = open('js/app.js').read()

a = "a + x.rollos * (x.precio != null ? x.precio : (p.precio || 0)), 0);"
b = "filaD('Valor a precio de venta', x.precio != null ? money(x.rollos * x.precio) : '') +"

assert a in s and b in s, "No encontré el texto, no se cambió nada"

s = s.replace(a, "a + x.rollos * (p.precio || 0), 0);")
s = s.replace(b, "filaD('Valor a precio de venta', money(x.rollos * ((p && p.precio) != null ? p.precio : (x.precio || 0)))) +")

open('js/app.js', 'w').write(s)
print("Listo")
