import os, re, subprocess, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from estilo import CSS, mvc_svg

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


def bloque(id_, titulo, patron, problema, antes, solucion, despues, por_que, consecuencias, ref="", extra="", diag=None):
    return f'''<article class="mejora" id="{id_}">
<h3>{titulo} <span class="badge impl">implementada</span></h3>
{('<p class="ref">' + ref + '</p>') if ref else ''}
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
    "Information Expert (GRASP): la cuota conoce a su crédito y el crédito conoce su estado, así que la cuota decide si se la puede cobrar.",
    "<code>Cuota.registrarCobranza</code> (<code>model/Cuota.java</code>) validaba cuota paga e importe, nunca el estado del crédito: se cobraban cuotas de un crédito anulado (TPO-004).",
    cb("v2", "model/Cuota.java", method("v2", "model/Cuota.java", r"public Cobranza registrarCobranza")),
    "Primera validación del método: si el crédito está anulado, <code>BusinessException</code> (el handler la devuelve como 400).",
    cb("main", "model/Cuota.java", method("main", "model/Cuota.java", r"public Cobranza registrarCobranza")),
    "Un crédito anulado no puede recibir pagos, y esa es una regla del dominio. <code>Cuota</code> ya valida las otras condiciones del cobro, así que se completa ahí sin tocar el servicio ni el controlador.",
    "Gana: la regla está en un solo lugar y vale para cualquier camino que cobre. Cuesta: <code>Cuota</code> navega a <code>Credito</code> en cada cobro, una relación que ya existía.",
    "Cierra TPO-004. Clase y método: <code>model/Cuota.java</code>, <code>registrarCobranza(BigDecimal)</code>. Test: <code>backend/src/test/java/com/uade/tpejemplo/model/CuotaTest.java</code>.")

m2 = f'''<article class="mejora" id="m2">
<h3>M2. “Tiene cobranzas” ignora las anuladas <span class="badge impl">absorbida por M8</span></h3>
<p class="ref">No tiene commit propio: la resolvió <a href="#m8">M8</a> al llevar la regla al agregado <code>Credito</code>. Se deja numerada para que la lista de mejoras conserve la trazabilidad con el análisis previo.</p>
<dl class="estructura">
<dt>Patrón</dt><dd>Information Expert: quien sabe si una cobranza cuenta es <code>Cuota.estaPagada()</code>, que ya ignoraba las anuladas.</dd>
<dt>Problema (código antes)</dt><dd><p>La consulta contaba también las cobranzas anuladas. Si se cobraba una cuota y se anulaba esa cobranza, el crédito ya no se podía anular nunca.</p>
{cb("v2", "repository/CobranzaRepository.java", lines("v2", "repository/CobranzaRepository.java", "existeCobranzaDelCredito", 1, 1))}
{cb("v2", "service/impl/CreditoServiceImpl.java", method("v2", "service/impl/CreditoServiceImpl.java", r"public void anularCredito"))}</dd>
<dt>Solución (código después)</dt><dd><p><code>Credito.tieneCobranzas()</code> (<code>model/Credito.java</code>) recorre sus cuotas con <code>Cuota::estaPagada</code>. <code>existeCobranzaDelCredito</code> desapareció del repositorio. Código en M8.</p></dd>
<dt>Por qué</dt><dd>Era el mismo error que TPO-005 (el boolean <code>anulada</code> sin filtrar). Al mover la decisión al crédito, la regla ya correcta de la cuota se reutiliza en vez de duplicarse en una query.</dd>
<dt>Consecuencias</dt><dd>Las mismas que M8. Test: <code>CreditoTest</code>, caso “la única cobranza fue anulada”.</dd>
</dl>
{diagramas("m2", tit_a="Antes (V2): el servicio consulta y le pasa un boolean al crédito", solo_antes=True)}
</article>'''

m3 = bloque("m3", "M3. Dashboard con números verdaderos",
    "Sin patrón GoF: corrección de consultas. La parte de “créditos activos” aplica Information Expert (la vigencia la define <code>Credito.estado()</code>).",
    "<code>DashboardServiceImpl.obtenerEstadisticasGenerales()</code> contaba todos los créditos (también anulados), “financiado” sumaba <code>importeCuota</code> (el valor de una cuota, no lo prestado) y “cobrado” sumaba cobranzas anuladas (TPO-003).",
    cb("v2", "service/impl/DashboardServiceImpl.java", method("v2", "service/impl/DashboardServiceImpl.java", r"obtenerEstadisticasGenerales"))
    + cb("v2", "repository/CreditoRepository.java", lines("v2", "repository/CreditoRepository.java", "sumarImporteCuotaTotal", 1, 1))
    + cb("v2", "repository/CobranzaRepository.java", lines("v2", "repository/CobranzaRepository.java", "sumarImporteTotal", 1, 1)),
    "Las sumas filtran lo anulado y “financiado” suma <code>deudaOriginal</code>. “Créditos activos” cuenta los que <code>Credito.estado()</code> da como <code>VIGENTE</code> (ni anulados ni cancelados), con la misma carga sin N+1 que usa M8 (ajuste O4 de la revisión).",
    cb("main", "service/impl/DashboardServiceImpl.java", method("main", "service/impl/DashboardServiceImpl.java", r"obtenerEstadisticasGenerales"))
    + cb("main", "repository/CreditoRepository.java", lines("main", "repository/CreditoRepository.java", "sumarDeudaOriginalVigente", 1, 1))
    + cb("main", "repository/CobranzaRepository.java", lines("main", "repository/CobranzaRepository.java", "sumarImporteVigente", 1, 1)),
    "Los cuatro números del supervisor tienen que reflejar la cartera viva. La regla de vigencia vive en un solo lugar del modelo y el dashboard la consulta en vez de repetirla en SQL.",
    "Gana: el dashboard y el listado de créditos coinciden. Cuesta: “créditos activos” carga todos los créditos en memoria; para el volumen del TPO no pesa, con miles de créditos convendría una consulta que replique la regla.",
    "Cierra TPO-003 y la parte de anulados de B-04 (V0). Commits <code>8877f29</code> y <code>87f0631</code> (O4).")

m4 = bloque("m4", "M4. Permisos de anulación aplicados en el backend",
    "MVC (validación por capa) + Information Expert: la vista oculta el botón, el controlador identifica al usuario y el modelo (<code>Permisos</code>) decide.",
    "<code>CreditoController.anularCredito</code> y <code>CreditoServiceImpl.anularCredito</code> no sabían quién anulaba. Los permisos que asigna el supervisor se guardaban y nadie los consultaba: solo el front ocultaba el botón y cualquier operador anulaba por API (TPO-007). Lo mismo en <code>CobranzaController</code> / <code>CobranzaServiceImpl.anularCobranza</code>.",
    cb("v2", "controller/CreditoController.java", method("v2", "controller/CreditoController.java", r"anularCredito"))
    + cb("v2", "service/impl/CreditoServiceImpl.java", method("v2", "service/impl/CreditoServiceImpl.java", r"public void anularCredito")),
    "El controlador recibe el usuario autenticado con <code>@AuthenticationPrincipal</code> y el servicio le pregunta a sus <code>Permisos</code>. Si no puede, <code>AccessDeniedException</code>, que <code>GlobalExceptionHandler</code> traduce a 403.",
    cb("main", "controller/CreditoController.java", method("main", "controller/CreditoController.java", r"public ResponseEntity<Void> anularCredito"))
    + cb("main", "service/impl/CreditoServiceImpl.java", method("main", "service/impl/CreditoServiceImpl.java", r"public void anularCredito")),
    "El caso de uso “Asignar permisos de anulación” (CU19) era decorativo. En MVC la vista puede ocultar, pero quien valida es el modelo; la pregunta “¿puede anular?” la contesta <code>Permisos</code>, que tiene el dato.",
    "Gana: el permiso se respeta aunque se llame a la API sin el front (smoke: 403 con <code>user</code>). Cuesta: <code>anularCredito</code> y <code>anularCobranza</code> ahora reciben el <code>IUsuario</code> autenticado.",
    "Cierra TPO-007 (B-01 de V0). Archivos: <code>controller/CreditoController.java</code>, <code>controller/CobranzaController.java</code>, <code>service/impl/CreditoServiceImpl.java</code>, <code>service/impl/CobranzaServiceImpl.java</code>, <code>security/UsuarioDetails.java</code> (<code>getUsuario()</code>).")

m5 = bloque("m5", "M5. Handlers HTTP específicos",
    "MVC: el controlador (<code>GlobalExceptionHandler</code>, un <code>@RestControllerAdvice</code> de Spring) convierte errores del modelo y de la infraestructura en respuestas HTTP con el código correcto.",
    "<code>GlobalExceptionHandler</code> solo conocía tres excepciones; el resto caía en <code>handleGeneral</code> y respondía 500. Login incorrecto, ruta inexistente, acceso denegado y método no soportado daban 500 (TPO-001, TPO-002).",
    cb("v2", "exception/GlobalExceptionHandler.java", method("v2", "exception/GlobalExceptionHandler.java", r"handleGeneral")),
    "Cuatro handlers nuevos con el mismo <code>ErrorResponse</code>: 401, 403, 404 y 405. El 500 genérico ya no devuelve el mensaje interno y lo loguea (S4).",
    cb("main", "exception/GlobalExceptionHandler.java",
       method("main", "exception/GlobalExceptionHandler.java", r"handleAuth"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleDenied"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleNoResource"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleMetodo"), "",
       method("main", "exception/GlobalExceptionHandler.java", r"handleGeneral")),
    "Un error del cliente no es una falla del servidor. El front ahora distingue credenciales malas (401), falta de permiso (403), recurso inexistente (404) y método incorrecto (405) de un 500 real.",
    "Gana: los códigos que documenta Swagger son los que la API devuelve de verdad. Cuesta: un handler por familia de excepciones; el armado de <code>ErrorResponse</code> se repite (smell BS2, pendiente).",
    "Cierra TPO-001 y TPO-002. Archivo: <code>exception/GlobalExceptionHandler.java</code>.")

m6 = bloque("m6", "M6. Cuota.estaVencida()",
    "Information Expert (GRASP): la cuota tiene <code>fechaVencimiento</code> y sabe si está pagada, entonces ella responde si está vencida.",
    "<code>fechaVencimiento</code> se guardaba y nadie la usaba. No existía la mora: la vista solo distinguía Pagada / Pendiente.",
    cb("v2", "model/Cuota.java", method("v2", "model/Cuota.java", r"public boolean estaPagada")),
    "<code>Cuota.estaVencida()</code>, declarado en <code>ICuota</code>. <code>CuotaResponse</code> suma el campo <code>vencida</code> y <code>frontend/src/pages/Creditos.jsx</code> muestra Pagada / Vencida / Pendiente.",
    cb("main", "model/Cuota.java", method("main", "model/Cuota.java", r"public boolean estaPagada"), "", method("main", "model/Cuota.java", r"public boolean estaVencida")),
    "Saber qué cuotas están en mora es la pregunta central de un sistema de cobranzas (hueco H3, A-05 de V0). La regla vive en la entidad que tiene los datos, no en el servicio ni en la vista.",
    "Gana: la mora es consultable desde el modelo y reutilizable (dashboard, reportes). Cuesta: depende de <code>LocalDate.now()</code>; para testear una fecha fija habría que inyectar un <code>Clock</code>.",
    "Archivos: <code>model/Cuota.java</code>, <code>model/interfaces/ICuota.java</code>, <code>dto/response/CuotaResponse.java</code>, <code>frontend/src/pages/Creditos.jsx</code>.")

# ---- M7 Adapter (foco) ----
roles7 = '''<table><thead><tr><th>Rol (apunte clase 10)</th><th>Adapter 1: tokens (nuevo en V3)</th><th>Adapter 2: usuario (desde V1)</th></tr></thead><tbody>
<tr><td><strong>Cliente</strong>: solo conoce el Target</td><td><code>service/impl/AuthServiceImpl.java</code> (login y registro) y <code>security/JwtAuthFilter.java</code> (cada request)</td><td><code>DaoAuthenticationProvider</code> de Spring Security, vía <code>security/UserDetailsServiceImpl.java</code></td></tr>
<tr><td><strong>Target</strong>: la interfaz que el cliente espera</td><td><code>service/TokenService.java</code> (propia: <code>generarToken</code>, <code>extraerUsername</code>, <code>esValido</code>)</td><td><code>UserDetails</code> (de Spring Security, no la controlamos)</td></tr>
<tr><td><strong>Adapter</strong>: implementa el Target y contiene al Adaptado</td><td><code>security/JwtUtil.java implements TokenService</code></td><td><code>security/UsuarioDetails.java implements UserDetails</code></td></tr>
<tr><td><strong>Adaptado</strong>: lo existente que no se toca</td><td>la librería jjwt (<code>Jwts.builder()</code>, <code>Jwts.parser()</code>, <code>Claims</code>, <code>Keys</code>, <code>JwtException</code>)</td><td><code>model/interfaces/IUsuario.java</code> / <code>model/Usuario.java</code></td></tr>
</tbody></table>'''

extra7 = f'''<h4 style="margin-top:22px">Roles</h4>{roles7}
<p>Variante: <strong>Object Adapter</strong> (por composición). <code>UsuarioDetails</code> guarda un <code>IUsuario</code> en un campo y <code>JwtUtil</code> delega en la API de jjwt. El Class Adapter necesita herencia múltiple y en Java no se puede.</p>
<div class="cuadro">
<div><h4>GRASP de fondo</h4><ul>
<li><strong>Indirection</strong>: <code>TokenService</code> se interpone entre los clientes y jjwt.</li>
<li><strong>Pure Fabrication</strong>: <code>JwtUtil</code> y <code>UsuarioDetails</code> no son conceptos del préstamo; existen para mantener el dominio limpio.</li>
<li><strong>Protected Variations</strong>: si cambia la librería de tokens, el cambio queda encerrado en <code>JwtUtil</code>.</li>
<li><strong>Low Coupling</strong>: el filtro y el servicio de auth no importan nada de jjwt.</li></ul></div>
<div><h4>SOLID de fondo</h4><ul>
<li><strong>DIP</strong>: <code>AuthServiceImpl</code> y <code>JwtAuthFilter</code> dependen de la abstracción propia <code>TokenService</code>, no de una clase concreta atada a una librería.</li>
<li><strong>SRP</strong>: <code>JwtUtil</code> solo traduce entre nuestro contrato y jjwt; <code>UsuarioDetails</code> solo traduce entre <code>IUsuario</code> y <code>UserDetails</code>.</li>
<li><strong>OCP</strong>: otra implementación de tokens (opacos, otra librería) es una clase nueva que implementa <code>TokenService</code>, sin modificar los clientes.</li></ul></div>
</div>
<h4>Cuándo usarlo (y por qué acá sí)</h4>
<p>El apunte dice: usar Adapter cuando hay que integrar código de terceros o legacy <em>que no se puede modificar</em>. Si se puede tocar la clase origen, es más simple modificarla. Lo que no podemos tocar acá es jjwt, la librería de terceros, y no <code>JwtUtil</code>: por eso jjwt es el Adaptado y <code>JwtUtil</code> el Adapter. En el segundo caso, <code>UserDetails</code> es de Spring Security y tampoco se toca. <code>Usuario</code> sí es nuestro, pero en V0 implementaba <code>UserDetails</code> con cuatro <code>return true</code> y dejaba al dominio atado al framework.</p>
<h4>Errores típicos del apunte, contrastados</h4>
<ul>
<li><em>“El Target sigue exponiendo tipos del Adaptado”</em>: en la primera versión de M7 el filtro atrapaba <code>io.jsonwebtoken.JwtException</code> y <code>esValido</code> recibía un <code>UserDetails</code>. La revisión O2 lo corrigió: <code>extraerUsername</code> devuelve <code>Optional&lt;String&gt;</code>, <code>JwtUtil</code> atrapa las excepciones de jjwt y <code>esValido</code> recibe el username.</li>
<li><em>“Usarlo cuando se puede cambiar la clase”</em>: no aplica. Ni jjwt ni <code>UserDetails</code> se pueden cambiar.</li>
<li><em>“Decenas de Adapters sobre un subsistema”</em>: hay uno por subsistema externo (tokens y Spring Security), así que no hace falta una Facade.</li>
<li><em>“Olvidar mantenerlo sincronizado”</em>: si jjwt cambia su API (ya pasó de <code>parserBuilder()</code> a <code>parser()</code> en la 0.12), se toca solo <code>JwtUtil</code>.</li></ul>
<h4>Preguntas incómodas</h4>
<dl class="qa">
<dt>“¿Por qué es un Adapter, si <code>JwtUtil</code> es código de ustedes?”</dt>
<dd>Porque el Adaptado es jjwt, no <code>JwtUtil</code>. <code>JwtUtil</code> es el Adapter: implementa nuestro Target (<code>service/TokenService.java</code>) traduciendo a <code>Jwts.builder()</code> / <code>Jwts.parser()</code>. Los clientes (<code>JwtAuthFilter</code>, <code>AuthServiceImpl</code>) no saben que jjwt existe.</dd>
<dt>“¿Una interfaz con una sola implementación no es sobre-ingeniería?”</dt>
<dd>Es el costo que el apunte acepta para DIP: con una interfaz propia, cambiar el proveedor de tokens o sustituirlo en un test es tocar una clase. Además el Target no expone nada de jjwt: sin la interfaz, el contrato <em>sería</em> la librería.</dd>
<dt>“<code>TokenService</code> está en <code>service/</code> y su implementación en <code>security/</code>: ¿el Target no está acoplado al framework?”</dt>
<dd>Ya no. Desde O2 la firma es <code>esValido(String token, String username)</code> y <code>extraerUsername</code> devuelve <code>Optional&lt;String&gt;</code>: ningún tipo de Spring Security ni de jjwt en el Target. El Target vive del lado de quien lo usa (DIP) y la implementación, del lado de la infraestructura.</dd>
<dt>“¿Y <code>UsuarioDetails</code>?”</dt>
<dd>Es el Adapter más limpio: compone un <code>IUsuario</code> (<code>security/UsuarioDetails.java</code>) y traduce <code>getRol()</code> a <code>getAuthorities()</code>. Implementa solo los tres miembros que el dominio sabe contestar; los otros cuatro quedan con el default de <code>UserDetails</code>.</dd>
</dl>
<h4>Diagramas: Adapter 2, <code>UsuarioDetails</code> (V0 → V1)</h4>
{diagramas("adapter", tit_a="Antes (V0): Usuario implements UserDetails", tit_d="Después (V1 en adelante)")}
<h4>Diagramas: Adapter 1, tokens (V2 → V3)</h4>'''

m7 = bloque("m7", "M7. Adapter: JwtUtil detrás de TokenService (y UsuarioDetails)",
    "<strong>Adapter</strong> (GoF, estructural): convertir la interfaz de algo existente que no podemos modificar en la interfaz que espera el cliente. Acá protege a los clientes de autenticación de jjwt, una librería de terceros. jjwt es la implementación Java de JWT (JSON Web Token, un token firmado que el backend emite en el login y valida en cada request para saber quién llama).",
    "<code>AuthServiceImpl</code> y <code>JwtAuthFilter</code> dependían de la clase concreta <code>JwtUtil</code>, que exponía jjwt sin interfaz propia. El filtro además conocía la excepción de jjwt.",
    cb("v2", "service/impl/AuthServiceImpl.java", lines("v2", "service/impl/AuthServiceImpl.java", r"private final JwtUtil", 1), "", method("v2", "service/impl/AuthServiceImpl.java", r"public AuthResponse login"))
    + cb("v2", "security/JwtAuthFilter.java", lines("v2", "security/JwtAuthFilter.java", r"private final JwtUtil", 1), "// ...", lines("v2", "security/JwtAuthFilter.java", r"extraerUsername", 4, 1)),
    "Target propio <code>TokenService</code>; <code>JwtUtil</code> lo implementa y es la única clase que importa jjwt. Los clientes dependen de <code>TokenService</code>.",
    cb("main", "service/TokenService.java", body("main", "service/TokenService.java"))
    + cb("main", "security/JwtUtil.java", body("main", "security/JwtUtil.java"))
    + cb("main", "security/JwtAuthFilter.java", lines("main", "security/JwtAuthFilter.java", r"private final TokenService", 1), "// ...", lines("main", "security/JwtAuthFilter.java", r"tokenService.extraerUsername", 4), "// ...", lines("main", "security/JwtAuthFilter.java", r"tokenService.esValido", 3))
    + cb("main", "service/impl/AuthServiceImpl.java", lines("main", "service/impl/AuthServiceImpl.java", r"private final TokenService", 1)),
    "Los clientes de autenticación estaban atados a una librería externa: cambiar de proveedor de tokens o mockearlo en un test obligaba a tocar el servicio y el filtro. Con <code>TokenService</code> la dependencia apunta a una abstracción propia y jjwt queda encerrada en un solo Adapter, como el dominio ya quedaba aislado de Spring Security con <code>UsuarioDetails</code>.",
    "<ul><li>Gana: los clientes no conocen jjwt; otra implementación de tokens (u otra librería) es tocar una sola clase.</li><li>Cuesta: una interfaz más con una única implementación hoy, y mantener <code>JwtUtil</code> al día si jjwt cambia.</li><li>Un token mal formado o vencido sigue dando 401 (smoke, caso token inválido).</li></ul>",
    "Commits <code>aa76375</code> y <code>de78c07</code> (O2). Archivos: <code>service/TokenService.java</code>, <code>security/JwtUtil.java</code>, <code>security/JwtAuthFilter.java</code>, <code>service/impl/AuthServiceImpl.java</code>, <code>security/UsuarioDetails.java</code>.",
    extra=extra7)

m8 = bloque("m8", "M8. EstadoCredito y Credito como agregado de sus cuotas",
    "Information Expert y Creator (GRASP): el crédito crea sus cuotas y las conoce, así que es quien responde su estado, su saldo y si puede anularse. Absorbe M2.",
    "El estado era un boolean <code>anulado</code>: no existía “cancelado” ni saldo (H1, H2). Para anular, el servicio le contaba al crédito si tenía cobranzas, con una consulta que contaba también las anuladas (M2).",
    cb("v2", "model/Credito.java", lines("v2", "model/Credito.java", r"private boolean anulado", 1, 1), "", method("v2", "model/Credito.java", r"public void anular"))
    + cb("v2", "service/impl/CreditoServiceImpl.java", method("v2", "service/impl/CreditoServiceImpl.java", r"public void anularCredito")),
    "<code>EstadoCredito</code> (<code>VIGENTE</code>, <code>CANCELADO</code>, <code>ANULADO</code>) se deriva; no se persiste. <code>Credito</code> navega sus cuotas y calcula estado, saldo, cancelación y anulabilidad. El servicio trae cuotas y cobranzas con <code>JOIN FETCH</code> en dos consultas.",
    cb("main", "model/EstadoCredito.java", body("main", "model/EstadoCredito.java"))
    + cb("main", "model/Credito.java", lines("main", "model/Credito.java", r"private List<Cuota> cuotas", 1, 3), "",
         method("main", "model/Credito.java", r"public EstadoCredito estado"), "",
         method("main", "model/Credito.java", r"public BigDecimal saldo"), "",
         method("main", "model/Credito.java", r"public boolean estaCancelado"), "",
         method("main", "model/Credito.java", r"public boolean tieneCobranzas"), "",
         method("main", "model/Credito.java", r"public boolean puedeAnularse"), "",
         method("main", "model/Credito.java", r"public void anular"))
    + cb("main", "service/impl/CreditoServiceImpl.java", method("main", "service/impl/CreditoServiceImpl.java", r"private Credito buscarCredito")),
    "Cierra H1 (estado como boolean), H2 (el sistema no sabía cuánto debe un crédito) y M2. El servicio deja de consultar al repositorio para pasarle un boolean al crédito: la decisión vuelve al experto.",
    "Gana: estado y saldo en un solo lugar, sin columna nueva ni migración (<code>anulado</code> sigue siendo el dato persistido); <code>listarPorCliente</code> pasa de N+1 a dos consultas fijas. Cuesta: el crédito necesita sus cuotas y cobranzas cargadas dentro de una transacción. Dos colecciones en un solo <code>JOIN FETCH</code> tiran <code>MultipleBagFetchException</code>, por eso son dos consultas. La llamada a <code>cuotaRepository.buscarPorCredito</code> sin usar el resultado es a propósito: deja las cobranzas cargadas en el contexto de persistencia de JPA.",
    "Archivos: <code>model/EstadoCredito.java</code>, <code>model/Credito.java</code>, <code>service/impl/CreditoServiceImpl.java</code>, <code>repository/CreditoRepository.java</code>, <code>repository/CuotaRepository.java</code>, <code>dto/response/CreditoResponse.java</code>. Tests: <code>CreditoTest</code>.")

# ---- M9 Strategy (foco) ----
roles9 = '''<table><thead><tr><th>Rol (apunte clase 10)</th><th>Clase</th></tr></thead><tbody>
<tr><td><strong>Contexto</strong>: usa la estrategia y delega</td><td><code>model/Credito.java</code>: guarda <code>tipoPlan</code> y delega el cálculo en el constructor, al otorgar</td></tr>
<tr><td><strong>Estrategia</strong>: interfaz común</td><td><code>model/interfaces/CalculoDeCuota.java</code> (<code>importeCuota</code>)</td></tr>
<tr><td><strong>Estrategias concretas</strong></td><td><code>model/plan/InteresSimple.java</code>, <code>model/plan/SistemaFrances.java</code></td></tr>
<tr><td><strong>Selección</strong></td><td><code>model/TipoPlan.java</code> (enum persistido, asocia cada valor con su estrategia); lo elige quien otorga, vía <code>dto/request/CreditoRequest.java</code> (<code>tipoPlan</code>) y el <code>&lt;select&gt;</code> de <code>frontend/src/pages/Creditos.jsx</code></td></tr>
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
<p>Un préstamo se devuelve en cuotas. Cada cuota tiene dos partes: <strong>capital</strong> (un pedazo de lo que te prestaron) e <strong>interés</strong> (lo que cobra el que presta por haberte dado la plata). Lo que cambia entre un sistema y otro es <em>sobre qué</em> se calcula el interés.</p>
<p><strong>Interés simple (como lo modelamos).</strong> Se calcula una sola vez sobre todo lo prestado y se reparte en partes iguales. “30 %” quiere decir: devolvés lo prestado más un 30 % de eso, en total, sin importar en cuántas cuotas. El interés no baja aunque ya hayas devuelto la mitad.</p>
<p><strong>Sistema francés.</strong> Es el que usan los bancos para préstamos personales. La cuota es siempre la misma, pero el interés de cada mes se calcula sobre lo que <em>todavía debés</em> (el saldo). Al principio debés mucho, así que la cuota es casi todo interés; a medida que devolvés, el interés baja y la cuota se va en capital. “5 %” quiere decir: 5 % <em>por mes</em> sobre el saldo. La fórmula <code>cuota = C·i / (1 − (1+i)^−n)</code> es la que hace que esa cuota fija deje el saldo justo en cero en la última.</p>
<p><strong>Ejemplo: $12.000 en 6 cuotas.</strong></p>
<div class="cuadro">
<div><h4>Interés simple, tasa 30 % total</h4><p>Total = 12.000 × 1,30 = <strong>15.600</strong>. Cuota = 15.600 / 6 = <strong>2.600</strong> todos los meses: 2.000 de capital y 600 de interés. Interés total: <strong>3.600</strong>.</p></div>
<div><h4>Sistema francés, tasa 5 % mensual</h4><p>Cuota fija = <strong>{fmt(FQ)}</strong>. Mes 1: interés 5 % de 12.000 = 600. Mes 6: interés 5 % de lo poco que queda = 112,58. Total = <strong>{fmt(FQ*6)}</strong>; interés total: <strong>{fmt(int_fr)}</strong>.</p></div>
</div>
<p>Las dos tasas arrancan cobrando lo mismo el primer mes (600). La diferencia es que el simple sigue cobrando 600 sobre los 12.000 originales hasta el final, y el francés cobra sobre lo que falta. Por eso el francés sale más barato con “el mismo” 5 % por mes.</p>
<div class="mvcsvg">{_grafico()}</div>
<table><thead><tr><th>Mes</th><th>Cuota francés</th><th>Interés</th><th>Capital</th><th>Saldo después</th></tr></thead><tbody>{filas_fr}</tbody></table>
<p><strong>Por qué la tasa significa cosas distintas.</strong> Cada sistema define su tasa de la forma en que se usa en la práctica: el interés simple, como un recargo único sobre el total; el francés, como tasa por período sobre saldo, porque así se calcula mes a mes. Mismo campo <code>tasaInteres</code> en <code>model/Credito.java</code>, dos significados; por eso <code>frontend/src/pages/Creditos.jsx</code> rotula la tasa según el plan elegido (“% total” o “% mensual”).</p>
<h4>¿Está bien modelado con Strategy?</h4>
<p>Sí, en lo que pide el apunte. El <strong>Context</strong> es <code>Credito</code>: no conoce ninguna fórmula y delega en <code>tipoPlan.calculo().importeCuota(...)</code>. La <strong>Strategy</strong> es <code>CalculoDeCuota</code>, con una sola operación. Las <strong>ConcreteStrategies</strong> son <code>InteresSimple</code> y <code>SistemaFrances</code>, que no se conocen entre sí. <strong>Elige</strong> quien otorga el crédito (el <code>&lt;select&gt;</code> del front → <code>CreditoRequest.tipoPlan</code>), y <code>TipoPlan</code> traduce esa elección a la estrategia sin <code>if</code> en el Context. <strong>No hay <code>setEstrategia</code></strong> porque el plan es parte del contrato: se fija al otorgar y cambiarlo después alteraría cuotas ya emitidas.</p>
<p><strong>Lo que no es ideal.</strong> (1) El Context guarda el enum y no la estrategia, porque JPA no persiste una interfaz: la selección vive en <code>TipoPlan</code>, así que un plan nuevo obliga a tocar el enum además de agregar la clase (OCP se cumple para <code>Credito</code>, no para el enum). (2) El mismo campo <code>tasaInteres</code> cambia de significado según la estrategia; lo ideal sería que cada plan declare su unidad de tasa en vez de depender del rótulo de la vista. (3) La estrategia solo devuelve el importe de la cuota: la cuota guardada no separa capital e interés, así que la tabla de arriba no se puede reconstruir desde la base. (4) Nuestro “interés simple” es un recargo plano sobre el total, una simplificación que no es la forma en que se cobra un préstamo real.</p>
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
<h4>Cuándo usarlo (y por qué acá sí)</h4>
<p>El apunte: una misma tarea con varios algoritmos intercambiables; la señal de alarma es un <code>switch(tipoDeAlgoritmo)</code> que crece con cada caso. Advierte que aplicarlo con algoritmos que casi nunca cambian es sobre-ingeniería. Acá hay dos algoritmos reales y distintos: el interés simple (tasa única sobre el total) y el sistema francés (cuota fija con tasa mensual sobre saldo, el habitual en préstamos). Sin el patrón, el segundo entraba como un <code>if</code> dentro de <code>Credito</code>.</p>
<p><strong>Revierte una decisión anterior.</strong> El 15/09 (V2) se descartó el sistema francés y <code>Credito</code> justificaba el interés simple porque “no se modela amortización”. V3 reabre esa decisión: el francés entra como segunda estrategia real, así el patrón no queda con una sola implementación.</p>
<h4>Preguntas incómodas</h4>
<dl class="qa">
<dt>“¿Quién elige la estrategia y dónde está el <code>setEstrategia</code>?”</dt>
<dd>La elige quien otorga el crédito: <code>&lt;select&gt;</code> en <code>frontend/src/pages/Creditos.jsx</code> → <code>CreditoRequest.tipoPlan</code> → <code>TipoPlan.calculo()</code>. No hay <code>setEstrategia</code> a propósito: el plan queda fijo al otorgar, porque cambiarlo después alteraría cuotas ya emitidas. El cliente sabe qué estrategias existen porque <code>TipoPlan</code> las enumera (otro error típico del apunte que queda cubierto).</dd>
<dt>“¿Por qué el Contexto guarda un enum y no la estrategia?”</dt>
<dd>Porque <code>Credito</code> es una entidad JPA (Java Persistence API, el mapeo de objetos a tablas que hace Hibernate) y una interfaz no se persiste. El enum se guarda en la columna <code>tipo_plan</code> y es el único punto de registro de las estrategias. <code>Credito</code> no tiene <code>if</code> ni <code>switch</code>: llama <code>tipoPlan.calculo().importeCuota(...)</code>.</dd>
<dt>“¿Dos algoritmos no es sobre-ingeniería?”</dt>
<dd>No, porque los dos se usan: se otorgan créditos de ambos tipos (smoke: simple 1200 al 10 % en 3 → 440; francés → 482,54). El francés tapa un hueco: en V2 un plan con tasa mensual sobre saldo no se podía expresar.</dd>
<dt>“Si cambian la fórmula, ¿qué pasa con los créditos ya otorgados?”</dt>
<dd>Nada. La cuota se calcula y se guarda al otorgar (<code>Credito.importeCuota</code>) y el total sale de las cuotas emitidas (revisión O3). La estrategia solo corre al crear.</dd>
<dt>“¿<code>EstadoCredito</code> no es un State?”</dt>
<dd>No. Es un valor derivado de <code>anulado</code> y de las cuotas pagas, no cambia el comportamiento del crédito y hay una sola transición con regla (<code>anular()</code>). Clases por estado serían sobre-ingeniería, y el apunte advierte contra confundir Strategy con State: en Strategy las estrategias no se conocen entre sí.</dd>
</dl>'''

m9 = bloque("m9", "M9. Strategy del cálculo de cuota",
    "<strong>Strategy</strong> (GoF, comportamiento): la misma acción (calcular la cuota) con algoritmos intercambiables, encapsulados detrás de una interfaz común.",
    "El algoritmo estaba cableado en la entidad. Agregar otro sistema obligaba a meter un <code>if</code> por tipo dentro de <code>Credito</code>.",
    cb("v2", "model/Credito.java", method("v2", "model/Credito.java", r"public BigDecimal totalADevolver"), "", method("v2", "model/Credito.java", r"private BigDecimal calcularImporteCuota")),
    "<code>Credito</code> delega en la estrategia que corresponde a su <code>TipoPlan</code>, solo al otorgar. El total sale de las cuotas emitidas.",
    cb("main", "model/Credito.java", lines("main", "model/Credito.java", r"this.importeCuota = tipoPlan", 1), "", method("main", "model/Credito.java", r"public BigDecimal totalADevolver"))
    + cb("main", "model/interfaces/CalculoDeCuota.java", body("main", "model/interfaces/CalculoDeCuota.java"))
    + cb("main", "model/plan/InteresSimple.java", body("main", "model/plan/InteresSimple.java"))
    + cb("main", "model/plan/SistemaFrances.java", body("main", "model/plan/SistemaFrances.java"))
    + cb("main", "model/TipoPlan.java", body("main", "model/TipoPlan.java")),
    "El cálculo del plan es “la misma acción con distintos algoritmos”, el caso típico de Strategy. En V2 el sistema solo sabía otorgar a interés simple fijo; un plan francés no se podía expresar. Ahora <code>Credito</code> no conoce ninguna fórmula: delega.",
    "<ul><li>Gana: un sistema nuevo es una clase y un valor del enum, sin tocar <code>Credito</code>. Cada fórmula se testea aislada.</li><li>Cuesta: la tasa cambia de significado según el plan (% total en simple, % mensual en francés) y la UI lo rotula; una columna más en <code>creditos</code> (default <code>INTERES_SIMPLE</code> para los existentes).</li><li>Redondeo: 10.000 al 45 % en 6 cuotas da 6 × 2.416,67 = 14.500,02. Se muestra eso, que es lo que se cobra.</li><li>La cuota no se descompone en capital e interés: el francés define el importe, no la tabla de amortización.</li></ul>",
    "Commits <code>065eb37</code>, <code>9ea428d</code> y <code>1f9fc50</code> (O3).",
    extra=extra9)

m10 = bloque("m10", "M10. Dashboard también para ADMIN",
    "Control de acceso por rol en <code>SecurityConfig</code>. Sin patrón de diseño nuevo: corrección de una regla de acceso.",
    "<code>hasRole(\"SUPERVISOR\")</code> exacto sobre <code>/api/dashboard/**</code>: el ADMIN no veía el dashboard (H10, TPO-010). El front repetía la misma condición en <code>frontend/src/pages/Dashboard.jsx</code> y <code>frontend/src/components/Navbar.jsx</code>.",
    cb("v2", "config/SecurityConfig.java", lines("v2", "config/SecurityConfig.java", r'hasRole\("SUPERVISOR"\)', 1)),
    "Se separa el matcher del dashboard del de <code>/api/supervisor/**</code>, para que los permisos de anulación sigan siendo solo del supervisor.",
    cb("main", "config/SecurityConfig.java", lines("main", "config/SecurityConfig.java", r'"/api/admin/\*\*"', 3)),
    "El administrador tiene que poder ver las estadísticas sin cambiarse de rol. El título del dashboard muestra el rol real (<code>d35fc0e</code>).",
    "Gana: el ADMIN accede al dashboard. Cuesta: la regla de visibilidad está en el backend y en dos componentes del front; el backend es el que manda.",
    "Cierra TPO-010. Commit <code>f7ce757</code>.")

mejoras = [m1, m2, m3, m4, m5, m6, m7, m8, m9, m10]

indice = [
 ("m1", "Cobro sobre crédito anulado", "Information Expert", "TPO-004"),
 ("m2", "“Tiene cobranzas” ignora anuladas (absorbida por M8)", "Information Expert", "H5"),
 ("m3", "Dashboard con números verdaderos", "Corrección + Expert", "TPO-003"),
 ("m4", "Permisos de anulación en el backend", "MVC + Expert", "TPO-007"),
 ("m5", "Handlers HTTP 401/403/404/405", "MVC", "TPO-001, 002"),
 ("m6", "Cuota.estaVencida()", "Information Expert", "H3"),
 ("m7", "TokenService / JwtUtil + UsuarioDetails", "<strong>Adapter</strong>", "foco"),
 ("m8", "EstadoCredito + Credito agregado", "Expert + Creator", "H1, H2"),
 ("m9", "Cálculo de cuota", "<strong>Strategy</strong>", "foco"),
 ("m10", "Dashboard para ADMIN", "Control de acceso", "TPO-010"),
]
tabla_indice = "".join(f'<tr><td><a href="#{k}">{k.upper()}</a></td><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for k, a, b, c in indice)

# ---------------- revisión ----------------
rev = [
 ("O1", "444031f, 64cee96", "La vista decidía si un crédito se podía anular (<code>!cr.anulado</code>, sin mirar cobranzas) y, tras anular, solo marcaba <code>anulado = true</code> en el store: el listado seguía en VIGENTE con el saldo viejo.",
  "<code>dto/response/CreditoResponse.java</code> expone <code>puedeAnularse</code> (de <code>Credito.puedeAnularse()</code>); <code>frontend/src/pages/Creditos.jsx</code> lo usa y vuelve a pedir los créditos tras anular; <code>frontend/src/store/slices/creditosSlice.js</code> deja de recalcular.",
  "MVC: la vista representa, el modelo decide. Information Expert."),
 ("O2", "de78c07", "<code>security/JwtAuthFilter.java</code> importaba <code>io.jsonwebtoken.JwtException</code> y <code>esValido</code> recibía un <code>UserDetails</code>: el Target exponía tipos del Adaptado.",
  "<code>TokenService.extraerUsername</code> devuelve <code>Optional&lt;String&gt;</code>, <code>JwtUtil</code> atrapa las excepciones de jjwt y <code>esValido(String token, String username)</code>.",
  "Adapter bien aplicado, Protected Variations, DIP (ver M7)."),
 ("O3", "1f9fc50", "<code>Credito.totalADevolver()</code> volvía a correr la estrategia en cada lectura y no cerraba con la suma de las cuotas (14.500,00 contra 14.500,02).",
  "<code>model/Credito.java</code>: <code>totalADevolver()</code> = <code>importeCuota × cantidadCuotas</code>. <code>CalculoDeCuota</code> queda con un solo método; el total de <code>InteresSimple</code> pasa a privado.",
  "Strategy con el alcance correcto: el Contexto no depende de la estrategia para datos históricos."),
 ("O4", "87f0631", "“Créditos activos” contaba <code>anulado = false</code> con <code>CreditoRepository.contarVigentes()</code> y sumaba los cancelados.",
  "<code>service/impl/DashboardServiceImpl.java</code> cuenta <code>estado() == VIGENTE</code>; se borra <code>contarVigentes</code>.",
  "Information Expert: la vigencia se define en un solo lugar."),
 ("O5", "5b7f165", "La regla “al ADMIN no se le tocan permisos ni rol” estaba en la vista y, a medias, en <code>AdminServiceImpl.actualizarRol</code>; por <code>PUT</code> un supervisor podía quitarle permisos al admin.",
  "<code>model/Usuario.java</code>: <code>otorgarPermisos</code> y <code>asignarRol</code> rechazan con <code>BusinessException</code>; <code>service/impl/AdminServiceImpl.java</code> pierde la guarda duplicada.",
  "MVC (validación de negocio en el modelo) + Information Expert."),
 ("S1", "67ba784", "Solo <code>CreditoServiceImpl</code> tenía transacciones; <code>CobranzaServiceImpl.anularCobranza</code> leía, mutaba y guardaba sin transacción.",
  "<code>@Transactional</code> en las escrituras y <code>@Transactional(readOnly = true)</code> en las lecturas de <code>service/impl/AdminServiceImpl.java</code>, <code>AuthServiceImpl.java</code>, <code>ClienteServiceImpl.java</code> y <code>CobranzaServiceImpl.java</code>.",
  "La unidad de trabajo vive en el servicio (Spring: transacciones declarativas)."),
 ("S2", "1e87795", "Open-in-view encendido por defecto: Spring mantiene la sesión de JPA abierta hasta la vista y tapa servicios sin transacción.",
  "<code>spring.jpa.open-in-view=false</code> en <code>backend/src/main/resources/application.properties</code>.",
  "Las transacciones de S1 son la única fuente de verdad de la carga."),
 ("S3", "45a35c9", "<code>jwt.secret</code> hardcodeado en un repo público (TPO-009).",
  "<code>jwt.secret=${JWT_SECRET:...}</code> en <code>application.properties</code>: variable de entorno con default de desarrollo.",
  "Configuración fuera del código."),
 ("S4", "904fa1e", "<code>GlobalExceptionHandler.handleGeneral</code> devolvía <code>ex.getMessage()</code> (SQL, nombres de clase) y no logueaba nada.",
  "Responde “Error interno” y loguea la excepción con <code>@Slf4j</code> (Lombok) en <code>exception/GlobalExceptionHandler.java</code>.",
  "El cliente no ve detalles internos; el servidor sí los registra."),
 ("D1", "5ac2155", "<code>UsuarioRepository.findByRol</code> sin llamadores.", "Borrado de <code>repository/UsuarioRepository.java</code>.", "Código muerto."),
 ("D2", "3bd8b61", "<code>@Builder</code> y <code>@NoArgsConstructor</code> sin uso en <code>AuthResponse</code>.", "Borrados de <code>dto/response/AuthResponse.java</code>.", "Código muerto."),
 ("BS1", "5f2c334", "<code>AdminService.listarTodos</code> y <code>listarUsuarios</code> eran el mismo stream; el supervisor recibía también al admin y el front lo deshabilitaba a mano.",
  "<code>controller/SupervisorController.java</code> usa <code>listarUsuarios()</code> (sin admins); se borra <code>listarTodos</code> de <code>service/AdminService.java</code> y <code>service/impl/AdminServiceImpl.java</code>, y el caso especial de <code>frontend/src/pages/GestorPermisos.jsx</code>.",
  "Bad smell: código duplicado."),
 ("DF1", "830a998", "<code>frontend/src/store/index.js</code> armaba un segundo store que nadie importaba.", "Borrado; queda <code>frontend/src/store/store.js</code>.", "Código muerto (front)."),
 ("DF3", "5d2dbc4", "<code>frontend/src/pages/Creditos.jsx</code> hacía <code>console.log</code> del usuario con su JWT en cada render.", "Línea borrada.", "Código de depuración que filtraba el token."),
 ("BSF1", "c19e707", "Comentarios de copy-paste (<code>[cite: 4]</code>, “Asumiendo que…”) en <code>frontend/src/store/slices/permisosSlice.js</code>, <code>cobranzasSlice.js</code> y <code>frontend/src/pages/GestorPermisos.jsx</code>.", "Borrados.", "Bad smell: comentarios que no explican el código."),
]
rev_html = "".join(f'<div class="rev" id="{i.lower()}"><h4>{i} <span class="ref">· commit <code>{c}</code></span></h4><p><strong>Problema.</strong> {p}</p><p><strong>Cambio.</strong> {s}</p><p><strong>Concepto.</strong> {k}</p></div>' for i, c, p, s, k in rev)

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
<ul><li><strong>Strategy</strong>: cálculo de cuota, interés simple y sistema francés (M9)</li><li><strong>Adapter</strong>: <code>TokenService</code> sobre jjwt (M7)</li><li><code>EstadoCredito</code>, saldo, mora (M6, M8)</li><li>Permisos y errores HTTP en el backend (M4, M5), Swagger</li><li>Dashboard corregido (M3, M10); 25 tests</li><li>Revierte V2: sistema francés descartado el 15/09</li></ul></div>
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
<dt>Spring Boot</dt><dd>Framework Java que arma la aplicación web con configuración por convención. Es el backend: controladores REST, servicios y seguridad.</dd>
<dt>Spring Security</dt><dd>Módulo de Spring para autenticación y autorización. Filtra cada request, decide 401/403 y aplica las reglas por rol de <code>SecurityConfig</code>.</dd>
<dt>JWT y jjwt</dt><dd>JWT es un token firmado que el backend entrega en el login y el front manda en cada request. jjwt es la librería Java que lo genera y lo valida; es el Adaptado de M7.</dd>
<dt>JPA / Hibernate y Spring Data</dt><dd>JPA mapea las clases del modelo a tablas; Hibernate es la implementación. Spring Data genera los repositorios. Explica los <code>JOIN FETCH</code> y el <code>LazyInitializationException</code> de M8.</dd>
<dt>H2</dt><dd>Base de datos en memoria. La usamos para correr el TPO sin instalar un motor; se reinicia en cada arranque.</dd>
<dt>Lombok</dt><dd>Genera getters, constructores y loggers con anotaciones (<code>@Getter</code>, <code>@RequiredArgsConstructor</code>, <code>@Slf4j</code>). Reduce código repetido en entidades y DTO.</dd>
<dt>springdoc-openapi / Swagger UI</dt><dd>Lee los controladores y publica el contrato de la API (OpenAPI) en una página navegable. Lo usamos como documentación viva y para probar endpoints con token.</dd>
<dt>React, Redux y Vite</dt><dd>React construye la interfaz con componentes; Redux guarda el estado del cliente (usuario, créditos); Vite levanta el servidor de desarrollo y arma el build.</dd>
<dt>JUnit 5 + AssertJ</dt><dd>Framework de tests y librería de aserciones de Java. Con ellos están los 25 tests del dominio.</dd>
<dt>Maven</dt><dd>Herramienta de build de Java: baja dependencias, compila y corre los tests (<code>mvn test</code>).</dd>
<dt>PlantUML</dt><dd>Genera diagramas UML a partir de texto. Con él están hechos los diagramas antes/después y el diagrama de clases.</dd>
</dl>'''

