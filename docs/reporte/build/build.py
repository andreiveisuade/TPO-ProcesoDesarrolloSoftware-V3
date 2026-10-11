import os, re, subprocess, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from estilo import CSS

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.abspath(os.path.join(OUT, "..", ".."))
J = "backend/src/main/java/com/uade/tpejemplo/"
e = html.escape


def show(c, path):
    return subprocess.run(["git", "-C", REPO, "show", f"{c}:{path}"], capture_output=True, text=True, check=True).stdout


def full(path):
    return path if path.startswith(("backend/", "frontend/")) else J + path


def method(c, path, sig):
    ls = show(c, full(path)).split("\n")
    i = next(k for k, l in enumerate(ls) if re.search(sig, l))
    s = i
    while s > 0 and ls[s - 1].strip().startswith(("@", "//")):
        s -= 1
    depth = 0; started = False; j = i
    while True:
        depth += ls[j].count("{") - ls[j].count("}")
        if "{" in ls[j]:
            started = True
        if started and depth == 0:
            break
        j += 1
    return "\n".join(ls[s:j + 1])


def lines(c, path, sig, n=1, before=0):
    ls = show(c, full(path)).split("\n")
    i = next(k for k, l in enumerate(ls) if re.search(sig, l))
    return "\n".join(ls[i - before:i + n])


def body(c, path):
    t = show(c, full(path))
    t = re.sub(r"^package .*?\n", "", t)
    t = re.sub(r"^import .*?\n", "", t, flags=re.M)
    return t.strip()


def cb(c, path, *partes):
    ver = "V2 (git show v2)" if c == "v2" else "V3 (main)"
    return f'<div class="ruta">{e(full(path))} <span class="ver">· {ver}</span></div><pre><code>{e(chr(10).join(partes))}</code></pre>'


def svg(key, suf):
    return re.sub(r"<\?xml[^>]*\?>", "", open(f"{OUT}/puml/{key}-{suf}.svg").read())


def diagramas(key, tit_a="Antes (V2)", tit_d="Después (V3)", solo_antes=False):
    sufs = (("antes", tit_a),) if solo_antes else (("antes", tit_a), ("despues", tit_d))
    out = '<div class="par">'
    for suf, tit in sufs:
        src = open(f"{OUT}/puml/{key}-{suf}.puml").read()
        out += f'<figure><figcaption>{tit}</figcaption><div class="svgbox">{svg(key, suf)}</div>' \
               f'<details><summary>puml/{key}-{suf}.puml</summary><pre><code>{e(src)}</code></pre></details></figure>'
    return out + '</div>'


def archify_svg(n):
    # Prefija los id con el nombre del diagrama: varios SVG inline no pueden repetir id ni pisar anclas del reporte.
    t = open(os.path.join(REPO, f"docs/diagramas/archify/{n}.svg")).read()
    t = re.sub(r'\bid="([^"]+)"', rf'id="{n}-\1"', t)
    t = re.sub(r'url\(#([^)]+)\)', rf'url(#{n}-\1)', t)
    t = re.sub(r'(aria-labelledby|aria-describedby)="([^"]+)"', lambda m: m.group(1) + '="' + " ".join(f"{n}-{i}" for i in m.group(2).split()) + '"', t)
    t = re.sub(r'href="#([^"]+)"', rf'href="#{n}-\1"', t)
    return re.sub(r'<svg ', '<svg style="width:100%;height:auto" ', t, count=1)


def figura(n, titulo):
    return f'<figure style="margin-top:18px"><figcaption>{titulo}</figcaption><div class="mvcsvg">{archify_svg(n)}</div></figure>'


def bloque(id_, titulo, patron, problema, antes, solucion, despues, por_que, consecuencias, ref="", extra="", diag=None, intro=""):
    return f'''<article class="mejora" id="{id_}">
<h3>{titulo} <span class="badge impl">implementada</span></h3>
{('<p class="ref">' + ref + '</p>') if ref else ''}
{intro}
<dl class="estructura">
<dt>Patrón</dt><dd>{patron}</dd>
<dt>Problema (código antes)</dt><dd><p>{problema}</p>{antes}</dd>
<dt>Solución (código después)</dt><dd><p>{solucion}</p>{despues}</dd>
<dt>Por qué</dt><dd>{por_que}</dd>
<dt>Consecuencias</dt><dd>{consecuencias}</dd>
</dl>
{extra}
{diag if diag is not None else diagramas(id_)}
</article>'''


# ---------------- M1..M10 ----------------
m1 = bloque("m1", "M1. Rechazar el cobro sobre un crédito anulado",
    "<strong>Information Expert</strong>: la cuota conoce su crédito y decide si admite el cobro.",
    "Se <strong>cobraban cuotas de créditos anulados</strong> (TPO-004).",
    cb("v2", "model/Cuota.java", method("v2", "model/Cuota.java", r"public Cobranza registrarCobranza")),
    "Crédito anulado: <code>BusinessException</code> (400).",
    cb("main", "model/Cuota.java", method("main", "model/Cuota.java", r"public Cobranza registrarCobranza")),
    "Es <strong>regla de dominio</strong>. Decide <code>Cuota</code> y no el servicio ni <code>Credito</code>: es quien <strong>crea la cobranza</strong> (Creator) y conoce su crédito.",
    "La regla vale para todo cobro desde <strong>un único lugar</strong>.",
    "Cierra TPO-004. Test: <code>CuotaTest</code>.")

m2 = f'''<article class="mejora" id="m2">
<h3>M2. “Tiene cobranzas” ignora las anuladas <span class="badge impl">absorbida por M8</span></h3>
<p class="ref">Resuelta por <a href="#m8">M8</a>.</p>
<dl class="estructura">
<dt>Patrón</dt><dd><strong>Information Expert</strong>.</dd>
<dt>Problema (código antes)</dt><dd><p>Contaba <strong>cobranzas anuladas</strong>: el crédito no podía anularse.</p>
{cb("v2", "repository/CobranzaRepository.java", lines("v2", "repository/CobranzaRepository.java", "existeCobranzaDelCredito", 1, 1))}
{cb("v2", "service/impl/CreditoServiceImpl.java", method("v2", "service/impl/CreditoServiceImpl.java", r"public void anularCredito"))}</dd>
<dt>Solución (código después)</dt><dd><p><code>Credito.tieneCobranzas()</code> usa <code>Cuota::estaPagada</code>; la query se elimina.</p></dd>
<dt>Por qué</dt><dd><strong>Reutiliza la regla</strong> del modelo en lugar de duplicarla en SQL.</dd>
<dt>Consecuencias</dt><dd>Test: <code>CreditoTest</code>.</dd>
</dl>
{diagramas("m2", tit_a="Antes (V2): el servicio consulta y pasa un boolean al crédito", solo_antes=True)}
</article>'''

m3 = bloque("m3", "M3. Dashboard con números verdaderos",
    "<strong>Corrección</strong> + <strong>Information Expert</strong> (<code>Credito.estado()</code>).",
    "El dashboard <strong>contaba anulados</strong> y “financiado” sumaba una cuota, no el capital (TPO-003).",
    cb("v2", "service/impl/DashboardServiceImpl.java", method("v2", "service/impl/DashboardServiceImpl.java", r"obtenerEstadisticasGenerales"))
    + cb("v2", "repository/CreditoRepository.java", lines("v2", "repository/CreditoRepository.java", "sumarImporteCuotaTotal", 1, 1))
    + cb("v2", "repository/CobranzaRepository.java", lines("v2", "repository/CobranzaRepository.java", "sumarImporteTotal", 1, 1)),
    "Se excluye lo anulado; financiado = <code>deudaOriginal</code>; activos = <code>estado() == VIGENTE</code>. Saldo y vencido los suma cada crédito (<code>saldo()</code>, <code>montoVencido()</code>).",
    cb("main", "service/impl/DashboardServiceImpl.java", method("main", "service/impl/DashboardServiceImpl.java", r"obtenerEstadisticasGenerales"))
    + cb("main", "repository/CreditoRepository.java", lines("main", "repository/CreditoRepository.java", "sumarDeudaOriginalNoAnulada", 1, 1))
    + cb("main", "repository/CobranzaRepository.java", lines("main", "repository/CobranzaRepository.java", "sumarImporteNoAnulado", 1, 1)),
    "El <strong>estado lo decide el modelo</strong>; las sumas, la query. Por eso el financiado <strong>incluye cancelados</strong>.",
    "Gana: dashboard y listado coinciden. Cuesta: carga los créditos en memoria.",
    "Cierra TPO-003. Commits <code>8877f29</code>, <code>87f0631</code>.")

