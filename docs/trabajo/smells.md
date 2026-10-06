# T18: código muerto y bad smells (propuesta, sin cambios de código)

Base: main@c962ff3. `…/` = `backend/src/main/java/com/uade/tpejemplo/`. Nombres de smells según el apunte de clase 3 (`CLASE_04_adoo_clase_3_bad_smells.pdf`). Todo uso o no uso se verificó con `grep -rn` sobre `backend/src` (main + test) y `frontend/src`.

Fuera de este documento, porque ya están en otros: precargas de M8 en `CreditoServiceImpl` (no son código muerto, auditoría I2 y m8.md), `@PreAuthorize` duplicado con reglas de URL (spring-practicas S6), `@Transactional` faltantes (S1), comentario obsoleto de `Dashboard.jsx` (auditoría m4). Tampoco se repite lo que V1 ya corrigió (endpoint TODO del supervisor, `countAll`, `@CrossOrigin`, nombres `IdId`, `Double` en el dashboard, etc.).

## Backend

### Código muerto

#### D1. `UsuarioRepository.findByRol` sin llamadores
- Evidencia: `…/repository/UsuarioRepository.java:18`. Ningún uso en back ni en tests. `AdminServiceImpl.listarUsuarios` filtra en memoria (`…/service/impl/AdminServiceImpl.java:34-37`) en vez de usarlo.
- Arreglo mínimo: borrar el método (y el import de `Rol` y `List`).
- Tamaño S. **ANTES DEL 13/10**.

#### D2. `@Builder` sin uso en `AuthResponse`
- Evidencia: `…/dto/response/AuthResponse.java:10`. `AuthResponse.builder()` no aparece en ningún lado; `desde()` usa el constructor (`:22`). Por lo mismo sobra `@NoArgsConstructor` (`:11`): nadie lo deserializa.
- Arreglo mínimo: sacar `@Builder` y `@NoArgsConstructor`, dejar `@AllArgsConstructor` como en `UsuarioResponse`.
- Tamaño S. **ANTES DEL 13/10**.

#### D3. Métodos de `ICredito` que solo usa la propia clase o los tests
- Evidencia: `…/model/interfaces/ICredito.java:40-44` publica `estaCancelado()`, `tieneCobranzas()` y `puedeAnularse()`. Los dos primeros solo se llaman desde dentro de `Credito` (`…/model/Credito.java:120,142,149`); `puedeAnularse()` solo desde `CreditoTest` (`backend/src/test/.../CreditoTest.java:40,68,86,98`). Ningún servicio, DTO ni el front los usa.
- Arreglo mínimo: ninguno ahora. `puedeAnularse()` está cubierto por tests y es la pregunta que el front necesitaría para mostrar u ocultar el botón Anular.
- Tamaño S. **NO HACER**: borrarlos achica la interfaz pero tira tests y una pregunta de dominio legítima; no molesta a nadie.

#### D4. `IRol`: interfaz con un solo implementador que nadie usa como tipo
- Evidencia: `…/model/interfaces/IRol.java:3`. Solo `Rol implements IRol` (`…/model/Rol.java:5`); ninguna variable, parámetro ni retorno es de tipo `IRol` (`IUsuario.getRol()` devuelve `Rol`, `…/model/interfaces/IUsuario.java:14`).
- Arreglo mínimo: borrar `IRol` y dejar `autoridad()` en el enum.
- Tamaño S. **NO HACER** antes del 13/10: las interfaces de modelo se restituyeron en V2 a propósito (decisión defendida); sacar una sola rompe la simetría del diagrama. Si se quiere, DESPUÉS, junto con una pasada sobre todas.

