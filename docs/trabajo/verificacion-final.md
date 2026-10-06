# Verificación final de V3 (T22)

Hecha el 2026-10-06 sobre main `3245795`, con el backend (8080) y el front (5173) ya levantados. Usuarios semilla `admin`, `supervisor`, `user` (password = username). API con curl; visual con el browser de cmux (perfil default). Código sin tocar.

## API

| Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Login con password incorrecta | 401 | 401 "Bad credentials" | OK |
| Login correcto | 200 con token y rol | 200, `rol:ADMIN` | OK |
| Token basura (O2) | 401 | 401 | OK |
| Token con payload o firma alterados (O2) | 401 | 401 | OK |
| Token vencido (O2) | 401 | 401 | OK |
| Sin token | 401 | 401 | OK |
| `/api/noexiste` | 404 | 404 | OK |
| `PUT /api/clientes`, `PATCH /api/dashboard/stats` | 405 | 405 | OK |
| Crear cliente | 201 | 201 | OK |
| Simple 1200, 10 %, 3 cuotas | total 1320, cuota 440 | 1320.00 / 440.00 | OK |
| Francés 1200, 10 %, 3 cuotas | cuota 482,54 | 482.54, total 1447.62 | OK |
| Simple 1000, 5 %, 2 cuotas | cuota 525 | 525.00, total 1050.00 | OK |
| `totalADevolver` = cuota x cantidad (O3) | 440x3, 525x2 | 1320.00, 1050.00 | OK |
| Crédito nuevo: estado y saldo | `VIGENTE`, saldo = total | `VIGENTE`, 1320.00 | OK |
| Cuota vencida (fecha 2025-01-01) | `vencida:true` | ambas `true` | OK |
| Cobrar cuota 1 | 201, cuota pagada | 201, `pagada:true`, saldo 880.00 | OK |
| `puedeAnularse` con cobranzas | `false` | `false` | OK |
| Cobrar cuota ya pagada | 400 | 400 "La cuota 1 del crédito 1 ya fue pagada" | OK |
| Pagar todas las cuotas | `CANCELADO`, saldo 0 | `CANCELADO`, `saldo:0` | OK |
| Anular crédito con cobranzas / cancelado | 400 | 400 "tiene cobranzas registradas" | OK |
| Anular con `user` sin permiso | 403 | 403 | OK |
| Anular crédito inexistente | 404 | 404 | OK |
| Anular sin cobranzas (supervisor) | 204 | 204 | OK |
| Anular crédito ya anulado | 400 | 400 "ya está anulado" | OK |
| Cobrar crédito anulado | 400 | 400 "está anulado" | OK |
| Crédito anulado | `ANULADO`, saldo 0 | `ANULADO`, `saldo:0` | OK |
| Dashboard: créditos activos (O4) | vigentes (1 y 4) = 2 | `cantidadCreditos:2`, financiado 3200.00, cobrado 1490.00 | OK |
| Dashboard SUPERVISOR / ADMIN | 200 | 200, mismos números | OK |
| Dashboard con `user` | 403 | 401 | FALLA |
| Supervisor lista usuarios (O5) | sin ADMIN | lista solo `supervisor` y `user` | OK |
| Supervisor modifica permisos del ADMIN (BS1) | rechazo | 400 "No se pueden modificar los permisos de un administrador" | OK |
| Supervisor llama `/api/admin/**` (usuarios, permisos, rol) | 403 | 401 | FALLA |
| `user` llama `/api/supervisor/usuarios` | 403 | 401 | FALLA |
| Error 500 no expone mensaje interno (S4) | mensaje genérico | 500 `"Error interno"` | OK |
| `GET /api/creditos/abc`, JSON roto, `tipoPlan` inválido | 400 | 500 `"Error interno"` | FALLA (menor: el status debería ser 400) |

## Visual