m4 = bloque("m4", "M4. Permisos de anulación aplicados en el backend",
    "<strong>MVC</strong> + <strong>Information Expert</strong>: la vista oculta, <strong>el modelo decide</strong>.",
    "Solo el front ocultaba el botón: <strong>cualquier usuario anulaba por API</strong> (TPO-007).",
    cb("v2", "controller/CreditoController.java", method("v2", "controller/CreditoController.java", r"anularCredito"))
    + cb("v2", "service/impl/CreditoServiceImpl.java", method("v2", "service/impl/CreditoServiceImpl.java", r"public void anularCredito")),
    "El controlador pasa el usuario (<code>@AuthenticationPrincipal</code>); sin permiso, 403.",
    cb("main", "controller/CreditoController.java", method("main", "controller/CreditoController.java", r"public ResponseEntity<Void> anularCredito"))
    + cb("main", "service/impl/CreditoServiceImpl.java", method("main", "service/impl/CreditoServiceImpl.java", r"public void anularCredito")),
    "La vista <strong>no es una barrera de seguridad</strong>.",
    "Gana: el permiso vale sin el front. Cuesta: los servicios reciben el <code>IUsuario</code>. No alcanza <code>@PreAuthorize</code>: el permiso es por usuario, no por rol.",
    "Cierra TPO-007.",
    extra=figura("anular-credito", "Secuencia: anular un crédito"))

m5 = bloque("m5", "M5. Handlers HTTP específicos",
    "<strong>MVC</strong>: el controlador traduce errores a <strong>códigos HTTP</strong>.",
    "Login inválido, ruta inexistente o método no soportado: <strong>todo daba 500</strong>; sin token, 403 en vez de 401 (TPO-001, 002).",
    cb("v2", "exception/GlobalExceptionHandler.java", method("v2", "exception/GlobalExceptionHandler.java", r"handleGeneral")),
    "Handlers 401, 403, 404, 405, entre otros; el 500 no expone detalles (S4).",
    cb("main", "exception/GlobalExceptionHandler.java",
       method("main", "exception/GlobalExceptionHandler.java", r"handleNoAutenticado"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleAccesoDenegado"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleRutaNoEncontrada"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleMetodoNoPermitido"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleGeneral")),
    "<strong>Un error del cliente no es una falla del servidor.</strong>",
    "Swagger documenta los códigos reales. Sin token o sin rol responde el filtro (<code>SecurityConfig</code>); el resto de los errores, este handler.",
    "Cierra TPO-001 y TPO-002.")

m6 = bloque("m6", "M6. Cuota.estaVencida()",
    "<strong>Information Expert</strong>: la cuota tiene la fecha, conoce su crédito y sabe si venció (la de un crédito anulado no entra en mora).",
    "<strong>No existía la mora</strong>: <code>fechaVencimiento</code> sin uso.",
    cb("v2", "model/Cuota.java", method("v2", "model/Cuota.java", r"public boolean estaPagada")),
    "<code>Cuota.estaVencida()</code>; la vista muestra Pagada / Vencida / Pendiente.",
    cb("main", "model/Cuota.java", method("main", "model/Cuota.java", r"public boolean estaPagada"), "", method("main", "model/Cuota.java", r"public boolean estaVencida")),
    "La mora es <strong>la consulta central</strong> de cobranzas.",
    "Reutilizable: el dashboard y la vista usan la misma regla. La fecha entra por parámetro: <strong>testeable sin reloj</strong>.",
    "Archivos: <code>model/Cuota.java</code>, <code>dto/response/CuotaResponse.java</code>.")

# ---- M7 Adapter (foco) ----
roles7 = """<table><thead><tr><th>Rol (slides 26 y 28, clase 10)</th><th>UsuarioDetails (desde V1)</th><th>JwtUtil (V3)</th></tr></thead><tbody>
<tr><td><strong>Client</strong>: solo conoce el Target</td><td>Spring Security (<code>DaoAuthenticationProvider</code>, vía <code>UserDetailsServiceImpl</code>)</td><td><code>AuthServiceImpl</code>, <code>JwtAuthFilter</code></td></tr>
<tr><td><strong>Target</strong>: interfaz que espera el cliente</td><td><code>UserDetails</code> (Spring, no modificable)</td><td><code>TokenService</code> (propia)</td></tr>
<tr><td><strong>Adapter</strong>: implementa el Target y <strong>contiene</strong> al Adaptee</td><td><code>UsuarioDetails</code>: <code>private final IUsuario usuario</code></td><td><code>JwtUtil</code>: <code>private final SecretKey key</code>, <code>private final JwtParser parser</code></td></tr>
<tr><td><strong>Adaptee</strong>: componente con otra interfaz</td><td><code>IUsuario</code></td><td>jjwt: <code>JwtParser</code>, <code>Jwts</code></td></tr>
</tbody></table>"""

extra7 = figura("adapter-jwt", "Secuencia: cada request valida el token sin conocer jjwt") + f"""<h4 style="margin-top:22px">Roles</h4>{roles7}
<ul>
<li><strong>Object Adapter</strong> (composición): única variante viable en Java (slide 27).</li>
<li><code>UsuarioDetails</code> sigue el <code>AdapterPagosExternos</code> (slide 28): traduce <code>getRol().autoridad()</code> a <code>GrantedAuthority</code>.</li>
</ul>
<div class="cuadro">
<div><h4>GRASP de fondo</h4><ul>
<li><strong>Indirection</strong>: <code>TokenService</code> media entre los clientes y jjwt.</li>
<li><strong>Pure Fabrication</strong>: <code>JwtUtil</code>, <code>UsuarioDetails</code>.</li>
<li><strong>Protected Variations</strong>: cambiar la librería afecta solo a <code>JwtUtil</code>.</li></ul></div>
<div><h4>SOLID de fondo</h4><ul>
<li><strong>DIP</strong>: los clientes dependen de <code>TokenService</code>, no de jjwt.</li>
<li><strong>SRP</strong>: cada Adapter solo traduce.</li>
<li><strong>Target limpio</strong> (O2): sin tipos de jjwt ni de Spring.</li></ul></div>
</div>
<details><summary>Objeciones previsibles</summary>
<dl class="qa">
<dt>“¿Por qué es Adapter si <code>JwtUtil</code> es propio?”</dt>
<dd>El Adaptee es <strong>jjwt</strong>; <code>JwtUtil</code> es el Adapter.</dd>
<dt>“¿Una interfaz con una sola implementación?”</dt>
<dd>Es el costo de <strong>DIP</strong>: sin ella, el contrato sería la librería.</dd>
<dt>“¿<code>UsuarioDetails</code> adapta una clase propia?”</dt>
<dd>Sí; la clase 9 lo admite (“externas al dominio, <strong>o no</strong>”). Lo no modificable es <code>UserDetails</code>, y así el dominio no depende de Spring.</dd>
</dl>
</details>
<h4>Diagramas: <code>UsuarioDetails</code> (V0 → V1)</h4>
{diagramas("adapter", tit_a="Antes (V0): Usuario implements UserDetails", tit_d="Después (V1 en adelante)")}
<h4>Diagramas: <code>JwtUtil</code> (V2 → V3)</h4>"""

