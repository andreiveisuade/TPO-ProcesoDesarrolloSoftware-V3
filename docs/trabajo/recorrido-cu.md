# Recorrido de casos de uso por la UI (2026-10-06)

Front en `localhost:5173` manejado con `cmux browser`, back en 8080. Cada paso se comparó con `curl` al mismo recurso. Usuarios: semilla `user`, `supervisor`, `admin`, más `rec1` registrado desde la UI. Capturas en `docs/trabajo/capturas/recorrido/`. Datos que quedaron en la base: cliente 40111333 con los créditos 4 (cobranza 3 anulada) y 5 (anulado), y el usuario `rec1`.

Todo el recorrido salió del front, salvo la preparación de H4 (el permiso a `rec1` se dio por API) y el confirm del navegador, que se reemplazó por `window.confirm=()=>true` porque el diálogo nativo no se puede manejar desde cmux.

## Tabla

| CU | Flujo recorrido | Resultado | Captura |
|---|---|---|---|
| UC01 Registrarse | Contraseña corta (error), usuario repetido (error), registro válido de `rec1` y entrada a `/clientes` | OK | `CU-01-pass-corta.png`, `CU-01-usuario-repetido.png`, `CU-01-registro-ok.png` |
| UC02 Iniciar sesión | `user` con contraseña mala ("Bad credentials"), `user`, `supervisor` y `admin` correctos | OK | `CU-02-login-form.png`, `CU-02-login-error.png`, `CU-02-login-ok-user.png`, `CU-02-login-ok-supervisor.png`, `CU-02-login-ok-admin.png` |
| UC04 Registrar cliente | Alta de 40111333 y alta con DNI repetido (mensaje del back) | OK | `CU-04-alta-ok.png`, `CU-04-dni-repetido.png` |
| UC05 Listar clientes | Tabla al entrar, contador y filas igual que `GET /api/clientes` | OK | `CU-04-alta-ok.png` |
| UC06 Buscar cliente por DNI | No tiene pantalla | NO APLICA (sin UI) | — |
| UC07 Otorgar crédito | Interés simple 1200 al 10 % x3 y sistema francés 1200 al 5 % x3; cliente inexistente (404 visible) | OK | `CU-07-credito-creado-listado.png`, `CU-07-cliente-inexistente.png` |
| UC08 Generar plan | Cuotas 1..3 con vencimiento mensual, igual que la API | OK | `CU-07-credito-creado-listado.png` |
| UC09 Consultar crédito | No tiene pantalla | NO APLICA (sin UI) | — |
| UC10 Listar créditos del cliente | Búsqueda por DNI (estado, saldo, plan, cuotas) y DNI inexistente | OK (con O1, O2) | `CU-07-credito-creado-listado.png`, `CU-10-cliente-inexistente.png` |
| UC11 Anular crédito | `user` sin botón; `supervisor` ve el botón solo en el crédito sin cobranzas; anula el 5 y queda ANULADO con saldo 0. El error de "con cobranzas" no se alcanza por UI: el botón no se ofrece | OK | `CU-11-user-sin-boton-anular.png`, `CU-11-supervisor-con-boton-anular.png`, `CU-11-anulado.png` |
| UC13 Registrar cobranza | Cuota 1 del crédito 4 (OK), misma cuota otra vez ("ya fue pagada"), importe 100 ("no coincide") | OK (con O3) | `CU-13-cobranza-ok.png`, `CU-13-cuota-ya-pagada.png`, `CU-13-importe-distinto.png` |
| UC14 Listar cobranzas | Búsqueda por crédito 4: ID, cuota, importe y fecha igual que la API | OK | `CU-14-listado.png` |
| UC15 Anular cobranza | `supervisor` anula la cobranza 3: queda `[ANULADA]` sin botón y la cuota vuelve a impaga (saldo 1320). `user` sin permiso no ve el botón | OK | `CU-15-antes-anular.png`, `CU-15-anulada.png` |
| UC16 Ver estadísticas | `supervisor` y `admin` ven las 4 tarjetas iguales a `/api/dashboard/stats`; `rec1` (USER) ve "No tienes permisos para ver el dashboard." | OK | `CU-16-dashboard-supervisor.png`, `CU-16-dashboard-admin.png`, `CU-16-user-denegado.png` |
| UC18 Listar usuarios | Gestor del supervisor y panel del admin muestran `supervisor`/`user` sin ADMIN, igual que la API; `rec1` en `/admin/roles` vuelve a `/creditos` | OK (con O5) | `CU-18-gestor-permisos.png`, `CU-18-user-denegado.png` |
| UC19 Asignar permisos | Se tilda "anular crédito" de `user`: la API lo confirma; se destilda | OK (con H4) | `CU-19-permiso-otorgado.png`, `CU-19-H4-sin-boton-tras-permiso.png` |
| UC20 Cambiar rol | Admin pasa `user` a SUPERVISOR (la API confirma) y lo devuelve a USER | OK | `CU-20-panel-admin.png`, `CU-20-rol-cambiado.png` |