clases_svg = re.sub(r"<\?xml[^>]*\?>", "", open(os.path.join(REPO, "docs/diagramas/clases-v3-general.svg")).read())
clases_svg = re.sub(r'(<svg[^>]*?) style="[^"]*" width="[^"]*" height="[^"]*"', r'\1 style="width:100%;height:auto"', clases_svg, count=1)

pendientes = '''<ul>
<li><strong>O6</strong>: que <code>Credito</code> genere su plan de cuotas en el constructor con <code>cascade</code> (hoy lo pide <code>CreditoServiceImpl.crear</code>). Creator completo. Tamaño M, para el 27/10.</li>
<li><strong>O7</strong>: saldo pendiente y monto vencido en el dashboard, con <code>Credito.saldo()</code> y <code>Cuota.estaVencida()</code>.</li>
<li><strong>O8</strong>: pagos parciales. Cambia <code>Cuota.estaPagada()</code> a saldo por cuota; fuera de alcance de V3.</li>
<li><strong>S5 a S10</strong>: <code>AuthenticationProvider</code> duplicado, reglas de URL repetidas con <code>@PreAuthorize</code>, consola H2 en <code>permitAll</code> (TPO-008), CORS sin configurar, <code>ddl-auto</code>/<code>show-sql</code>, rename del paquete <code>com.uade.tpejemplo</code> (TPO-014).</li>
<li><strong>Smells</strong>: BS2 (armado de <code>ErrorResponse</code> repetido), BS3, BS4, BS6; front DF2, BSF2, BSF4, BSF5, BSF6 (TPO-012).</li>
<li><strong>Tests</strong>: <code>@WebMvcTest</code> de los códigos HTTP, <code>@DataJpaTest</code> del dashboard, seguridad 401/403, <code>Clock</code> inyectable para <code>Cobranza.anular()</code> y <code>Cuota.estaVencida()</code>.</li>
<li><strong>Trazabilidad</strong>: qué usuario cobró o anuló (H8).</li>
<li>Descartados con motivo: <code>EstadoCredito</code> como State (O9) y Strategy/Adapter “para mostrar” (O10).</li>
</ul>'''