| Pantalla | Esperado | Visto | Resultado | Captura |
|---|---|---|---|---|
| Login | Formulario | Usuario, password, Ingresar | OK | capturas/final/01-login.png |
| Login con password incorrecta | Error visible | Mensaje de error | OK | capturas/final/02-login-error.png |
| Login admin | /clientes con rol | "admin (ADMIN)" | OK | capturas/final/03-login-ok.png |
| Créditos | Búsqueda y alta | Formulario de alta y búsqueda | OK | capturas/final/04-creditos.png |
| Botón Anular según `puedeAnularse` | Solo en #4 y #5 (vigentes sin cobranzas) | 2 botones Anular; ninguno en #1 (con cobranza), #2 (anulado), #3 (cancelado) | OK | capturas/final/05-creditos-listado.png |
| Anular #5 y refresco del listado (O1) | `[ANULADO]` y saldo $0 sin re-buscar | `Saldo: $0 [ANULADO]` al instante | OK | capturas/final/06-anular-refresca.png |
| Dashboard ADMIN | Título con el rol real | "Panel de Estadísticas (Modo Admin)", 1 cliente, 2 activos, $3200, $1490 | OK | capturas/final/07-dashboard-admin.png |
| Dashboard SUPERVISOR | Título con el rol real | "Modo Supervisor", mismos números | OK | capturas/final/08-dashboard-supervisor.png |
| `user`: Anular oculto | Sin botón | 0 botones Anular | OK | capturas/final/09-user-sin-anular.png |
| Console sin JWT | Sin logs con el token | Hook sobre console.log/info/debug/warn/error durante login, navegación y anulación: 0 entradas; `grep console.` en `frontend/src`: sin resultados | OK | |

## Fallas

- Rutas protegidas por rol (`/api/dashboard/stats` para `user`, `/api/admin/**` para `supervisor`, `/api/supervisor/**` para `user`) devuelven 401 con cuerpo vacío en vez de 403. `SecurityConfig` solo configura `authenticationEntryPoint` (`HttpStatusEntryPoint(UNAUTHORIZED)`) y no un `accessDeniedHandler`. Es una regresión contra `smoke.md`, que daba 403 con `user` en el dashboard.
- Requests con body mal formado, enum inválido o tipo de path incorrecto caen en el handler general y responden 500 en vez de 400. El mensaje no se expone.

## Testeo final 06/10 noche

Sobre main `6c470a9`, backend 8080 y front 5173 con base vacía al inicio. Código sin tocar. `mvn -q clean test` exit 0 (36 tests), `npm run build` exit 0. Capturas en `capturas/final2/`.

### API

| Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Login con password incorrecta | 401 | 401 "Bad credentials" | OK |
| Login correcto | 200, rol | `rol:ADMIN` | OK |
| `GET /api/auth/me` (admin, user) | 200 con rol y permisos | 200, `ADMIN`/`USER` con sus flags | OK |
| `GET /api/auth/me` sin token | 401 | 401 | OK |
| Token basura, firma alterada, payload alterado | 401 | 401 | OK |
| Token vencido | 401 | no re-probado en esta pasada | NO PROBADO |
| `/api/noexiste` | 404 | 404 | OK |
| `PUT /api/clientes`, `PATCH /api/dashboard/stats` | 405 | 405 | OK |
| `GET /api/creditos/abc`, JSON roto | 400 | 400 "Solicitud inválida" | OK |
| Cliente con DNI y nombre vacíos | 400 | 400 con los dos mensajes | OK |
| Crédito con deuda -5, tasa 5000, 0 cuotas | 400 | 400 con 4 mensajes | OK |
| Crédito con `tipoPlan` inválido | 400 | 400 | OK |
| Crear cliente | 201 | 201 | OK |
| Simple 1200, 10 %, 3 cuotas (O6) | 3 cuotas de 440, total 1320 | 3 cuotas de 440.00, 1320.00 | OK |
| Francés 1200, 10 %, 3 cuotas (O6) | cuota 482,54 | 3 cuotas de 482.54, total 1447.62 | OK |
| Simple 1000, 5 %, 2 cuotas (O6) | 2 cuotas de 525 | 525.00 x2, total 1050.00 | OK |
| Cuotas con fecha 2025-01-01 | `vencida:true` | las 3 `true` | OK |
| Dashboard con 3 créditos (O7) | financiado 3400, saldo 3817,62, vencido 1320 | 3400.00 / 3817.62 / 1320.00 | OK |
| Cobrar cuota 1 del crédito 3 | 201 | 201, saldo 525.00, `puedeAnularse:false` | OK |
| Dashboard tras cobro (O7) | cobrado 525, saldo 3292,62 | 525.00 / 3292.62 | OK |
| Cobrar cuota ya pagada | 400 | 400 "ya fue pagada" | OK |
| Cobrar importe -1 | 400 | 400 | OK |
| Anular cobranza con `user` sin permiso | 403 | 403 | OK |
| Anular cobranza con supervisor | 204 | 204 | OK |
| Anular la misma cobranza otra vez | rechazo | 400 "ya está anulada" | OK |
| Anular cobranza inexistente | 404 | 404 | OK |
| Crédito tras anular la cobranza | saldo vuelve a 1050 | 1050.00, `puedeAnularse:true` | OK |
| Anular crédito con `user` | 403 | 403 | OK |
| Anular crédito sin cobranzas (supervisor) | 204 | 204 | OK |
| Anular crédito ya anulado | 400 | 400 | OK |
| Cobrar crédito anulado | 400 | 400 | OK |
| Anular crédito inexistente | 404 | 404 | OK |
| Dashboard tras anular (O7) | financiado 2200, saldo 2370, vencido 1320 | 2200.00 / 2370.00 / 1320.00 | OK |
| Dashboard con `user` | 403 | 403 | OK |
| Dashboard supervisor y admin | 200 | 200 | OK |
| Supervisor llama `/api/admin/**` | 403 | 403 | OK |
| `user` llama `/api/supervisor/usuarios` | 403 | 403 | OK |
| Supervisor lista usuarios (O5) | sin ADMIN | `supervisor` y `user` | OK |
| Supervisor modifica permisos del ADMIN (BS1) | rechazo | 400 "No se pueden modificar los permisos de un administrador" | OK |
| Supervisor modifica permisos de `user` | 200 | 200 | OK |

