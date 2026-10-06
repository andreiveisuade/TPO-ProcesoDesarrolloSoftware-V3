# Oportunidades de mejora — iteración 3 (T13)

Revisión de solo lectura sobre `main@11779e7` (ya incluye `fixes-auditoria` y `tests-dominio`). No repite lo de `auditoria.md`. Rutas Java relativas a `backend/src/main/java/com/uade/tpejemplo/`; rutas de front relativas a `frontend/src/`.

Criterio: cada propuesta tapa un hueco que se puede mostrar con el código, o corrige un mal uso de un concepto del apunte. Si una idea no cumple eso, va a NO HACER con su motivo.

## Diagnóstico por eje

**MVC.** La base está bien y se puede defender. Los controllers son delgados: `controller/CreditoController.java:32-35` solo traduce HTTP y llama al service. La validación está en las tres capas que pide el apunte de la clase 09: la vista con `pages/Creditos.jsx:75-76`, el controller con `@Valid` y `dto/request/CreditoRequest.java:21-39`, y el modelo con `model/Cuota.java:76-95` y `model/Credito.java:145-155`. Los DTO separan bien: `dto/response/*Response.desde(I*)` lee interfaces del modelo y ninguna entidad llega a la vista. Fallan dos cosas: la vista decide reglas de negocio que el modelo ya sabe (O1, O5), y el store recalcula estado por su cuenta (O1). Lo único de infraestructura en el modelo es `Rol.autoridad()` (`model/Rol.java:14-17`, el prefijo `ROLE_` de Spring), una decisión de V2. Se puede defender y no justifica una propuesta.

**Strategy.** Los roles están bien y la elección entra por el enum `TipoPlan`, sin `switch` (ver auditoría I5). Falla el alcance: el Contexto consulta la estrategia en cada lectura del total, no solo al otorgar (O3). No hay otro Strategy natural en el dominio (O10).

**Adapter.** `UsuarioDetails` es un Object Adapter de manual: compone `IUsuario` (`security/UsuarioDetails.java:25`). `JwtUtil` delega en la API estática de jjwt. Falla en que el Cliente conoce un tipo del Adaptado (O2). La firma con `UserDetails` ya está en la auditoría (I6).

**GRASP/SOLID.**
- Information Expert: se cumple en `Cuota`, `Credito` y `Cobranza`; falla en el dashboard (O4) y en la vista (O1, O5).
- Creator: `Cuota` crea `Cobranza` (`model/Cuota.java:92`) y está bien. `Credito` crea sus cuotas solo si el service se lo pide (O6).
- Protected Variations y bajo acoplamiento: fallan en O2 y O3.
- OCP: para agregar un plan hace falta una constante nueva en `TipoPlan` (`model/TipoPlan.java:8-9`), pero `Credito` no cambia. Ver defensa P2.
- SRP: `AdminService` atiende a dos actores, ADMIN y SUPERVISOR (`controller/SupervisorController.java:24`). Con O5 la regla baja al modelo y compartir el service deja de ser un problema.

**Dominio.** Está bien modelado lo siguiente: los estados derivados (VIGENTE/CANCELADO/ANULADO), el saldo como suma de las cuotas impagas, el vencimiento mensual, el importe exacto y el rechazo del cobro sobre un crédito anulado. Hay tres huecos reales: el total no cierra con las cuotas (O3), el dashboard cuenta como activos los créditos cancelados (O4) y falta la mora en el dashboard (O7). Los pagos parciales quedan fuera del alcance (O8).

## Propuestas

Orden sugerido para antes del 13/10: O2, O3, O1, O4, O5. Todas son S y ninguna toca la persistencia.

### O1 — La vista decide si un crédito se puede anular y recalcula su estado

