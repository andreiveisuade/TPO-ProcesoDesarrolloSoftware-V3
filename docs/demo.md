# Demo en nvim

`docs/demo.sh` abre nvim con una tab por archivo cambiado: v2 a la izquierda (solo lectura), main a la derecha, en modo diff. El título de cada tab es el ID del cambio y el archivo. Moverse con `gt` / `gT`, salir con `:qa`.

`docs/demo.sh --headless` solo verifica que la sesión se arma sin errores.

## Orden y qué decir

1. **M9 Strategy** (`Credito`, `CalculoDeCuota`, `plan/*`, `TipoPlan`): `Credito` ya no conoce ninguna fórmula, delega en la estrategia. El francés entra como segunda implementación real y revierte la decisión de V2.
2. **M7 Adapter** (`TokenService`, `JwtUtil`, `JwtAuthFilter`, `UsuarioDetails`): la dependencia apunta a una abstracción propia y jjwt queda encerrada en un solo Adapter. `UsuarioDetails` aísla el dominio de Spring Security.
3. **M8 + M2 EstadoCredito y agregado** (`EstadoCredito`, `Credito`, `Cuota`, `CreditoServiceImpl`): el estado deja de ser boolean y el crédito sabe cuánto debe. "Con cobranzas no se anula" usa `Cuota.estaPagada()` y la decisión vuelve al experto.
4. **M4 permisos en backend** (`CreditoController`, `Usuario`, `CreditoServiceImpl`): en MVC el controller identifica y el modelo decide. La vista solo oculta, la regla se valida en el backend.
5. **M5 Swagger/401** (`GlobalExceptionHandler`, `SecurityConfig`, `OpenApiConfig`): un error del cliente ya no se reporta como 500 y el front distingue 401/403/404/405.
6. **Cortos**:
   - **M1** (`Cuota`): no se cobra una cuota de un crédito anulado, la regla vive en `Cuota`.
   - **M3** (`DashboardServiceImpl`): los cuatro números del dashboard reflejan solo lo vigente.
   - **M6** (`Cuota`): `estaVencida()` en la entidad que tiene los datos.
   - **M10** (`SecurityConfig`): el ADMIN ve el dashboard sin ganar los permisos de anulación del supervisor.
