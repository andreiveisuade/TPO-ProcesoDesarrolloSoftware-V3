# API — contrato documentado con Swagger

Rama `api-swagger`. Swagger UI en `/swagger-ui.html`, especificación en `/v3/api-docs`. Botón Authorize: pegar el token de `/api/auth/login`.

## Mapa de endpoints

"auth" = cualquier usuario con token válido. Sin token: 401 en todo salvo `/api/auth/**` y Swagger.

| Método | Ruta | Controller#método | Request | Response | Roles / permisos | Códigos |
|---|---|---|---|---|---|---|
| POST | /api/auth/register | AuthController#register | RegisterRequest | AuthResponse | público | 201, 400 |
| POST | /api/auth/login | AuthController#login | LoginRequest | AuthResponse | público | 200, 400, 401 |
| POST | /api/clientes | ClienteController#crear | ClienteRequest | ClienteResponse | auth | 201, 400, 401 |
| GET | /api/clientes/{dni} | ClienteController#buscarPorDni | — | ClienteResponse | auth | 200, 401, 404 |
| GET | /api/clientes | ClienteController#listarTodos | — | List\<ClienteResponse> | auth | 200, 401 |
| POST | /api/creditos | CreditoController#crear | CreditoRequest | CreditoResponse | auth | 201, 400, 401, 404 |
| GET | /api/creditos | CreditoController#listarTodos | — | List\<CreditoResponse> | auth | 200, 401 |
| GET | /api/creditos/{id} | CreditoController#buscarPorId | — | CreditoResponse | auth | 200, 401, 404 |
| GET | /api/creditos/cliente/{dni} | CreditoController#listarPorCliente | — | List\<CreditoResponse> | auth | 200, 401, 404 |
| DELETE | /api/creditos/anular/{id} | CreditoController#anularCredito | — | — | auth + `puedeAnularCredito` | 204, 400, 401, 403, 404 |
| POST | /api/cobranzas | CobranzaController#registrar | CobranzaRequest | CobranzaResponse | auth | 201, 400, 401, 404 |
| GET | /api/cobranzas/credito/{idCredito} | CobranzaController#listarPorCredito | — | List\<CobranzaResponse> | auth | 200, 401 |
| DELETE | /api/cobranzas/{id} | CobranzaController#anularCobranza | — | — | auth + `puedeAnularCobranza` | 204, 400, 401, 403, 404 |
| GET | /api/dashboard/stats | DashboardController#obtenerEstadisticas | — | DashboardStatsResponse | SUPERVISOR, ADMIN | 200, 401, 403 |
| GET | /api/admin/usuarios | AdminController#listarUsuarios | — | List\<UsuarioResponse> | ADMIN | 200, 401, 403 |
| PUT | /api/admin/usuarios/{id}/permisos | AdminController#actualizarPermisos | PermisosRequest | UsuarioResponse | ADMIN | 200, 400, 401, 403, 404 |
| PUT | /api/admin/usuarios/{id}/rol | AdminController#actualizarRol | RolRequest | UsuarioResponse | ADMIN | 200, 400, 401, 403, 404 |
| GET | /api/supervisor/usuarios | SupervisorController#obtenerUsuarios | — | List\<UsuarioResponse> | SUPERVISOR | 200, 401, 403 |
| PUT | /api/supervisor/usuarios/{id}/permisos-anulacion | SupervisorController#actualizarPermisosAnulacion | PermisosRequest | UsuarioResponse | SUPERVISOR | 200, 400, 401, 403, 404 |

## Patrón
MVC: el controlador es la frontera HTTP del sistema. Traduce los errores del modelo y de la seguridad a códigos HTTP, y su contrato (rutas, cuerpos y códigos) queda publicado para quien consume la API.

## Problema
1. Sin token, Spring Security usaba su entry point por defecto y respondía **403**, igual que un usuario autenticado sin permiso. El front no podía distinguir "sesión vencida" de "no te corresponde".
2. `RolRequest` y `PermisosRequest` entraban sin validar:
   ```java
   public UsuarioResponse actualizarRol(@PathVariable Long id, @RequestBody RolRequest request)
   ```
   Con un body `{}` el `rol` llegaba `null` al service.
3. El contrato vivía solo en el código: para saber qué devolvía cada endpoint había que leer controller, service y `GlobalExceptionHandler`.
4. No existía un listado general de créditos; solo por cliente.

## Solución
1. `SecurityConfig#filterChain`:
   ```java
   .exceptionHandling(e -> e.authenticationEntryPoint(new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED)))
   ```
2. `@Valid @RequestBody` en `AdminController` y `SupervisorController`, y `@NotNull` en `RolRequest.rol`. Un body `{}` en `/rol` da 400 por `MethodArgumentNotValidException`, que ya mapeaba `GlobalExceptionHandler`.
3. springdoc-openapi 2.8.6 (línea compatible con Spring Boot 3.4). `OpenApiConfig` declara el esquema `bearerAuth` (HTTP bearer JWT) como requisito global; `AuthController` lo anula con `@SecurityRequirements`. Cada controller lleva `@Tag` y cada endpoint `@Operation` + `@ApiResponse` con los códigos que realmente produce:
   ```java
   @Operation(summary = "Anular crédito")
   @ApiResponse(responseCode = "204", description = "Sin contenido")
   @ApiResponse(responseCode = "400", description = "Error de validación o regla de negocio")
   @ApiResponse(responseCode = "401", description = "Sin token o token inválido")
   @ApiResponse(responseCode = "403", description = "Sin rol o permiso")
   @ApiResponse(responseCode = "404", description = "No encontrado")
   @DeleteMapping("/anular/{id}")
   ```
4. `GET /api/creditos` → `CreditoServiceImpl#listarTodos`, con la misma carga que dejó M8: `CreditoRepository#buscarTodosConCuotas` (fetch de cliente y cuotas) y `CuotaRepository#buscarTodasConCobranzas` (fetch de cobranzas). Son dos consultas fijas, sin N+1. Mismo acceso que el resto de `/api/creditos`.

## Por qué
- El controlador decide la representación HTTP; el modelo solo lanza `BusinessException`, `ResourceNotFoundException` o `AccessDeniedException`. Separar 401 de 403 completa esa traducción para el caso que nunca llega al controller.
- Validar en la frontera evita que el modelo reciba datos que no puede interpretar.
- Los códigos documentados son los mismos que mapea `GlobalExceptionHandler` (M5), así que el contrato publicado no puede divergir de lo que la API hace sin que se note en Swagger.
- El listado general tapa un hueco del dashboard: el supervisor no tenía cómo ver la cartera completa.

Verificación: `mvn -q -DskipTests compile` → exit 0; `/v3/api-docs` 200 (17 paths, esquema `bearerAuth`); `GET /api/creditos` sin token 401, con token 200; `PUT /api/admin/usuarios/2/rol` con `{}` 400.
