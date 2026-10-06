# Backlog consolidado de mejoras pendientes

Junta lo que quedó abierto en `docs/trabajo/oportunidades.md`, `spring-practicas.md`, `smells.md`, `tests.md`, `auditoria.md`, `api-propuesta.md`, en la sección 6 de `dominio.md` y en el tablero. Se cruzó con `git log v2..main` y con el código de `main`: no se lista lo que ya está hecho (O1-O5, S1-S4, D1, D2, BS1, DF1, DF3, BSF1, título ADMIN, `@Valid` de permisos y rol, 401 sin token, `GET /api/creditos`, `tipoPlan` en `CreditoResponse`, `esValido(String, String)` en `TokenService`).

`…/` = `backend/src/main/java/com/uade/tpejemplo/`. Rutas de front relativas a `frontend/src/`. Tamaño: S (pocas líneas), M (varios archivos), L (cambia el modelo). Tamaño con `*` = estimación, la fuente no lo da. Fechas: 27/10 y 03/11 son iteraciones, 17/11 es la entrega final.

## Dominio y patrones

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| O6 | `Credito` genera sus cuotas en el constructor y las persiste por cascade; `generarPlanDeCuotas` sale de `ICredito` | `…/model/Credito.java`, `…/model/interfaces/ICredito.java`, `…/service/impl/CreditoServiceImpl.java` | M | 27/10 | Creator y agregado: hoy un crédito sin plan queda VIGENTE con saldo 0 y nunca se cancela. Riesgo medio por el cascade de JPA |
| O7 | `saldoPendiente` y `montoVencido` en el dashboard, con dos tarjetas | `…/dto/response/DashboardStatsResponse.java`, `…/service/impl/DashboardServiceImpl.java`, `pages/Dashboard.jsx` | M | 27/10 | Hueco de dominio A-05 / A-02: la mora solo se ve entrando crédito por crédito. Dependía de O4, que ya está |
| H8 | Trazabilidad de usuario en `Cobranza`: quién registró y quién anuló | `…/model/Cobranza.java`, `…/controller/CobranzaController.java`, `…/dto/response/CobranzaResponse.java` | M* | 27/10 | Modelo nuevo que toca la API; `dominio.md` lo dejó como candidato para esta iteración |
| O3b | Ajustar la última cuota para que el total cierre exacto (hoy 10.000 al 45 % en 6 cuotas: total 14.500,02) | `…/model/plan/InteresSimple.java`, `…/model/plan/SistemaFrances.java`, `…/model/Credito.java` | M | 03/11 | Alternativa que O3 dejó para después; hoy el centavo se explica como redondeo por cuota |
| C1 | Renombrar `CalculoDeCuota` a `ICalculoDeCuota` o justificar que es un rol de patrón | `…/model/interfaces/CalculoDeCuota.java` | S* | 03/11 | Inconsistencia de nombres con `ICredito`, `ICuota`, `IPermisos` (auditoría, Convenciones) |

## Spring

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| I2 | `@EntityGraph` en las queries de `CreditoRepository` en vez de la precarga por efecto lateral (`cuotaRepository.buscarPorCredito(id);` sin usar el resultado) | `…/service/impl/CreditoServiceImpl.java`, `…/repository/CreditoRepository.java`, `…/repository/CuotaRepository.java` | M* | 27/10 | Leída en frío parece código muerto y, si alguien la borra, `Cuota.estaPagada()` tira `LazyInitializationException`. Ojo con `MultipleBagFetchException` si las dos colecciones son `List`. Va junto con O6 |
| S3b | `@ConfigurationProperties` para las propiedades de JWT | `…/security/JwtUtil.java`, `backend/src/main/resources/application.properties` | S* | 03/11 | Propiedades de JWT tipadas en vez de leer `jwt.secret` suelto en `JwtUtil` |
| S5 | Borrar el `@Bean authenticationProvider()` y el `.authenticationProvider(...)` | `…/config/SecurityConfig.java` | S | 03/11 | Con `UserDetailsService` y `PasswordEncoder` como beans, Spring arma el provider y desaparece el warning |
| S6 | Una sola fuente de autorización por rol: reglas de URL o `@PreAuthorize` | `…/config/SecurityConfig.java`, `…/controller/AdminController.java`, `…/controller/SupervisorController.java` | S | 03/11 | Duplicadas; no rompe nada y se defiende como defensa en profundidad |
| S7 | Consola H2 solo en dev; sacar `/h2-console/**` del `permitAll` redundante (TPO-008) | `…/config/SecurityConfig.java`, `application.properties` | S | 03/11 | La consola da acceso total a la base sin autenticación. Un perfil `dev` solo para esto es sobreingeniería |
| S8 | Borrar `.cors(Customizer.withDefaults())` o declarar un `CorsConfigurationSource` | `…/config/SecurityConfig.java` | S | 03/11 | El front pasa por el proxy de Vite (`frontend/vite.config.js`); la línea no hace nada y sugiere que CORS está resuelto |
| S9 | `ddl-auto=create-drop` y `show-sql=false` | `backend/src/main/resources/application.properties` | S | 03/11 | `update` no tiene sentido con H2 en memoria; `show-sql` ensucia la consola en la demo |
| S10 | Renombrar el paquete `com.uade.tpejemplo`, `TpEjemploApplication` y el `artifactId` (TPO-014) | `backend/pom.xml`, todo `backend/src` | M | 17/11 | El nombre de plantilla no comunica el dominio. Diff ruidoso que taparía los cambios reales: NO antes del 13/10, evaluar para la entrega final |

