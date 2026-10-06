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
    "<strong>Information Expert</strong>: la cuota conoce su crédito y decide si se puede cobrar.",
    "Se <strong>cobraban cuotas de créditos anulados</strong> (TPO-004).",
    cb("v2", "model/Cuota.java", method("v2", "model/Cuota.java", r"public Cobranza registrarCobranza")),
    "Si el crédito está anulado: <code>BusinessException</code> (400).",
    cb("main", "model/Cuota.java", method("main", "model/Cuota.java", r"public Cobranza registrarCobranza")),
    "Es <strong>regla del dominio</strong>: va en <code>Cuota</code>, no en el servicio.",
    "Gana: <strong>un solo lugar</strong>, vale para todo cobro.",
    "Cierra TPO-004. Test: <code>backend/src/test/java/com/uade/tpejemplo/model/CuotaTest.java</code>.")

m2 = f'''<article class="mejora" id="m2">
<h3>M2. “Tiene cobranzas” ignora las anuladas <span class="badge impl">absorbida por M8</span></h3>
<p class="ref">Resuelta por <a href="#m8">M8</a>.</p>
<dl class="estructura">
<dt>Patrón</dt><dd><strong>Information Expert</strong>.</dd>
<dt>Problema (código antes)</dt><dd><p>Contaba <strong>cobranzas anuladas</strong>: el crédito quedaba inanulable.</p>
{cb("v2", "repository/CobranzaRepository.java", lines("v2", "repository/CobranzaRepository.java", "existeCobranzaDelCredito", 1, 1))}
{cb("v2", "service/impl/CreditoServiceImpl.java", method("v2", "service/impl/CreditoServiceImpl.java", r"public void anularCredito"))}</dd>
<dt>Solución (código después)</dt><dd><p><code>model/Credito.java</code> <code>tieneCobranzas()</code> usa <code>Cuota::estaPagada</code>; se borra la query.</p></dd>
<dt>Por qué</dt><dd><strong>Reusar la regla</strong> en vez de duplicarla en SQL.</dd>
<dt>Consecuencias</dt><dd>Test: <code>CreditoTest</code>.</dd>
</dl>
{diagramas("m2", tit_a="Antes (V2): el servicio consulta y le pasa un boolean al crédito", solo_antes=True)}
</article>'''

m3 = bloque("m3", "M3. Dashboard con números verdaderos",
    "<strong>Corrección</strong> + <strong>Information Expert</strong> (<code>Credito.estado()</code>).",
    "El dashboard <strong>contaba anulados</strong> y “financiado” sumaba una cuota, no lo prestado (TPO-003).",
    cb("v2", "service/impl/DashboardServiceImpl.java", method("v2", "service/impl/DashboardServiceImpl.java", r"obtenerEstadisticasGenerales"))
    + cb("v2", "repository/CreditoRepository.java", lines("v2", "repository/CreditoRepository.java", "sumarImporteCuotaTotal", 1, 1))
    + cb("v2", "repository/CobranzaRepository.java", lines("v2", "repository/CobranzaRepository.java", "sumarImporteTotal", 1, 1)),
    "Se filtra lo anulado; “financiado” = <code>deudaOriginal</code>; activos = <code>estado() == VIGENTE</code>.",
    cb("main", "service/impl/DashboardServiceImpl.java", method("main", "service/impl/DashboardServiceImpl.java", r"obtenerEstadisticasGenerales"))
    + cb("main", "repository/CreditoRepository.java", lines("main", "repository/CreditoRepository.java", "sumarDeudaOriginalVigente", 1, 1))
    + cb("main", "repository/CobranzaRepository.java", lines("main", "repository/CobranzaRepository.java", "sumarImporteVigente", 1, 1)),
    "La <strong>vigencia se define una vez</strong>, en el modelo.",
    "Gana: dashboard y listado coinciden. Cuesta: carga los créditos en memoria.",
    "Cierra TPO-003. Commits <code>8877f29</code>, <code>87f0631</code>.")

m4 = bloque("m4", "M4. Permisos de anulación aplicados en el backend",
    "<strong>MVC</strong> + <strong>Information Expert</strong>: la vista oculta, <strong>el modelo decide</strong>.",
    "Solo el front ocultaba el botón: <strong>cualquiera anulaba por API</strong> (TPO-007).",
    cb("v2", "controller/CreditoController.java", method("v2", "controller/CreditoController.java", r"anularCredito"))
    + cb("v2", "service/impl/CreditoServiceImpl.java", method("v2", "service/impl/CreditoServiceImpl.java", r"public void anularCredito")),
    "El controlador pasa el usuario (<code>@AuthenticationPrincipal</code>); sin permiso, 403.",
    cb("main", "controller/CreditoController.java", method("main", "controller/CreditoController.java", r"public ResponseEntity<Void> anularCredito"))
    + cb("main", "service/impl/CreditoServiceImpl.java", method("main", "service/impl/CreditoServiceImpl.java", r"public void anularCredito")),
    "La <strong>vista puede ocultar, pero valida el modelo</strong>.",
    "Gana: el permiso vale sin el front. Cuesta: los servicios reciben el <code>IUsuario</code>.",
    "Cierra TPO-007.")

m5 = bloque("m5", "M5. Handlers HTTP específicos",
    "<strong>MVC</strong>: el controlador traduce errores a <strong>códigos HTTP</strong>.",
    "Login malo, ruta inexistente o sin permiso: <strong>todo daba 500</strong> (TPO-001, 002).",
    cb("v2", "exception/GlobalExceptionHandler.java", method("v2", "exception/GlobalExceptionHandler.java", r"handleGeneral")),
    "Handlers 401, 403, 404, 405; el 500 no filtra detalles (S4).",
    cb("main", "exception/GlobalExceptionHandler.java",
       method("main", "exception/GlobalExceptionHandler.java", r"handleAuth"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleDenied"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleNoResource"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleMetodo"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleGeneral")),
    "<strong>Error del cliente ≠ falla del servidor.</strong>",
    "Gana: Swagger documenta los códigos reales.",
    "Cierra TPO-001 y TPO-002.")

m6 = bloque("m6", "M6. Cuota.estaVencida()",
    "<strong>Information Expert</strong>: la cuota tiene la fecha, ella sabe si venció.",
    "<strong>No existía la mora</strong>: <code>fechaVencimiento</code> sin uso.",
    cb("v2", "model/Cuota.java", method("v2", "model/Cuota.java", r"public boolean estaPagada")),
    "<code>Cuota.estaVencida()</code>; la vista muestra Pagada / Vencida / Pendiente.",
    cb("main", "model/Cuota.java", method("main", "model/Cuota.java", r"public boolean estaPagada"), "", method("main", "model/Cuota.java", r"public boolean estaVencida")),
    "La mora es <strong>la pregunta central</strong> de cobranzas (H3).",
    "Gana: reutilizable (dashboard). La fecha entra por parámetro: <strong>testeable sin reloj</strong>.",
    "Archivos: <code>model/Cuota.java</code>, <code>dto/response/CuotaResponse.java</code>.")