### Visual

| Pantalla | Esperado | Visto | Resultado | Captura |
|---|---|---|---|---|
| Login | Formulario | Usuario, password, Ingresar | OK | capturas/final2/01-login.png |
| Login con password incorrecta | Error visible | "Bad credentials" | OK | capturas/final2/02-login-error.png |
| Login admin | /clientes con rol | "admin (ADMIN)", Panel Admin | OK | capturas/final2/03-admin.png |
| Login supervisor y user | /clientes con su rol | "supervisor (SUPERVISOR)" con Gestor de Permisos; "user (USER)" | OK | |
| Alta de cliente | Aparece en la lista | Lista de 2 clientes | OK | capturas/final2/04-cliente-alta.png |
| Búsqueda por DNI (UC06) | Cliente / mensaje | "Cliente Smoke · DNI 40222333"; inexistente: "Cliente no encontrado" | OK | capturas/final2/05-busqueda-dni.png |
| Crédito simple (UC09) | Creado y detalle | #4: total 1650, 3 x 550, saldo 1650 | OK | capturas/final2/08-detalle-simple.png |
| Crédito francés (UC09) | Creado y detalle | #5: total 1575,76, 4 x 393,94 | OK | capturas/final2/09-detalle-frances.png |
| Cobro con aviso | Aviso verde de éxito | "Cobranza #2 registrada: cuota 1 del crédito #4." | OK | capturas/final2/10-cobro-exito.png |
| Anular cobranza | `[ANULADA]` sin botón | `#2 [ANULADA]`, sin botón | OK | capturas/final2/12-cobranza-anulada.png |
| Anular crédito | `ANULADO`, saldo 0 | `ANULADO`, saldo $ 0,00 | OK | capturas/final2/13-credito-anulado.png |
| `user` sin permiso | Sin botón Anular | Sin botón | OK | capturas/final2/14-user-sin-permiso.png |
| Supervisor habilita a `user`, sin reloguear | Botón Anular aparece | Aparece al reconsultar | OK | capturas/final2/15-user-con-permiso.png |
| Dashboard (O7) | Coherente con los créditos | 2 clientes, 3 activos, 3700 / 0 / 4020 / 1320 | OK | capturas/final2/16-dashboard-dark.png |
| Dark theme | Legible | Contraste >= 4,5 en todos los textos de /creditos | OK | capturas/final2/18-creditos-dark.png |

### Entrega

| Caso | Resultado |
|---|---|
| `git archive HEAD` sin `docs/trabajo`, `target`, `node_modules` ni archivos de IDE | OK |
| Reporte y manual HTML: imágenes y links locales | OK, 0 rotos |
| `mvn -q test` dentro de la copia extraída | OK, exit 0 |
| `git log v2..main` con claude, co-authored o anthropic | 0 |

### Observaciones

- Con una sesión guardada en localStorage, abrir una ruta inexistente o `/login` muestra el navbar de la sesión sobre el formulario de login (capturas/final2/01-login.png). Menor, no bloquea.
- Las fallas de la verificación anterior (403 devuelto como 401, 400 devuelto como 500) están resueltas.
