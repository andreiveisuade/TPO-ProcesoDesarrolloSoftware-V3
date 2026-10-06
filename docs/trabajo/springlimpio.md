# springlimpio — S5, S6 y BS2

Rama `spring-limpio` (desde `main@8eb2106`).

## S5 — Warning de AuthenticationManager
- Problema: `backend/src/main/java/com/uade/tpejemplo/config/SecurityConfig.java` declaraba un `@Bean AuthenticationProvider` (un `DaoAuthenticationProvider` armado a mano) y además lo registraba con `.authenticationProvider(...)`. Al arrancar, Spring avisaba: "Global AuthenticationManager configured with an AuthenticationProvider bean. UserDetailsService beans will not be used...".
- Cambio: se borró el bean `authenticationProvider()`, la línea `.authenticationProvider(...)` y el campo `userDetailsService`. Con `UserDetailsService` (`security/UserDetailsServiceImpl.java`) y `PasswordEncoder` como beans, Spring arma solo el `DaoAuthenticationProvider`.
- Por qué: menos código y una sola configuración del proveedor.
- Consecuencias: en el arranque queda solo el INFO "configured with UserDetailsService bean with name userDetailsServiceImpl". Login y los 26 tests igual.
- Commit: `013c07a`.

## S6 — Una sola forma de controlar roles
- Pendiente: el cambio (sacar `@PreAuthorize` de `controller/AdminController.java` y `controller/SupervisorController.java` y `@EnableMethodSecurity` de `SecurityConfig`, dejando las reglas de URL) lo bloqueó el clasificador de permisos de Claude Code. No se aplicó.
- Elección propuesta: las reglas de URL en `SecurityConfig`, porque ya cubren las tres zonas (`/api/admin/**`, `/api/supervisor/**`, `/api/dashboard/**`, este último sin anotación) en un solo lugar; con `@PreAuthorize` habría que anotar también el dashboard. La regla de anulación sigue en `Permisos` (Information Expert).

## BS2 — ErrorResponse duplicado
- Problema: `exception/GlobalExceptionHandler.java` repetía nueve veces `ResponseEntity.status(X).body(new ErrorResponse(n, ...))`, con el número escrito a mano al lado del `HttpStatus`.
- Cambio: método privado `error(HttpStatus, String, List<String>)` que saca el código de `status.value()`; cada handler llama a ese.
- Por qué: el código numérico ya no puede desalinearse del `HttpStatus`.
- Consecuencias: el JSON de error no cambia.
- Commit: `0df40d1`.

## Verificación
- `mvn test`: 26 tests, 0 fallas.
- curl en 8099 (admin, supervisor, user, anónimo sobre admin, supervisor, dashboard y `/api/auth/me`): 401, 403 y 200 idénticos antes y después.
