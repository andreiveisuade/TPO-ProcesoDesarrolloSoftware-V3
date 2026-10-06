# Auditoría final de V3 (T51) — 06/10/2026

Revisión de solo lectura de `main@4e27ed0`, antes del push y de la defensa del 13/10. Rutas Java relativas a `backend/src/main/java/com/uade/tpejemplo/`, rutas de front relativas a `frontend/src/`. Se mide contra `CLASE_09_Patrones_mvc_strategy_adapter.pdf`, `CLASE_10_ADOO_Repaso_GRASP_SOLID_Adapter_Strategy.pdf` y la convención de comentarios (sin javadoc, 1-3 líneas por clase, 1 línea por patrón, y solo los porqués no obvios).

## Veredicto

**NO, todavía.** Hay **un bloqueante de 10 minutos**: el diagrama de clases que se entrega dibuja el Adapter viejo (B1).

**Con B1 corregido, SÍ para push y defensa.** Compila, pasan los 37 tests y el build y el lint salen limpios. El recorrido de API (304 casos, 4 roles) da los códigos esperados salvo los casos de I1-I3, y el dashboard cuadra con lo cargado. Strategy, Adapter, MVC y GRASP/SOLID cumplen contra las slides.

Antes del 13/10 conviene cerrar los IMPORTANTES:
- **XS**: I2 (una línea de config), I3, I4 e I6.
- **S**: I1. Si no entra, va al reporte como pendiente reproducido.
- **Ajustes del reporte**: I5.

## Hallazgos

### BLOQUEANTE

**B1. El diagrama de clases entregable contradice el código en el Adapter, el foco de la iteración.**
- **Qué pasa**: dibuja `JwtUtil` con `- secret : String` y una dependencia punteada a `io.jsonwebtoken.Jwts` (estático). Desde `2ef8410` el código tiene `SecretKey key` y `JwtParser parser` como `final`, es decir, Object Adapter por composición. El reporte y la lista de mejoras lo dicen; el UML que va a Teams no.
- **Dónde**: `docs/diagramas/clases-v3.puml:102-109`, `:167`, y su render `clases-v3-general.svg`/`.png`.
- **Arreglo (XS)**:
  - Atributos: `- key : SecretKey`, `- parser : JwtParser`, `- expirationMs : long`.
  - Adaptee `JwtParser (jjwt)` y `JwtUtil *-- JwtParser`, en lugar de `JwtUtil ..> Jwts : delega`.
  - En `Credito` (`:240-257`), sumar `- calculo() : CalculoDeCuota`.
  - Re-renderizar SVG y PNG.

### IMPORTANTE

**I1. Carrera entre anular un crédito y cobrar una de sus cuotas: queda un crédito ANULADO con una cobranza vigente.**
- **Reproducción**: 12 de 12 intentos con requests paralelos, y 6 de 6 con curl. Los dos requests responden éxito (204 y 201).
- **Efecto**: el `montoTotalCobrado` del dashboard suma cobranzas de créditos anulados (en la prueba, +12.000).
- **Por qué pasa**: `anularCredito` lee el crédito sin lock, y `registrar` bloquea solo la fila de la cuota (TOCTOU).
- **Dónde**: `service/impl/CreditoServiceImpl.java:78-87`, `:94-99`; `service/impl/CobranzaServiceImpl.java:31`; `model/Cuota.java:78`.
- **Contexto**: el backlog lo tiene como M-3 "no reproducida"; ya está reproducida.
- **Arreglo (S)**:
  - `@Lock(PESSIMISTIC_WRITE)` sobre el crédito en los dos caminos, con el mismo orden de bloqueo: crédito, después cuota.
  - Un test hermano de `CobranzaConcurrenteTest`.
  - Si no entra para el 13/10, actualizar M-3 en `docs/backlog.md` y nombrarlo en "Cambios pendientes" del reporte.
- **Repro**: crédito de 1 cuota; en paralelo, `DELETE /api/creditos/anular/{id}` con supervisor y `POST /api/cobranzas {"idCredito":id,"numeroCuota":1,"importe":1000}`. Resultado: `estado=ANULADO` con una cobranza `anulada=false`.