- **Qué.** Exponer `Credito.puedeAnularse()` en el DTO y, después de anular, volver a pedir el crédito al backend en vez de modificarlo en el store.
- **Evidencia.**
  - `Credito.puedeAnularse()` (`model/Credito.java:141-143`, declarada en `model/interfaces/ICredito.java:44`) no se usa en ningún código de producción, solo en `CreditoTest`. `CreditoResponse` no la expone (`dto/response/CreditoResponse.java:31-33, 48-50`).
  - `pages/Creditos.jsx:103` muestra "Anular" con `!cr.anulado && user?.puedeAnularCredito`. Copia la mitad de la regla y se saltea "tiene cobranzas": el botón aparece en créditos con cuotas pagas y el backend contesta 400.
  - `store/slices/creditosSlice.js:51-56`: después de anular solo hace `anulado = true`. Quedan `estado` en `VIGENTE` y `saldo` sin cambios, y `pages/Creditos.jsx:99` muestra `[VIGENTE]` y el saldo viejo de un crédito que el modelo ya da por ANULADO y con saldo 0 (`model/Credito.java:117-118, 124-125`). En la demo en vivo, anulás un crédito y el badge no cambia. Esto sale de leer el código, no se corrió.
  - Con las cobranzas pasa lo mismo: `pages/Cobranzas.jsx:94` ofrece anular cobranzas de cualquier día, pero la regla "solo las del día" está en `Cobranza.anular()` (`model/Cobranza.java:61-66`). Ese método además acepta anular dos veces en silencio.
- **Cambio.**
  - Crédito: agregar `anulable` a `CreditoResponse` con el valor de `credito.puedeAnularse()`; en el JSX, `cr.anulable && user?.puedeAnularCredito`. Cuando `anularCreditoThunk` termina bien, reemplazar el crédito con `getCredito(id)` (`api/creditos.js:4`).
  - Cobranza (opcional, mismo patrón): `Cobranza.puedeAnularse()` (del día y no anulada), usarla en `anular()` y exponerla en `CobranzaResponse`.
- **Concepto que corrige.** MVC: según el apunte de la clase 09, "en el modelo se deberían realizar las validaciones explícitas del negocio", y la vista representa datos, no los recalcula. También Information Expert.
- **Tamaño** S (unas 15 líneas). **Riesgo** bajo. **Prioridad: ANTES DEL 13/10.**

### O2 — El Adapter de JWT le pasa una excepción de jjwt al Cliente

- **Qué.** Que el Adapter traduzca las excepciones de jjwt y que `JwtAuthFilter` dependa solo de `TokenService`.
- **Evidencia.** `security/JwtAuthFilter.java:4` importa `io.jsonwebtoken.JwtException` y la atrapa en `:66`. El filtro es el Cliente de `TokenService` (`:27`), pero conoce la excepción del Adaptado. El apunte de la clase 10 lo lista entre los errores típicos del Adapter: "que el Target siga exponiendo tipos del Adaptado". Si se cambia jjwt, que es justo la variación que M7 dice proteger, el filtro deja de compilar o deja escapar la excepción y la request termina en 500.
- **Cambio.** `TokenService.extraerUsername` devuelve `Optional<String>` y `JwtUtil` (`security/JwtUtil.java:38-41`) atrapa adentro `JwtException | IllegalArgumentException`. El filtro queda solo con `UsernameNotFoundException`. En el mismo cambio entra el pendiente de la auditoría I6: `esValido(String token, String username)` en vez de `UserDetails`. Actualizar `m7.md`.
- **Concepto que corrige.** Adapter, Protected Variations y DIP.
- **Tamaño** S (3 archivos). **Riesgo** bajo: re-smoke del 401 con token inválido. **Prioridad: ANTES DEL 13/10.**

### O3 — El total se recalcula con la estrategia en cada lectura y no cierra con las cuotas

- **Qué.** Que el total del crédito salga de las cuotas que se emitieron, y que la estrategia se use solo al otorgar.
- **Evidencia.**
  - `model/Credito.java:45-52` guarda `importeCuota` "para que el credito conserve el importe con el que se otorgo aunque despues cambie la forma de calcularlo". Sin embargo, `Credito.totalADevolver()` (`:93-95`) vuelve a llamar a `tipoPlan.calculo()` en cada GET. Hay dos fuentes de verdad para el mismo contrato.
  - El efecto ya se ve. Con interés simple, 10.000 al 45 % en 6 cuotas, `CreditoResponse` muestra total 14.500,00 y saldo inicial 14.500,02, porque `Credito.saldo()` suma las cuotas (`:123-131`). En 7 cuotas da 14.500,01. Se verificó con la misma aritmética de `model/plan/InteresSimple.java:17-26`, y lo confirman `InteresSimpleTest.java:22-28` y `docs/trabajo/tests.md` ("Diferencias de centavos"). `CreditoTest` usa 900 al 0 % en 3 cuotas, que divide justo, y por eso no lo detecta (`CreditoTest.java:14-18`).