# ---- M7 Adapter (foco) ----
roles7 = """<table><thead><tr><th>Rol (slide 26/28, clase 10)</th><th>Adapter 1: UsuarioDetails (desde V1)</th><th>Adapter 2: JwtUtil (V3)</th></tr></thead><tbody>
<tr><td><strong>Client</strong>: solo conoce el Target</td><td>Spring Security (<code>DaoAuthenticationProvider</code>, vía <code>security/UserDetailsServiceImpl.java</code>)</td><td><code>service/impl/AuthServiceImpl.java</code>, <code>security/JwtAuthFilter.java</code></td></tr>
<tr><td><strong>Target</strong>: la interfaz que el cliente espera</td><td><code>UserDetails</code> (de Spring, no se toca)</td><td><code>service/TokenService.java</code> (propia)</td></tr>
<tr><td><strong>Adapter</strong>: implementa el Target y <strong>contiene</strong> al Adaptee</td><td><code>security/UsuarioDetails.java</code>: <code>private final IUsuario usuario</code></td><td><code>security/JwtUtil.java</code>: <code>private final SecretKey key</code>, <code>private final JwtParser parser</code></td></tr>
<tr><td><strong>Adaptee</strong>: lo existente con otra interfaz</td><td><code>model/interfaces/IUsuario.java</code></td><td>jjwt: <code>JwtParser</code> y <code>SecretKey</code>, armados una vez en el constructor</td></tr>
</tbody></table>"""

extra7 = f"""<h4 style="margin-top:22px">Roles</h4>{roles7}
<ul>
<li><strong>Object Adapter</strong> (composición 1 a 1): en Java es el único viable (slide 27).</li>
<li><code>UsuarioDetails</code> es el <strong>ejemplo de manual</strong>: calca el <code>AdapterPagosExternos</code> de la slide 28. Traduce <code>getRol().autoridad()</code> → <code>GrantedAuthority</code>.</li>
<li><code>JwtUtil</code> <strong>contiene</strong> al Adaptee: <code>SecretKey</code> y <code>JwtParser</code> como campos <code>final</code> (<code>2ef8410</code>). Antes rearmaba la clave y el parser en cada llamada: era un wrapper de estáticos, no un Object Adapter.</li>
</ul>
<h4>Cuándo usarlo (apunte)</h4>
<p>Integrar código de terceros o legacy <strong>que no se puede modificar</strong>. Acá: <code>UserDetails</code> (Spring) y jjwt. Si la clase se puede tocar, se modifica y listo.</p>
<div class="cuadro">
<div><h4>GRASP de fondo</h4><ul>
<li><strong>Indirection</strong>: <code>TokenService</code> entre los clientes y jjwt.</li>
<li><strong>Pure Fabrication</strong>: <code>JwtUtil</code>, <code>UsuarioDetails</code>.</li>
<li><strong>Protected Variations</strong>: cambiar la librería toca solo <code>JwtUtil</code>.</li></ul></div>
<div><h4>SOLID de fondo</h4><ul>
<li><strong>DIP</strong>: los clientes dependen de <code>TokenService</code>.</li>
<li><strong>SRP</strong>: cada Adapter solo traduce.</li>
<li><strong>Target limpio</strong> (O2): sin tipos de jjwt ni de Spring.</li></ul></div>
</div>
<h4>Preguntas incómodas</h4>
<dl class="qa">
<dt>“¿Por qué es Adapter si <code>JwtUtil</code> es de ustedes?”</dt>
<dd>El Adaptee es <strong>jjwt</strong>, no <code>JwtUtil</code>. <code>JwtUtil</code> es el Adapter.</dd>
<dt>“¿Una interfaz con una sola implementación?”</dt>
<dd>Es el costo de <strong>DIP</strong>: sin interfaz, el contrato sería la librería.</dd>
<dt>“¿<code>UsuarioDetails</code> adapta una clase propia?”</dt>
<dd>Sí, clase 9 lo admite (“externas al dominio, <strong>o no</strong>”). Lo intocable es <code>UserDetails</code>: el dominio no depende de Spring.</dd>
</dl>
<h4>Diagramas: <code>UsuarioDetails</code> (V0 → V1)</h4>
{diagramas("adapter", tit_a="Antes (V0): Usuario implements UserDetails", tit_d="Después (V1 en adelante)")}
<h4>Diagramas: <code>JwtUtil</code> (V2 → V3)</h4>"""

m7 = bloque("m7", "M7. Adapter: UsuarioDetails y JwtUtil",
    "<strong>Adapter</strong> (GoF, estructural): <strong>convertir la interfaz</strong> de algo que no podemos modificar en la que espera el cliente. jjwt es la librería de JWT (token firmado que se emite en el login y se valida en cada request).",
    "Los clientes dependían de la clase concreta <code>security/JwtUtil.java</code>, <strong>atados a jjwt</strong>; el filtro conocía su excepción.",
    cb("v2", "service/impl/AuthServiceImpl.java", lines("v2", "service/impl/AuthServiceImpl.java", r"private final JwtUtil", 1), "", method("v2", "service/impl/AuthServiceImpl.java", r"public AuthResponse login"))
    + cb("v2", "security/JwtAuthFilter.java", lines("v2", "security/JwtAuthFilter.java", r"private final JwtUtil", 1), "// ...", lines("v2", "security/JwtAuthFilter.java", r"extraerUsername", 4, 1)),
    "Target propio <code>service/TokenService.java</code>. <code>JwtUtil</code> lo implementa y <strong>contiene</strong> <code>SecretKey</code> y <code>JwtParser</code>: única clase que importa jjwt.",
    cb("main", "service/TokenService.java", body("main", "service/TokenService.java"))
    + cb("main", "security/JwtUtil.java", body("main", "security/JwtUtil.java"))
    + cb("main", "security/JwtAuthFilter.java", lines("main", "security/JwtAuthFilter.java", r"private final TokenService", 1), "// ...", lines("main", "security/JwtAuthFilter.java", r"tokenService.extraerUsername", 4), "// ...", lines("main", "security/JwtAuthFilter.java", r"tokenService.esValido", 3))
    + cb("main", "service/impl/AuthServiceImpl.java", lines("main", "service/impl/AuthServiceImpl.java", r"private final TokenService", 1)),
    "<strong>DIP + Protected Variations</strong>: la dependencia apunta a una abstracción propia; jjwt queda encerrada en un Adapter.",
    "<ul><li>Gana: cambiar de librería toca una clase; la clave se arma una vez, no por request.</li><li>Cuesta: una interfaz con una sola implementación.</li></ul>",
    "Commits <code>aa76375</code>, <code>de78c07</code> (O2), <code>2ef8410</code> (composición). Archivos: <code>service/TokenService.java</code>, <code>security/JwtUtil.java</code>, <code>security/JwtAuthFilter.java</code>, <code>service/impl/AuthServiceImpl.java</code>, <code>security/UsuarioDetails.java</code>.",
    extra=extra7,
    intro='<h4>Primero, el ejemplo de manual: <code>UsuarioDetails</code></h4><p>Implementa el Target de Spring (<code>UserDetails</code>) y <strong>contiene</strong> un <code>IUsuario</code>. El dominio no depende de Spring Security.</p>'
      + cb("main", "security/UsuarioDetails.java", body("main", "security/UsuarioDetails.java"))
      + '<h4>Después, <code>JwtUtil</code> sobre jjwt</h4>')