## Smells

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| BS3 | `IUsuario.puedeAnularCredito()` / `puedeAnularCobranza()` en vez de navegar `usuario.getPermisos().isPuedeAnular*()` | `…/model/interfaces/IUsuario.java`, `…/model/Usuario.java`, `…/service/impl/CreditoServiceImpl.java`, `…/service/impl/CobranzaServiceImpl.java` | S | 27/10 | Feature envy y cadena de mensajes; Information Expert. Reemplazar, no sumar al lado (auditoría I3) |
| BS2 | Método privado `error(HttpStatus, String, List<String>)` para armar `ErrorResponse` | `…/exception/GlobalExceptionHandler.java` | S | 03/11 | Ocho repeticiones del mismo `ResponseEntity.status(...).body(...)`; mecánico, no lógico |
| BS4 | Tipar `rol` como `Rol` en las respuestas | `…/dto/response/UsuarioResponse.java`, `…/dto/response/AuthResponse.java` | S | 03/11 | Primitive obsession; el JSON no cambia |
| BS6 | `SupervisorController.obtenerUsuarios` pasa a `listarUsuarios`; `JwtUtil` a `JwtTokenService` solo si se lo toca por otra razón | `…/controller/SupervisorController.java`, `…/security/JwtUtil.java` | S | 03/11 | Mismo caso con dos verbos distintos; `listarTodos` ya cayó con BS1 |

## Tests

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| T-1 | `@WebMvcTest` de los controllers con los códigos HTTP de M5 (`BusinessException` → 4xx, no encontrado → 404), services mockeados | `backend/src/test/java/com/uade/tpejemplo/controller/` | M* | 27/10 | Controllers y códigos HTTP no tienen cobertura |
| T-2 | `@DataJpaTest` de las queries del dashboard (M3) sobre H2 con créditos, cuotas vencidas y cobranzas anuladas | `backend/src/test/java/com/uade/tpejemplo/repository/` | M* | 27/10 | Repositories y queries sin cobertura |
| T-3 | Tests de `Permisos` y `IPermisos` | `backend/src/test/java/com/uade/tpejemplo/model/` | S* | 27/10 | Estaban bloqueados por `fixes-auditoria`, que ya se mergeó |
| T-4 | Seguridad: sin token → 401, rol sin permiso → 403 (`@WebMvcTest` + `spring-security-test`, dependencia nueva) | `backend/pom.xml`, `backend/src/test/java/com/uade/tpejemplo/security/` | M* | 03/11 | JWT y roles sin cobertura |
| T-5 | Inyectar un `Clock` en `Cobranza` para testear el rechazo de anular una cobranza de otro día | `…/model/Cobranza.java`, `CobranzaTest` | S* | 17/11 | Hoy la fecha sale de `LocalDate.now()` y no se puede testear. Es un cambio de código: decidirlo antes |

## API

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| A-1 | `GET /usuarios/me`, o rol y permisos en `AuthResponse`; verificar antes cómo lo resuelve el front | `…/controller/AuthController.java` | S* | 03/11 | RECOMENDADA si el front guarda los permisos del login: quedan viejos hasta volver a loguearse |
| A-2 | Quitar `PUT /api/admin/usuarios/{id}/permisos` o justificarlo | `…/controller/AdminController.java` | S | 03/11 | Duplicado del de supervisor y sin uso en el front |
| A-3 | `GET /api/cobranzas/credito/{id}` con crédito inexistente responde 404 en vez de `[]` | `…/controller/CobranzaController.java`, `…/service/impl/CobranzaServiceImpl.java` | S* | 03/11 | Observación del mapa de API |

## Front