**I2. El perfil prod promete más de lo que da, y S3 está a medias.**
- **Secret por defecto**: `jwt.secret=${JWT_SECRET:clave-super-secreta-…}` deja el secret del repo público como default. Con prod levantado sin `JWT_SECRET`, un token HS256 forjado con ese secret entra como admin (`GET /api/admin/usuarios` da 200).
- **Usuarios semilla**: `DataInitializer` no tiene `@Profile`, así que prod también crea `admin/admin`, `supervisor/supervisor` y `user/user`.
- **Base**: prod sigue en H2 en memoria, con lo que `ddl-auto=update` y "esquema sin borrar" no significan nada.
- **Swagger**: `/v3/api-docs` y `/swagger-ui/index.html` quedan abiertos.
- **Lo que dice el reporte**: S3 ("jwt.secret en un repo público → `${JWT_SECRET}`") y Perfiles ("lo cómodo para la demo no llega a prod").
- **Dónde**: `backend/src/main/resources/application.properties:20`, `:7`; `application-prod.properties:1-2`; `config/DataInitializer.java:15-28`; `config/SecurityConfig.java:57`; `docs/reporte/reporte-v3.html:1909` (Perfiles) y `:1915` (S3).
- **Arreglo (XS)**:
  - En `application-prod.properties`, `jwt.secret=${JWT_SECRET}` sin default: obligatoria, falla al arrancar igual que `CORS_ORIGIN`.
  - Sacar "esquema sin borrar" de `:1`.
  - En el reporte, prod pasa a ser "perfil de despliegue de la demo: base en memoria y usuarios semilla; pendiente base real y alta de admin".
  - Swagger abierto en prod: decidirlo y escribirlo.

**I3. Un error del cliente responde 500.**
- **Qué pasa**: un `POST`/`PUT` con `Content-Type: text/plain`, `xml` o sin header cae en `handleGeneral` y responde **500 con stack trace en el log** (9 ERROR en el recorrido). Un `Accept` no JSON responde 401 sin cuerpo.
- **Qué contradice**: M5 y F2 ("error del cliente ≠ falla del servidor"). Postman con body *raw* manda `text/plain` por defecto, así que si el profe prueba la API a mano lo ve.
- **Dónde**: `exception/GlobalExceptionHandler.java:69-73`, que no tiene handler para `HttpMediaTypeNotSupportedException` ni para `HttpMediaTypeNotAcceptableException`.
- **Arreglo (XS)**: sumar los dos handlers, con 415 y 406, y un caso en `controller/CodigosHttpTest.java`.
- **Repro**: `curl -X POST :8080/api/clientes -H "Authorization: Bearer $T" -H 'Content-Type: text/plain' -d '{"dni":"1","nombre":"x"}'` da 500.

**I4. Bug visible en la demo: un alta aparece en la lista de otro cliente.**
- **Qué pasa**: si buscás los créditos del DNI A y creás uno para el DNI B, el de B aparece en la lista de A. Con cobranzas igual: buscás el crédito X, cobrás una cuota del crédito Y, y la cobranza de Y aparece bajo X.
- **Por qué pasa**: el `fulfilled` hace `push` a la lista buscada sin mirar a quién pertenece. Viene de V2.
- **Dónde**: `store/slices/creditosSlice.js:46`, `store/slices/cobranzasSlice.js:46`. La recarga correcta ya está en `pages/Creditos.jsx:62` y `pages/Cobranzas.jsx:40`.
- **Arreglo (2 líneas)**: en los dos `fulfilled`, solo `state.loading = false`.

**I5. El reporte dice cosas que el código no hace y filtra proceso interno.**
- **M3**: "la vigencia se define una vez, en el modelo" (`reporte-v3.html:1284`) es falso.
  - Activos sale de `Credito.estado() == VIGENTE`, en el modelo.
  - Financiado sale de JPQL `anulado = false`, que **incluye CANCELADOS** aunque la query se llame `sumarDeudaOriginalVigente` (`repository/CreditoRepository.java:33-34`).
  - El manual cita un `contarVigentes` inexistente y una regla vieja (`docs/manual/index.html:532`).
  - Arreglo: "Activos = `estado()` VIGENTE (modelo); financiado y cobrado = lo no anulado (query)", y corregir R18.
- **Matriz SOLID** (`:1899-1903`; `docs/entrega/lista-mejoras.md`, tabla de convenciones):
  - ISP figura "Parcial" porque `IRol` no tiene consumidor, pero una interfaz sin clientes no viola ISP.
  - DIP figura "Parcial" mientras el texto dice "Es DIP bien aplicado".
  - Arreglo: los dos en "Cumple"; `IRol` queda solo en Convenciones; borrar `:1900-1903`.
