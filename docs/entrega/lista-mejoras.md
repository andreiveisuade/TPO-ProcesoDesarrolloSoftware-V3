# Lista de mejoras — Iteración 3 (TPO Grupo 7, Dashboard de préstamos)

Rutas Java relativas a `backend/src/main/java/com/uade/tpejemplo/`. Reporte completo: `docs/reporte/reporte-v3.html`. Casos de uso: `docs/casos-de-uso/README.md`.

## Foco de la consigna: Strategy y Adapter

| ID | Qué | Clase y método | Patrón / concepto |
|---|---|---|---|
| M9 | Cálculo de cuota intercambiable: interés simple y sistema francés | `model/interfaces/CalculoDeCuota.java`; `model/plan/InteresSimple.java`, `model/plan/SistemaFrances.java`; `model/TipoPlan.java`; `model/Credito.java` (constructor, `totalADevolver`) | **Strategy** (+ OCP, Polymorphism) |
| M7 | JwtUtil detrás de TokenService; UsuarioDetails documentado | `service/TokenService.java`; `security/JwtUtil.java`; clientes `security/JwtAuthFilter.java`, `service/impl/AuthServiceImpl.java`; `security/UsuarioDetails.java` | **Adapter** (+ DIP, Protected Variations) |

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
| UI | Moneda y fechas es-AR, crédito con badge de estado y datos rotulados, fecha de cobranza, todos los mensajes de error, tabla de clientes | `frontend/src/utils/formato.js`; `frontend/src/pages/Creditos.jsx`, `Cobranzas.jsx`, `Clientes.jsx`, `Dashboard.jsx`; `frontend/src/api/apiClient.js` | Vista (MVC); detalle en `docs/trabajo/ui.md` |
| DT | Dark theme con variables CSS semánticas y `prefers-color-scheme` | `frontend/src/index.css`; `frontend/src/pages/*.jsx`, `frontend/src/components/Navbar.jsx` | Protected Variations (estilo) |
| COM | Comentarios: 1-3 líneas por clase, una línea por patrón, una por componente del front | `backend/src/main/java/**`, `frontend/src/**` | Bad smell: comentarios |
| LIM | Limpieza del repo: `.factorypath` sin trackear, `docs/trabajo` fuera del `git archive`, docs de proceso borrados, README corto | `.gitattributes`, `README.md`, `docs/` | Entrega |
| CU | Casos de uso V3: fichas, diagrama, trazabilidad y verificación por API | `docs/casos-de-uso/README.md`, `docs/casos-de-uso/verificar-cu.sh` | Documentación |
| H1 | Anular una cobranza ya anulada se rechaza (400), como el crédito | `model/Cobranza.java` `anular` | Information Expert |
| Tests | 26 tests (25 de dominio + contexto), 0 fallas | `backend/src/test/java/com/uade/tpejemplo/model/**` | JUnit 5 + AssertJ |

## Pendientes

| ID | Qué | Dónde | Por qué queda |
|---|---|---|---|
| O6 | El crédito genera su plan en el constructor (cascade) | `model/Credito.java`, `service/impl/CreditoServiceImpl.java` `crear` | Tamaño M, riesgo JPA; 27/10 |
| O7 | Saldo pendiente y monto vencido en el dashboard | `service/impl/DashboardServiceImpl.java`, `dto/response/DashboardStatsResponse.java` | Depende de O4; 27/10 |
| O8 | Pagos parciales | `model/Cuota.java` `estaPagada` y todo lo que depende | Tamaño L, fuera de alcance de V3 |
| S5-S9 | AuthenticationProvider duplicado, reglas de URL + `@PreAuthorize`, consola H2 (TPO-008), CORS, `ddl-auto`/`show-sql` | `config/SecurityConfig.java`, `application.properties` | No rompen nada; prolijidad |
| S10 | Renombrar paquete `com.uade.tpejemplo` (TPO-014) | todo el backend | Diff ruidoso; evaluar para el 17/11 |
| BS2-BS6 | `ErrorResponse` repetido, chequeo de permiso en services, rol como String, nombres | `exception/GlobalExceptionHandler.java`, services, DTO | Menores |
| Front | DF2, BSF2, BSF4, BSF5, BSF6 (TPO-012) | `frontend/src/**` | Menores |
| Tests | `@WebMvcTest` de códigos HTTP, `@DataJpaTest` del dashboard, seguridad, `Clock` inyectable | `backend/src/test` | Siguiente iteración |
| H8 | Trazabilidad: qué usuario cobró o anuló | `model/Cobranza.java`, `model/Credito.java` | Modelo nuevo y cambio de API |
| H4 | El front ve permisos y rol nuevos recién al volver a loguearse | `frontend/src/store/slices/authSlice.js` | Necesita `GET /usuarios/me` (A-1 del backlog) |
| M9 | Tasa con unidad declarada por plan; cuota con capital/interés separados | `model/TipoPlan.java`, `model/Cuota.java` | Límites del Strategy actual (ver reporte) |

Descartados con motivo: `EstadoCredito` como State (O9: es un valor derivado) y Strategy/Adapter "para mostrar" (O10: no tapan huecos).
