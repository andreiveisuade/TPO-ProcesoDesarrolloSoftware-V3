# Lista de mejoras — Iteración 3 (TPO Grupo 7, Dashboard de préstamos)

Rutas Java relativas a `backend/src/main/java/com/uade/tpejemplo/`. Reporte completo: `docs/reporte/reporte-v3.html`. Casos de uso: `docs/casos-de-uso/README.md`.

## Foco de la consigna: Strategy y Adapter

| ID | Qué | Clase y método | Patrón / concepto |
|---|---|---|---|
| M9 | Cálculo de cuota intercambiable: interés simple y sistema francés | `model/interfaces/CalculoDeCuota.java`; `model/plan/InteresSimple.java`, `model/plan/SistemaFrances.java`; `model/TipoPlan.java`; `model/Credito.java` (constructor, `totalADevolver`) | **Strategy** (+ OCP, Polymorphism) |
| M7 | Target `TokenService`, Adapter `JwtUtil`, Adaptee jjwt (librería que no controlamos); además `UsuarioDetails` adapta `IUsuario` a `UserDetails` | `service/TokenService.java`; `security/JwtUtil.java`; clientes `security/JwtAuthFilter.java`, `service/impl/AuthServiceImpl.java`; `security/UsuarioDetails.java` | **Adapter** (+ DIP, Protected Variations) |

## Hechos

