# T9 — API: mapa, Swagger y CRUDs faltantes (propuesta, sin código)

Base: `main`, Spring Boot 3.4.3, JWT stateless. Errores via `GlobalExceptionHandler`: `ResourceNotFoundException`→404, `BusinessException`→400, validación→400, `AuthenticationException`→401, `AccessDeniedException`→403, `NoResourceFoundException`→404, método no soportado→405, resto→500. Todos con cuerpo `ErrorResponse`.

## 1. Mapa actual

Roles: "auth" = cualquier usuario autenticado (`anyRequest().authenticated()`). Sin token → 401 en todo salvo `/api/auth/**`.

| Método | Ruta | Controller#método | Request | Response | Roles/permisos | Códigos | Front |
|---|---|---|---|---|---|---|---|
| POST | /api/auth/register | AuthController#register | RegisterRequest | AuthResponse | público | 201, 400 (validación, usuario ya existe) | sí (`auth.js`) |
| POST | /api/auth/login | AuthController#login | LoginRequest | AuthResponse | público | 200, 400, 401 | sí |
| POST | /api/clientes | ClienteController#crear | ClienteRequest | ClienteResponse | auth | 201, 400 (validación, DNI duplicado), 401 | sí |
| GET | /api/clientes/{dni} | ClienteController#buscarPorDni | — | ClienteResponse | auth | 200, 401, 404 | sí |
| GET | /api/clientes | ClienteController#listarTodos | — | List\<ClienteResponse> | auth | 200, 401 | sí |
| POST | /api/creditos | CreditoController#crear | CreditoRequest | CreditoResponse | auth | 201, 400, 401, 404 (cliente) | sí |
| GET | /api/creditos/{id} | CreditoController#buscarPorId | — | CreditoResponse | auth | 200, 401, 404 | sí |
| GET | /api/creditos/cliente/{dni} | CreditoController#listarPorCliente | — | List\<CreditoResponse> | auth | 200, 401, 404 | sí |
| DELETE | /api/creditos/anular/{id} | CreditoController#anularCredito | — | 204 | auth + `puedeAnularCredito` (en service) | 204, 400 (tiene cobranzas), 401, 403, 404 | sí |
| POST | /api/cobranzas | CobranzaController#registrar | CobranzaRequest | CobranzaResponse | auth | 201, 400 (crédito anulado, cuota pagada, importe distinto, validación), 401, 404 (cuota) | sí |
| GET | /api/cobranzas/credito/{idCredito} | CobranzaController#listarPorCredito | — | List\<CobranzaResponse> | auth | 200, 401 | sí |
| DELETE | /api/cobranzas/{id} | CobranzaController#anularCobranza | — | 204 | auth + `puedeAnularCobranza` (en service) | 204, 400 (no es del día), 401, 403, 404 | sí |
| GET | /api/dashboard/stats | DashboardController#obtenerEstadisticas | — | DashboardStatsResponse | SUPERVISOR, ADMIN | 200, 401, 403 | sí (`dashboardSlice`) |
| GET | /api/admin/usuarios | AdminController#listarUsuarios | — | List\<UsuarioResponse> | ADMIN (filter + @PreAuthorize) | 200, 401, 403 | sí (`permisosSlice`) |
| PUT | /api/admin/usuarios/{id}/permisos | AdminController#actualizarPermisos | PermisosRequest | UsuarioResponse | ADMIN | 200, 401, 403, 404 | **no** |
| PUT | /api/admin/usuarios/{id}/rol | AdminController#actualizarRol | RolRequest | UsuarioResponse | ADMIN | 200, 400 (admin), 401, 403, 404 | sí (`admin.js`) |
| GET | /api/supervisor/usuarios | SupervisorController#obtenerUsuarios | — | List\<UsuarioResponse> | SUPERVISOR | 200, 401, 403 | sí |
| PUT | /api/supervisor/usuarios/{id}/permisos-anulacion | SupervisorController#actualizarPermisosAnulacion | PermisosRequest | UsuarioResponse | SUPERVISOR | 200, 401, 403, 404 | sí |

Observaciones:
- `PermisosRequest` y `RolRequest` no llevan `@Valid` en el controller; `RolRequest.rol` null llega al service.
- `AdminController#actualizarPermisos` duplica lo del supervisor y el front no lo usa.
- `DELETE /creditos/anular/{id}` mezcla verbo en la ruta con DELETE para algo que no borra (el crédito queda `anulado=true`). Igual con `DELETE /cobranzas/{id}`. Ver punto 3.
- `GET /cobranzas/credito/{id}` con crédito inexistente devuelve `[]`, no 404.

## 2. Swagger / OpenAPI

springdoc **no está** en el pom. Para Spring Boot 3.4.x la línea compatible es `springdoc-openapi-starter-webmvc-ui` **2.8.x** (2.7 apuntaba a Boot 3.4 también; 2.8 es la última de esa rama). Mínimo:

1. `pom.xml`:
   ```xml
   <dependency>
       <groupId>org.springdoc</groupId>
       <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
       <version>2.8.6</version>
   </dependency>
   ```