#### D5. `GET /api/creditos` sin consumidor en el front
- Evidencia: `…/controller/CreditoController.java:40-43` → `CreditoServiceImpl.listarTodos` (`…/service/impl/CreditoServiceImpl.java:55-61`) y `CuotaRepository.buscarTodasConCobranzas` (`…/repository/CuotaRepository.java:21-22`). `frontend/src/api/creditos.js` no lo llama.
- Arreglo mínimo: ninguno. Está documentado en `docs/trabajo/api.md:17,60` como parte de la API (Swagger).
- Tamaño S. **NO HACER**: es API pública documentada, no código muerto.

### Bad smells

#### BS1. Código duplicado: `AdminService.listarTodos` / `listarUsuarios`
- Evidencia: `…/service/impl/AdminServiceImpl.java:26-30` y `:33-38` son el mismo stream; el segundo solo agrega el filtro de ADMIN. Además los nombres no dicen la diferencia (ver BS6). El supervisor recibe también al admin (`…/controller/SupervisorController.java:32`), y por eso el front tiene que deshabilitar a mano la fila del admin (`frontend/src/pages/GestorPermisos.jsx:58,68-76`).
- Arreglo mínimo: que el supervisor use `listarUsuarios()` (sin admins) y borrar `listarTodos()`. Con eso el `isAdmin` de `GestorPermisos.jsx` queda muerto y se borra también.
- Tamaño S. **ANTES DEL 13/10**: es un hueco real (un supervisor ve al admin en su gestor de permisos) y se arregla en dos líneas.

#### BS2. Código duplicado: armado de `ErrorResponse` en el handler
- Evidencia: `…/exception/GlobalExceptionHandler.java:22-24, 29-31, 39-41, 46-48, 53-55, 60-62, 67-69, 74-76`. Ocho veces `ResponseEntity.status(X).body(new ErrorResponse(código, título, lista, LocalDateTime.now()))`, con el código numérico repetido a mano junto al `HttpStatus`.
- Arreglo mínimo: un `private ResponseEntity<ErrorResponse> error(HttpStatus status, String titulo, List<String> mensajes)` que saque el número de `status.value()`.
- Tamaño S. **DESPUÉS**: es repetición mecánica, no lógica; no rompe nada.

#### BS3. Feature envy: el chequeo de permiso de anulación vive en los servicios
- Evidencia: `…/service/impl/CreditoServiceImpl.java:79` (`usuario.getPermisos().isPuedeAnularCredito()`) y `…/service/impl/CobranzaServiceImpl.java:48` (`usuario.getPermisos().isPuedeAnularCobranza()`). El servicio navega `usuario → permisos → flag` para decidir algo que sabe el usuario (también es cadena de mensajes).
- Arreglo mínimo: `IUsuario.puedeAnularCredito()` / `puedeAnularCobranza()` que deleguen en `Permisos`, y los servicios preguntan `usuario.puedeAnularCredito()`.
- Tamaño S. **DESPUÉS**: es Expert/Tell-don't-ask de GRASP; si T13 lo propone como mejora, lo absorbe. Ojo con auditoría I3 (ya hubo métodos duplicados en `Permisos`): reemplazar, no sumar al lado.

#### BS4. Primitive obsession: `rol` como `String` en las respuestas
- Evidencia: `…/dto/response/UsuarioResponse.java:15,23` y `…/dto/response/AuthResponse.java:17,25` convierten `Rol` a `String` con `.name()`, mientras `CreditoResponse` expone enums tal cual (`…/dto/response/CreditoResponse.java:26,32`). El front compara strings sueltos en 6 lugares (ver BSF4).
- Arreglo mínimo: tipar el campo como `Rol`. El JSON no cambia (Jackson serializa el enum por nombre), así que el front no se entera.
- Tamaño S. **DESPUÉS**.

#### BS5. Parámetros largos: `Credito.nuevo` con 6 parámetros
- Evidencia: `…/model/Credito.java:88-89` y el constructor `:71-72`.
- Arreglo mínimo: ninguno.
- Tamaño M. **NO HACER**: son los 6 datos del alta de un crédito, todos obligatorios y de tipos distintos (no se confunden por posición). Agruparlos en un objeto parámetro es sobreingeniería para un solo llamador (`CreditoServiceImpl.java:34-41`).