m7 = bloque("m7", "M7. Adapter: UsuarioDetails y JwtUtil",
    "<strong>Adapter</strong> (GoF, estructural): convierte la interfaz de un componente no modificable en la que espera el cliente. Aquí, jjwt (librería de JWT).",
    "Los clientes dependían de la clase concreta <code>JwtUtil</code> y, por ella, <strong>de jjwt</strong>: el filtro capturaba su excepción.",
    cb("v2", "service/impl/AuthServiceImpl.java", lines("v2", "service/impl/AuthServiceImpl.java", r"private final JwtUtil", 1), "", method("v2", "service/impl/AuthServiceImpl.java", r"public AuthResponse login"))
    + cb("v2", "security/JwtAuthFilter.java", lines("v2", "security/JwtAuthFilter.java", r"private final JwtUtil", 1), "// ...", lines("v2", "security/JwtAuthFilter.java", r"extraerUsername", 4, 1)),
    "Target propio <code>TokenService</code>; <code>JwtUtil</code> lo implementa, <strong>contiene</strong> el <code>JwtParser</code> de jjwt (y su <code>SecretKey</code>) y es la única clase que importa jjwt.",
    cb("main", "service/TokenService.java", body("main", "service/TokenService.java"))
    + cb("main", "security/JwtUtil.java", body("main", "security/JwtUtil.java"))
    + cb("main", "security/JwtAuthFilter.java", lines("main", "security/JwtAuthFilter.java", r"private final TokenService", 1), "// ...", lines("main", "security/JwtAuthFilter.java", r"tokenService.extraerUsername", 4), "// ...", lines("main", "security/JwtAuthFilter.java", r"tokenService.esValido", 3))
    + cb("main", "service/impl/AuthServiceImpl.java", lines("main", "service/impl/AuthServiceImpl.java", r"private final TokenService", 1)),
    "Aislar a los clientes de una <strong>librería externa que no se puede modificar</strong>.",
    "<ul><li>Gana: cambiar de librería toca una clase; la clave se arma una vez (antes, en cada llamada).</li><li>Cuesta: una interfaz con una sola implementación; mantener el Adapter si jjwt cambia.</li></ul>",
    "Commits <code>aa76375</code>, <code>de78c07</code> (O2), <code>2ef8410</code> (composición).",
    extra=extra7,
    intro='<h4>Caso de manual: <code>UsuarioDetails</code></h4><p>Implementa <code>UserDetails</code> (Target de Spring) y <strong>contiene</strong> un <code>IUsuario</code>: el dominio no depende de Spring Security.</p>'
      + cb("main", "security/UsuarioDetails.java", body("main", "security/UsuarioDetails.java"))
      + '<h4>Caso V3: <code>JwtUtil</code> sobre jjwt</h4>')

m8 = bloque("m8", "M8. EstadoCredito y Credito como agregado de sus cuotas",
    "<strong>Information Expert</strong>: el crédito conoce sus cuotas y calcula estado y saldo (que las cree es O6).",
    "El estado era un boolean <code>anulado</code>: <strong>sin “cancelado” ni saldo</strong>.",
    cb("v2", "model/Credito.java", lines("v2", "model/Credito.java", r"private boolean anulado", 1, 1), "", method("v2", "model/Credito.java", r"public void anular"))
    + cb("v2", "service/impl/CreditoServiceImpl.java", method("v2", "service/impl/CreditoServiceImpl.java", r"public void anularCredito")),
    "<code>EstadoCredito</code> <strong>derivado</strong>, no persistido. <code>Credito</code> calcula estado, saldo y si puede anularse.",
    cb("main", "model/EstadoCredito.java", body("main", "model/EstadoCredito.java"))
    + cb("main", "model/Credito.java", lines("main", "model/Credito.java", r"private List<Cuota> cuotas", 1, 3), "",
         method("main", "model/Credito.java", r"public EstadoCredito estado"), "",
         method("main", "model/Credito.java", r"public BigDecimal saldo"), "",
         method("main", "model/Credito.java", r"public boolean estaCancelado"), "",
         method("main", "model/Credito.java", r"public boolean tieneCobranzas"), "",
         method("main", "model/Credito.java", r"public boolean puedeAnularse"), "",
         method("main", "model/Credito.java", r"public void anular"))
    + cb("main", "service/impl/CreditoServiceImpl.java", method("main", "service/impl/CreditoServiceImpl.java", r"private Credito buscarCredito")),
    "<strong>La decisión vuelve al experto</strong>: el servicio ya no le pasa un boolean.",
    "Gana: sin migración; de N+1 a 2 consultas. Cuesta: cuotas cargadas en la transacción.",
    "Tests: <code>CreditoTest</code>.",
    extra=figura("credito-estados", "Estados del crédito (derivados, solo se guarda anulado)"))

# ---- M9 Strategy (foco) ----
roles9 = '''<table><thead><tr><th>Rol (apunte clase 10)</th><th>Clase</th></tr></thead><tbody>
<tr><td><strong>Context</strong>: obtiene la Strategy y delega</td><td><code>Credito</code> guarda <code>tipoPlan</code>, que le entrega la Strategy (<code>TipoPlan.calculo()</code>); le delega <code>importeCuota</code> en el constructor</td></tr>
<tr><td><strong>Strategy</strong>: interfaz común</td><td><code>model/interfaces/CalculoDeCuota.java</code></td></tr>
<tr><td><strong>ConcreteStrategies</strong>: no se conocen entre sí</td><td><code>model/plan/InteresSimple.java</code>, <code>model/plan/SistemaFrances.java</code></td></tr>
<tr><td><strong>Cliente que elige</strong></td><td>quien otorga: <code>&lt;select&gt;</code> de <code>Creditos.jsx</code> → <code>CreditoRequest.tipoPlan</code> → <code>TipoPlan</code> (enum persistido, registro de estrategias)</td></tr>
</tbody></table>'''


# ---- M9: explicación de los dos planes ----
from decimal import Decimal as D_
def _frances(C, i, n):
    q = (C * i / (1 - 1 / (1 + i) ** n)).quantize(D_("0.01"))
    s = C; filas = []
    for m in range(1, n + 1):
        it = (s * i).quantize(D_("0.01")); k = q - it; s -= k
        filas.append((m, q, k, it, s))
    return q, filas
FQ, FFILAS = _frances(D_(12000), D_("0.05"), 6)
fmt = lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _grafico():
    W, H, x0, y0, top = 860, 340, 70, 290, 30
    esc = (y0 - top) / 2800
    g = []
    for v in range(0, 2801, 500):
        y = y0 - v * esc
        g.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{W-20}" y2="{y:.1f}" stroke="#D9E1EC"/><text x="{x0-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#666">{v:,}</text>'.replace(",", "."))
    paso = (W - 20 - x0) / 6
    for m, q, k, it, s in FFILAS:
        cx = x0 + paso * (m - 1) + paso / 2
        # simple: 2000 capital + 600 interés
        for xb, cap, inte in ((cx - 34, 2000, 600), (cx + 4, float(k), float(it))):
            hc, hi = cap * esc, inte * esc
            g.append(f'<rect x="{xb:.1f}" y="{y0-hc:.1f}" width="30" height="{hc:.1f}" fill="#2E75B6"/>')
            g.append(f'<rect x="{xb:.1f}" y="{y0-hc-hi:.1f}" width="30" height="{hi:.1f}" fill="#E8A33D"/>')
        g.append(f'<text x="{cx-19:.1f}" y="{y0-2600*esc-5:.1f}" text-anchor="middle" font-size="10" fill="#1D2B4F">S</text>')
        g.append(f'<text x="{cx+19:.1f}" y="{y0-float(q)*esc-5:.1f}" text-anchor="middle" font-size="10" fill="#1D2B4F">F</text>')
        g.append(f'<text x="{cx:.1f}" y="{y0+18}" text-anchor="middle" font-size="12" fill="#222">Mes {m}</text>')
    g.append(f'<rect x="{x0}" y="8" width="12" height="12" fill="#2E75B6"/><text x="{x0+18}" y="18" font-size="12" fill="#222">capital (devuelve lo prestado)</text>')
    g.append(f'<rect x="{x0+230}" y="8" width="12" height="12" fill="#E8A33D"/><text x="{x0+248}" y="18" font-size="12" fill="#222">interés (lo que gana el prestamista)</text>')
    g.append(f'<text x="{W-20}" y="18" text-anchor="end" font-size="12" fill="#222">S = interés simple · F = sistema francés</text>')
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cuota por mes, simple contra francés" xmlns="http://www.w3.org/2000/svg" font-family="Calibri, Carlito, sans-serif">' + "".join(g) + '</svg>'