- **Cambio.** `Credito.totalADevolver()` pasa a ser `importeCuota × cantidadCuotas`, lo que de verdad se cobra. `CalculoDeCuota` pierde `totalADevolver` (`model/interfaces/CalculoDeCuota.java:9`) y queda con un solo método, que es el algoritmo intercambiable. `InteresSimple` deja su total como privado. Hay que ajustar los dos tests de plan, `m9.md` y el diagrama.
- **Costo visible.** En ese ejemplo el total pasa a mostrar 14.500,02. Se explica como redondeo a centavos por cuota. Ajustar la última cuota para que cierre en 14.500,00 es la alternativa, de tamaño M: va a DESPUÉS.
- **Concepto que corrige.** Strategy con el alcance correcto: el Contexto no depende de la estrategia para datos históricos. También Protected Variations, Information Expert (`Credito` conoce sus cuotas) y la consistencia de importes.
- **Tamaño** S. **Riesgo** bajo-medio: cambian dos tests y un número visible. **Prioridad: ANTES DEL 13/10.**

### O4 — "Créditos activos" usa una definición de vigente distinta de la del modelo

- **Qué.** Contar los créditos vigentes con `Credito.estado()` y no con una query que tiene su propia regla.
- **Evidencia.** `CreditoRepository.contarVigentes()` (`repository/CreditoRepository.java:33-34`) cuenta `anulado = false`, así que suma los cancelados. Lo usa `service/impl/DashboardServiceImpl.java:30` y se muestra como "Créditos Activos" en `pages/Dashboard.jsx:36`. M8 definió VIGENTE como "ni anulado ni cancelado" (`model/Credito.java:116-121`), mientras `docs/trabajo/m3.md:36` promete que el dashboard "refleja solo lo vigente". Un crédito pagado completo sigue contando como activo. M3 y M8 se contradicen.
- **Cambio.** `DashboardServiceImpl` carga con `creditoRepository.buscarTodosConCuotas()` y `cuotaRepository.buscarTodasConCobranzas()`, que ya existen (los usa `service/impl/CreditoServiceImpl.java:56-57`), dentro de `@Transactional(readOnly = true)`, y cuenta `estado() == VIGENTE`. Después se borra `contarVigentes`. Para el volumen del TPO, cargar todo en memoria no pesa; anotarlo en el doc. La salida mínima, si no hay tiempo, es renombrar la tarjeta a "Créditos no anulados".
- **Concepto que corrige.** Information Expert: la regla de vigencia vive en un solo lugar.
- **Tamaño** S. **Riesgo** bajo. **Prioridad: ANTES DEL 13/10.**

### O5 — La regla "al ADMIN no se le tocan los permisos" está solo en la vista

- **Qué.** Llevar al modelo la guarda que protege al ADMIN y aplicarla a los permisos, no solo al rol.
- **Evidencia.**
  - `pages/GestorPermisos.jsx:58, 68-71, 83-86` deshabilita los checkboxes del ADMIN y además los muestra destildados, aunque el admin tiene `Permisos.todos()` (`config/DataInitializer.java:27`).
  - En el backend, `AdminServiceImpl.actualizarRol` protege al ADMIN (`service/impl/AdminServiceImpl.java:58-63`), pero `actualizarPermisos` no (`:41-52`), y `SupervisorController.actualizarPermisosAnulacion` (`controller/SupervisorController.java:41-44`) llega directo. Un SUPERVISOR puede sacarle los permisos al admin con un PUT. Es el mismo caso que TPO-007 (permisos validados solo en JSX), que M4 cerró solo para las anulaciones.
