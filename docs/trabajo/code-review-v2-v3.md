# Code review V2 → V3

Rango revisado: `v2..main` (main en `fd5529d`, 317 archivos). Skill `code-review` nivel `high`, todos los hallazgos, solo lectura. Excluye lo ya resuelto en `auditoria-final.md` (I1–I6, M1–M20). Son candidatos sin pasada de verificación.

Resumen: **3 altas, 5 medias, 4 bajas**.

## Alta

### A1. Recarga post-anulación usa el input vivo, no lo buscado
`frontend/src/pages/Creditos.jsx:70` (también `frontend/src/pages/Cobranzas.jsx:40` y `:83`)

Tras anular, la lista se recarga con el `dni` que esté escrito en el buscador en ese momento. El fix de I4 sacó el `anulado = true` del reducer, así que sin esa recarga la ficha queda vieja.

**Falla:** buscás el DNI A, escribís B sin apretar Buscar y anulás un crédito de A. `fetchCreditosPorCliente('B')` muestra los créditos de B bajo "Créditos del cliente". Con el input vacío no recarga: el crédito sigue VIGENTE con el botón Anular, y el segundo clic da 400. En Cobranzas, buscás el crédito 5, tipeás 7 y cobrás una cuota del 5: la lista no se recarga y el título dice "crédito #7". Es la misma clase de bug que I4 y puede aparecer en la demo.

### A2. `refrescarUsuario.fulfilled` pisa la sesión sin validarla
`frontend/src/store/slices/authSlice.js:59`

Pisa `state.user` y `localStorage.authUser` sin chequear que la sesión siga activa ni que sea del mismo usuario.

**Falla:** sale un GET /auth/me, hacés logout antes de que vuelva y la respuesta llega después: `user` se recrea con `token: undefined` y se persiste. Al recargar, la UI se ve logueada pero todo da 401, y `rejected` no desloguea. Si B se loguea mientras vuelve el /me de A, B queda con el rol y los permisos de A en el front.

### A3. Alta de cliente con check-then-insert y id asignado
`backend/src/main/java/com/uade/tpejemplo/service/impl/ClienteServiceImpl.java:26` (mismo patrón en `AuthServiceImpl.registrar:34`)

`existsById` + `save` sin lock. Como el id es el DNI, `save` hace `merge` y no `persist`.

**Falla:** dos altas simultáneas con el mismo DNI. Si T1 commitea antes del SELECT del merge de T2, T2 hace UPDATE y responde 201: pisa en silencio el cliente de T1. Si no, la PK duplicada da un 500. En register, un username repetido choca con el unique y también da 500.

## Media

### M1. `Cuota.estaVencida` ignora el crédito anulado
`backend/src/main/java/com/uade/tpejemplo/model/Cuota.java:70`

`DashboardServiceImpl.java:54` filtra `!credito.isAnulado()` aparte: el parche está en quien llama y no en el Information Expert.

**Falla:** un crédito anulado muestra el badge ANULADO con saldo $0, pero las cuotas pasadas siguen en rojo como "Vencida" (`CuotaResponse.vencida = true`).

### M2. Timeout del lock pesimista termina en 500
`backend/src/main/java/com/uade/tpejemplo/exception/GlobalExceptionHandler.java:84`

El lock sobre el crédito (`CreditoRepository.java:36`) puede tirar `PessimisticLockingFailureException` o un timeout de H2. Ninguno tiene handler, así que caen en `handleGeneral`.

**Falla:** un cobro o una anulación que espera más que el lock timeout responde 500 "Error interno" con stack trace, cuando es un conflicto que debería ser 409.

### M3. `AnulacionConcurrenteTest` pasa aunque fallen las dos operaciones
`backend/src/test/java/com/uade/tpejemplo/service/AnulacionConcurrenteTest.java:69`

Se traga las excepciones de los dos hilos y solo verifica que no se den "anulado y cobranza vigente" a la vez.

**Falla:** si anular y cobrar fallan las dos (deadlock, timeout o una regresión), el test pasa. Falta comprobar que exactamente una salió bien (`anulado ^ hayCobranzaVigente`).

### M4. El error de anulación aparece en el formulario de alta
`frontend/src/pages/Creditos.jsx:171` (también `frontend/src/pages/Cobranzas.jsx:71`)

`anularCreditoThunk.rejected` setea el `error` compartido del slice, y ese error se muestra en el card "Nuevo crédito".

**Falla:** anulás un crédito con cobranzas: sale el alert y además el mismo mensaje queda fijo en rojo debajo del formulario de alta.

### M5. El alert asume que el error es un string
`frontend/src/pages/Creditos.jsx:73`

El `getCredito` de `:71` tira un `Error` dentro del mismo try que la anulación.

**Falla:** la anulación sale bien y falla el refresco (por ejemplo, token vencido): el alert dice "Error: Error: …" y da a entender que la anulación falló.

## Baja

### B1. DNI en la URL sin `encodeURIComponent`
`frontend/src/api/clientes.js:4` (también `frontend/src/api/creditos.js:3`)

El backend acepta cualquier string de hasta 15 caracteres como DNI.

**Falla:** con un DNI como "AB/12" el cliente no se puede buscar (404 en inglés), y con "12%3" da un 400 de Tomcat sin JSON.

### B2. Lock de la cuota redundante
`backend/src/main/java/com/uade/tpejemplo/repository/CuotaRepository.java:34`

Desde I1, el lock del crédito ya serializa todos los cobros del crédito, así que el `PESSIMISTIC_WRITE` sobre la cuota sobra.

**Falla:** cada cobro toma dos locks, y el comentario describe un mecanismo que ya no es el que sostiene la regla. En la defensa confunde cuál lock evita el doble cobro.

### B3. Doble lectura del crédito al anular
`backend/src/main/java/com/uade/tpejemplo/service/impl/CreditoServiceImpl.java:85` (también `CobranzaServiceImpl.java:33`)

Se descarta el resultado de `bloquearPorId(id)` y `buscarCredito(id)` vuelve a leer la misma fila.

**Falla:** hace tres consultas cuando alcanzan dos, y no queda claro cuál de las dos lecturas es la que cuenta.

### B4. GestorPermisos y PanelAdmin no usan `Aviso`
`frontend/src/pages/GestorPermisos.jsx:30` (también `frontend/src/pages/PanelAdmin.jsx:25`)

Arman el error con `styles.error` propio en vez del componente `Aviso`.

**Falla:** quedan tres estilos de error en el front (Aviso, div rojo y alert). M15 solo cubrió `Clientes.jsx`.