doc = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reporte V3 — TPO Grupo 7</title><style>{CSS}</style></head>
<body>
<div id="barra"><strong style="color:var(--navy)">Reporte V3</strong>
<nav><a href="#portada">Portada</a><a href="#timeline">Timeline</a><a href="#mvc">MVC</a><a href="#mejoras">Mejoras</a><a href="#m7">Adapter</a><a href="#m9">Strategy</a><a href="#revision">Revisión</a><a href="#verificacion">Verificación</a><a href="#clases">Clases</a><a href="#pendientes">Pendientes</a></nav>
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
<p>Cada iteración aplica un tema de la cursada sobre la versión anterior.</p>
{timeline}</section>

<section id="tecnologias"><h2>Tecnologías</h2>
{tecnologias}</section>

<section id="mvc"><h2>MVC en Spring Boot</h2>
<p>MVC separa <em>componentes</em>, no clases. El modelo y el controlador viven en el backend Spring Boot y la vista es la SPA React: es <strong>MVC distribuido, con la vista en el cliente</strong>. La vista no observa al modelo: le pide los datos al controlador por HTTP, y vista y controlador se hablan por DTO, como pide la slide de la clase 9.</p>
<div class="mvcsvg">{mvc_svg}</div>
<table><thead><tr><th>Clase / paquete</th><th>Componente</th><th>Justificación</th></tr></thead><tbody>{rows}</tbody></table>
<h3>Qué cambió en V3</h3>
<ul>
<li><strong>El contrato está publicado.</strong> Swagger UI (<code>/swagger-ui.html</code>, <code>config/OpenApiConfig.java</code>) documenta 19 operaciones con su request, response y los códigos que realmente produce. Mapa completo en <a href="../trabajo/api.md"><code>docs/trabajo/api.md</code></a>.</li>
<li><strong>El controlador traduce todos los errores.</strong> <code>exception/GlobalExceptionHandler.java</code> mapea las excepciones del modelo y de la seguridad a 400/401/403/404/405/500 con el mismo <code>ErrorResponse</code> (M5, S4).</li>
<li><strong>401 y 403 son distintos.</strong> Sin token, <code>config/SecurityConfig.java</code> responde 401 con <code>HttpStatusEntryPoint</code>; con token y sin rol o sin permiso, 403. Antes ambos daban 403.</li>
<li><strong>La regla está en el modelo y la vista solo oculta.</strong> Permisos de anulación (M4), guarda del ADMIN (O5) y anulabilidad (O1) dejaron de vivir solo en JSX.</li>
<li><strong>Validación en las tres capas</strong>: <code>required</code> en el JSX, <code>@Valid</code> en el controlador (sumado a <code>RolRequest</code> y <code>PermisosRequest</code>) y reglas en las entidades.</li>
</ul>
</section>

