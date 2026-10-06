# T16 — Buenas prácticas de Spring Boot (propuesta, sin cambios de código)

Base: `backend/src/main/java/com/uade/tpejemplo` (abreviado `…/`). Criterio: solo lo necesario para el tamaño del TPO.

Lo que ya está bien y no se toca: inyección por constructor con `@RequiredArgsConstructor` en todo el código (sin `@Autowired` de campo); entidades con `@Getter` + `@NoArgsConstructor(PROTECTED)`, sin `@Data` (el `@Data` está solo en DTOs, correcto); `@EqualsAndHashCode` solo en `…/model/Permisos.java:17`, que es `@Embeddable` (value object: correcto); `@Valid` en todos los `@RequestBody`; 201 en altas (`…/controller/ClienteController.java:31`, `CreditoController.java:34`, `CobranzaController.java:34`, `AuthController.java:31`) y 204 en anulaciones (`CreditoController.java:72`, `CobranzaController.java:54`); CSRF deshabilitado con JWT stateless (`…/config/SecurityConfig.java:46-47`); BCrypt (`SecurityConfig.java:79`); controllers sin `@Transactional`; respuestas por DTO, sin entidades expuestas.

## S1 — Transacciones faltantes en servicios que escriben
- Qué: agregar `@Transactional` a las escrituras y `@Transactional(readOnly = true)` a las lecturas en `ClienteServiceImpl`, `AdminServiceImpl`, `AuthServiceImpl.registrar`, `DashboardServiceImpl` y `CobranzaServiceImpl.anularCobranza`/`listarPorCredito`, como ya hace `CreditoServiceImpl`.
- Evidencia: `…/service/impl/CobranzaServiceImpl.java:47` (`anularCobranza`: lee, muta y guarda sin transacción), `…/service/impl/AdminServiceImpl.java:41,55` (`actualizarPermisos`, `actualizarRol`), `…/service/impl/ClienteServiceImpl.java:22,32,39`, `…/service/impl/DashboardServiceImpl.java:28`. Solo `CreditoServiceImpl.java:29-76` y `CobranzaServiceImpl.java:27` están anotados.
- Por qué: la unidad de trabajo vive en el servicio; hoy la consistencia es dispar entre servicios y la lectura depende de open-in-view.
- Tamaño S. Riesgo bajo. **ANTES DEL 13/10**.

## S2 — `spring.jpa.open-in-view` sin declarar
- Qué: `spring.jpa.open-in-view=false` en `backend/src/main/resources/application.properties`, junto con S1.
- Evidencia: ausente en `application.properties`; Spring Boot lo deja en `true` y loguea el warning al arrancar.
- Por qué: con OSIV un LAZY se resuelve en la vista y tapa servicios sin transacción; apagarlo hace que S1 sea la única fuente de verdad.
- Tamaño S. Riesgo medio: un `LazyInitializationException` destapa un mapeo a DTO fuera de transacción. Correr la app y los tests después. **ANTES DEL 13/10** (solo si S1 entra; si no, DESPUÉS).

## S3 — `jwt.secret` hardcodeado (TPO-009)
- Qué: `jwt.secret=${JWT_SECRET:clave-dev-...}` en `application.properties`.
- Evidencia: `backend/src/main/resources/application.properties` (línea `jwt.secret=clave-super-secreta-...uade2026`), leído en `…/security/JwtUtil.java:18`.
- Por qué: el secreto no debe vivir en el repo; el default deja la app corriendo en dev sin configurar nada.
- Tamaño S. Riesgo nulo. **ANTES DEL 13/10**.

## S4 — `GlobalExceptionHandler` filtra mensajes internos en el 500
- Qué: en `handleGeneral` devolver un mensaje genérico ("Error interno") y loguear `ex` con el logger, en vez de `ex.getMessage()`.
- Evidencia: `…/exception/GlobalExceptionHandler.java:73-76`. No filtra stack trace, pero sí el mensaje crudo (SQL, nombres de clase, NPE) y no lo loguea en ningún lado.
- Por qué: el cliente no debe ver detalles internos y el servidor sí debe registrarlos.
- Tamaño S. Riesgo nulo. **ANTES DEL 13/10**.

## S5 — Warning "Global AuthenticationManager configured with an AuthenticationProvider bean"
- Qué: borrar el `@Bean authenticationProvider()` y el `.authenticationProvider(...)`; con `UserDetailsService` y `PasswordEncoder` como beans Spring arma el `DaoAuthenticationProvider` solo.
- Evidencia: `…/config/SecurityConfig.java:58` y `:64-70`; el `AuthenticationManager` sale de `AuthenticationConfiguration` (`:72-75`), que es lo que dispara el warning.
- Por qué: menos código y sin configuración duplicada del proveedor.
- Tamaño S. Riesgo bajo (probar login). DESPUÉS.

## S6 — Reglas de URL duplicadas con `@PreAuthorize`
- Qué: dejar una sola fuente de autorización por rol: o las reglas de URL o `@PreAuthorize` en la clase.
- Evidencia: `…/config/SecurityConfig.java:52-53` (`/api/admin/**` ADMIN, `/api/supervisor/**` SUPERVISOR) duplican `…/controller/AdminController.java:21` y `…/controller/SupervisorController.java:20`.
- Por qué: si cambian en un lugar y no en el otro, la regla real es la más restrictiva y confunde.
- Tamaño S. Riesgo bajo. DESPUÉS (no rompe nada; se defiende como "defensa en profundidad" si pregunta el profe).

## S7 — Consola H2 abierta e ignorada por Security (TPO-008)
- Qué: dejar la consola solo en dev; si no se quiere perfil, mínimo sacar `/h2-console/**` del `permitAll` (ya está en `web.ignoring()`, es redundante) y documentar que no va a prod.
- Evidencia: `application.properties` (`spring.h2.console.enabled=true`), `…/config/SecurityConfig.java:39` (`web.ignoring()`) y `:50` (`permitAll` redundante).
- Por qué: la consola da acceso total a la base sin autenticación.
- Tamaño S. Riesgo nulo. DESPUÉS (H2 en memoria y sin prod real; un perfil `dev` solo para esto es sobreingeniería ahora).

## S8 — CORS habilitado sin configuración
- Qué: o borrar `.cors(Customizer.withDefaults())` (el front pasa por el proxy de Vite, `frontend/vite.config.js:8`) o declarar un `CorsConfigurationSource` con el origen del front.
- Evidencia: `…/config/SecurityConfig.java:45`; no hay `CorsConfigurationSource` ni `WebMvcConfigurer` en el backend.
- Por qué: hoy la línea no hace nada y sugiere que CORS está resuelto.
- Tamaño S. Riesgo nulo. DESPUÉS.

## S9 — `ddl-auto=update` y `show-sql=true`
- Qué: `create-drop` (H2 en memoria, más honesto) y `show-sql=false` o vía logger.
- Evidencia: `application.properties` (bloque JPA).
- Por qué: `update` no tiene sentido con base en memoria; `show-sql` ensucia la consola en la demo en vivo.
- Tamaño S. Riesgo nulo. DESPUÉS.

## S10 — Paquete `com.uade.tpejemplo` (TPO-014)
- Qué: renombrar a algo como `com.uade.prestamos` (también `artifactId` en `backend/pom.xml` y `TpEjemploApplication`).
- Por qué: el nombre de plantilla no comunica el dominio.
- Tamaño M (toca todos los archivos, diff ruidoso que tapa los cambios reales de la iteración). **NO HACER antes del 13/10**; evaluar para la entrega final del 17/11.