- **Cambio.** `Usuario.otorgarPermisos` y `Usuario.asignarRol` (`model/Usuario.java:47-57`) rechazan con `BusinessException` si el usuario es ADMIN. `AdminServiceImpl` pierde la guarda duplicada. La vista mantiene el `disabled` solo como ayuda visual.
- **Concepto que corrige.** MVC (las validaciones de negocio van en el modelo) e Information Expert (el usuario conoce su propio rol).
- **Tamaño** S. **Riesgo** bajo. **Prioridad: ANTES DEL 13/10**, en último lugar. Si no entra, va como pendiente en la lista de mejoras.

### O6 — El crédito arma sus cuotas solo si el service se lo pide

- **Qué.** Que el agregado nazca completo.
- **Evidencia.** `Credito.nuevo` (`model/Credito.java:88-91`) devuelve un crédito sin cuotas. `CreditoServiceImpl.crear` (`service/impl/CreditoServiceImpl.java:34-42`) tiene que llamar a `generarPlanDeCuotas()` y a `cuotaRepository.saveAll(...)`. El método es público y está en `ICredito` (`model/interfaces/ICredito.java:32`), así que lo ve cualquiera que use la interfaz. Si alguien se olvida de llamarlo, el crédito queda VIGENTE con saldo 0 y nunca se cancela, porque `estaCancelado()` exige `!cuotas.isEmpty()` (`:134`).
- **Cambio.** Generar el plan en el constructor y poner `cascade = CascadeType.PERSIST` en `cuotas` (`:66-69`). El service guarda solo el crédito, y `generarPlanDeCuotas` sale de `ICredito`.
- **Concepto que corrige.** Creator y agregado, con bajo acoplamiento entre el service y la estructura interna del crédito.
- **Tamaño** M. **Riesgo** medio: hay que probar el cascade de JPA, re-smoke y los tests que llaman a `generarPlanDeCuotas`. **Prioridad: DESPUÉS** (27/10).

### O7 — El dashboard no dice cuánto hay vencido ni cuánto falta cobrar

- **Qué.** Sumar al dashboard el saldo pendiente y el monto vencido.
- **Evidencia.** `docs-v0/docs/REQUERIMIENTOS.md` §10 lista A-05, "cuotas vencidas impagas, el caso de uso central de una cobranza", y A-02, saldo pendiente. El modelo ya los sabe calcular: `Cuota.estaVencida()` (`model/Cuota.java:68-70`) y `Credito.saldo()` (`model/Credito.java:123-131`). Pero `DashboardStatsResponse` (`dto/response/DashboardStatsResponse.java:13-16`) solo trae clientes, créditos, financiado y cobrado. La mora se ve únicamente entrando crédito por crédito por DNI (`pages/Creditos.jsx:122-123`).
- **Cambio.** Agregar `saldoPendiente` (suma de `saldo()` de los vigentes) y `montoVencido` (suma de las cuotas `estaVencida()`), calculados en `DashboardServiceImpl` sobre la misma carga de O4, más dos tarjetas en `pages/Dashboard.jsx`. Sin estado EN_MORA y sin punitorios.
- **Concepto que corrige.** Hueco de dominio, resuelto con Information Expert.
- **Tamaño** M. **Riesgo** bajo. **Prioridad: DESPUÉS** (27/10). Depende de O4.

### O8 — Pagos parciales

- **Qué.** Que una cuota se pueda pagar en partes (A-01 de los requerimientos v0).
- **Por qué no.** Cambia `Cuota.estaPagada()` de sí/no a un saldo por cuota, y con eso `Cobranza`, `Credito.saldo()`, `estaCancelado()`, el dashboard y la vista. Es tamaño L y de riesgo alto a una semana de la entrega. Exigir el importe exacto (`model/Cuota.java:87-91`, TPO-006) es una decisión que se puede defender para este alcance.
- **Prioridad: NO HACER** en V3. Va como pendiente en el reporte.

### O9 — Convertir `EstadoCredito` en patrón State

- **Por qué no.** El estado se calcula a partir de `anulado` y de las cuotas pagas (`model/Credito.java:116-121`). No se guarda y no cambia el comportamiento del crédito: hay una sola transición con regla, `anular()` (`:145-155`). Hacer clases por estado sería sobre-ingeniería, y el apunte advierte justamente contra confundir Strategy con State.
- **Prioridad: NO HACER.** Usarlo como respuesta en la defensa (P4).