filas_fr = "".join(f"<tr><td>{m}</td><td>{fmt(q)}</td><td>{fmt(it)}</td><td>{fmt(k)}</td><td>{fmt(s)}</td></tr>" for m, q, k, it, s in FFILAS)
int_fr = sum(f[3] for f in FFILAS)
explica9 = f"""<h4 style="margin-top:22px">Los dos planes de pago</h4>
<ul>
<li><strong>Interés simple</strong>: tasa única sobre el capital, repartida en cuotas iguales. 30 % = 30 % del total.</li>
<li><strong>Sistema francés</strong>: cuota fija; interés mensual sobre el saldo. 5 % = 5 % por mes. <code>cuota = C·i / (1 − (1+i)^−n)</code>.</li>
</ul>
<details><summary>Ejemplo: $12.000 en 6 cuotas</summary>
<div class="cuadro">
<div><h4>Interés simple, 30 % total</h4><p>Cuota = 12.000 × 1,30 / 6 = <strong>2.600</strong> (2.000 de capital y 600 de interés). Interés total: <strong>3.600</strong>.</p></div>
<div><h4>Sistema francés, 5 % mensual</h4><p>Cuota fija = <strong>{fmt(FQ)}</strong>. Interés del mes 1: 600; del mes 6: 112,58. Interés total: <strong>{fmt(int_fr)}</strong>.</p></div>
</div>
<div class="mvcsvg">{_grafico()}</div>
<table><thead><tr><th>Mes</th><th>Cuota francés</th><th>Interés</th><th>Capital</th><th>Saldo después</th></tr></thead><tbody>{filas_fr}</tbody></table>
</details>
<h4>Justificación del patrón</h4>
<ul>
<li><strong>Revierte V2</strong>: el 15/09 se descartó el francés porque la convención interfaz + clase se cumplía con un algoritmo. Strategy exige dos que varíen de verdad.</li>
<li><strong>Sin <code>setEstrategia</code></strong>: el plan es parte del contrato; cambiarlo alteraría cuotas emitidas. Es enum porque JPA persiste un <code>@Enumerated</code>, no una interfaz.</li>
</ul>
"""

extra9 = explica9 + f'''<h4 style="margin-top:22px">Roles</h4>{roles9}
<div class="cuadro">
<div><h4>GRASP de fondo</h4><ul>
<li><strong>Polymorphism</strong>: dos clases con la misma operación reemplazan el <code>if</code> por tipo.</li>
<li><strong>Protected Variations</strong>: agregar o cambiar un sistema no toca <code>Credito</code>.</li>
<li><strong>Information Expert</strong>: el total sale de las cuotas emitidas (<code>importeCuota × cantidadCuotas</code>), sin recalcular.</li></ul></div>
<div><h4>SOLID de fondo</h4><ul>
<li><strong>OCP</strong>: un sistema nuevo es una clase en <code>model/plan/</code> y una constante en <code>TipoPlan</code>; <code>Credito</code> no cambia.</li>
<li><strong>DIP</strong>: <code>Credito</code> depende de <code>CalculoDeCuota</code>, no de las estrategias concretas.</li>
<li><strong>SRP</strong>: una fórmula por clase, testeada aislada (<code>InteresSimpleTest</code>, <code>SistemaFrancesTest</code>).</li></ul></div>
</div>
<details><summary>Objeciones previsibles</summary>
<dl class="qa">
<dt>“¿Dos algoritmos no es sobre-ingeniería?”</dt>
<dd>Con una sola fórmula lo sería (slide 38). Hay <strong>dos algoritmos reales que el usuario elige</strong>, y el francés entró sin tocar <code>Credito</code> (1200 al 10 % en 3 cuotas: simple 440, francés 482,54).</dd>
<dt>“Si cambia la fórmula, ¿qué pasa con los créditos otorgados?”</dt>
<dd>Nada: la cuota <strong>se guarda al otorgar</strong> (O3).</dd>
<dt>“¿<code>EstadoCredito</code> no es un State?”</dt>
<dd>No: es un <strong>valor derivado</strong> que no cambia el comportamiento (O9).</dd>
</dl>
</details>'''

m9 = bloque("m9", "M9. Strategy del cálculo de cuota",
    "<strong>Strategy</strong> (GoF, comportamiento): algoritmos intercambiables para una misma acción, detrás de una interfaz común.",
    "Fórmula <strong>cableada</strong> en <code>Credito</code>: cada sistema nuevo exigía un <code>if</code> por tipo.",
    cb("v2", "model/Credito.java", method("v2", "model/Credito.java", r"public BigDecimal totalADevolver"), "", method("v2", "model/Credito.java", r"private BigDecimal calcularImporteCuota")),
    "<code>Credito</code> <strong>delega</strong> el cálculo en la estrategia de su plan (<code>calculo()</code>) al otorgar.",
    cb("main", "model/Credito.java", lines("main", "model/Credito.java", r"this.importeCuota = calculo", 1), "", method("main", "model/Credito.java", r"private CalculoDeCuota calculo"), "", method("main", "model/Credito.java", r"public BigDecimal totalADevolver"))
    + cb("main", "model/interfaces/CalculoDeCuota.java", body("main", "model/interfaces/CalculoDeCuota.java"))
    + cb("main", "model/plan/InteresSimple.java", body("main", "model/plan/InteresSimple.java"))
    + cb("main", "model/plan/SistemaFrances.java", body("main", "model/plan/SistemaFrances.java"))
    + cb("main", "model/TipoPlan.java", body("main", "model/TipoPlan.java")),
    "<strong>Misma acción, distintos algoritmos</strong>, elegidos por el usuario al otorgar.",
    "<ul><li>Gana: un sistema nuevo no modifica <code>Credito</code>.</li><li>Cuesta: <code>tasaInteres</code> cambia de unidad según el plan (la vista rotula “% total” o “% mensual”); columna <code>tipo_plan</code> nueva; la cuota no separa capital e interés (P-M9).</li></ul>",
    "Commits <code>065eb37</code>, <code>9ea428d</code>, <code>1f9fc50</code> (O3), <code>fa0c180</code> (<code>calculo()</code>).",
    extra=extra9)

m10 = bloque("m10", "M10. Dashboard también para ADMIN",
    "<strong>Corrección</strong>, sin patrón.",
    "<strong>El ADMIN no veía el dashboard</strong> (TPO-010).",
    cb("v2", "config/SecurityConfig.java", lines("v2", "config/SecurityConfig.java", r'hasRole\("SUPERVISOR"\)', 1)),
    "Matcher propio para <code>/api/dashboard/**</code> con los dos roles.",
    cb("main", "config/SecurityConfig.java", lines("main", "config/SecurityConfig.java", r'"/api/admin/\*\*"', 3)),
    "El admin ve estadísticas <strong>sin cambiar de rol</strong>.",
    "La autorización queda en el backend.",
    "Cierra TPO-010. Commit <code>f7ce757</code>.")

mejoras = [m9, m7, m1, m2, m3, m4, m5, m6, m8, m10]