#### BS6. Nombres
- Evidencia:
  - `AdminService.listarTodos` vs `listarUsuarios` (`…/service/AdminService.java:11,13`): ambos listan usuarios; el nombre no dice que uno excluye admins. Se resuelve con BS1.
  - `SupervisorController.obtenerUsuarios` (`…/controller/SupervisorController.java:31`) vs `AdminController.listarUsuarios` (`…/controller/AdminController.java:32`): mismo caso, dos verbos.
  - `JwtUtil` (`…/security/JwtUtil.java:16`) es un componente con estado inyectado que implementa `TokenService`, no una utilidad estática.
  - `TpEjemploApplication` y el paquete `tpejemplo`: ya está como TPO-014 / spring-practicas S10, no se repite.
- Arreglo mínimo: el primero cae con BS1; `obtenerUsuarios` → `listarUsuarios`. `JwtUtil` → `JwtTokenService` solo si se toca por otra razón (m7.md lo nombra como Adapter).
- Tamaño S. **DESPUÉS** (salvo lo que arrastra BS1).

#### BS7. Data class: los DTO
- Evidencia: `…/dto/request/*` y `…/dto/response/*` son `@Data` sin comportamiento.
- Arreglo mínimo: ninguno.
- **NO HACER**: un DTO es una estructura de datos por diseño; el apunte apunta al smell en clases de dominio, y esas ya tienen comportamiento desde V1 (`Cuota.estaPagada`, `Credito.estado`, `Cobranza.anular`).

Smells del apunte que no aparecen en el back de main: método largo (el más largo es `Cuota.registrarCobranza`, 20 líneas con tres guardas), God class (`Credito`, 156 líneas, todo dominio del crédito), Lazy class (salvo D4), herencia rechazada (no hay herencia propia), intimidad inapropiada, switch (lo resolvió Strategy en `TipoPlan`), comentarios que tapan mal código (los Javadoc explican decisiones, no código confuso).

## Frontend (TPO-012, fuera de alcance desde V1: listado aparte)

### Código muerto

#### DF1. `store/index.js` huérfano y duplicado de `store/store.js`
- Evidencia: `frontend/src/store/index.js:1-16` arma un store con 4 reducers y nadie lo importa; `main.jsx:4` usa `store/store.js`, que tiene los 6.
- Arreglo mínimo: borrar `store/index.js`.
- Tamaño S. **ANTES DEL 13/10**: confunde en vivo ("¿cuál es el store?").

#### DF2. Archivos y exports sin uso
- Evidencia: `frontend/src/App.css` y `frontend/src/assets/react.svg` (restos del template de Vite, nadie los importa); `getCliente` (`api/clientes.js:4`) y `getCredito` (`api/creditos.js:4`) sin llamadores; acciones `clearError` exportadas en `store/slices/clientesSlice.js:41`, `cobranzasSlice.js:66`, `creditosSlice.js:62` y `authSlice.js:57`, ninguna despachada.
- Arreglo mínimo: borrar los dos archivos, las dos funciones y los cuatro `clearError`.
- Tamaño S. **DESPUÉS**.

#### DF3. `console.log` de depuración
- Evidencia: `frontend/src/pages/Creditos.jsx:9` imprime el usuario de Redux (con su token) en cada render.
- Arreglo mínimo: borrar la línea.
- Tamaño S. **ANTES DEL 13/10**: se ve en la consola durante la demo y filtra el JWT.

### Bad smells

#### BSF1. Comentarios que tapan mal código (y restos de un asistente)
- Evidencia: `store/slices/permisosSlice.js:4` (`// Asumiendo que esta función hace el PUT del rol[cite: 4]`), `:9` (`// Asegúrate de tener este endpoint creado...`), `:37`; `pages/GestorPermisos.jsx:3` (`// Asumiendo que renombrarás las acciones si lo deseas`), `:74` (`// Opcional: ...`); `store/slices/cobranzasSlice.js:20` (`// NUEVO THUNK PARA ANULAR`).
- Arreglo mínimo: borrarlos. No explican nada del código y el `[cite: 4]` delata copy-paste.
- Tamaño S. **ANTES DEL 13/10**: el profe lee el código en vivo.