- **S3 y Perfiles**: según I2.
- **Ids internos**: títulos `T34`, `T35`, `T36`, `T40` y `T42`, y un párrafo sobre el proceso (`:1914-1915`). Arreglo: títulos por concepto y los cortes de §4.

**I6. Comentarios: faltan los marcadores del foco y dos comentarios engañan.**
- **Sin marcador de patrón**: la interfaz Strategy, las dos estrategias concretas y el Target del Adapter no tienen su `// Strategy:` o `// Adapter:`. Archivos: `model/interfaces/CalculoDeCuota.java:5`, `model/plan/InteresSimple.java:8`, `model/plan/SistemaFrances.java:9`, `service/TokenService.java:5`.
- **DTO que contradice al francés**: `dto/request/CreditoRequest.java:32` dice "porcentaje único sobre el capital", cuando en el francés la tasa es mensual.
- **Precargas sin explicar**: tres llamadas descartan su resultado sin decir por qué (`service/impl/CreditoServiceImpl.java:57`, `:70`; `service/impl/DashboardServiceImpl.java:42`); en frío parecen código muerto. La única comentada (`CreditoServiceImpl.java:97`) exagera: dentro de `@Transactional` la carga lazy funciona igual, así que es optimización (evita N+1) y no requisito.
- **Arreglo (XS, una línea cada uno)**:
  - `// Strategy: interfaz común del cálculo de cuota`, `// Strategy: estrategia concreta`, `// Adapter: Target que usan AuthServiceImpl y JwtAuthFilter`.
  - En el DTO: `// Interés simple: % total; sistema francés: % mensual.`
  - En las precargas: `// Precarga cobranzas en la sesión: 2 consultas en vez de N+1`. El cambio de fondo ya está en el backlog (I2).

### MENOR

Backend:
- **M1. WARN en cada arranque, dev y prod.**
  - `spring.jpa.database-platform` (`application.properties:13`) dispara HHH90000025. Arreglo: borrar la línea.
  - `web.ignoring()` de `/h2-console` (`config/SecurityConfig.java:42-45`) dispara "This is not recommended". Arreglo: en dev, `permitAll` + `frameOptions().sameOrigin()`, o aceptar el WARN.
- **M2. Anular la misma cobranza 10 veces en paralelo da 8×204 y 2×400.** Debería ser una sola 204. El estado final es correcto, pero no hay lock (`service/impl/CobranzaServiceImpl.java:55`). Arreglo: el mismo lock que I1.
- **M3. Errores heterogéneos.**
  - Los 401/403 de la cadena de seguridad salen sin cuerpo (`config/SecurityConfig.java:63-65`); los del handler salen como JSON.
  - Hay mensajes de Spring en inglés ("Bad credentials", "Access Denied", "No static resource…") en `exception/GlobalExceptionHandler.java:51,56,61,66`.
  - Los conflictos (duplicado, doble cobro) dan 400, nunca 409.
  - Defendible; si se toca: mensajes fijos en español y `ErrorResponse` también en la cadena.
- **M4. `PermisosRequest` con `boolean` primitivos.** Un `{}` resetea los dos permisos a false con 200, y el `@Valid` de `AdminController.java:45` y `SupervisorController.java:44` no valida nada. Arreglo: `Boolean` + `@NotNull` en `dto/request/PermisosRequest.java:11-12`.
- **M5. Validación del crédito.**
  - `cantidadCuotas: 2.7` se trunca a 2 cuotas (coerción de Jackson).
  - No hay tope de cuotas: 10.000 cuotas son 1,1 MB de respuesta.
  - Una deuda de 0,01 en 3 cuotas genera cuotas de 0,00 que no se pueden cobrar nunca (`dto/request/CreditoRequest.java:24-41`).
  - Arreglo: `@Max` de cuotas y rechazar cuota 0 en `Credito`.