indice = [
 ("m9", "Cálculo de cuota", "<strong>Strategy</strong>", "foco"),
 ("m7", "TokenService / JwtUtil + UsuarioDetails", "<strong>Adapter</strong>", "foco"),
 ("m1", "Cobro sobre crédito anulado", "Information Expert", "TPO-004"),
 ("m2", "“Tiene cobranzas” ignora anuladas (absorbida por M8)", "Information Expert", "revisión del dominio"),
 ("m3", "Dashboard con números verdaderos", "Corrección + Expert", "TPO-003"),
 ("m4", "Permisos de anulación en el backend", "MVC + Expert", "TPO-007"),
 ("m5", "Handlers HTTP 400 a 415", "MVC", "TPO-001, 002"),
 ("m6", "Cuota.estaVencida()", "Information Expert", "revisión del dominio"),
 ("m8", "EstadoCredito + Credito agregado", "Information Expert", "revisión del dominio"),
 ("m10", "Dashboard para ADMIN", "Corrección, sin patrón", "TPO-010"),
]
tabla_indice = "".join(f'<tr><td><a href="#{k}">{k.upper()}</a></td><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for k, a, b, c in indice)

# ---------------- revisión ----------------
rev = [
 ("API", "f551cbc, 1ea0375, 1737bd9, 940958e", "Sin token respondía 403; admin sin <code>@Valid</code>.", "401 con <code>HttpStatusEntryPoint</code>; <code>@Valid</code> en admin y supervisor; <code>GET /api/creditos</code>."),
 ("H1", "fcc9bf6", "Una cobranza anulada podía <strong>anularse otra vez</strong>.", "<code>Cobranza.anular</code> la rechaza."),
 ("O1", "444031f, 64cee96", "La vista <strong>decidía</strong> si un crédito era anulable.", "El DTO expone <code>puedeAnularse</code>."),
 ("O2", "de78c07", "El Target <strong>exponía tipos de jjwt</strong>.", "<code>extraerUsername</code> devuelve <code>Optional</code>; <code>JwtUtil</code> absorbe las excepciones."),
 ("O3", "1f9fc50", "El total <strong>no coincidía con las cuotas</strong>.", "<code>totalADevolver</code> = cuota × cantidad; la estrategia actúa solo al otorgar."),
 ("O4", "87f0631", "“Activos” <strong>contaba cancelados</strong>.", "Cuenta <code>estado() == VIGENTE</code>."),
 ("O5", "5b7f165", "La API permitía <strong>modificar permisos del ADMIN</strong>.", "<code>Usuario</code> lo rechaza."),
 ("S1, S2", "67ba784, 1e87795", "Escrituras <strong>sin transacción</strong>, ocultas por open-in-view.", "<code>@Transactional</code> en <code>service/impl</code>; <code>open-in-view=false</code>."),
 ("S3", "45a35c9, e8a1372", "<code>jwt.secret</code> <strong>en un repo público</strong> (TPO-009); prod creaba <code>admin/admin</code>.", "Prod exige <code>${JWT_SECRET}</code>; la semilla solo corre en dev."),
 ("S4", "904fa1e", "El 500 <strong>exponía</strong> SQL y clases.", "Mensaje genérico y log."),
 ("S5, BS2", "013c07a, 0df40d1", "Provider armado a mano; <code>ErrorResponse</code> <strong>repetido 9 veces</strong>.", "Spring arma el provider; un único método <code>error</code>."),
 ("D1, D2, BS1, DF1, DF3, BSF1", "5ac2155, 3bd8b61, 5f2c334, 830a998, 5d2dbc4, c19e707", "Código sin uso o duplicado; un <code>console.log</code> <strong>imprimía el JWT</strong>.", "Eliminados."),
 ("F1", "f0e5c59", "Autenticado sin rol recibía <strong>401 en lugar de 403</strong>.", "<code>accessDeniedHandler</code>."),
 ("F2, I3", "06fc842, 8e01d49", "JSON malformado o <code>Content-Type</code>/<code>Accept</code> no JSON daban <strong>500</strong>.", "400, 415 y 406."),
 ("I1", "9c3d4ae", "Anular y cobrar en paralelo dejaba un crédito <strong>ANULADO con cobranza vigente</strong>.", "Bloqueo pesimista del crédito en ambos caminos, mismo orden."),
 ("I-1", "8888df6", "Dos cobros simultáneos <strong>duplicaban la cobranza</strong>.", "Bloqueo pesimista de la cuota; test de 20 hilos."),
 ("I4", "3eae70f", "Un alta <strong>aparecía en la lista filtrada</strong> de otro cliente.", "La página recarga la lista en vez de agregar."),
 ("O6, O7", "d89d62d, 6cc5e17", "Crédito <strong>sin cuotas</strong>; dashboard sin saldo ni mora.", "El constructor de <code>Credito</code> crea las cuotas; saldo y vencido en el dashboard, calculados por el crédito (<code>saldo()</code>, <code>montoVencido()</code>)."),
 ("BS3, BS4", "5246f27, 7c6dd63, f96f53a", "El servicio consultaba permisos; rol como <code>String</code>.", "<code>Usuario.puedeAnularCredito</code>; enum <code>Rol</code> en los DTO."),
 ("Front", "dfa2c12, d9b0b8f, a085f66, f5c8d05, 0e3284e", "Rutas por rol <strong>duplicadas</strong>; roles como strings.", "<code>RoleRoute</code> y <code>utils/roles.js</code>."),
 ("DER", "8eb2106", "<strong>Sin DER</strong>.", "<code>der-v3</code>; detectó tres inconsistencias del modelo, resueltas."),
]
rev_html = '<table><thead><tr><th>ID · commits</th><th>Problema</th><th>Cambio</th></tr></thead><tbody>' + "".join(f'<tr><td><strong>{i}</strong><br><span class="ref"><code>{c}</code></span></td><td>{p}</td><td>{s}</td></tr>' for i, c, p, s in rev) + '</tbody></table>'

evol = [
 ("Swagger", "f551cbc, a4b2077",
  "<strong>Sin contrato</strong>: el front deducía endpoints y códigos.",
  "<code>/swagger-ui.html</code>: 20 operaciones, Bearer JWT, códigos reales.",
  "contrato vista-controlador explícito (MVC)."),
 ("Perfiles dev/prod y CORS", "e744600, 45a35c9",
  "Una configuración para demo y producción; <strong>consola H2 sin login</strong>; CORS sin origen (TPO-008).",
  "Perfil dev (H2, SQL en logs) y prod (sin consola, <code>CORS_ORIGIN</code> obligatoria).",
  "configuración externalizada; prod sigue en H2 en memoria."),
 ("UI", "01fabb9, 08c8fda, 1ec4ccb, f0d2372, 4f42ebd, 86b7083",
  "Importes sin formato, fechas ISO, <strong>sin aviso</strong> al crear, nombres técnicos en los mensajes.",
  "Formato es-AR, badge de estado, avisos, mensajes centralizados en <code>apiClient.js</code>.",
  "cambia solo la vista (MVC)."),
 ("Dark theme", "979ab37",
  "Colores <strong>fijos</strong> en cada componente.",
  "Variables CSS semánticas; <code>prefers-color-scheme</code> elige el tema. Contraste WCAG AA.",
  "la paleta varía en un solo lugar."),
 ("UC06, UC09 y permisos", "0e7a1ad, 1210424, 28840ac",
  "UC06 y UC09 <strong>sin pantalla</strong>; un permiso nuevo no se veía hasta reiniciar sesión (H4).",
  "Búsqueda por DNI y por número de crédito; <code>PrivateRoute</code> consulta <code>/api/auth/me</code>.",
  "el modelo es la autoridad sobre permisos (MVC, M4)."),
 ("Tests y validación", "6f552e0..82fc486, 4d35266, 77dec02, 90d0e5e, 8888df6",
  "<strong>Cero tests</strong> en V2; un DNI largo o una deuda enorme daban 500 (I-2).",
  "42 tests; <code>@Size</code>/<code>@Digits</code> en los DTO; <code>Cuota.estaVencida(LocalDate)</code> recibe la fecha.",
  "el dominio se prueba sin Spring ni reloj."),
 ("Limpieza", "ddbdebb, 3478af6, c36658f, 6a1c363, 4713828",
  "Javadoc redundante; archivos de IDE y de proceso en el zip.",
  "Una línea por patrón; <code>.factorypath</code> fuera del repo; <code>export-ignore</code> para docs de proceso.",
  "el zip lleva solo código vigente."),
]
evol_html = '<table><thead><tr><th>Mejora · commits</th><th>Problema</th><th>Solución</th></tr></thead><tbody>' + "".join(f'<tr><td><strong>{t}</strong><br><span class="ref"><code>{c}</code></span></td><td>{p}</td><td>{s}</td></tr>' for t, c, p, s, k in evol) + '</tbody></table>'

convenciones = """<p>Convención: <strong>una <code>I&lt;Clase&gt;</code> por clase de modelo</strong> en <code>model/interfaces/</code> y <strong><code>XService</code> + <code>service/impl/XServiceImpl</code></strong>. Excepciones deliberadas:</p>
<table><thead><tr><th>Clase</th><th>Excepción</th><th>Motivo</th></tr></thead><tbody>
<tr><td><code>model/EstadoCredito.java</code></td><td>sin <code>IEstadoCredito</code></td><td>Enum <strong>sin comportamiento</strong>: la interfaz quedaría vacía.</td></tr>
<tr><td><code>model/TipoPlan.java</code></td><td>sin <code>ITipoPlan</code></td><td>Enum <strong>registro de estrategias</strong>: solo devuelve la Strategy.</td></tr>
<tr><td><code>model/interfaces/CalculoDeCuota.java</code></td><td>sin prefijo <code>I</code></td><td><strong>Interfaz Strategy</strong>: lleva nombre de rol, como <code>EstrategiaDescuento</code> en el apunte.</td></tr>
<tr><td><code>service/TokenService.java</code> → <code>security/JwtUtil.java</code></td><td>no es <code>TokenServiceImpl</code> en <code>service/impl/</code></td><td><strong>Adapter</strong>: nombre de rol; es infraestructura, no caso de uso.</td></tr>
<tr><td><code>model/interfaces/IRol.java</code></td><td>sin consumidor como tipo</td><td>Existe <strong>solo por la convención</strong>.</td></tr>
</tbody></table>"""

matriz = [
 ("Information Expert", "<code>model/Credito.java</code> <code>estado</code>, <code>saldo</code>, <code>montoVencido</code>, <code>puedeAnularse</code>; <code>model/Cuota.java</code> <code>estaVencida</code>", "Cumple"),
 ("Creator", "<code>model/Credito.java</code> genera sus cuotas (O6); <code>Cuota.registrarCobranza</code> crea la <code>Cobranza</code>; <code>Usuario.nuevo</code> es la única fábrica de usuarios. Qué rol recibe quien se registra solo (USER, sin permisos) es política del caso de uso: la decide <code>AuthServiceImpl.registrar</code>, no una segunda fábrica con un solo uso.", "Cumple"),
 ("Controller", "<code>controller/*Controller</code> por caso de uso, delegan en <code>XService</code>", "Cumple"),
 ("Bajo acoplamiento / Alta cohesión", "controllers → interfaces de servicio; clientes → <code>service/TokenService.java</code>", "Cumple"),
 ("Polymorphism", "<code>model/interfaces/CalculoDeCuota.java</code>, sin <code>if</code> por plan", "Cumple"),
 ("Pure Fabrication / Indirection", "repositorios, <code>security/JwtUtil.java</code>, <code>security/UsuarioDetails.java</code>", "Cumple"),
 ("Protected Variations", "<code>CalculoDeCuota</code> (fórmula), <code>TokenService</code> (librería)", "Cumple"),
 ("SRP / OCP / LSP", "una fórmula por estrategia; plan nuevo sin tocar <code>Credito</code>; estrategias intercambiables", "Cumple"),
 ("ISP", "<code>service/TokenService.java</code> (3 métodos, todos usados); <code>model/interfaces/CalculoDeCuota.java</code> (1)", "Cumple"),
 ("DIP", "<code>model/Credito.java</code> → <code>CalculoDeCuota</code>; clientes → <code>TokenService</code>; servicios inyectados por interfaz", "Cumple"),
]
matriz_html = "<p>Los diez criterios se cumplen.</p><table><thead><tr><th>Principio</th><th>Dónde</th></tr></thead><tbody>" + "".join(f"<tr><td><strong>{a}</strong></td><td>{b}</td></tr>" for a, b, c in matriz) + "</tbody></table>"


def cap(sub, nom, alt):
    return f'<figure><figcaption>{alt}</figcaption><a href="capturas/{sub}/{nom}.png"><img src="capturas/{sub}/{nom}.png" alt="{alt}" style="width:100%;border:1px solid var(--linea);border-radius:4px"></a></figure>'

capturas_ui = (''
    + '<div class="par">' + cap("ui-antes", "03-creditos", "Créditos, antes") + cap("ui-despues", "03-creditos", "Créditos, después") + '</div>'
    + '<div class="par">' + cap("ui-antes", "04-cobranzas", "Cobranzas, antes") + cap("ui-despues", "04-cobranzas", "Cobranzas, después") + '</div>'
    + '<div class="par">' + cap("dark", "creditos", "Créditos, dark theme") + cap("dark", "dashboard", "Dashboard, dark theme") + '</div>')

# ---------------- timeline ----------------
n_v3 = len(subprocess.run(["git", "-C", REPO, "log", "--oneline", "--no-merges", "v2..main"], capture_output=True, text=True).stdout.strip().split("\n"))
log_v3 = subprocess.run(["git", "-C", REPO, "log", "--oneline", "v2..main"], capture_output=True, text=True).stdout.strip()

timeline = f'''<div class="timeline">
<div class="hito"><div class="punto"></div><h4>V0</h4><p class="tema">Punto 0, proyecto inicial</p><p class="meta"><code>main@2a90af8</code> (repo Arreglos)</p>
<ul><li>CRUD de clientes, créditos y cobranzas</li><li>Importe de cuota cargado a mano</li><li>Usuario como UserDetails</li><li>MetaCobranza sin uso</li></ul></div>
<div class="hito"><div class="punto"></div><h4>V1</h4><p class="tema">Iteración 1: bad smells</p><p class="meta">Entregada 08/09 · <code>andrei-iteracion1@86c75cc</code> · 28 commits</p>
<ul><li>13 smells: god class, data class, primitive obsession, encapsulamiento</li><li>Sin <code>MetaCobranza</code>; <code>Cuota.estaPagada()</code> y <code>registrarCobranza</code></li><li><code>UsuarioDetails</code> como Adapter</li><li>Resueltos TPO-005, 006, 013, 015</li></ul></div>
<div class="hito"><div class="punto"></div><h4>V2</h4><p class="tema">Iteración 2: GRASP + interfaces</p><p class="meta">Mergeada 15/09 · <code>main@45e228c</code> (tag <code>v2</code>) · 5 commits</p>
<ul><li>Information Expert: <code>Cobranza.anular()</code>, <code>Credito.anular()</code></li><li>Creator: <code>Usuario.nuevo</code></li><li>Interfaz por cada clase del modelo y de servicio</li><li>Revierte §3.7 de V1 (Lazy class): restituye las interfaces de servicio</li></ul></div>
<div class="hito actual"><div class="punto"></div><h4>V3</h4><p class="tema">Iteración 3: MVC + Strategy + Adapter</p><p class="meta">Entrega 13/10/2026 · repo V3, <code>main</code> · {n_v3} commits sin merges</p>
<ul><li><strong>Strategy</strong>: cálculo de cuota, interés simple y sistema francés (M9)</li><li><strong>Adapter</strong>: <code>TokenService</code> sobre jjwt (M7)</li><li><code>EstadoCredito</code>, saldo, mora (M6, M8)</li><li>Permisos y errores HTTP en el backend (M4, M5)</li><li>Dashboard con saldo y vencido (M3, M10, O7); 41 tests</li><li>Revierte V2: el sistema francés, descartado el 15/09, vuelve como segunda estrategia</li><li>Swagger, perfiles dev/prod, UI, dark theme, UC06/UC09</li></ul></div>
</div>
<details><summary>Commits V2 → V3 (git log v2..main)</summary><pre><code>{e(log_v3)}</code></pre></details>'''

mapeo = [
 ("model/*, model/interfaces/*, model/plan/*", "Modelo", "Datos y reglas de negocio; estrategias (M9) y agregado (M8)."),
 ("repository/*", "Modelo", "Acceso a datos; los implementa Spring Data."),
 ("service/*, service/impl/*", "Modelo", "Casos de uso y transacción (S1). <code>TokenService</code>: Target de M7."),
 ("exception/BusinessException, ResourceNotFoundException", "Modelo", "Regla violada o recurso inexistente."),
 ("controller/*", "Controlador", "Reciben el evento HTTP, validan forma, identifican al usuario (M4), invocan al modelo, devuelven DTO."),
 ("dto/request/*, dto/response/*", "Controlador (frontera)", "Contrato vista-controlador; el modelo no los conoce."),
 ("exception/GlobalExceptionHandler", "Controlador", "Excepción → código HTTP, sin detalles internos (M5, S4, I3)."),
 ("security/*, config/SecurityConfig", "Controlador", "Filtran antes del controlador: 401 sin token, 403 sin rol. <code>JwtUtil</code> y <code>UsuarioDetails</code>: Adapters."),
 ("config/OpenApiConfig + anotaciones <code>@Operation</code>", "Controlador (contrato)", "Contrato publicado en Swagger UI."),
 ("config/DataInitializer", "Modelo", "Semilla de usuarios vía <code>Usuario.nuevo</code>, solo en dev."),
 ("Frontend pages/*, components/*", "Vista", "Presentan y envían acciones; las decisiones vienen del modelo (O1)."),
 ("Frontend store/slices/*, api/*", "Vista", "Estado del cliente (Redux) y única puerta HTTP."),
]
rows = "\n".join(f"<tr><td><code>{a}</code></td><td><strong>{b}</strong></td><td>{c}</td></tr>" for a, b, c in mapeo)

tecnologias = '''<dl class="tec">
<dt>Spring Boot</dt><dd>Framework Java del backend: REST, servicios, seguridad.</dd>
<dt>Spring Security</dt><dd>Autenticación y autorización por request (401/403).</dd>
<dt>JWT y jjwt</dt><dd>Token firmado de sesión; jjwt es el Adaptado de M7.</dd>
<dt>JPA / Hibernate / Spring Data</dt><dd>Mapeo objeto-relacional y repositorios generados.</dd>
<dt>H2</dt><dd>Base en memoria, sin instalación.</dd>
<dt>Lombok</dt><dd>Getters, constructores y loggers por anotación.</dd>
<dt>springdoc / Swagger UI</dt><dd>Contrato de la API navegable.</dd>
<dt>React, Redux, Vite</dt><dd>Componentes, estado del cliente, build.</dd>
<dt>JUnit 5, AssertJ, Mockito</dt><dd>Tests, aserciones y dobles; <code>@WebMvcTest</code> carga solo la capa web.</dd>
<dt>Bean Validation</dt><dd>Restricciones en los DTO; lo inválido responde 400.</dd>
<dt>Maven</dt><dd>Dependencias, compilación y tests.</dd>
<dt>PlantUML y d2</dt><dd>Diagramas a partir de texto.</dd>
</dl>'''



def d2svg(n):
    t = re.sub(r"<\?xml[^>]*\?>", "", open(os.path.join(REPO, f"docs/diagramas/d2/{n}.svg")).read())
    return re.sub(r'<svg ', '<svg style="width:100%;height:auto;max-height:900px" ', t, count=1)

der_svg = re.sub(r"<\?xml[^>]*\?>", "", open(os.path.join(REPO, "docs/diagramas/der-v3.svg")).read())
der_svg = re.sub(r'(<svg[^>]*?) style="[^"]*" width="[^"]*" height="[^"]*"', r'\1 style="width:100%;height:auto"', der_svg, count=1)

pendientes = '''<ul>
<li><strong>H8</strong>: trazabilidad. <code>Cobranza</code> no registra quién cobró ni quién anuló; requiere cambio de modelo y de API.</li>
<li><strong>O8</strong>: pagos parciales. Hoy se exige el importe exacto (TPO-006); requiere saldo por cuota.</li>
<li><strong>Base persistente</strong>: prod usa H2 en memoria; los datos se pierden al reiniciar. Falta PostgreSQL con migraciones.</li>
<li><strong>TPO-014</strong>: el paquete <code>com.uade.tpejemplo</code> no nombra el sistema. El renombre ocultaría los cambios reales en el diff; se evalúa para el 17/11.</li>
</ul>'''

LIGHTBOX = """<div class="lightbox" id="lb" role="dialog" aria-modal="true" aria-label="Diagrama ampliado">
<div class="lb-bar"><span class="lb-title" id="lbTitle"></span>
<button class="sec" id="lbOut" aria-label="Alejar">−</button><span class="lb-zoom" id="lbZoom">100%</span><button class="sec" id="lbIn" aria-label="Acercar">+</button>
<button class="sec" id="lbFit">Ajustar</button><button id="lbClose" aria-label="Cerrar">✕</button></div>
<div class="lb-scroll" id="lbScroll"><div class="lb-canvas" id="lbCanvas"></div></div></div>
<script>
(function () {
  var lb = document.getElementById("lb"), canvas = document.getElementById("lbCanvas"), sc = document.getElementById("lbScroll");
  var label = document.getElementById("lbZoom"), w = 800, h = 600, k = 1;
  function size(svg) {
    var vb = (svg.getAttribute("viewBox") || "").trim().split(/[\\s,]+/).map(Number);
    if (vb.length === 4 && vb[2] > 0) return [vb[2], vb[3]];
    var r = svg.getBoundingClientRect(); return [r.width || 800, r.height || 600];
  }
  function apply() { canvas.style.width = Math.round(w * k) + "px"; canvas.style.height = Math.round(h * k) + "px"; label.textContent = Math.round(k * 100) + "%"; }
  function fit() { k = Math.min((sc.clientWidth - 60) / w, (sc.clientHeight - 60) / h, 1.5); apply(); sc.scrollLeft = sc.scrollTop = 0; }
  function zoom(f, cx, cy) {
    var r = sc.getBoundingClientRect(), ax = cx == null ? sc.clientWidth / 2 : cx - r.left, ay = cy == null ? sc.clientHeight / 2 : cy - r.top;
    var x = sc.scrollLeft + ax, y = sc.scrollTop + ay, p = k;
    k = Math.min(Math.max(k * f, 0.1), 8); apply();
    sc.scrollLeft = x * k / p - ax; sc.scrollTop = y * k / p - ay;
  }
  function open(svg, title) {
    var c = svg.cloneNode(true); c.removeAttribute("style"); c.removeAttribute("width"); c.removeAttribute("height");
    var d = size(svg); w = d[0]; h = d[1];
    canvas.innerHTML = ""; canvas.appendChild(c);
    document.getElementById("lbTitle").textContent = title;
    lb.classList.add("open"); document.body.classList.add("lb-locked"); fit();
  }
  function close() { lb.classList.remove("open"); document.body.classList.remove("lb-locked"); canvas.innerHTML = ""; }
  function titulo(box) {
    var fig = box.closest("figure"), cap = fig && fig.querySelector("figcaption");
    if (cap) return cap.textContent.trim();
    for (var n = box.previousElementSibling; n; n = n.previousElementSibling) if (/^H[2-4]$/.test(n.tagName)) return n.textContent.trim();
    var art = box.closest("article"); return art ? art.querySelector("h3").textContent.replace("implementada", "").trim() : "Diagrama";
  }
  document.querySelectorAll(".svgbox, .mvcsvg, .clases").forEach(function (box) {
    var svg = box.querySelector("svg"); if (!svg) return;
    box.classList.add("zoomable");
    box.addEventListener("click", function () { open(svg, titulo(box)); });
  });
  document.getElementById("lbClose").onclick = close;
  document.getElementById("lbIn").onclick = function () { zoom(1.3); };
  document.getElementById("lbOut").onclick = function () { zoom(1 / 1.3); };
  document.getElementById("lbFit").onclick = fit;
  lb.addEventListener("click", function (e) { if (e.target === lb || e.target === sc) close(); });
  document.addEventListener("keydown", function (e) {
    if (!lb.classList.contains("open")) return;
    if (e.key === "Escape") close();
    else if (e.key === "+" || e.key === "=") zoom(1.3);
    else if (e.key === "-") zoom(1 / 1.3);
    else if (e.key === "0") fit();
  });
  sc.addEventListener("wheel", function (e) { e.preventDefault(); zoom(e.deltaY < 0 ? 1.12 : 1 / 1.12, e.clientX, e.clientY); }, { passive: false });
  var drag = false, sx, sy, l0, t0, moved = false;
  sc.addEventListener("mousedown", function (e) { drag = true; moved = false; sx = e.clientX; sy = e.clientY; l0 = sc.scrollLeft; t0 = sc.scrollTop; sc.classList.add("grabbing"); });
  window.addEventListener("mousemove", function (e) { if (!drag) return; moved = true; sc.scrollLeft = l0 - (e.clientX - sx); sc.scrollTop = t0 - (e.clientY - sy); });
  window.addEventListener("mouseup", function () { drag = false; sc.classList.remove("grabbing"); });
})();
</script>"""


doc = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reporte V3 — TPO Grupo 7</title><style>{CSS}</style></head>
<body>
<div id="barra"><strong style="color:var(--navy)">Reporte V3</strong>
<nav><a href="#portada">Portada</a><a href="#timeline">Timeline</a><a href="#tecnologias">Tecnologías</a><a href="#mvc">MVC</a><a href="#mejoras">Mejoras</a><a href="#m9">Strategy</a><a href="#m7">Adapter</a><a href="#convenciones">Convenciones</a><a href="#matriz">GRASP/SOLID</a><a href="#evolucion">Evolución</a><a href="#revision">Revisión</a><a href="#verificacion">Verificación</a><a href="#casos-de-uso">Casos de uso</a><a href="#clases">Diagramas</a><a href="#pendientes">Pendientes</a></nav>
<button class="sec" onclick="document.querySelectorAll('details.detalle').forEach(d=>d.open=true);window.print()">Exportar PDF</button></div>
<main>

<section id="portada" class="portada">
<div class="marca">UADE</div>
<h1>TPO Grupo 7<br>Dashboard de préstamos</h1><div class="rule"></div>
<div class="sub">Iteración 3: MVC + Strategy + Adapter</div>
<div class="sub">Proceso de Desarrollo de Software · 13/10/2026</div>
<ul><li><strong>Integrantes:</strong> Andrei, Regulo</li>
<li><strong>Código:</strong> repo V3, rama <code>main</code>. “Antes” = tag <code>v2</code>; “después” = <code>main</code>.</li>
<li><strong>Rutas:</strong> las clases Java se citan relativas a <code>backend/src/main/java/com/uade/tpejemplo/</code>.</li></ul>
</section>

<section id="timeline"><h2>Timeline V0 → V1 → V2 → V3</h2>

{timeline}</section>

<section id="tecnologias"><h2>Tecnologías</h2>
{tecnologias}</section>

<section id="mvc"><h2>MVC en Spring Boot</h2>
<p><strong>MVC distribuido</strong>: modelo y controlador en Spring Boot, vista en React; se comunican <strong>por DTO</strong> (clase 9).</p>
<div class="clases">{archify_svg("mvc")}</div>
<table><thead><tr><th>Clase / paquete</th><th>Componente</th><th>Justificación</th></tr></thead><tbody>{rows}</tbody></table>
<h3>Qué cambió en V3</h3>
<ul>
<li><strong>Contrato publicado</strong>: Swagger (<code>config/OpenApiConfig.java</code>).</li>
<li><strong>Errores traducidos</strong> a HTTP (<code>exception/GlobalExceptionHandler.java</code>).</li>
<li><strong>401 ≠ 403</strong> (<code>config/SecurityConfig.java</code>).</li>
<li><strong>La regla vive en el modelo; la vista solo oculta</strong> (M4, O1, O5).</li>
</ul>
</section>

<section id="mejoras"><h2>Mejoras al dominio</h2>
<p>Cada mejora tapa <strong>un hueco real</strong>. Formato: <strong>Patrón → Problema (código <code>v2</code>) → Solución (código <code>main</code>) → Por qué → Consecuencias</strong>. Primero el foco de la consigna: <strong>Strategy (M9)</strong> y <strong>Adapter (M7)</strong>.</p>
<table><thead><tr><th>ID</th><th>Mejora</th><th>Patrón / concepto</th><th>Hueco</th></tr></thead><tbody>{tabla_indice}</tbody></table>
{"".join(mejoras)}
</section>

<section id="convenciones"><h2>Convenciones de la cátedra</h2>
{convenciones}
</section>

<section id="matriz"><h2>GRASP y SOLID</h2>
{matriz_html}
</section>

<section id="evolucion"><h2>Evolución del sistema: mejoras propuestas e implementadas</h2>
<ul>{"".join(f"<li><strong>{t}</strong>: {k}</li>" for t, _, _, _, k in evol)}</ul>
<details class="detalle"><summary>Detalle: problema, solución, commits</summary>{evol_html}</details>
<details class="detalle"><summary>Capturas de la UI</summary>{capturas_ui}</details>
</section>

<section id="revision"><h2>Mejoras de la revisión</h2>
<p>Correcciones puntuales posteriores a la revisión. Lo abierto queda en el <a href="../backlog.md">backlog</a>.</p>
<ul>
<li><strong>Error del cliente = 4xx; 401 ≠ 403</strong>: API, F1, F2, I3, S4.</li>
<li><strong>MVC: decide el modelo, la vista lo refleja</strong>: O1, I4.</li>
<li><strong>Expert, Creator, Tell don't ask</strong>: H1, O4, O5, O6, O7, BS3.</li>
<li><strong>Adapter y Strategy bien aplicados</strong>: O2, O3.</li>
<li><strong>Transacciones y bloqueo pesimista</strong>: S1, S2, I1, I-1.</li>
<li><strong>Configuración fuera del código</strong>: S3, S5.</li>
<li><strong>Bad smells</strong> (muerto, duplicado, primitive obsession): D1, D2, BS1, BS2, BS4, DF1, DF3, BSF1, front.</li>
<li><strong>Esquema revisado</strong>: DER.</li>
</ul>
<details class="detalle"><summary>Detalle por corrección</summary>{rev_html}</details>
</section>

<section id="verificacion"><h2>Verificación</h2>
<ul>
<li><strong>42 tests, 0 fallas</strong> (<code>mvn test</code>): 29 de dominio, 10 HTTP (<code>@WebMvcTest</code>), 2 de concurrencia, <code>contextLoads</code>.</li>
<li><strong>Smoke</strong>: API 12/12, recorrido visual 9/9; auditoría de API: 304 casos con 4 roles.</li>
<li><strong>Fallas halladas y corregidas</strong>: 401/403 y 500 mal mapeados (F1, F2); 2 visuales (O1, <code>d35fc0e</code>).</li>
</ul>
</section>

<section id="casos-de-uso"><h2>Casos de uso</h2>
<p>Fichas, diagrama y trazabilidad: <a href="../casos-de-uso/README.md"><code>docs/casos-de-uso/README.md</code></a>. Verificados con <code>docs/casos-de-uso/verificar-cu.sh</code>.</p>
<p><a href="../casos-de-uso/casos-de-uso-v3.svg"><img src="../casos-de-uso/casos-de-uso-v3.svg" alt="Diagrama de casos de uso V3" style="width:100%;background:#fff;border:1px solid var(--linea);border-radius:4px"></a></p>
</section>

<section id="clases"><h2>Diagramas de clases y DER</h2>
<p>Entregable UML en tres vistas (<code>docs/diagramas/clases-v3.puml</code>): capas MVC, seguridad y Adapter, y modelo con Strategy. Todas las clases con sus tres compartimentos.</p>
<h3>Diagrama de clases: capas MVC (UML)</h3>
<div class="clases">{re.sub(r"<\?xml[^>]*\?>", "", open(os.path.join(REPO, "docs/diagramas/clases-v3-mvc.svg")).read())}</div>
<h3>Diagrama de clases: seguridad y Adapter (UML)</h3>
<div class="clases">{re.sub(r"<\?xml[^>]*\?>", "", open(os.path.join(REPO, "docs/diagramas/clases-v3-seguridad.svg")).read())}</div>
<h3>Diagrama de clases: detalle del modelo (UML)</h3>
<div class="clases">{re.sub(r"<\?xml[^>]*\?>", "", open(os.path.join(REPO, "docs/diagramas/clases-v3-modelo.svg")).read())}</div>
<p>Abajo, esquemas parciales en d2 (sin compartimentos, solo para leer rápido).</p>
<h3>Esquema: Strategy</h3>
<div class="clases">{d2svg("strategy")}</div>
<h3>Esquema: Adapter</h3>
<div class="clases">{d2svg("adapter")}</div>
<h3>Esquema: modelo de dominio</h3>
<p>Rombo lleno: composición (el todo crea y contiene a sus partes).</p>
<div class="clases">{d2svg("dominio")}</div>
<h3>DER</h3>
<p>Tablas generadas por JPA, con tipos SQL, claves y cada FK unida columna a columna (<code>docs/diagramas/der-v3.py</code>).</p>
<div class="clases">{der_svg}</div>
</section>

<section id="pendientes"><h2>Cambios pendientes</h2>
{pendientes}
<p>Lista completa de cambios hechos y pendientes: <code>docs/entrega/lista-mejoras.md</code>.</p>
</section>
</main>
{LIGHTBOX}
</body></html>'''
open(OUT + "/reporte-v3.html", "w").write(doc)
print(len(doc))