#### BSF2. Código duplicado: rutas protegidas por rol
- Evidencia: `components/AdminRoute.jsx:5-17` y `components/SupervisorRoute.jsx:5-17` son idénticos salvo el string del rol. Y además cada página repite el mismo chequeo (`pages/PanelAdmin.jsx:10,22-24`, `GestorPermisos.jsx:11,29-31`, `Dashboard.jsx:11,19`), redundante con la ruta.
- Arreglo mínimo: un `RoleRoute({ roles, children })`.
- Tamaño S. **DESPUÉS**.

#### BSF3. Código duplicado: thunks y estilos
- Evidencia: los 11 thunks de `store/slices/*.js` repiten `try { return await x() } catch (err) { return rejectWithValue(err.message) }`; `pending/rejected` se repiten en cada slice (solo `authSlice.js:38-45` y `permisosSlice.js:54-56` los factorizan). Los objetos `styles` repiten `card`, `btn`, `error`, `input` en las 8 páginas (p. ej. `Clientes.jsx:54,57,58` vs `Cobranzas.jsx:114,117,118`).
- Arreglo mínimo: ninguno ahora.
- Tamaño M. **NO HACER** antes del 13/10: es el boilerplate estándar de Redux Toolkit y de estilos inline; factorizarlo cambia todo el front sin tapar ningún hueco.

#### BSF4. Primitive obsession: roles como strings sueltos
- Evidencia: `'ADMIN'`/`'SUPERVISOR'` comparados a mano en `components/Navbar.jsx:13-14`, `AdminRoute.jsx:12`, `SupervisorRoute.jsx:12`, `pages/Dashboard.jsx:11`, `GestorPermisos.jsx:11,58`, `PanelAdmin.jsx:10`.
- Arreglo mínimo: una constante `ROLES` en un archivo y usarla. Va junto con BSF2.
- Tamaño S. **DESPUÉS**.

#### BSF5. Acceso inconsistente a la API (intimidad inapropiada con `apiClient`)
- Evidencia: casi todo pasa por `src/api/*.js`, pero `store/slices/dashboardSlice.js:2,8` y `permisosSlice.js:2,10` llaman `api.get` directo; `api/admin.js:3-6` y `api/supervisor.js:3-11` envuelven en `async/await` + `return response` lo que el resto hace en una línea. Además `cobranzasSlice.js:26` lee `err.response?.data?.mensajes`, forma de error de axios que `apiClient.js:12` nunca produce (siempre cae al `err.message`).
- Arreglo mínimo: `api/dashboard.js` y `getUsuariosAdmin` en `api/admin.js`; dejar `rejectWithValue(err.message)` en `cobranzasSlice.js:26`.
- Tamaño S. **DESPUÉS**.

#### BSF6. Método largo / switch anidado en el render
- Evidencia: `pages/Creditos.jsx:97` arma el renglón del crédito en una sola línea con ternario de plan; `:122-123` resuelve el estado de la cuota con dos ternarios anidados repetidos (color y texto).
- Arreglo mínimo: un objeto `ESTADO_CUOTA = { pagada: {...}, vencida: {...}, pendiente: {...} }`.
- Tamaño S. **DESPUÉS**.

## Prioridades

| Prioridad | IDs |
|---|---|
| ANTES DEL 13/10 | D1, D2, BS1, DF1, DF3, BSF1 |
| DESPUÉS | BS2, BS3, BS4, BS6, DF2, BSF2, BSF4, BSF5, BSF6 |
| NO HACER | D3, D4, D5, BS5, BS7, BSF3 |