- **M6. `GET /api/cobranzas/credito/{id}` con id inexistente da 200 `[]`.** Ya está en el backlog (A-3).
- **M7. Usernames case-sensitive**: `Admin` y `admin` conviven (`service/impl/AuthServiceImpl.java:34`).
- **M8. El supervisor edita sus propios permisos y los de otros supervisores.** `service/impl/AdminServiceImpl.java:28-33` filtra solo al ADMIN y `model/Usuario.java:55-60` bloquea solo al ADMIN. Además, `pages/GestorPermisos.jsx:36` dice "rol USER". Defenderlo como diseño o filtrar al propio usuario.
- **M9. Detalles de `TokenService`/`JwtUtil`.**
  - `esValido` es tautológico en su único uso: el filtro carga el usuario cuyo nombre sacó del mismo token y vuelve a parsearlo para comparar, lo que da siempre true con doble parseo (`security/JwtAuthFilter.java:62-76`, `security/JwtUtil.java:53-55`).
  - `extraerClaim` es genérico para un solo uso (`JwtUtil.java:57-62`).
  - `secret.getBytes()` va sin charset (`:28`).
- **M10. La escala de `BigDecimal` difiere entre POST (`12000`) y GET (`12000.00`).** El front formatea igual.
- **M11. Estilo.**
  - `service/impl/DashboardServiceImpl.java:27-35` arma el constructor a mano (el resto usa `@RequiredArgsConstructor`) y tiene espacios finales en `:27-28`.
  - `AdminController` y `SupervisorController` devuelven tipos crudos; el resto, `ResponseEntity`.
  - Imports desordenados: `config/SecurityConfig.java:5,28`, `controller/AdminController.java:3-4`, `controller/SupervisorController.java:3-4`.
  - `dto/request/RolRequest.java` tiene un espacio al principio de `:1` y uno al final de `:11`; `model/Usuario.java:8-9` no tiene línea en blanco antes del comentario de clase.
  - `config/OpenApiConfig.java:15` pone el comentario entre anotaciones.
  - Hay `save()` redundantes sobre entidades gestionadas (`AdminServiceImpl.java:45,56`; `CobranzaServiceImpl.java:59`; `CreditoServiceImpl.java:86`).
- **M12. Comentarios fuera de la convención.**
  - `service/impl/AdminServiceImpl.java:19` dice "alta" y no hay alta.
  - `repository/ClienteRepository.java:7-9` narra un borrado.
  - `model/Usuario.java:40-42` compara con un builder que ya no existe.
  - Duplican la línea de patrón que tienen debajo: `model/Cuota.java:59-60`, `:74-75`; `model/Cobranza.java:55-57`.
  - `model/interfaces/IRol.java:5` repite `model/Rol.java:11-12`.
  - `model/Credito.java:118` lleva tildes y el resto de los comentarios no.
  - 36 clases sin comentario de clase: DTOs, `model/interfaces/*`, repositorios, interfaces de servicio y `TpEjemploApplication`.
- **M13. Falta un test de `Credito` con `SISTEMA_FRANCES`.** `CreditoTest.java:16` usa solo `INTERES_SIMPLE`, así que no está probado que el Contexto delegue en la segunda estrategia.

Front:
- **M14. Guardas de ruta.**
  - `/estadisticas` no usa `RoleRoute` y la página vuelve a chequear el rol (`App.jsx:26`; `pages/Dashboard.jsx:14,22`), contra lo que dice T42.
  - `RoleRoute` redirige a `/creditos` (`components/RoleRoute.jsx:14`) y el catch-all a `/clientes` (`App.jsx:29`).
  - `RoleRoute` no refresca el usuario, así que un cambio de rol se ve recién en otra pantalla.
- **M15. Manejo de errores.**
  - `alert()` en `pages/Creditos.jsx:73` y `pages/Cobranzas.jsx:49`, contra `Aviso` en el resto; `pages/Clientes.jsx:51` usa un div propio.
  - `togglePermiso` y `cambiarRol` no tienen `.rejected`, y el error queda silencioso (`store/slices/permisosSlice.js:59-73`).
  - `refrescarUsuario.rejected` no cierra la sesión cuando el token venció (`store/slices/authSlice.js:59-62`).
  - Los 401/403 sin cuerpo llegan como `statusText` en inglés (`api/apiClient.js:11`).
- **M16. Slop defensivo.** `lista || []` y `cr.cuotas || []` sobre arrays que siempre existen (`pages/Creditos.jsx:89,97,125`; `pages/Cobranzas.jsx:54`). El ternario anidado de `estadoCuota` sigue en `pages/Creditos.jsx:13`, aunque `0e3284e` dice haberlo sacado.
- **M17. Estilo.**
  - `import React` sin uso en `components/RoleRoute.jsx:1`, `pages/Dashboard.jsx:2`, `pages/GestorPermisos.jsx:1` y `pages/PanelAdmin.jsx:1`. El lint lo deja pasar por `varsIgnorePattern: '^[A-Z_]'`.
  - Mezcla de `const X = () =>` y `export default function`.
  - Indentación en `store/slices/creditosSlice.js:50`; espacios finales en `cobranzasSlice.js:44,57-58`, `Navbar.jsx:10,29,55-56` y `Dashboard.jsx:4,29`.
  - Sufijo `Api` solo en `anularCreditoApi`/`anularCobranzaApi`.