| ID | Qué | Clase y método | Patrón / concepto |
|---|---|---|---|
| M1 | Rechazar el cobro sobre un crédito anulado (TPO-004) | `model/Cuota.java` `registrarCobranza` | Information Expert |
| M2 | "Tiene cobranzas" ignora las anuladas (absorbida por M8) | `model/Credito.java` `tieneCobranzas`; se borra `repository/CobranzaRepository.java` `existeCobranzaDelCredito` | Information Expert |
| M3 | Dashboard solo con lo vigente; financiado = deuda original (TPO-003) | `service/impl/DashboardServiceImpl.java` `obtenerEstadisticasGenerales`; `repository/CreditoRepository.java` `sumarDeudaOriginalVigente`; `repository/CobranzaRepository.java` `sumarImporteVigente` | Corrección + Expert |
| M4 | Permisos de anulación validados en el backend (TPO-007) | `controller/CreditoController.java` `anularCredito`, `service/impl/CreditoServiceImpl.java` `anularCredito`, `service/impl/CobranzaServiceImpl.java` `anularCobranza` | MVC + Information Expert |
| M5 | Handlers 401/403/404/405 (TPO-001, TPO-002) | `exception/GlobalExceptionHandler.java` `handleAuth`, `handleDenied`, `handleNoResource`, `handleMetodo` | MVC |
| M6 | Cuota vencida (mora) | `model/Cuota.java` `estaVencida`; `dto/response/CuotaResponse.java` | Information Expert |
| M8 | EstadoCredito y Credito como agregado (estado, saldo, anulación) | `model/EstadoCredito.java`; `model/Credito.java` `estado`, `saldo`, `estaCancelado`, `puedeAnularse`, `anular`; `service/impl/CreditoServiceImpl.java` `buscarCredito` | Information Expert + Creator |
| M10 | Dashboard también para ADMIN (TPO-010) | `config/SecurityConfig.java` `filterChain`; `frontend/src/pages/Dashboard.jsx`, `frontend/src/components/Navbar.jsx` | Control de acceso |
| API | Swagger, 401 sin token, `@Valid` en admin/supervisor, `GET /api/creditos` | `config/OpenApiConfig.java`; `config/SecurityConfig.java`; `controller/AdminController.java`, `controller/SupervisorController.java`; `service/impl/CreditoServiceImpl.java` `listarTodos` | MVC (contrato del controlador) |
| O1 | La vista usa `puedeAnularse` del modelo y recarga tras anular | `dto/response/CreditoResponse.java`; `frontend/src/pages/Creditos.jsx`; `frontend/src/store/slices/creditosSlice.js` | MVC + Expert |
| O2 | El Adapter traduce las excepciones de jjwt; Target sin tipos externos | `security/JwtUtil.java` `extraerUsername`, `esValido`; `security/JwtAuthFilter.java` | Adapter, Protected Variations |
| O3 | El total sale de las cuotas emitidas | `model/Credito.java` `totalADevolver`; `model/interfaces/CalculoDeCuota.java` | Strategy (alcance), Expert |
| O4 | "Créditos activos" con `Credito.estado()` | `service/impl/DashboardServiceImpl.java` `obtenerEstadisticasGenerales` | Information Expert |
| O5 | La guarda del ADMIN vive en el modelo | `model/Usuario.java` `otorgarPermisos`, `asignarRol`; `service/impl/AdminServiceImpl.java` | MVC + Expert |
| S1 | Transacciones en los services | `service/impl/AdminServiceImpl.java`, `AuthServiceImpl.java`, `ClienteServiceImpl.java`, `CobranzaServiceImpl.java` | Spring: `@Transactional` |
| S2 | open-in-view apagado | `backend/src/main/resources/application.properties` | Spring JPA |
| S3 | `jwt.secret` desde `JWT_SECRET` (TPO-009) | `backend/src/main/resources/application.properties` | Configuración fuera del código |
| S4 | El 500 no filtra el mensaje interno y se loguea | `exception/GlobalExceptionHandler.java` `handleGeneral` | Seguridad / MVC |
| D1 | Borrar `findByRol` sin uso | `repository/UsuarioRepository.java` | Código muerto |
| D2 | Borrar `@Builder`/`@NoArgsConstructor` sin uso | `dto/response/AuthResponse.java` | Código muerto |
| BS1 | Supervisor lista usuarios sin admins; se borra `listarTodos` | `controller/SupervisorController.java`; `service/AdminService.java`; `service/impl/AdminServiceImpl.java`; `frontend/src/pages/GestorPermisos.jsx` | Código duplicado |
| DF1 | Borrar store huérfano | `frontend/src/store/index.js` | Código muerto (front) |
| DF3 | Sacar `console.log` que imprimía el JWT | `frontend/src/pages/Creditos.jsx` | Código de depuración |
| BSF1 | Borrar comentarios de copy-paste | `frontend/src/store/slices/permisosSlice.js`, `cobranzasSlice.js`; `frontend/src/pages/GestorPermisos.jsx` | Comentarios |
| F1 | Usuario autenticado sin el rol recibe 403, no 401 | `config/SecurityConfig.java` `filterChain` (`accessDeniedHandler`) | MVC (controlador) |
| F2 | Body mal formado o parámetro de tipo incorrecto responde 400, no 500 | `exception/GlobalExceptionHandler.java` `handleRequestInvalida` | MVC (controlador) |
| UI | Moneda y fechas es-AR, crédito con badge de estado y datos rotulados, fecha de cobranza, todos los mensajes de error, tabla de clientes | `frontend/src/utils/formato.js`; `frontend/src/pages/Creditos.jsx`, `Cobranzas.jsx`, `Clientes.jsx`, `Dashboard.jsx`; `frontend/src/api/apiClient.js` | Vista (MVC) |
| DT | Dark theme con variables CSS semánticas y `prefers-color-scheme` | `frontend/src/index.css`; `frontend/src/pages/*.jsx`, `frontend/src/components/Navbar.jsx` | Protected Variations (estilo) |
| COM | Comentarios: 1-3 líneas por clase, una línea por patrón, una por componente del front | `backend/src/main/java/**`, `frontend/src/**` | Bad smell: comentarios |
| LIM | Limpieza del repo: `.factorypath` sin trackear, `docs/trabajo` fuera del `git archive`, docs de proceso borrados, README corto | `.gitattributes`, `README.md`, `docs/` | Entrega |
| CU | Casos de uso V3: fichas, diagrama, trazabilidad y verificación por API | `docs/casos-de-uso/README.md`, `docs/casos-de-uso/verificar-cu.sh` | Documentación |
| H1 | Anular una cobranza ya anulada se rechaza (400), como el crédito | `model/Cobranza.java` `anular` | Information Expert |
| O6 | El crédito nace con su plan de cuotas: el constructor las genera y JPA las guarda por cascade; `generarPlanDeCuotas` pasa a privado y sale de `ICredito` | `model/Credito.java` constructor, `generarPlanDeCuotas`; `model/interfaces/ICredito.java`; `service/impl/CreditoServiceImpl.java` `crear` | Creator |
| O7 | Saldo pendiente y monto vencido en el dashboard | `service/impl/DashboardServiceImpl.java` `obtenerEstadisticasGenerales`; `dto/response/DashboardStatsResponse.java`; `frontend/src/pages/Dashboard.jsx` | Information Expert |
| S5 | Spring arma el `DaoAuthenticationProvider` con los beans `UserDetailsService` y `PasswordEncoder`; se borra el armado a mano y el warning del arranque | `config/SecurityConfig.java` | Spring Security |
| BS2 | El `ErrorResponse` se arma en un solo método; el código sale del `HttpStatus` | `exception/GlobalExceptionHandler.java` `error` | Código duplicado |
| I-2 | Largo y escala acotados en los request: lo que no entra en la columna da 400 y no 500 ni un redondeo silencioso | `dto/request/ClienteRequest.java`, `CreditoRequest.java`, `CobranzaRequest.java`, `RegisterRequest.java` (`@Size`, `@Digits`) | Validación en el controlador (MVC) |
| T-1 | Tests de los códigos HTTP 400/401/403/404/405 con la seguridad JWT real y los servicios simulados | `backend/src/test/java/com/uade/tpejemplo/controller/CodigosHttpTest.java` (`@WebMvcTest`) | Tests |
| T-5 | La fecha de hoy entra por parámetro: se testea anular una cobranza de otro día y el vencimiento sin depender del reloj | `model/Cobranza.java` `anular(LocalDate)`; `model/Cuota.java` `estaVencida(LocalDate)` | Tests |
| DER | Diagrama entidad-relación de la base, con claves y restricciones | `docs/diagramas/der-v3.puml`, `.svg`, `.png` | Documentación |
| Tests | 36 tests, 0 fallas | `backend/src/test/java/com/uade/tpejemplo/` | JUnit 5 + AssertJ, `@WebMvcTest` |