m8 = bloque("m8", "M8. EstadoCredito y Credito como agregado de sus cuotas",
    "<strong>Information Expert</strong> + <strong>Creator</strong>: el crédito crea y conoce sus cuotas.",
    "Estado = boolean <code>anulado</code>: <strong>sin “cancelado” ni saldo</strong> (H1, H2).",
    cb("v2", "model/Credito.java", lines("v2", "model/Credito.java", r"private boolean anulado", 1, 1), "", method("v2", "model/Credito.java", r"public void anular"))
    + cb("v2", "service/impl/CreditoServiceImpl.java", method("v2", "service/impl/CreditoServiceImpl.java", r"public void anularCredito")),
    "<code>EstadoCredito</code> <strong>derivado</strong>, no persistido. <code>Credito</code> calcula estado, saldo y si se puede anular.",
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
    "Tests: <code>CreditoTest</code>.")

# ---- M9 Strategy (foco) ----
roles9 = '''<table><thead><tr><th>Rol (apunte clase 10)</th><th>Clase</th></tr></thead><tbody>
<tr><td><strong>Context</strong>: tiene referencia a la Strategy y delega</td><td><code>model/Credito.java</code>: <code>private CalculoDeCuota calculo()</code> devuelve la estrategia; el constructor llama <code>calculo().importeCuota(...)</code></td></tr>
<tr><td><strong>Strategy</strong>: interfaz común</td><td><code>model/interfaces/CalculoDeCuota.java</code> (<code>importeCuota</code>)</td></tr>
<tr><td><strong>ConcreteStrategies</strong>: no se conocen entre sí</td><td><code>model/plan/InteresSimple.java</code>, <code>model/plan/SistemaFrances.java</code></td></tr>
<tr><td><strong>Cliente que elige</strong></td><td>quien otorga: <code>&lt;select&gt;</code> de <code>frontend/src/pages/Creditos.jsx</code> → <code>dto/request/CreditoRequest.java</code> (<code>tipoPlan</code>) → <code>model/TipoPlan.java</code> (enum persistido que enumera las estrategias)</td></tr>
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
explica9 = f"""<h4 style="margin-top:22px">Los dos planes, en criollo</h4>
<p>Cuota = <strong>capital</strong> (lo prestado) + <strong>interés</strong> (lo que cobra el que presta). Los sistemas difieren en <em>sobre qué</em> se calcula el interés.</p>
<ul>
<li><strong>Interés simple</strong>: una vez, sobre todo lo prestado, repartido en partes iguales. “30 %” = 30 % del total.</li>
<li><strong>Sistema francés</strong> (el de los bancos): cuota fija, interés mensual <strong>sobre el saldo</strong>. “5 %” = 5 % por mes. Fórmula: <code>cuota = C·i / (1 − (1+i)^−n)</code>.</li>
</ul>
<p><strong>Ejemplo: $12.000 en 6 cuotas.</strong></p>
<div class="cuadro">
<div><h4>Interés simple, tasa 30 % total</h4><p>Total = 12.000 × 1,30 = <strong>15.600</strong>. Cuota = 15.600 / 6 = <strong>2.600</strong> todos los meses: 2.000 de capital y 600 de interés. Interés total: <strong>3.600</strong>.</p></div>
<div><h4>Sistema francés, tasa 5 % mensual</h4><p>Cuota fija = <strong>{fmt(FQ)}</strong>. Mes 1: interés 5 % de 12.000 = 600. Mes 6: interés 5 % de lo poco que queda = 112,58. Total = <strong>{fmt(FQ*6)}</strong>; interés total: <strong>{fmt(int_fr)}</strong>.</p></div>
</div>
<p>Mes 1 cobran lo mismo (600). Después el simple sigue sobre 12.000 y el francés <strong>sobre lo que falta</strong>: sale más barato.</p>
<div class="mvcsvg">{_grafico()}</div>
<table><thead><tr><th>Mes</th><th>Cuota francés</th><th>Interés</th><th>Capital</th><th>Saldo después</th></tr></thead><tbody>{filas_fr}</tbody></table>
<p>Mismo campo <code>tasaInteres</code> (<code>model/Credito.java</code>), <strong>dos unidades</strong>: <code>frontend/src/pages/Creditos.jsx</code> rotula “% total” o “% mensual” según el plan.</p>
<h4>Por qué el francés: la segunda ConcreteStrategy</h4>
<ul>
<li><strong>“Misma acción, distintos algoritmos”</strong> (clase 9): calcular la cuota, dos fórmulas reales.</li>
<li>Con <strong>una sola</strong> estrategia el patrón sería sobre-ingeniería (slide 38). El francés lo hace real.</li>
<li><strong>OCP</strong>: el sistema alemán sería una clase en <code>model/plan/</code> + una constante en <code>TipoPlan</code>. <code>Credito</code> no se toca.</li>
<li><strong>Revierte el descarte del 15/09 (V2).</strong> En V2 el objetivo era la convención interfaz + clase, y un solo algoritmo alcanzaba. En V3 el tema es Strategy: necesita dos algoritmos que de verdad varíen.</li>
</ul>
<h4>Quién elige y por qué no hay <code>setEstrategia</code></h4>
<ul>
<li><strong>Elige quien otorga</strong>, en ejecución: <code>&lt;select&gt;</code> → <code>CreditoRequest.tipoPlan</code> → <code>TipoPlan.calculo()</code>.</li>
<li><strong>Sin <code>setEstrategia</code></strong>: el plan es parte del contrato. Cambiarlo alteraría cuotas ya emitidas.</li>
<li><strong>Enum y no campo de interfaz</strong>: JPA persiste un <code>@Enumerated</code>, no una interfaz. <code>TipoPlan</code> es el registro de estrategias; <code>Credito</code> no tiene <code>if</code> por tipo.</li>
</ul>
<h4>Límites conocidos</h4>
<ul>
<li>Un plan nuevo toca el enum (registro): OCP se cumple para <code>Credito</code> y las estrategias.</li>
<li>La cuota no separa capital e interés; el “interés simple” es un recargo plano (P-M9).</li>
</ul>
"""

extra9 = explica9 + f'''<h4 style="margin-top:22px">Roles</h4>{roles9}
<div class="cuadro">
<div><h4>GRASP de fondo</h4><ul>
<li><strong>Polymorphism</strong>: la variación “cómo se calcula la cuota” se resuelve con dos clases que implementan la misma operación, no con un <code>if</code> por tipo.</li>
<li><strong>Protected Variations</strong>: <code>Credito</code> queda protegido de las fórmulas; agregar o cambiar un sistema no lo toca.</li>
<li><strong>Information Expert</strong>: el total del crédito sale de las cuotas que el crédito emitió (<code>importeCuota × cantidadCuotas</code>), no de volver a correr la estrategia.</li></ul></div>
<div><h4>SOLID de fondo</h4><ul>
<li><strong>OCP</strong>: un sistema nuevo (alemán, etc.) es una clase en <code>model/plan/</code> y una constante en <code>TipoPlan</code>; <code>Credito</code> no cambia.</li>
<li><strong>DIP</strong>: <code>Credito</code> depende de <code>CalculoDeCuota</code>, no de <code>InteresSimple</code> ni de <code>SistemaFrances</code>.</li>
<li><strong>SRP</strong>: cada estrategia tiene una sola fórmula y se testea aislada (<code>InteresSimpleTest</code>, <code>SistemaFrancesTest</code>).</li></ul></div>
</div>
<h4>Cuándo usarlo (apunte)</h4>
<p>Varios algoritmos <strong>intercambiables</strong> para la misma tarea; la alarma es un <code>switch(tipo)</code> que crece. Acá, sin el patrón, el francés era un <code>if</code> dentro de <code>Credito</code>.</p>
<h4>Preguntas incómodas</h4>
<dl class="qa">
<dt>“¿Dos algoritmos no es sobre-ingeniería?”</dt>
<dd>No: <strong>los dos se usan</strong> (simple 1200 al 10 % en 3 → 440; francés → 482,54).</dd>
<dt>“Si cambia la fórmula, ¿qué pasa con los créditos otorgados?”</dt>
<dd>Nada: la cuota <strong>se guarda al otorgar</strong> y el total sale de las cuotas emitidas (O3).</dd>
<dt>“¿<code>EstadoCredito</code> no es un State?”</dt>
<dd>No: es un <strong>valor derivado</strong>, no cambia el comportamiento (O9).</dd>
</dl>'''

m9 = bloque("m9", "M9. Strategy del cálculo de cuota",
    "<strong>Strategy</strong> (GoF, comportamiento): la misma acción (calcular la cuota) con algoritmos intercambiables, encapsulados detrás de una interfaz común.",
    "Fórmula <strong>cableada</strong> en <code>model/Credito.java</code>: otro sistema era un <code>if</code> por tipo.",
    cb("v2", "model/Credito.java", method("v2", "model/Credito.java", r"public BigDecimal totalADevolver"), "", method("v2", "model/Credito.java", r"private BigDecimal calcularImporteCuota")),
    "<code>Credito</code> tiene referencia a la Strategy (<code>calculo()</code>) y <strong>delega</strong> al otorgar. El total sale de las cuotas emitidas.",
    cb("main", "model/Credito.java", lines("main", "model/Credito.java", r"this.importeCuota = calculo", 1), "", method("main", "model/Credito.java", r"private CalculoDeCuota calculo"), "", method("main", "model/Credito.java", r"public BigDecimal totalADevolver"))
    + cb("main", "model/interfaces/CalculoDeCuota.java", body("main", "model/interfaces/CalculoDeCuota.java"))
    + cb("main", "model/plan/InteresSimple.java", body("main", "model/plan/InteresSimple.java"))
    + cb("main", "model/plan/SistemaFrances.java", body("main", "model/plan/SistemaFrances.java"))
    + cb("main", "model/TipoPlan.java", body("main", "model/TipoPlan.java")),
    "<strong>Misma acción, distintos algoritmos.</strong> <code>Credito</code> no conoce ninguna fórmula.",
    "<ul><li>Gana: <strong>OCP</strong>, un sistema nuevo no toca <code>Credito</code>; cada fórmula se testea aislada.</li><li>Cuesta: la tasa cambia de unidad según el plan; columna <code>tipo_plan</code> nueva.</li></ul>",
    "Commits <code>065eb37</code>, <code>9ea428d</code>, <code>1f9fc50</code> (O3), <code>fa0c180</code> (<code>calculo()</code>).",
    extra=extra9)

m10 = bloque("m10", "M10. Dashboard también para ADMIN",
    "<strong>Control de acceso</strong> por rol.",
    "<strong>El ADMIN no veía el dashboard</strong> (TPO-010).",
    cb("v2", "config/SecurityConfig.java", lines("v2", "config/SecurityConfig.java", r'hasRole\("SUPERVISOR"\)', 1)),
    "Matcher propio para <code>/api/dashboard/**</code> con los dos roles.",
    cb("main", "config/SecurityConfig.java", lines("main", "config/SecurityConfig.java", r'"/api/admin/\*\*"', 3)),
    "El admin ve estadísticas <strong>sin cambiar de rol</strong>.",
    "Manda el backend.",
    "Cierra TPO-010. Commit <code>f7ce757</code>.")

mejoras = [m9, m7, m1, m2, m3, m4, m5, m6, m8, m10]

indice = [
 ("m9", "Cálculo de cuota", "<strong>Strategy</strong>", "foco"),
 ("m7", "TokenService / JwtUtil + UsuarioDetails", "<strong>Adapter</strong>", "foco"),
 ("m1", "Cobro sobre crédito anulado", "Information Expert", "TPO-004"),
 ("m2", "“Tiene cobranzas” ignora anuladas (absorbida por M8)", "Information Expert", "H5"),
 ("m3", "Dashboard con números verdaderos", "Corrección + Expert", "TPO-003"),
 ("m4", "Permisos de anulación en el backend", "MVC + Expert", "TPO-007"),
 ("m5", "Handlers HTTP 401/403/404/405", "MVC", "TPO-001, 002"),
 ("m6", "Cuota.estaVencida()", "Information Expert", "H3"),
 ("m8", "EstadoCredito + Credito agregado", "Expert + Creator", "H1, H2"),
 ("m10", "Dashboard para ADMIN", "Control de acceso", "TPO-010"),
]
tabla_indice = "".join(f'<tr><td><a href="#{k}">{k.upper()}</a></td><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for k, a, b, c in indice)

# ---------------- revisión ----------------
rev = [
 ("API", "f551cbc, 1ea0375, 1737bd9, 940958e", "Sin token daba 403; requests de admin sin <code>@Valid</code>.", "401 con <code>HttpStatusEntryPoint</code> en <code>config/SecurityConfig.java</code>; <code>@Valid</code> en <code>controller/AdminController.java</code>, <code>controller/SupervisorController.java</code>; <code>GET /api/creditos</code>.", "<strong>MVC</strong>: el controlador valida forma."),
 ("H1", "fcc9bf6", "Una cobranza anulada se <strong>anulaba otra vez</strong>.", "<code>model/Cobranza.java</code> <code>anular</code> la rechaza.", "<strong>Information Expert</strong>."),
 ("O1", "444031f, 64cee96", "La vista <strong>decidía</strong> si se podía anular.", "<code>dto/response/CreditoResponse.java</code> expone <code>puedeAnularse</code>; <code>frontend/src/pages/Creditos.jsx</code> lo usa y recarga.", "<strong>MVC</strong>: el modelo decide."),
 ("O2", "de78c07", "El Target <strong>exponía tipos de jjwt</strong>.", "<code>service/TokenService.java</code> <code>extraerUsername</code> devuelve <code>Optional</code>; <code>security/JwtUtil.java</code> atrapa las excepciones.", "<strong>Adapter</strong> bien aplicado."),
 ("O3", "1f9fc50", "El total <strong>recalculaba la estrategia</strong> y no cerraba con las cuotas.", "<code>model/Credito.java</code> <code>totalADevolver</code> = cuota × cantidad.", "<strong>Strategy</strong> solo al otorgar."),
 ("O4", "87f0631", "“Activos” <strong>sumaba cancelados</strong>.", "<code>service/impl/DashboardServiceImpl.java</code> cuenta <code>estado() == VIGENTE</code>.", "<strong>Information Expert</strong>."),
 ("O5", "5b7f165", "Por API se le <strong>tocaban permisos al ADMIN</strong>.", "<code>model/Usuario.java</code> <code>otorgarPermisos</code>, <code>asignarRol</code> lo rechazan.", "<strong>Regla en el modelo</strong>."),
 ("S1", "67ba784", "Escrituras <strong>sin transacción</strong>.", "<code>@Transactional</code> en <code>service/impl/*</code>; <code>readOnly</code> en lecturas.", "<strong>Unidad de trabajo</strong> en el servicio."),
 ("S2", "1e87795", "Open-in-view <strong>tapaba</strong> servicios sin transacción.", "<code>spring.jpa.open-in-view=false</code> (<code>application.properties</code>).", "Carga explícita."),
 ("S3", "45a35c9", "<code>jwt.secret</code> <strong>en un repo público</strong> (TPO-009).", "<code>${JWT_SECRET}</code> en <code>application.properties</code>.", "<strong>Config fuera del código</strong>."),
 ("S4", "904fa1e", "El 500 <strong>filtraba</strong> SQL y clases.", "“Error interno” + log en <code>exception/GlobalExceptionHandler.java</code>.", "<strong>No exponer internos</strong>."),
 ("D1, D2", "5ac2155, 3bd8b61", "<code>findByRol</code> y anotaciones de <code>AuthResponse</code> sin uso.", "Borrados (<code>repository/UsuarioRepository.java</code>, <code>dto/response/AuthResponse.java</code>).", "<strong>Código muerto</strong>."),
 ("BS1", "5f2c334", "<code>listarTodos</code> = <code>listarUsuarios</code>.", "Se borra <code>listarTodos</code> (<code>service/AdminService.java</code>).", "<strong>Código duplicado</strong>."),
 ("DF1, DF3", "830a998, 5d2dbc4", "Store huérfano; <code>console.log</code> <strong>imprimía el JWT</strong>.", "Borrados (<code>frontend/src/store/index.js</code>, <code>frontend/src/pages/Creditos.jsx</code>).", "<strong>Código muerto / de depuración</strong>."),
 ("BSF1", "c19e707", "Comentarios de copy-paste en el front.", "Borrados (<code>frontend/src/store/slices/*</code>).", "<strong>Bad smell: comentarios</strong>."),
 ("F1", "f0e5c59", "Autenticado sin rol recibía <strong>401 en vez de 403</strong>.", "<code>accessDeniedHandler</code> en <code>config/SecurityConfig.java</code>.", "<strong>401 = quién sos; 403 = no podés.</strong>"),
 ("F2", "06fc842", "JSON roto daba <strong>500</strong>.", "<code>exception/GlobalExceptionHandler.java</code> <code>handleRequestInvalida</code>: 400.", "<strong>Error del cliente = 4xx</strong>."),
 ("T34", "8eb2106", "<strong>Sin DER</strong> ni revisión del esquema.", "<code>docs/diagramas/der-v3.puml</code>; encontró I-1, I-2, I-3 (todas resueltas).", "Esquema: identidad; entidades: reglas."),
 ("T35", "013c07a, 0df40d1", "Provider armado a mano; <code>ErrorResponse</code> <strong>repetido 9 veces</strong>.", "S5: Spring arma el provider (<code>config/SecurityConfig.java</code>). BS2: un método <code>error</code> en <code>exception/GlobalExceptionHandler.java</code>.", "<strong>Convención de Spring</strong>; código duplicado."),
 ("T36", "d89d62d, 6cc5e17", "Un crédito podía quedar <strong>sin cuotas</strong>; dashboard sin saldo ni mora.", "O6: el constructor de <code>model/Credito.java</code> genera las cuotas. O7: saldo y vencido en <code>service/impl/DashboardServiceImpl.java</code>.", "<strong>Creator</strong>; <strong>Information Expert</strong>."),
 ("T40", "8888df6, 5246f27, 7c6dd63, f96f53a", "Dos cobros simultáneos <strong>duplicaban la cobranza</strong> (I-1); el servicio preguntaba permisos (BS3); rol como <code>String</code> (BS4).", "<code>@Lock(PESSIMISTIC_WRITE)</code> en <code>repository/CuotaRepository.java</code> + test de 20 hilos; <code>model/Usuario.java</code> <code>puedeAnularCredito</code>; <code>Rol</code> en los DTO.", "<strong>Bloqueo pesimista</strong>; <strong>Tell, don't ask</strong>; primitive obsession."),
 ("T42", "dfa2c12, d9b0b8f, a085f66, f5c8d05, 0e3284e", "Front: rutas por rol <strong>duplicadas</strong>, roles como strings sueltos.", "<code>frontend/src/components/RoleRoute.jsx</code>, <code>frontend/src/utils/roles.js</code>, todo por <code>src/api</code>.", "<strong>Código duplicado</strong>, strings mágicos."),
]
rev_html = "".join(f'<div class="rev" id="{i.lower()}"><h4>{i} <span class="ref">· <code>{c}</code></span></h4><p><strong>Problema.</strong> {p} <strong>Cambio.</strong> {s} <strong>Concepto.</strong> {k}</p></div>' for i, c, p, s, k in rev)

evol = [
 ("Swagger (contrato de la API)", "f551cbc, a4b2077",
  "<strong>No había contrato</strong>: el front adivinaba endpoints y códigos.",
  "springdoc publica <code>/swagger-ui.html</code> con las 20 operaciones, esquema Bearer JWT y los códigos reales (<code>config/OpenApiConfig.java</code>, <code>@Operation</code> en <code>controller/*</code>).",
  "<strong>MVC</strong>: contrato vista-controlador explícito, vía DTO."),
 ("Perfiles dev/prod y CORS", "e744600, 45a35c9",
  "Una sola config mezclaba demo y producción; <strong>consola H2 abierta sin login</strong>; CORS sin origen (TPO-008).",
  "<code>backend/src/main/resources/application-dev.properties</code> (H2, SQL en logs, CORS a <code>localhost:5173</code>) y <code>application-prod.properties</code> (sin consola, <code>CORS_ORIGIN</code> obligatoria). <code>config/SecurityConfig.java</code> <code>corsConfigurationSource</code>; <code>jwt.secret</code> desde <code>JWT_SECRET</code> (S3).",
  "<strong>Configuración externalizada</strong>: lo cómodo para la demo no llega a prod."),
 ("UI: moneda, fechas, badges, avisos", "01fabb9, 08c8fda, 1ec4ccb, f0d2372, 4f42ebd, 86b7083",
  "Importes <code>55081.29</code>, fechas ISO, crédito en una línea, <strong>sin aviso</strong> al crear, mensajes con el nombre técnico del campo.",
  "Formato es-AR en <code>frontend/src/utils/formato.js</code>; badge de estado y progreso en <code>frontend/src/pages/Creditos.jsx</code>; <code>frontend/src/components/Aviso.jsx</code>; todos los mensajes en <code>frontend/src/api/apiClient.js</code>; <code>exception/GlobalExceptionHandler.java</code> <code>handleValidation</code> sin prefijo.",
  "<strong>MVC</strong>: la vista solo presenta; sin cambios de modelo."),
 ("Dark theme", "979ab37",
  "Colores <strong>escritos a mano</strong> en cada <code>.jsx</code>.",
  "Paleta como variables CSS semánticas en <code>frontend/src/index.css</code> (<code>--color-surface</code>, <code>--color-danger</code>); <code>prefers-color-scheme</code> (tema del sistema operativo) cambia los valores. Contraste WCAG AA.",
  "<strong>Protected Variations</strong> aplicado al estilo: la paleta cambia en un lugar."),
 ("Casos de uso y pantallas nuevas", "0e7a1ad, 1210424, 28840ac",
  "UC06 y UC09 <strong>sin pantalla</strong>; un permiso otorgado no se veía hasta reloguear (H4).",
  "Búsqueda por DNI en <code>frontend/src/pages/Clientes.jsx</code> y por número en <code>frontend/src/pages/Creditos.jsx</code> (<code>fichaCredito</code>). <code>GET /api/auth/me</code> (<code>controller/AuthController.java</code> <code>me</code>) lo pide <code>frontend/src/components/PrivateRoute.jsx</code> en cada pantalla. Fichas en <code>docs/casos-de-uso/</code>.",
  "<strong>MVC</strong>: el modelo es la autoridad (M4); la vista deja de mostrar datos viejos."),
 ("Tests (37) y validación", "6f552e0..82fc486, 4d35266, 77dec02, 90d0e5e, 8888df6",
  "<strong>Cero tests</strong> en V2; un DNI largo o una deuda enorme daban 500 (I-2).",
  "27 de dominio (<code>backend/src/test/java/com/uade/tpejemplo/model/</code>), 8 de códigos HTTP (<code>controller/CodigosHttpTest.java</code>, <code>@WebMvcTest</code>), 1 de concurrencia (<code>service/CobranzaConcurrenteTest.java</code>), <code>contextLoads</code>. <code>@Size</code>/<code>@Digits</code> en <code>dto/request/</code>. La fecha de hoy entra por parámetro (<code>model/Cuota.java</code> <code>estaVencida(LocalDate)</code>).",
  "<strong>Testeabilidad</strong>: el dominio se prueba sin Spring ni reloj."),
 ("Limpieza", "ddbdebb, 3478af6, c36658f, 6a1c363, 4713828",
  "Javadoc que repetía el código, <code>.factorypath</code> trackeado, docs de proceso en el zip.",
  "1-3 líneas por clase y <strong>una línea por patrón</strong> (<code>// Adapter: ...</code> en <code>security/JwtUtil.java</code>); <code>export-ignore</code> en <code>.gitattributes</code>; README corto.",
  "<strong>Bad smell: comentarios</strong>. El zip lleva solo código vigente."),
]
evol_html = "".join(f'<div class="rev"><h4>{t} <span class="ref">· commit <code>{c}</code></span></h4><p><strong>Problema.</strong> {p}</p><p><strong>Solución.</strong> {s}</p><p><strong>Buena práctica.</strong> {k}</p></div>' for t, c, p, s, k in evol)

convenciones = """<p>Convención: <strong>una <code>I&lt;Clase&gt;</code> por clase de modelo</strong> en <code>model/interfaces/</code> y <strong><code>XService</code> + <code>service/impl/XServiceImpl</code></strong>. Excepciones, a propósito:</p>
<table><thead><tr><th>Clase</th><th>Excepción</th><th>Motivo</th></tr></thead><tbody>
<tr><td><code>model/EstadoCredito.java</code></td><td>sin <code>IEstadoCredito</code></td><td>Enum de <strong>valores sin comportamiento</strong>: la interfaz quedaría vacía.</td></tr>
<tr><td><code>model/TipoPlan.java</code></td><td>sin <code>ITipoPlan</code></td><td>Enum <strong>registro de estrategias</strong>; su única operación devuelve la Strategy.</td></tr>
<tr><td><code>model/interfaces/CalculoDeCuota.java</code></td><td>sin prefijo <code>I</code></td><td>Es la <strong>interfaz Strategy</strong>, no la de una clase: nombre de rol, como <code>EstrategiaDescuento</code> en la slide.</td></tr>
<tr><td><code>service/TokenService.java</code> → <code>security/JwtUtil.java</code></td><td>no es <code>TokenServiceImpl</code> en <code>service/impl/</code></td><td>Es el <strong>Adapter</strong>: pesa el nombre de rol, y es infraestructura, no caso de uso.</td></tr>
<tr><td><code>model/interfaces/IRol.java</code></td><td>sin consumidor como tipo</td><td>Existe <strong>por la convención</strong>; ningún cliente depende de ella (ISP en la matriz).</td></tr>
</tbody></table>"""

matriz = [
 ("Information Expert", "<code>model/Credito.java</code> <code>estado</code>, <code>saldo</code>, <code>puedeAnularse</code>; <code>model/Cuota.java</code> <code>estaVencida</code>", "Cumple"),
 ("Creator", "<code>model/Credito.java</code> genera sus cuotas (O6); <code>Cuota.registrarCobranza</code> crea la <code>Cobranza</code>", "Cumple"),
 ("Controller", "<code>controller/*Controller</code> por caso de uso, delegan en <code>XService</code>", "Cumple"),
 ("Bajo acoplamiento / Alta cohesión", "controllers → interfaces de servicio; clientes → <code>service/TokenService.java</code>", "Cumple"),
 ("Polymorphism", "<code>model/interfaces/CalculoDeCuota.java</code>, sin <code>if</code> por plan", "Cumple"),
 ("Pure Fabrication / Indirection", "repositorios, <code>security/JwtUtil.java</code>, <code>security/UsuarioDetails.java</code>", "Cumple"),
 ("Protected Variations", "<code>CalculoDeCuota</code> (fórmula), <code>TokenService</code> (librería)", "Cumple"),
 ("SRP / OCP / LSP", "una fórmula por estrategia; plan nuevo sin tocar <code>Credito</code>; estrategias intercambiables", "Cumple"),
 ("ISP", "<code>TokenService</code> (3 métodos, todos usados); <code>model/interfaces/IRol.java</code> sin consumidor", "Parcial"),
 ("DIP", "servicios inyectados por interfaz; <code>TokenService</code> implementado en <code>security/</code>", "Parcial"),
]
matriz_html = "<table><thead><tr><th>Principio</th><th>Dónde</th><th>Veredicto</th></tr></thead><tbody>" + "".join(f"<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in matriz) + "</tbody></table>"


def cap(sub, nom, alt):
    return f'<figure><figcaption>{alt}</figcaption><a href="capturas/{sub}/{nom}.png"><img src="capturas/{sub}/{nom}.png" alt="{alt}" style="width:100%;border:1px solid var(--linea);border-radius:4px"></a></figure>'

capturas_ui = ('<h3>Capturas de la UI</h3><p>Antes y después de las mejoras de presentación, y el tema oscuro.</p>'
    + '<div class="par">' + cap("ui-antes", "03-creditos", "Créditos, antes") + cap("ui-despues", "03-creditos", "Créditos, después") + '</div>'
    + '<div class="par">' + cap("ui-antes", "04-cobranzas", "Cobranzas, antes") + cap("ui-despues", "04-cobranzas", "Cobranzas, después") + '</div>'
    + '<div class="par">' + cap("dark", "creditos", "Créditos, dark theme") + cap("dark", "dashboard", "Dashboard, dark theme") + '</div>')

# ---------------- timeline ----------------
n_v3 = len(subprocess.run(["git", "-C", REPO, "log", "--oneline", "--no-merges", "v2..main"], capture_output=True, text=True).stdout.strip().split("\n"))
log_v3 = subprocess.run(["git", "-C", REPO, "log", "--oneline", "v2..main"], capture_output=True, text=True).stdout.strip()

timeline = f'''<div class="timeline">
<div class="hito"><div class="punto"></div><h4>V0</h4><p class="tema">Punto 0, proyecto inicial</p><p class="meta"><code>main@2a90af8</code> (repo Arreglos)</p>
<ul><li>CRUD de clientes, créditos y cobranzas</li><li>Cuota con importe cargado a mano</li><li>Usuario como UserDetails</li><li>MetaCobranza (ABM sin uso)</li></ul></div>
<div class="hito"><div class="punto"></div><h4>V1</h4><p class="tema">Iteración 1: bad smells</p><p class="meta">Entregada 08/09 · <code>andrei-iteracion1@86c75cc</code> · 28 commits</p>
<ul><li>13 smells corregidos (god class, data class, primitive obsession, encapsulamiento)</li><li><code>MetaCobranza</code> eliminada; <code>Cuota.estaPagada()</code> y <code>registrarCobranza</code></li><li><code>UsuarioDetails</code> como Adapter</li><li>Resueltos TPO-005, 006, 013, 015</li></ul></div>
<div class="hito"><div class="punto"></div><h4>V2</h4><p class="tema">Iteración 2: GRASP + interfaces</p><p class="meta">Mergeada 15/09 · <code>main@45e228c</code> (tag <code>v2</code>) · 5 commits</p>
<ul><li>Information Expert: <code>Cobranza.anular()</code>, <code>Credito.anular()</code></li><li>Creator: <code>Usuario.nuevo</code></li><li>Interfaz por cada clase del modelo y de servicio</li><li>Revierte §3.7 del informe 1 (Lazy class): interfaces de servicio restituidas</li></ul></div>
<div class="hito actual"><div class="punto"></div><h4>V3</h4><p class="tema">Iteración 3: MVC + Strategy + Adapter</p><p class="meta">Entrega 13/10/2026 · repo V3, <code>main</code> · {n_v3} commits sin merges</p>
<ul><li><strong>Strategy</strong>: cálculo de cuota, interés simple y sistema francés (M9)</li><li><strong>Adapter</strong>: <code>TokenService</code> sobre jjwt (M7)</li><li><code>EstadoCredito</code>, saldo, mora (M6, M8)</li><li>Permisos y errores HTTP en el backend (M4, M5), Swagger</li><li>Dashboard corregido y con saldo y vencido (M3, M10, O7); el crédito crea sus cuotas (O6); 37 tests</li><li>Revierte V2: sistema francés descartado el 15/09</li><li>Swagger, perfiles dev/prod, UI, dark theme, UC06/UC09</li></ul></div>
</div>
<details><summary>Commits V2 → V3 (git log v2..main)</summary><pre><code>{e(log_v3)}</code></pre></details>'''

mapeo = [
 ("model/*, model/interfaces/*, model/plan/*", "Modelo", "Datos y reglas de negocio (Expert). Acá viven las estrategias de M9 y el agregado de M8."),
 ("repository/*", "Modelo", "Acceso a datos con Spring Data JPA (interfaces que Spring implementa a partir de los nombres y las <code>@Query</code>)."),
 ("service/*, service/impl/*", "Modelo", "Orquestan casos de uso y fijan la transacción (S1). <code>TokenService</code> es el Target del Adapter de M7."),
 ("exception/BusinessException, ResourceNotFoundException", "Modelo", "Las lanza el modelo para decir “viola una regla” / “no existe”."),
 ("controller/*", "Controlador", "Reciben el evento HTTP, validan forma (<code>@Valid</code>), identifican al usuario (<code>@AuthenticationPrincipal</code>, M4), invocan al modelo y devuelven DTO."),
 ("dto/request/*, dto/response/*", "Controlador (frontera)", "Contrato vista-controlador (DTO/VO). Se arman desde las interfaces del modelo: el modelo no conoce el DTO."),
 ("exception/GlobalExceptionHandler", "Controlador", "Traduce excepciones a HTTP: 400 regla, 401 sin autenticar, 403 sin permiso, 404, 405, 500 sin detalles internos (M5, S4)."),
 ("security/*, config/SecurityConfig", "Controlador", "Se ejecutan antes del controller y deciden si el evento entra. Sin token responde 401 (<code>HttpStatusEntryPoint</code>); con token y sin rol, 403. <code>JwtUtil</code> y <code>UsuarioDetails</code> son Adapters."),
 ("config/OpenApiConfig + anotaciones <code>@Operation</code>", "Controlador (contrato)", "Publica el contrato de la API en Swagger UI (<code>/swagger-ui.html</code>), con esquema Bearer JWT."),
 ("config/DataInitializer", "Modelo", "Siembra usuarios vía <code>Usuario.nuevo</code>; no atiende eventos."),
 ("Frontend pages/*, components/*", "Vista", "Presentan datos y envían acciones; la decisión (<code>puedeAnularse</code>, O1) viene del modelo."),
 ("Frontend store/slices/*, api/*", "Vista", "Estado del cliente (Redux) y única puerta HTTP (<code>api/apiClient.js</code>) hacia los <code>@RestController</code>."),
]
rows = "\n".join(f"<tr><td><code>{a}</code></td><td><strong>{b}</strong></td><td>{c}</td></tr>" for a, b, c in mapeo)

tecnologias = '''<dl class="tec">
<dt>Spring Boot</dt><dd>Framework Java del backend: REST, servicios, seguridad.</dd>
<dt>Spring Security</dt><dd>Autenticación y autorización: filtra cada request, decide 401/403.</dd>
<dt>JWT y jjwt</dt><dd>Token firmado del login; jjwt lo genera y valida. Adaptee de M7.</dd>
<dt>JPA / Hibernate / Spring Data</dt><dd>Mapea clases a tablas; Spring Data genera los repositorios.</dd>
<dt>H2</dt><dd>Base en memoria: corre sin instalar motor.</dd>
<dt>Lombok</dt><dd>Genera getters, constructores y loggers por anotación.</dd>
<dt>springdoc / Swagger UI</dt><dd>Publica el contrato de la API en una página navegable.</dd>
<dt>React, Redux, Vite</dt><dd>Interfaz por componentes, estado del cliente, servidor de desarrollo y build.</dd>
<dt>JUnit 5, AssertJ, Mockito</dt><dd>Tests, aserciones y objetos simulados; <code>@WebMvcTest</code> levanta solo la capa web.</dd>
<dt>Bean Validation</dt><dd><code>@NotBlank</code>, <code>@Size</code>, <code>@Digits</code> en los DTO; lo inválido sale 400.</dd>
<dt>Maven</dt><dd>Build: dependencias, compilación, tests.</dd>
<dt>PlantUML y d2</dt><dd>Diagramas a partir de texto.</dd>
</dl>'''


def archify_svg(n):
    t = open(os.path.join(REPO, f"docs/diagramas/archify/{n}.svg")).read()
    return re.sub(r'<svg ', '<svg style="width:100%;height:auto" ', t, count=1)

def d2svg(n):
    t = re.sub(r"<\?xml[^>]*\?>", "", open(os.path.join(REPO, f"docs/diagramas/d2/{n}.svg")).read())
    return re.sub(r'<svg ', '<svg style="width:100%;height:auto;max-height:900px" ', t, count=1)

der_svg = re.sub(r"<\?xml[^>]*\?>", "", open(os.path.join(REPO, "docs/diagramas/der-v3.svg")).read())
der_svg = re.sub(r'(<svg[^>]*?) style="[^"]*" width="[^"]*" height="[^"]*"', r'\1 style="width:100%;height:auto"', der_svg, count=1)

pendientes = '''<ul>
<li><strong>H8</strong>: trazabilidad. <code>model/Cobranza.java</code> no sabe qué usuario cobró ni quién anuló; es modelo nuevo y cambia la API.</li>
<li><strong>O8</strong>: pagos parciales. Cambia <code>Cuota.estaPagada()</code> a saldo por cuota; fuera de alcance de V3, hoy se exige el importe exacto (TPO-006).</li>
<li><strong>TPO-014</strong>: el paquete <code>com.uade.tpejemplo</code> y <code>TpEjemploApplication</code> no nombran el sistema. Es un diff ruidoso que taparía los cambios reales: se evalúa para el 17/11.</li>
</ul>'''

doc = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reporte V3 — TPO Grupo 7</title><style>{CSS}</style></head>
<body>
<div id="barra"><strong style="color:var(--navy)">Reporte V3</strong>
<nav><a href="#portada">Portada</a><a href="#timeline">Timeline</a><a href="#tecnologias">Tecnologías</a><a href="#mvc">MVC</a><a href="#mejoras">Mejoras</a><a href="#m9">Strategy</a><a href="#m7">Adapter</a><a href="#convenciones">Convenciones</a><a href="#matriz">GRASP/SOLID</a><a href="#evolucion">Evolución</a><a href="#revision">Revisión</a><a href="#verificacion">Verificación</a><a href="#casos">Casos de uso</a><a href="#clases">Diagramas</a><a href="#pendientes">Pendientes</a></nav>
<button class="sec" onclick="window.print()">Exportar PDF</button></div>
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
<p><strong>MVC distribuido</strong>: modelo y controlador en Spring Boot, vista en React. Vista y controlador se hablan <strong>por DTO</strong> (clase 9).</p>
<div class="clases">{archify_svg("mvc")}</div>
<table><thead><tr><th>Clase / paquete</th><th>Componente</th><th>Justificación</th></tr></thead><tbody>{rows}</tbody></table>
<h3>Qué cambió en V3</h3>
<ul>
<li><strong>Contrato publicado</strong>: Swagger (<code>config/OpenApiConfig.java</code>).</li>
<li><strong>Todos los errores traducidos</strong> a HTTP (<code>exception/GlobalExceptionHandler.java</code>).</li>
<li><strong>401 ≠ 403</strong> (<code>config/SecurityConfig.java</code>).</li>
<li><strong>La regla en el modelo, la vista solo oculta</strong> (M4, O1, O5).</li>
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
<p><strong>Los dos parciales, defendibles:</strong></p>
<ul>
<li><strong>ISP</strong>: <code>IRol</code> la exige la convención; no rompe nada.</li>
<li><strong>DIP</strong>: el Target vive en <code>service/</code> y el Adapter en <code>security/</code>: <strong>el detalle depende de la abstracción</strong>. Es DIP bien aplicado; solo se aparta de la convención de paquetes.</li>
</ul>
</section>

<section id="evolucion"><h2>Evolución del sistema: mejoras propuestas e implementadas</h2>
<p>Problemas del sistema que <strong>supimos resolver</strong>, más allá del patrón de la iteración.</p>
{evol_html}
{capturas_ui}
</section>

<section id="revision"><h2>Mejoras de la revisión</h2>
<p>Revisión de solo lectura después de M1-M10: <strong>usos flojos de los conceptos, código muerto y bad smells</strong>. Entró lo chico que tapaba un hueco visible; lo abierto va al <a href="../backlog.md">backlog</a>.</p>
{rev_html}
</section>

<section id="verificacion"><h2>Verificación</h2>
<ul>
<li><strong>37 tests, 0 fallas</strong> (<code>mvn test</code>): 27 de dominio, 8 HTTP (<code>@WebMvcTest</code>), 1 de concurrencia, <code>contextLoads</code>.</li>
<li><strong>Smoke de API</strong>: 22 casos con curl, todos OK.</li>
<li><strong>Verificación final</strong>: encontró 401/403 y 500 mal mapeados; corregidos en F1, F2.</li>
<li><strong>Recorrido visual</strong>: 2 fallas, corregidas en O1 y <code>d35fc0e</code>.</li>
</ul>
</section>

<section id="casos"><h2>Casos de uso</h2>
<p>Fichas, diagrama y trazabilidad: <a href="../casos-de-uso/README.md"><code>docs/casos-de-uso/README.md</code></a>. Verificados con <code>docs/casos-de-uso/verificar-cu.sh</code>.</p>
<p><a href="../casos-de-uso/casos-de-uso-v3.svg"><img src="../casos-de-uso/casos-de-uso-v3.svg" alt="Diagrama de casos de uso V3" style="width:100%;background:#fff;border:1px solid var(--linea);border-radius:4px"></a></p>
</section>

<section id="clases"><h2>Diagramas de clases y DER</h2>
<p>Entregable UML: <a href="../diagramas/clases-v3-general.svg">vista general</a> y <a href="../diagramas/clases-v3-modelo.svg">modelo</a> (<code>docs/diagramas/clases-v3.puml</code>). Abajo, vistas en d2 (diagramas desde texto).</p>
<h3>Strategy</h3>
<div class="clases">{d2svg("strategy")}</div>
<h3>Adapter</h3>
<div class="clases">{d2svg("adapter")}</div>
<h3>Modelo de dominio</h3>
<p>El rombo lleno es composición: el todo crea y contiene a sus partes.</p>
<div class="clases">{d2svg("dominio")}</div>
<h3>DER</h3>
<p>Las tablas que genera JPA, con claves y restricciones. Fuente: <code>docs/diagramas/der-v3.puml</code>.</p>
<div class="clases">{der_svg}</div>
</section>

<section id="pendientes"><h2>Cambios pendientes</h2>
{pendientes}
<p>Lista completa de hechos y pendientes para Teams: <code>docs/entrega/lista-mejoras.md</code>.</p>
</section>
</main>
</body></html>'''
open(OUT + "/reporte-v3.html", "w").write(doc)
print(len(doc))