- **M18. Restos del template de Vite.** `frontend/index.html:2,5,7` tiene `lang="en"`, el favicon de Vite y `<title>frontend</title>`, que se ve en la pestaña durante la demo. Arreglo: `lang="es"` y el título "Créditos UADE".

Docs:
- **M19. Datos viejos en el reporte.** Dice "136 commits" (`:114`) y hoy son 137 sin merges; el log de `:117` arranca en `ec1e7d9`; "22 casos" (`:1921`) es el smoke viejo de T7, cuando el último fue API 12/12 y visual 9/9 (T45).
- **M20. Ticket desactualizado.** `tickets/TPO-008.md` (fuera del repo V3) sigue "abierto" aunque está resuelto por `e744600`.

## 1. Errores

- **Build**: `mvn -q clean test` corrió sobre una copia de `git archive main` en el scratchpad, porque la app de Andrei corre desde `backend/target/classes` y no se tocó.
  - Tests: 37, con 0 fallas y 0 errores (8 HTTP, 27 de dominio, 1 de concurrencia y `contextLoads`).
  - `npm ci && npm run build`: OK, 81 módulos y 292 kB de JS.
  - `npm run lint`: 0 problemas.
- **Arranque dev en 8099**: OK, con los dos WARN de M1.
- **Arranque prod**:
  - Sin `CORS_ORIGIN` falla rápido (exit 1, `PlaceholderResolutionException`). Es lo correcto, aunque la causa aparece al final de una traza larga.
  - Con `CORS_ORIGIN` arranca en 4,1 s, sin SQL en el log y con `/h2-console` en 404.
  - Preflight CORS: 200 para `localhost:5173`, 403 para otros orígenes.
  - Resto de prod: ver I2.
- **Recorrido de API**: 304 casos HTTP y 63 chequeos de datos sobre los 20 endpoints de Swagger. Roles: sin token, `user`, `supervisor`, `admin` y un usuario registrado.
  - Todo responde lo esperado (401/403/404/405/400, 201/204, reglas de negocio), salvo I1, I2, I3 y M2 a M10.
  - El dashboard coincide con lo recalculado desde la API: 7 clientes, 9 créditos vigentes, financiado 28.900,01, cobrado 9.628,25, saldo 54.558,03, vencido 12.410,75.
  - Saldo, estado y total son coherentes en los 26 créditos.
  - El lock de cuota funciona: 20 cobros paralelos dejan 1 cobranza vigente.
- **Logs**: no hay stack traces de negocio ni de JPA. Los 9 ERROR vienen del 500 por `Content-Type` (I3).

## 2. Código (`git diff v2..main -- backend/src frontend/src`, 100 archivos, +2081 / −998)

Lo que está bien resuelto:
- **Dependencias**: el modelo no importa nada de `service`, `dto`, `controller`, `repository`, `security` ni de Spring (verificado con `grep` de imports). Ningún controller importa repositorios.
- **DTOs**: se arman desde las interfaces `I*`.
- **Transacciones**: todas las escrituras tienen `@Transactional` y las lecturas `readOnly`; `open-in-view=false`.
- **Bloqueo pesimista**: va sin `JOIN FETCH`, con su porqué comentado (`repository/CuotaRepository.java:32-39`).
- **Javadoc**: no hay.

Hallazgos del diff: I4, I6, M2 a M18.

## 3. Conceptos (checklist de `/revision-catedra`)

### Strategy (M9): CUMPLE