2. `SecurityConfig`: agregar a los `permitAll` `"/swagger-ui.html", "/swagger-ui/**", "/v3/api-docs/**"`.
3. `config/OpenApiConfig.java` (nuevo, ~20 líneas): `@OpenAPIDefinition(info=@Info(title="Dashboard de préstamos", version="v3"), security=@SecurityRequirement(name="bearerAuth"))` + `@SecurityScheme(name="bearerAuth", type=HTTP, scheme="bearer", bearerFormat="JWT")`. Eso da el botón Authorize. En `AuthController` poner `@SecurityRequirements()` vacío para que login/register salgan sin candado.
4. `@Tag(name=...)` por controller (7).
5. `@Operation(summary=...)` + `@ApiResponse` por endpoint con los códigos de la tabla. Para no repetir: `@ApiResponse(responseCode="400", content=@Content(schema=@Schema(implementation=ErrorResponse.class)))` etc. Se puede definir 401/403/500 una sola vez con un `OpenApiCustomizer` que los agregue a todas las operaciones con seguridad, y dejar en cada método solo los propios (201/204/400/404).
6. DTOs: no anotar. springdoc lee las anotaciones de Bean Validation (`@NotBlank`, `@Min`, ...) solo.

Tamaño: pom +5, SecurityConfig +1 línea, 1 archivo nuevo, ~18 endpoints × 3-5 líneas de anotación. No toca lógica.

## 3. CRUDs faltantes

| Entidad | Operación faltante | Veredicto | Motivo | Archivos / tamaño |
|---|---|---|---|---|
| Cliente | PUT /clientes/{dni} (editar nombre) | DUDOSA | Corregir un nombre mal cargado es un hueco real de operación, pero ningún caso de uso ni ticket lo pide. Solo nombre: el DNI es la identidad. | ClienteController, ClienteService(+Impl), DTO nuevo o reusar ClienteRequest. ~30 líneas |
| Cliente | DELETE /clientes/{dni} | NO | Un cliente con créditos no se puede borrar sin romper historial; sin créditos el caso no existe en el dominio. | — |
| Credito | GET /creditos (listado general) | RECOMENDADA | Hoy solo se lista por cliente; el supervisor no puede ver la cartera sin entrar cliente por cliente. Hueco real del dashboard. | CreditoController, CreditoService(+Impl), CreditoRepository. ~15 líneas. **Choca con M8** |
| Credito | PUT /creditos/{id} | NO | Un crédito no se edita: cambiar monto/tasa invalida cuotas ya generadas. Se anula y se crea otro. | — |
| Credito | DELETE real | NO | Se anula (ya existe). | — |
| Credito | Anular como `POST /creditos/{id}/anulacion` en vez de `DELETE /creditos/anular/{id}` | DUDOSA | Más fiel al dominio (no borra) y REST. Cambia contrato: hay que tocar `creditos.js`. Defendible en MVC, pero es cosmético. | CreditoController, `frontend/src/api/creditos.js`. ~4 líneas. **Choca con M8** si M8 toca el controller |
| Cuota | Cualquier CRUD propio | NO | La cuota nace con el crédito y se paga vía cobranza; ya viene dentro de `CreditoResponse`. | — |
| Cuota | GET /creditos/{id}/cuotas | NO | Redundante con `CreditoResponse.cuotas`. | — |
| Cobranza | GET /cobranzas/{id} | DUDOSA | Nadie la consume; solo útil para Swagger/demos. | ~8 líneas |
| Cobranza | PUT / DELETE real | NO | Se anula (ya existe, con regla del día). | — |
| Cobranza | Anular como `POST /cobranzas/{id}/anulacion` | DUDOSA | Mismo argumento que crédito. | CobranzaController, `cobranzas.js`. ~4 líneas |
| Usuario | GET /usuarios/me (o rol/permisos en AuthResponse) | RECOMENDADA si el front hoy decodifica el JWT o guarda permisos del login | El front decide qué botones mostrar; si los permisos cambian después del login quedan viejos hasta re-loguear. Verificar antes cómo lo resuelve hoy el front. | Controller nuevo o AuthController, ~15 líneas |
| Usuario | DELETE / desactivar usuario | DUDOSA | Hueco operativo real (dar de baja un cobrador) pero no hay caso de uso ni campo `activo`. Requiere cambio de modelo. | Usuario, AdminService, Admin controller, JwtAuthFilter. ~40 líneas |
| Permisos | PUT /admin/usuarios/{id}/permisos | NO agregar — **quitar o justificar** | Duplicado del de supervisor y sin uso en el front. | AdminController, −4 líneas |
| Permisos/Rol | `@Valid` en PermisosRequest/RolRequest + `@NotNull` en `rol` | RECOMENDADA | Hoy un body `{}` en `/rol` llega con `rol=null` al service (posible 500). | 2 DTOs + 3 controllers, ~6 líneas |

## 4. Riesgos de conflicto con M8

M8 toca `Credito`, `CreditoServiceImpl`, `CuotaRepository`, `CreditoResponse`, `Creditos.jsx`.

- **Swagger en `CreditoController`**: no está en la lista de M8, pero si M8 agrega o cambia firmas de endpoints, las anotaciones de Swagger se pisan. Hacer Swagger **después** del merge de M8, o anotar primero los otros 6 controllers y Credito al final.
- **GET /creditos**: toca `CreditoService`/`CreditoServiceImpl` → conflicto directo. Esperar M8.
- **Anulación como POST**: toca `CreditoController` y el front de créditos (`creditos.js`, y si M8 cambia `Creditos.jsx` la llamada vive ahí). Esperar M8.
- **`CreditoResponse`**: no anotarlo con `@Schema` (punto 2.6), así no hay conflicto.
- Cliente, Cobranza, Admin, Supervisor, Auth, Dashboard, SecurityConfig, pom y `OpenApiConfig`: sin cruce con M8, se pueden hacer ya.
