# Comprobación visual de V3

Backend `mvn spring-boot:run` (H2) + front `npm run dev` (Vite 7). `npm run build`: OK, sin warnings ni errores (78 módulos). Usuarios de `DataInitializer`: `admin`, `supervisor`, `user` (password = username). Consola del browser: sin entradas en todo el recorrido.

| Pantalla | Esperado | Visto | Resultado | Captura |
|---|---|---|---|---|
| Login, password incorrecta | Mensaje de error del 401 | Muestra "Bad credentials" (texto crudo de Spring, en inglés) | OK (menor: mensaje sin traducir) | capturas/final/02-login-error.png |
| Login correcto (admin) | Redirige a /clientes con navbar y rol | `/clientes`, "admin (ADMIN)" | OK | capturas/final/03-login-ok.png |
| Clientes: alta | Cliente aparece en la lista | Ana Perez y Beto Gomez, lista (2) | OK | — |
| Créditos: otorgar simple y francés + listado | Plan, tasa rotulada, estado, saldo | "Interés simple 10% total", "Sistema francés 5% mensual", [VIGENTE], saldo. Saldo del simple: $110000.01 antes de cobrar (3 x 36666.67) | FALLA menor (centavo de redondeo en el saldo) | capturas/final/05-creditos-listado.png |
| Cobranzas: cobrar cuota 1 | Cobranza registrada | Fila #1 cuota 1 $36666.67 | OK | — |
| Cuotas: pagada / vencida | "Pagada" y "Vencida" donde corresponde | Cuota 1 Pagada, cuota 2 Vencida, saldo $73333.34 | OK | — |
| Anular crédito con cobranzas | Rechazo visible | "No se puede anular el crédito 1 porque tiene cobranzas registradas." | OK | — |
| Anular crédito sin cobranzas | Crédito anulado, estado actualizado | El botón desaparece pero el rótulo sigue en [VIGENTE] con saldo $70926.3; recién tras re-buscar muestra [ANULADO] y saldo $0 | FALLA (listado no refresca estado/saldo tras anular) | capturas/final/06-anular-refresca.png |
| Usuario `user` sin permiso | Botón Anular oculto | Sin botón Anular | OK | capturas/final/09-user-sin-anular.png |
| `user` forzado (puedeAnularCredito=true en localStorage) | 403 mostrado | "El usuario no tiene permiso para anular creditos" | OK | — |
| Dashboard ADMIN | Números coherentes | 2 clientes, 2 créditos activos, $150000 financiado, $36666.67 cobrado (cuadra con los datos; el crédito 2 anulado no cuenta) | OK (menor: título dice "Modo Supervisor" también para ADMIN) | capturas/final/07-dashboard-admin.png |
| Dashboard SUPERVISOR | Mismos números | Idénticos | OK | capturas/final/08-dashboard-supervisor.png |
| `/swagger-ui.html` + Authorize | Carga, token Bearer aceptado, endpoint protegido responde | 19 operaciones, "Authorized", GET /api/dashboard/stats devuelve 200 | OK | —, — |