| Rol (CLASE_09; CLASE_10 slides 35-36) | V3 | Veredicto |
|---|---|---|
| Strategy: interfaz con la firma | `model/interfaces/CalculoDeCuota.java:7` `importeCuota` | CUMPLE (le falta la línea `// Strategy:`, I6) |
| Estrategias concretas, que no se conocen entre sí | `model/plan/InteresSimple.java`, `model/plan/SistemaFrances.java` | CUMPLE |
| Contexto "tiene referencia a la Strategy y delega" | `model/Credito.java:80`, `:118-121` (`calculo()` → `tipoPlan.calculo()`) | CUMPLE. La referencia pasa por el enum, que es persistible |
| Quién elige | el que otorga: `pages/Creditos.jsx:179-182` → `dto/request/CreditoRequest.java:44` → `model/TipoPlan.java:10-11` | CUMPLE ("el cliente conoce las estrategias", slide 38) |
| Más de una implementación real | dos fórmulas en uso, con tests (`InteresSimpleTest`, `SistemaFrancesTest`) | CUMPLE. Riesgo en la defensa: la slide 38 avisa que "con dos algoritmos que casi nunca cambian" puede ser sobre-ingeniería. Respuesta en la pregunta 2 |

Matiz defendible:
- La delegación ocurre una sola vez, al otorgar, y `importeCuota` se persiste (`model/Credito.java:48-53`).
- No hay `setEstrategia` a propósito: cambiar el plan alteraría cuotas ya emitidas.
- Falta el test del Contexto con el francés (M13).

### Adapter (M7): CUMPLE

| Rol (CLASE_10 slides 26-28) | `JwtUtil` | `UsuarioDetails` |
|---|---|---|
| Target | `service/TokenService.java` | `UserDetails` (Spring) |
| Cliente que solo conoce el Target | `security/JwtAuthFilter.java:28`, `service/impl/AuthServiceImpl.java:29` | `DaoAuthenticationProvider` |
| Adapter que contiene al Adaptado (Object Adapter) | `security/JwtUtil.java:22-23` (`final SecretKey`, `final JwtParser`) | `security/UsuarioDetails.java:20` (`final IUsuario`) |
| Adaptado que no se toca | jjwt | `IUsuario` es propio; lo que no se toca es `UserDetails` (CLASE_09: "externas al dominio, **o no**") |

Código y reporte coinciden. El único desfasado es el UML entregable (B1). Los detalles de `TokenService` van en M9.

### GRASP y SOLID

| Principio | Evidencia | Veredicto |
|---|---|---|
| Information Expert | `model/Credito.java:111-156` (estado, saldo, anular), `model/Cuota.java:62-72` (pagada, vencida), `model/Cobranza.java:64-72`, `model/Usuario.java:47-72` | CUMPLE |
| Creator | `model/Credito.java:100-104` crea las cuotas; `model/Cuota.java:77-96` crea la cobranza; constructores package-private (`Cuota.java:52`, `Cobranza.java:51`) | CUMPLE |
| Controller | `controller/*Controller` de caso de uso, entre 32 y 76 líneas, sin reglas | CUMPLE |
| Bajo acoplamiento / Alta cohesión | controllers → interfaces de servicio; DTO → `I*`; `DashboardServiceImpl` con 4 repos (agregación) | CUMPLE |
| Polymorphism / Protected Variations | `CalculoDeCuota` (sin `if` por plan), `TokenService` | CUMPLE |
| Pure Fabrication / Indirection | repositorios, servicios, `JwtUtil`, `UsuarioDetails` | CUMPLE |
| SRP, OCP, LSP | una fórmula por clase; un plan nuevo = clase + constante en el enum registro | CUMPLE |
| ISP | `TokenService` (3 métodos usados), `CalculoDeCuota` (1) | CUMPLE. El reporte dice "Parcial" por un motivo equivocado (I5) |
| DIP | `Credito` → `CalculoDeCuota`; clientes → `TokenService`; servicios inyectados por interfaz | CUMPLE. El reporte dice "Parcial" y se contradice (I5) |

### MVC (CLASE_09)

- **Vista ↔ controlador por DTO**: CUMPLE (`dto/request`, `dto/response`).
- **Validación en los tres lugares de la slide**: CUMPLE.
  - La vista valida requeridos y tipos (`required`, `type="number"`, `min` en `pages/*.jsx`).
  - El controlador valida consistencia (`@Valid` + Bean Validation en `dto/request/*`, salvo M4).
  - El modelo valida las reglas (`Cuota.registrarCobranza`, `Credito.anular`, `Cobranza.anular`, `Usuario.asignarRol`).
- **Dependencias en una sola dirección**: CUMPLE (grep de imports, §2).
- **La vista no decide**: CUMPLE, porque `puedeAnularse` viene del modelo (`dto/response/CreditoResponse.java:34`). Desvío menor en M14.

### Convenciones