<section id="mejoras"><h2>Mejoras al dominio</h2>
<p>Cada mejora tapa un hueco real del dashboard de préstamos. Estructura: Patrón → Problema (código antes, <code>git show v2:&lt;ruta&gt;</code>) → Solución (código después, <code>main</code>) → Por qué → Consecuencias, con diagrama antes/después. M7 (Adapter) y M9 (Strategy) son el foco de la consigna y llevan además roles, GRASP/SOLID de fondo, cuándo usarlo y preguntas de defensa.</p>
<table><thead><tr><th>ID</th><th>Mejora</th><th>Patrón / concepto</th><th>Hueco</th></tr></thead><tbody>{tabla_indice}</tbody></table>
{"".join(mejoras)}
</section>

<section id="revision"><h2>Mejoras de la revisión</h2>
<p>Después de las diez mejoras, una revisión de solo lectura (<a href="../trabajo/oportunidades.md">oportunidades</a>, <a href="../trabajo/spring-practicas.md">prácticas de Spring</a>, <a href="../trabajo/smells.md">bad smells</a>) encontró usos flojos de los conceptos y código muerto. Entraron las que tapaban un hueco visible y eran chicas.</p>
{rev_html}
</section>

<section id="verificacion"><h2>Verificación</h2>
<div class="cuadro">
<div><h4>Tests automáticos</h4><p><code>cd backend &amp;&amp; mvn test</code>: <strong>25 tests, 0 fallas</strong>. Son 24 de dominio puro (JUnit 5 + AssertJ, sin contexto de Spring) más <code>contextLoads</code>. <code>InteresSimpleTest</code> y <code>SistemaFrancesTest</code> cubren cada estrategia aislada; <code>CreditoTest</code>, <code>CuotaTest</code> y <code>CobranzaTest</code> cubren M1, M2, M6 y M8. Detalle: <a href="../trabajo/tests.md"><code>docs/trabajo/tests.md</code></a>.</p></div>
<div><h4>Smoke de la API</h4><p>22 casos con curl contra el backend levantado: 401/404/405 (M5), los dos planes (M9), cobro sobre anulado (M1), 403 sin permiso (M4), vencidas (M6), dashboard por rol y con números correctos (M3, M10). Todos OK. Detalle: <a href="../trabajo/smoke.md"><code>docs/trabajo/smoke.md</code></a>.</p></div>
<div><h4>Comprobación visual</h4><p>Recorrido completo en el browser con capturas: login, alta, otorgamiento simple y francés, cobro, vencida, anulación, 403 forzado, dashboard ADMIN y SUPERVISOR, Swagger con token. Las dos fallas encontradas (listado sin refrescar tras anular y título “Modo Supervisor” para el ADMIN) se corrigieron en O1 y <code>d35fc0e</code>. Detalle: <a href="../trabajo/visual.md"><code>docs/trabajo/visual.md</code></a>, capturas en <a href="../trabajo/capturas/"><code>docs/trabajo/capturas/</code></a>.</p></div>
<div><h4>Auditoría</h4><p>Contraste de M1-M10 con el código y con el apunte de la clase 10, antes de la revisión: <a href="../trabajo/auditoria.md"><code>docs/trabajo/auditoria.md</code></a>.</p></div>
</div>
</section>

<section id="clases"><h2>Diagrama de clases V3</h2>
<p>Vista general con los tres compartimentos por clase. Fuente: <code>docs/diagramas/clases-v3.puml</code>; también en <code>docs/diagramas/clases-v3-general.svg</code> y <code>.png</code>. Para leer el detalle, abrir el SVG aparte.</p>
<div class="clases">{clases_svg}</div>
</section>

<section id="pendientes"><h2>Cambios pendientes</h2>
{pendientes}
<p>Lista completa de hechos y pendientes para Teams: <code>docs/entrega/lista-mejoras.md</code>.</p>
</section>
</main>
</body></html>'''
open(OUT + "/reporte-v3.html", "w").write(doc)
print(len(doc))
