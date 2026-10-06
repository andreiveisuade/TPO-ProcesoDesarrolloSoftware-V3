# Smoke V3 (T7r)

Backend levantado con `mvn -q spring-boot:run` (H2 en memoria, puerto 8080), probado con curl el 2026-10-06. Usuarios semilla: `admin`, `supervisor` (permisos todos), `user` (sin permisos); password = username.

| Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Login con password incorrecta (M5) | 401 | 401 `{"error":"No autenticado","mensajes":["Bad credentials"]}` | OK |
| Ruta inexistente `/api/noexiste` con token | 404 | 404 `No static resource api/noexiste.` | OK |
| `PUT /api/clientes` | 405 | 405 `Request method 'PUT' is not supported` | OK |
| `PATCH /api/dashboard/stats` | 405 | 405 | OK |
| Crear cliente 111 | 201 | 201 | OK |
| Crédito INTERES_SIMPLE 1200, 10 %, 3 cuotas (M9) | total 1320, cuota 440 | total 1320.00, cuota 440.00 x3 | OK |
| Crédito SISTEMA_FRANCES 1200, 10 % por período, 3 cuotas | cuota = 1200·0,1/(1−1,1^−3) = 482,54 | cuota 482.54 x3, total 1447.62 | OK |
| Crédito INTERES_SIMPLE 1000, 5 %, 2 cuotas | cuota 525 | 525.00 x2 | OK |
| Cobrar cuota 1 del crédito 1 | 201, cuota pagada | 201; la cuota 1 queda `pagada:true` | OK |
| Anular crédito con cobranzas | rechazo | 400 "No se puede anular el crédito 1 porque tiene cobranzas registradas." | OK |
| Anular crédito sin cobranzas (admin) | ok | 204 | OK |
| Cobrar sobre crédito anulado (M1) | rechazo | 400 "El crédito 2 está anulado, no admite cobranzas" | OK |
| Anular crédito con `user` sin permiso (M4) | 403 | 403 "El usuario no tiene permiso para anular creditos" | OK |
| Anular crédito con usuario recién registrado (permisos por defecto, sin NPE/Lazy) | 403 | 403, sin trazas de error en el log | OK |
| Anular cobranza con `user` sin permiso | 403 | 403 "El usuario no tiene permiso para anular cobranzas" | OK |
| Anular crédito con `supervisor` (con permiso) | ok | 204 | OK |
| Anular crédito inexistente | 404 | 404 "Crédito no encontrado con id: '999'" | OK |
| Cuota vencida (M6): crédito con fecha 2025-01-01 | `vencida:true` | cuotas 1 y 2 con `vencida:true`; las de 2026-11 en adelante `false` | OK |
| Dashboard con SUPERVISOR (M10) | 200 | 200 | OK |
| Dashboard con ADMIN (M10) | 200 | 200 | OK |
| Dashboard excluye anulados y financiado = deuda original (M3) | 2 créditos (1 y 4), financiado 1200 + 500 = 1700, cobrado 440 | `cantidadCreditos:2, montoTotalFinanciado:1700.00, montoTotalCobrado:440.00` | OK |
| Dashboard con `user` | 403 | 403 | OK |
| Frontend `npm run build` | solo si existe `node_modules` | `frontend/node_modules` no existe, no se instaló ni se corrió el build | NO PROBADO |

## Observaciones (no son fallas de lo pedido)

- Anular un crédito ya anulado devuelve 204 en vez de rechazo (comportamiento idempotente; el crédito 2 se anuló dos veces sin error). Conviene decidir si es intencional.
- Request sin token a `/api/dashboard/stats` responde 403 y no 401 (con `user` también 403, ese sí es correcto). Es el default de Spring Security sin `AuthenticationEntryPoint` para JWT ausente; el 401 del login sí sale bien.

## Trazas de error

Ninguna: el log del backend no tiene `LazyInitializationException` ni `NullPointerException` en ninguno de los casos. Backend detenido al final (puerto 8080 libre).

## Con M8

Repetido el smoke completo sobre main `61b7f74` (Merge m8-estado-credito), base H2 limpia. Todos los casos de la tabla anterior dan el mismo resultado (401, 404, 405, cuotas simple 440 y francés 482,54, cobro, rechazos, 403 sin permiso, usuario registrado sin NPE, vencidas, dashboard 200 supervisor/admin y 403 user). Se suma lo de M8 y M2:

| Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Respuesta del crédito recién creado | `estado` y `saldo` presentes | `estado:VIGENTE`, `saldo` = totalADevolver (1320.00) | OK |
| Saldo tras pagar 1 de 3 cuotas (1320, cuota 440) | 880 | `saldo:880.00`, `VIGENTE` | OK |
| Anular un crédito ya anulado | rechazo | 400 "El crédito 2 ya está anulado." (antes: 204) | OK |
| Crédito anulado en la respuesta | `ANULADO`, saldo 0 | `anulado:true`, `estado:ANULADO`, `saldo:0` | OK |
| Pagar todas las cuotas (crédito 5, 2 x 500) | `CANCELADO`, saldo 0 | tras la 1ª `VIGENTE` saldo 500.00; tras la 2ª `CANCELADO`, `saldo:0` | OK |
| Cobrar una cuota ya pagada | rechazo | 400 "La cuota 2 del crédito 5 ya fue pagada" | OK |
| Anular crédito cancelado (con cobranzas vigentes) | rechazo | 400 "No se puede anular el crédito 5 porque tiene cobranzas registradas." | OK |
| M2: anular cobranza (admin) y luego el crédito cuya única cobranza fue anulada | permite | cobranza 204; crédito 6 vuelve a `VIGENTE`, saldo 600.00; anular crédito 204 y queda `ANULADO` | OK |
| M2: anular cobranza con `user` sin permiso | 403 | 403 | OK |
| Cuota vencida (crédito 2025-01-01) | `vencida:true` | ambas cuotas `vencida:true`, crédito `VIGENTE` | OK |
| Dashboard (M3/M10) con créditos 1, 4, 5 activos; 2, 3 y 6 anulados | 3 créditos, financiado 1200+500+1000 = 2700, cobrado 440+500+500 = 1440 | `cantidadCreditos:3, montoTotalFinanciado:2700.00, montoTotalCobrado:1440.00` | OK |
| Frontend `npm run build` | solo si existe `node_modules` | no existe, no probado | NO PROBADO |

Pendiente que sigue igual: request sin token responde 403 y no 401. Log del backend sin ninguna excepción; backend detenido (puerto 8080 libre).