- **Nombres y paquetes**: `I<Clase>` en `model/interfaces/` y `XService` + `service/impl/XServiceImpl` CUMPLE. Las excepciones están declaradas en el reporte y son defendibles: `EstadoCredito`, `TipoPlan`, `CalculoDeCuota`, `TokenService` → `JwtUtil`, `IRol`.
- **Comentarios**: no hay javadoc. Faltan los marcadores del foco (I6) y hay restos fuera de la convención (M12).

## 4. Reporte para la defensa (`docs/reporte/reporte-v3.html`)

**Tamaño**: 4.362 palabras de prosa, sin contar código ni diagramas. Ningún párrafo pasa de 40 palabras. El problema no es el largo de cada párrafo sino **la repetición entre secciones** y los **ids internos**.

**Coincide con el código**:
- Los antes/después de M1-M10.
- M7 (composición) y M9 (`calculo()`).
- El ejemplo del francés: cuota de 2.364,21 y tabla de amortización, recalculadas a mano.
- Los 37 tests (27 + 8 + 1 + 1).

**No coincide**: M3 (`:1284`) y la matriz ISP/DIP (`:1899-1903`), ver I5; Perfiles y S3 (`:1909`, `:1915`), ver I2; T42 contra `pages/Dashboard.jsx`, ver M14; los números viejos de M19.

**Párrafos que sobran o se dicen en la mitad** (líneas del HTML):

| Línea | Qué | Acción |
|---|---|---|
| `:641` | "Credito no conoce ninguna fórmula" | Repite PV (`:686`) y DIP (`:690`). Cortar la segunda frase |
| `:642` | "Gana: OCP, un sistema nuevo no toca Credito" | OCP aparece 4 veces (`:642`, `:663`, `:674`, `:689`). Dejar `:689` y `:674`; en `:642`, solo "cada fórmula se testea aislada" |
| `:658` | "Mismo campo tasaInteres, dos unidades…" | Repite el "Cuesta" de `:642`. Fusionar en una línea |
| `:655` | "Mes 1 cobran lo mismo…" | La tabla ya lo muestra. Cortar |
| `:662`, `:663` | sobre-ingeniería; OCP del alemán | `:662` duplica la pregunta de `:697` y `:663` duplica `:689`. Cortar los dos |
| `:670` | "Enum y no campo… Credito no tiene if por tipo" | "Sin if" aparece 4 veces (`:571`, `:670`, `:685`, `:694`). Dejar solo `:685` (Polymorphism) |
| `:693-694` | "Cuándo usarlo (apunte)" | Repite el Problema de `:571`. Cortar o dejar en una línea |
| `:698` | "¿Dos algoritmos no es sobre-ingeniería? No: los dos se usan" | Respuesta floja. Reemplazar por la de la pregunta 2 de §5 |
| `:773` y `:891` | "ejemplo de manual" dos veces | Dejar `:773` |
| `:880`, `:902`, `:911` | DIP tres veces en M7 | Dejar `:880` (Por qué) y `:911` (pregunta) |
| `:894-895` | "Cuándo usarlo" en M7 | Repite la definición de `:798`. Cortar |
| `:1909` (Perfiles) y `:1915` (S3) | `JWT_SECRET` en dos secciones | Dejarlo en S3, ya corregido según I2 |
| `:1914` | "Revisión de solo lectura después de M1-M10…" (30 palabras) | "Correcciones chicas que tapaban un hueco visible." |
| `:1915` | títulos T34, T35, T36, T40, T42 | "DER"; "Spring arma el provider; error único"; "Creator: el crédito nace con cuotas; saldo y mora"; "Concurrencia, Tell don't ask, Primitive obsession"; "Front: RoleRoute y ROLES" |
| `:1921` | "22 casos" | Actualizar a la verificación final (T45) |

**Conceptos bien justificados**: M1, M2, M4, M6 y M8 (Expert/Creator); M5 (MVC: error del cliente ≠ falla del servidor, aunque I3 lo contradice hasta que se arregle); M9 (Strategy, con roles, GRASP y SOLID correctos); M7 (Object Adapter según la slide 27).

Dos para ajustar:
- **M10** pone "Control de acceso por rol" como concepto. Es la corrección de un ticket; alcanza con decir eso.
- **"Dark theme → Protected Variations"** (`:1909`) es una extensión libre del concepto. Defenderlo como "la paleta varía en un solo lugar".

## 5. Las 10 preguntas más probables del profe