Desglose de los 36 tests:

- `model/CreditoTest`: 8
- `model/CuotaTest`: 8
- `model/plan/InteresSimpleTest`: 4
- `model/plan/SistemaFrancesTest`: 4
- `model/CobranzaTest`: 3
- `controller/CodigosHttpTest`: 8
- `TpEjemploApplicationTests` (`contextLoads`): 1

Decisión S6: el control de roles queda doble a propósito, reglas de URL en `config/SecurityConfig.java` `filterChain` y `@PreAuthorize` en `controller/AdminController.java` y `controller/SupervisorController.java`. Es defensa en profundidad: si una ruta cambia y la regla de URL deja de cubrirla, el método sigue protegido.

## Recorrido de casos de uso por la UI (T33)

Salen de recorrer cada caso de uso por la UI (incluido H4).

| ID | Qué | Clase y método | Patrón / concepto |
|---|---|---|---|
| R1 | Aviso de éxito al crear crédito o cobranza; el error de búsqueda queda en el bloque de búsqueda | `frontend/src/components/Aviso.jsx`; `frontend/src/pages/Creditos.jsx` `buscar`, `handleSubmit`; `Cobranzas.jsx` `buscar`, `handleSubmit`; `creditosSlice.js`, `cobranzasSlice.js` (`fetch...rejected`) | Vista (MVC) |
| R2 | Validación sin prefijo de campo; título del dashboard como el resto | `exception/GlobalExceptionHandler.java` `handleValidation`; `frontend/src/pages/Dashboard.jsx` | Vista (MVC) |
| R3 | `GET /api/auth/me` y refresco de permisos al entrar a cada pantalla (H4) | `controller/AuthController.java` `me`; `service/impl/AuthServiceImpl.java` `actual`; `config/SecurityConfig.java`; `frontend/src/components/PrivateRoute.jsx`; `authSlice.js` `refrescarUsuario` | MVC + Information Expert |
| R4 | Pantallas de UC06 y UC09 | `frontend/src/pages/Clientes.jsx` `buscar`; `frontend/src/pages/Creditos.jsx` `consultar`, `fichaCredito` | Vista (MVC) |

**R1. Avisos bien ubicados.**
- Problema (UC07, UC10, UC13): al buscar un DNI inexistente, el "Cliente no encontrado" aparecía dentro de "Nuevo crédito" y además se listaba "Créditos del cliente (0)", como si el cliente existiera. Y al crear un crédito o una cobranza el formulario se vaciaba sin decir nada: el usuario no sabía si se había guardado ni con qué número.
- Qué se hizo: la búsqueda guarda su propio error y lo muestra en su bloque; si falla no se dibuja el listado. El `error` del slice queda solo para el alta. Al crear se muestra "Crédito #N creado..." o "Cobranza #N registrada...". El cuadrito de aviso es un componente `Aviso` porque se repite en tres pantallas.
- Por qué es lo mínimo: no hay toasts ni librería, ni estado global nuevo; es un `useState` por pantalla y un componente de 8 líneas.