TPO-012 (smells del front) es el paraguas: se cierra con las filas de abajo; BSF3 va a descartados.

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| DF2 | Borrar `App.css`, `assets/react.svg`, `getCliente`, `getCredito` y los cuatro `clearError` sin uso | `App.css`, `assets/react.svg`, `api/clientes.js`, `api/creditos.js`, `store/slices/*.js` | S | 03/11 | Restos del template de Vite y exports sin llamadores |
| BSF2 + BSF4 | Un `RoleRoute({ roles, children })` y una constante `ROLES` en vez de strings sueltos | `components/AdminRoute.jsx`, `components/SupervisorRoute.jsx`, `components/Navbar.jsx`, `pages/Dashboard.jsx`, `pages/GestorPermisos.jsx`, `pages/PanelAdmin.jsx` | S | 03/11 | Código duplicado y primitive obsession; van juntos |
| BSF5 | `api/dashboard.js` y `getUsuariosAdmin` en `api/admin.js`; `rejectWithValue(err.message)` en `cobranzasSlice.js` | `store/slices/dashboardSlice.js`, `store/slices/permisosSlice.js`, `store/slices/cobranzasSlice.js`, `api/admin.js`, `api/supervisor.js` | S | 03/11 | Acceso inconsistente a la API; `cobranzasSlice.js:26` lee una forma de error que `apiClient.js` nunca produce |
| BSF6 | Objeto `ESTADO_CUOTA` en vez de dos ternarios anidados en el render | `pages/Creditos.jsx` | S | 03/11 | Método largo y condicional anidado repetido |

## Docs

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| m1 | `git mv M4.md m4.md` y `M4-despues.puml m4-despues.puml` | `docs/trabajo/` | S | 27/10 | Nombres inconsistentes con el resto |
| m2 | Secciones `## Patrón` y `## Consecuencias` faltantes en `m1.md`, `m3.md`, `m5.md` | `docs/trabajo/` | S | 27/10 | La consigna §3 pide Consecuencias; plantilla no uniforme |

## Descartados (NO HACER)

| ID | Qué | Motivo |
|---|---|---|
| O8 | Pagos parciales (A-01) | Tamaño L y riesgo alto: cambia `Cuota.estaPagada()`, `Cobranza`, `Credito.saldo()`, el dashboard y la vista. Exigir el importe exacto (TPO-006) se defiende para este alcance. Va como pendiente en el reporte |
| O9 | `EstadoCredito` como patrón State | El estado es derivado, no se guarda y hay una sola transición con regla (`Credito.anular()`). Sobreingeniería; el apunte advierte contra confundir Strategy con State. Respuesta para la defensa |
| O10 | Strategy para punitorios, Adapter sobre `PasswordEncoder`, Adapter sobre `fetch` | Ninguno tapa un hueco: no hay punitorios, `PasswordEncoder` ya es la abstracción de Spring y `api/apiClient.js` ya hace de pasarela |
| D3 | Borrar `estaCancelado()`, `tieneCobranzas()` y `puedeAnularse()` de `…/model/interfaces/ICredito.java` | Tira tests y una pregunta de dominio legítima; no molesta a nadie |
| D4 | Borrar `…/model/interfaces/IRol.java` | Las interfaces de modelo se restituyeron en V2 a propósito; sacar una sola rompe la simetría del diagrama |
| D5 | Sacar `GET /api/creditos` por falta de consumidor | Es API pública documentada, no código muerto |
| BS5 | Objeto parámetro para `Credito.nuevo` (6 parámetros) | Datos obligatorios de tipos distintos y un solo llamador: sobreingeniería |
| BS7 | Quitar `@Data` de los DTO | Un DTO es una estructura de datos por diseño; las clases de dominio ya tienen comportamiento |
| BSF3 | Factorizar thunks y estilos inline del front | Boilerplate estándar de Redux Toolkit; cambia todo el front sin tapar ningún hueco |
| A-4 | `PUT /api/clientes/{dni}` (editar nombre) | DUDOSA: ningún caso de uso ni ticket lo pide |
| A-5 | `POST /api/creditos/{id}/anulacion` y `POST /api/cobranzas/{id}/anulacion` en vez de `DELETE` | DUDOSA: más REST pero cosmético, cambia el contrato y toca `api/creditos.js` y `api/cobranzas.js` |
| A-6 | `GET /api/cobranzas/{id}` | DUDOSA: nadie la consume |
| A-7 | Desactivar o borrar usuarios | DUDOSA: no hay caso de uso ni campo `activo`; requiere cambio de modelo |
| A-8 | `DELETE /api/clientes/{dni}`, `PUT` o `DELETE` real de crédito y de cobranza, CRUD de cuota, `GET /api/creditos/{id}/cuotas` | La fuente los marca NO: romperían el historial o las cuotas ya generadas, o son redundantes con `CreditoResponse.cuotas` |