Resultado: 15 de 15 casos con pantalla OK; UC06 y UC09 no tienen pantalla. No hubo FALLAS. Los errores del back que la UI no puede provocar (anular crédito con cobranzas, importes de otros días) no se recorrieron.

## Representación back ↔ front

Todo lo comparado coincidió: importes, total a devolver, cuota, saldo, plan y tasa, fechas de vencimiento, estado de cada cuota, estadísticas del dashboard y permisos/roles. Los mensajes de error salen tal cual del back.

- **H4 (confirmada)**. Pantalla: Créditos como `rec1`. Se ve: sin botón Anular aunque `rec1` ya tiene `puedeAnularCredito=true` en la API y el crédito 4 tiene `puedeAnularse=true`. Debería verse: el botón, o al menos refrescar el usuario al cargar la pantalla. Archivo: `frontend/src/store/slices/authSlice.js` (usuario sale de `localStorage`) y `frontend/src/pages/Creditos.jsx:114`.

## Observaciones de UI

- **O1. Error de búsqueda en el card equivocado.** Pantalla: Créditos, buscar DNI inexistente. Se ve: "Cliente no encontrado con DNI" dentro del card "Nuevo crédito" (el error es el mismo del alta) y debajo "Créditos del cliente (0) Sin créditos.". Debería verse: el error en el card de búsqueda y no listar un cliente que no existe. Archivo: `frontend/src/pages/Creditos.jsx` (un único `error` del slice para búsqueda y alta; `buscado` queda en true).
- **O2. Sin confirmación al crear.** Pantalla: Créditos y Cobranzas tras un alta correcta. Se ve: el formulario se vacía y no aparece nada más; en Créditos el listado no se actualiza si el DNI buscado es otro. Debería verse: mensaje de éxito (crédito #N creado, cobranza registrada). Archivos: `frontend/src/pages/Creditos.jsx`, `frontend/src/pages/Cobranzas.jsx`.
- **O3. Mensajes y formatos inconsistentes.** Pantalla: Cobranzas, importe distinto. Se ve: "El importe 100 no coincide con el de la cuota, 440.00" (punto decimal del back, sin signo) mientras la tabla muestra `$ 440,00`. Pantalla: Registro, contraseña corta: "password: La contraseña debe tener al menos 6 caracteres" con el nombre técnico del campo. Debería verse: el formato del resto de la UI y sin prefijo técnico. Archivos: mensajes en el back; `frontend/src/pages/Register.jsx` y `Cobranzas.jsx` para mostrarlos.
- **O4. Dashboard sin separación del título.** Pantalla: `/estadisticas`. Se ve: el título "Panel de Estadísticas (Modo Admin)" centrado pegado al borde superior de las tarjetas, mientras las otras pantallas tienen el título a la izquierda con margen. Debería verse: mismo margen y alineación que el resto. Archivo: `frontend/src/pages/Dashboard.jsx` (`styles.container`).
- **O5. Redirección silenciosa y alert nativo.** Pantalla: `/admin/roles` como USER: vuelve a `/creditos` sin mensaje (a diferencia del dashboard, que sí avisa). Pantalla: anular crédito/cobranza: usa `window.confirm` y `alert("Error: …")` nativos, fuera del dark theme. Archivos: `frontend/src/App.jsx` (ruteo), `frontend/src/pages/Creditos.jsx:handleAnular`, `frontend/src/pages/Cobranzas.jsx:37`.
- **O6. Cobranzas se tipea a mano.** Pantalla: Cobranzas. Se ve: id de crédito, número de cuota e importe a mano, y no hay lista de cuotas (ya señalado en UC13). Debería verse: elegir la cuota desde el crédito. Archivo: `frontend/src/pages/Cobranzas.jsx`.
