# Pendientes del backend: I-1, BS3, BS4, BS6

## I-1. Cobros simultaneos de la misma cuota (8888df6)
- Problema: `CobranzaServiceImpl.registrar` leia la cuota con `CuotaRepository.buscarPorCreditoYNumero` (con `LEFT JOIN FETCH c.cobranzas`), decidia en `Cuota.registrarCobranza` que estaba impaga y recien despues insertaba. Dos requests a la vez veian la cuota impaga y las dos cobraban.
- Cambio: `@Lock(PESSIMISTIC_WRITE)` en `backend/src/main/java/com/uade/tpejemplo/repository/CuotaRepository.java` y fuera el `JOIN FETCH` de esa query. Test: `backend/src/test/java/com/uade/tpejemplo/service/CobranzaConcurrenteTest.java` (20 hilos cobrando la misma cuota, espera 1 vigente).
- Por que: con el join, Hibernate emite `for update` pero H2 lee las cobranzas con la foto previa al bloqueo y sigue duplicando. Sin el join se cargan lazy despues del lock y ven la cobranza del otro request. Sin el arreglo el test falla (expected 1, was 10); con el arreglo pasa.
- Consecuencias: cada cobro toma un lock de fila sobre la cuota (se serializan solo cobros de la misma cuota). Las cobranzas de esa cuota se cargan con un select extra. M-3 (anular credito contra cobrar) sigue abierto.

## Smells
- BS1 ya no aplica: `AdminService.listarTodos` no existe en main.
- BS3 (`5246f27`): `IUsuario.puedeAnularCredito()` / `puedeAnularCobranza()`, implementados en `model/Usuario.java`; `CreditoServiceImpl.anularCredito` y `CobranzaServiceImpl.anularCobranza` preguntan al usuario en vez de navegar `getPermisos()`. Por que: Expert / Tell don't ask, la regla la sabe el usuario.
- BS4 (`7c6dd63`): `rol` pasa de `String` a `Rol` en `dto/response/UsuarioResponse.java` y `AuthResponse.java`. El JSON no cambia (Jackson serializa el enum por nombre). Esos dos DTO tambien usan `usuario.puedeAnular*()` de BS3.
- BS6 (`f96f53a`): `SupervisorController.obtenerUsuarios` pasa a `listarUsuarios`, igual que `AdminController`. `listarTodos` ya cayo con BS1; `JwtUtil` no se renombra (no se toco por otra razon).