| # | Pregunta | Respuesta en una línea | Dónde mostrarla |
|---|---|---|---|
| 1 | ¿Dónde está el Strategy? ¿Quién es cada rol y quién elige? | Strategy `CalculoDeCuota`; concretas `InteresSimple` y `SistemaFrances`; contexto `Credito`, vía `calculo()`. Elige quien otorga, con el `<select>` → `TipoPlan` | `model/Credito.java:80,118-121`; `model/TipoPlan.java:10-11`; `pages/Creditos.jsx:179-182`; reporte M9 "Roles" |
| 2 | Con dos algoritmos, ¿no es sobre-ingeniería (slide 38)? | No: son dos fórmulas reales con distinta semántica financiera, y la alternativa era un `if` por tipo dentro de `Credito` (código V2). Un plan nuevo (alemán, americano) es una clase más, sin tocar `Credito` | antes/después de M9; `model/plan/` |
| 3 | ¿Por qué no hay `setEstrategia`? ¿Dónde se elige en ejecución? | Se elige en ejecución, al otorgar. Cambiarla después alteraría cuotas ya emitidas, por eso `importeCuota` se persiste | `model/Credito.java:48-53,80` |
| 4 | ¿Un enum no es un switch encubierto? | No: el enum es el registro de estrategias que JPA puede persistir, y `Credito` no pregunta el tipo. OCP se cumple para el contexto y las estrategias; el enum solo suma una constante | `model/TipoPlan.java`; `model/Credito.java:119-121` |
| 5 | En el Adapter, ¿quién es Target, Adapter y Adaptado? ¿Por qué es Adapter si `JwtUtil` es de ustedes? | Target `TokenService`, Adapter `JwtUtil`, Adaptado jjwt (no se puede tocar), clientes `JwtAuthFilter` y `AuthServiceImpl`. `JwtUtil` es el Adapter, no el Adaptado | `service/TokenService.java`; `security/JwtUtil.java:18-31`; diagrama M7 |
| 6 | ¿Object o Class Adapter? | Object: `JwtUtil` contiene `JwtParser` y `SecretKey` como `final` (composición). En Java es el único viable (slide 27) | `security/JwtUtil.java:22-23`; `security/UsuarioDetails.java:20` |
| 7 | Mostrame el recorrido MVC de anular un crédito | Vista (`Creditos.jsx` → `api/creditos.js`) → controlador (`CreditoController.anularCredito`, que pasa el usuario) → servicio (permiso) → modelo (`Credito.anular()` decide) → `GlobalExceptionHandler` traduce a 204/400/403/404 | `controller/CreditoController.java:71-75`; `service/impl/CreditoServiceImpl.java:78-87`; `model/Credito.java:146-156`; `docs/diagramas/archify/anular-credito.svg` |
| 8 | Si el front oculta el botón, ¿para qué validar en el backend? | La vista solo oculta y el modelo es la autoridad (M4, TPO-007). Con el token de `user`, `DELETE /api/creditos/anular/{id}` da 403 | `service/impl/CreditoServiceImpl.java:79-81`; `model/Usuario.java:47-49`; en vivo desde Swagger |
| 9 | ¿Qué GRASP hay en cobrar una cuota? | Expert: la cuota sabe si está pagada y si su crédito está anulado. Creator: la cuota crea su `Cobranza`, cuyo constructor es package-private | `model/Cuota.java:77-96`; `model/Cobranza.java:51-53` |
| 10 | ¿`EstadoCredito` no debería ser un State? | No: es un valor derivado que no cambia el comportamiento, con una sola transición con regla (`anular`). State sería sobre-ingeniería (slide 39, State vs Strategy) | `model/EstadoCredito.java`; `model/Credito.java:111-116` |

De reserva:
- **"¿Por qué 14.500,02 y no 14.500?"** Por el redondeo por cuota: el total sale de las cuotas emitidas (O3) y el ajuste de la última cuota está pendiente (`InteresSimpleTest`).
- **"¿Y si dos cajeros cobran la misma cuota?"** Bloqueo pesimista y test de 20 hilos (`repository/CuotaRepository.java:32-39`, `service/CobranzaConcurrenteTest.java`). Ojo: anular el crédito y cobrar al mismo tiempo todavía no está cubierto (I1).
- **"¿Por qué la tasa significa otra cosa según el plan?"** En interés simple es % total y en el francés % mensual; la vista lo rotula (`pages/Creditos.jsx:15-17,180-181`).