**R2. Mensajes limpios.**
- Problema (UC01, UC16): el registro mostraba "password: La contraseña debe tener al menos 6 caracteres", con el nombre técnico del campo, y el dashboard tenía el título centrado y pegado a las tarjetas, distinto al resto.
- Qué se hizo: el handler de validación devuelve solo el mensaje (que ya está escrito en castellano en cada `@NotBlank`/`@Size`). El dashboard usa el mismo contenedor y título que las otras pantallas.
- Por qué es lo mínimo: se arregla en el único lugar donde se arma el texto (el back), en vez de recortar strings en cada pantalla del front.

**R3. Permisos sin reloguear (H4).**
- Problema (UC19, UC11, UC15): el front leía rol y permisos de `localStorage` al loguearse. Si el supervisor le daba "anular crédito" a alguien, esa persona no veía el botón Anular hasta cerrar sesión y volver a entrar.
- Qué se hizo: `GET /api/auth/me` devuelve el usuario autenticado con rol y permisos, reusando `AuthResponse` (con `token` en null, porque no se emite uno nuevo). `PrivateRoute`, la guarda por la que pasa toda pantalla con sesión, lo pide al cargar la app y en cada cambio de pantalla, y actualiza el store conservando el token. Verificado: con `user` en Créditos, el supervisor le da y le saca el permiso por API, `user` navega Cobranzas → Créditos sin recargar y el botón aparece y desaparece.
- Por qué es lo mínimo: una consulta por navegación, sin polling ni websockets. Se pone en `PrivateRoute` y no en cada pantalla porque es el único punto por el que pasan todas. El back sigue siendo la autoridad (M4): esto solo evita que la vista quede desactualizada.

**R4. UC06 y UC09 con pantalla.**
- Problema (UC06, UC09): los dos casos de uso existían en el back y en `api/clientes.js` / `api/creditos.js`, pero ninguna pantalla los usaba.
- Qué se hizo: en Clientes, "Buscar cliente por DNI" muestra nombre y DNI o el 404. En Créditos, "Consultar crédito por número" muestra la misma ficha del listado (estado, plan, saldo, cuotas, Anular), extraída a `fichaCredito` para no duplicarla.
- Por qué es lo mínimo: usa los endpoints y funciones de API que ya estaban, sin slice nuevo (el resultado no lo comparte ninguna otra pantalla), y reutiliza la ficha del crédito en vez de escribir otra.

## Pendientes

| ID | Qué | Dónde | Por qué queda |
|---|---|---|---|
| O8 | Pagos parciales | `model/Cuota.java` `estaPagada` y todo lo que depende | Tamaño L, fuera de alcance de V3 |
| S7-S9 | Consola H2 (TPO-008), CORS, `ddl-auto`/`show-sql` | `config/SecurityConfig.java`, `application.properties` | No rompen nada; prolijidad |
| S10 | Renombrar paquete `com.uade.tpejemplo` (TPO-014) | todo el backend | Diff ruidoso; evaluar para el 17/11 |
| BS3-BS6 | Chequeo de permiso en services, rol como String, nombres | services, DTO | Menores |
| Front | DF2, BSF2, BSF4, BSF5, BSF6 (TPO-012) | `frontend/src/**` | Menores |
| I-1 | Dos requests simultáneas pueden dejar dos cobranzas vigentes en la misma cuota. Arreglo probado: `@Lock(PESSIMISTIC_WRITE)` en `buscarPorCreditoYNumero` sin el `JOIN FETCH` de cobranzas | `repository/CuotaRepository.java` | 27/10, con su `@DataJpaTest` |
| Tests | `@DataJpaTest` del dashboard, `Permisos` | `backend/src/test` | Siguiente iteración |
| H8 | Trazabilidad: qué usuario cobró o anuló | `model/Cobranza.java`, `model/Credito.java` | Modelo nuevo y cambio de API |
| P-M9 | Tasa con unidad declarada por plan; cuota con capital/interés separados | `model/TipoPlan.java`, `model/Cuota.java` | Límites del Strategy actual (ver reporte) |

Descartados con motivo: `EstadoCredito` como State (O9: es un valor derivado) y Strategy/Adapter "para mostrar" (O10: no tapan huecos).