### O10 — Sumar Strategy o Adapter "para mostrar"

- **Candidatos descartados.**
  - Strategy para punitorios o mora: el dominio no tiene punitorios y habría una sola implementación.
  - Adapter sobre `PasswordEncoder`: ya es la abstracción de Spring (`config/SecurityConfig.java:77-80`).
  - Adapter sobre `fetch` en el front: `api/apiClient.js` ya hace de pasarela única (token, errores de `ErrorResponse`). Se menciona en la defensa de MVC sin tocar código.
- **Por qué no.** Ninguno tapa un hueco. El apunte dice que aplicar un patrón con algoritmos que casi nunca cambian es sobre-ingeniería, y el profe dijo en clase: "la idea no es aplicar todo".
- **Prioridad: NO HACER.**

## Defensa oral: las 5 preguntas más probables

**P1. "¿Dónde está el MVC, si el front es React y el back una API REST?"**
- Vista: `frontend/src/pages/*`, que presenta los datos y envía las acciones.
- Controlador: `controller/*`, que traduce HTTP, valida con `@Valid` e invoca al modelo, por ejemplo `controller/CreditoController.java:32-35`.
- Modelo: `model/*` y `service/impl/*`, donde están las reglas, por ejemplo `model/Cuota.java:76-95`.

Vista y controlador se hablan por DTO, como pide el apunte (`dto/request/CreditoRequest.java`, `dto/response/CreditoResponse.java`). Es un MVC distribuido: la vista no observa al modelo, le pide los datos a través del controlador. La validación está en las tres capas (`pages/Creditos.jsx:75-76`, `CreditoRequest.java:21-39`, `model/Credito.java:145-155`).

**P2. "¿Quién elige la estrategia y qué hay que tocar para agregar un plan?"**

La elige el usuario en `pages/Creditos.jsx:77-80`, viaja como `CreditoRequest.tipoPlan` (`dto/request/CreditoRequest.java:38-39`), y `TipoPlan` asocia cada valor con su `CalculoDeCuota` (`model/TipoPlan.java:8-9`). `Credito` delega sin `if` (`model/Credito.java:79`). Para agregar un plan alcanza con una clase en `model/plan/` y una constante en `TipoPlan`; `Credito` no cambia, así que el Contexto cumple OCP y el enum es el único punto de registro. No hay `setEstrategia` porque el plan queda fijo al otorgar (auditoría I5).

**P3. "¿Por qué es un Adapter, si `JwtUtil` es código de ustedes?"**

El Adaptado es jjwt (`security/JwtUtil.java:29-36, 53-60`), no `JwtUtil`. Los roles quedan así:
- Adapter: `JwtUtil`.
- Target: `TokenService` (`service/TokenService.java:5-12`).
- Clientes: `JwtAuthFilter` (`security/JwtAuthFilter.java:27`) y `AuthServiceImpl` (`service/impl/AuthServiceImpl.java:27`).

El apunte de la clase 09 dice que el Adapter sirve para "seguir adelante sin conocer exactamente cómo, quién y cuándo resolverá una parte". El segundo Adapter es `UsuarioDetails` (`security/UsuarioDetails.java:23-41`): envuelve `IUsuario` para Spring Security por composición (Object Adapter). Sin O2 queda un flanco abierto: el filtro conoce `JwtException`.

**P4. "¿`EstadoCredito` no es un State?"**

No. Es un valor derivado (`model/Credito.java:116-121`): sale de `anulado` y de las cuotas pagas, no se guarda y no cambia qué hace el crédito. Un State tendría una clase por estado que conoce sus transiciones; acá hay una sola transición con regla (`anular()`, `:145-155`). Ver O9.

**P5. "Si cambian la fórmula del interés simple, ¿qué pasa con los créditos ya otorgados?"**

Con O3 hecho, nada. La cuota se calculó y se guardó al otorgar (`model/Credito.java:50-52, 79`), el total sale de las cuotas emitidas y la estrategia solo se usa al crear. Sin O3, el total de los créditos viejos cambiaría (`model/Credito.java:93-95`) y quedaría distinto de la suma de sus cuotas: por eso O3 va antes del 13/10.
