# Backlog consolidado de mejoras pendientes

Junta lo que quedó abierto en la iteración 3 (dominio, prácticas de Spring, bad smells, tests, API y front), contrastado con el código de `main`. No se lista lo que ya está hecho (O1-O7, S5, BS2, I-2, T-1, T-4, T-5, H4 con `GET /api/auth/me`, pantallas de UC06 y UC09, S1-S4, D1, D2, BS1, DF1, DF3, BSF1, título ADMIN, `@Valid` de permisos y rol, 401 sin token, `GET /api/creditos`, `tipoPlan` en `CreditoResponse`, `esValido(String, String)` en `TokenService`, I-1 (bloqueo pesimista en `…/repository/CuotaRepository.java` `buscarPorCreditoYNumero`, test en `backend/src/test/java/com/uade/tpejemplo/service/CobranzaConcurrenteTest.java`), S7-S9 y TPO-008 (perfiles dev y prod, CORS con `CORS_ORIGIN`, consola H2 solo en dev), BS3, BS4, BS6, DF2, BSF2, BSF4, BSF5, BSF6 (TPO-012), 403 con token y sin rol, 400 en requests mal formadas, mejoras de UI, dark theme, comentarios y limpieza del repo).

`…/` = `backend/src/main/java/com/uade/tpejemplo/`. Rutas de front relativas a `frontend/src/`. Tamaño: S (pocas líneas), M (varios archivos), L (cambia el modelo). Tamaño con `*` = estimación. Fechas: 27/10 y 03/11 son iteraciones, 17/11 es la entrega final.

## Dominio y patrones

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| M-3 | Carrera entre anular un crédito y cobrar una de sus cuotas (no reproducida) | `…/service/impl/CreditoServiceImpl.java`, `…/service/impl/CobranzaServiceImpl.java` | S* | 27/10 | Mismo arreglo que I-1 (ya en `main`), bloqueando también el crédito |
| H8 | Trazabilidad de usuario en `Cobranza`: quién registró y quién anuló | `…/model/Cobranza.java`, `…/controller/CobranzaController.java`, `…/dto/response/CobranzaResponse.java` | M* | 27/10 | Modelo nuevo que toca la API |
| O3b | Ajustar la última cuota para que el total cierre exacto (hoy 10.000 al 45 % en 6 cuotas: total 14.500,02) | `…/model/plan/InteresSimple.java`, `…/model/plan/SistemaFrances.java`, `…/model/Credito.java` | M | 03/11 | Alternativa que O3 dejó para después; hoy el centavo se explica como redondeo por cuota |
| C1 | Renombrar `CalculoDeCuota` a `ICalculoDeCuota` o justificar que es un rol de patrón | `…/model/interfaces/CalculoDeCuota.java` | S* | 03/11 | Inconsistencia de nombres con `ICredito`, `ICuota`, `IPermisos` |

## Spring

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| I2 | `@EntityGraph` en las queries de `CreditoRepository` en vez de la precarga por efecto lateral (`cuotaRepository.buscarPorCredito(id);` sin usar el resultado) | `…/service/impl/CreditoServiceImpl.java`, `…/repository/CreditoRepository.java`, `…/repository/CuotaRepository.java` | M* | 27/10 | Leída en frío parece código muerto y, si alguien la borra, `Cuota.estaPagada()` tira `LazyInitializationException`. Ojo con `MultipleBagFetchException` si las dos colecciones son `List`. |
| S3b | `@ConfigurationProperties` para las propiedades de JWT | `…/security/JwtUtil.java`, `backend/src/main/resources/application.properties` | S* | 03/11 | Propiedades de JWT tipadas en vez de leer `jwt.secret` suelto en `JwtUtil` |
| S10 | Renombrar el paquete `com.uade.tpejemplo`, `TpEjemploApplication` y el `artifactId` (TPO-014) | `backend/pom.xml`, todo `backend/src` | M | 17/11 | El nombre de plantilla no comunica el dominio. Diff ruidoso que taparía los cambios reales: NO antes del 13/10, evaluar para la entrega final |

## Tests

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| T-2 | `@DataJpaTest` de las queries del dashboard (M3) sobre H2 con créditos, cuotas vencidas y cobranzas anuladas | `backend/src/test/java/com/uade/tpejemplo/repository/` | M* | 27/10 | Repositories y queries sin cobertura |
| T-3 | Tests de `Permisos` y `IPermisos` | `backend/src/test/java/com/uade/tpejemplo/model/` | S* | 27/10 | `Permisos` no tiene tests |

## API

| ID | Qué | Ruta | Tam. | Prioridad | Motivo |
|---|---|---|---|---|---|
| A-2 | Quitar `PUT /api/admin/usuarios/{id}/permisos` o justificarlo | `…/controller/AdminController.java` | S | 03/11 | Duplicado del de supervisor y sin uso en el front |
| A-3 | `GET /api/cobranzas/credito/{id}` con crédito inexistente responde 404 en vez de `[]` | `…/controller/CobranzaController.java`, `…/service/impl/CobranzaServiceImpl.java` | S* | 03/11 | Observación del mapa de API |

## Descartados (NO HACER)

| ID | Qué | Motivo |
|---|---|---|
| O8 | Pagos parciales (A-01) | Tamaño L y riesgo alto: cambia `Cuota.estaPagada()`, `Cobranza`, `Credito.saldo()`, el dashboard y la vista. Exigir el importe exacto (TPO-006) se defiende para este alcance. Va como pendiente en el reporte |
| O9 | `EstadoCredito` como patrón State | El estado es derivado, no se guarda y hay una sola transición con regla (`Credito.anular()`). Sobreingeniería; el apunte advierte contra confundir Strategy con State. Respuesta para la defensa |
| O10 | Strategy para punitorios, Adapter sobre `PasswordEncoder`, Adapter sobre `fetch` | Ninguno tapa un hueco: no hay punitorios, `PasswordEncoder` ya es la abstracción de Spring y `api/apiClient.js` ya hace de pasarela |
| S6 | Una sola fuente de autorización por rol (sacar `@PreAuthorize` o las reglas de URL) | Decisión: se mantienen las dos. Las reglas de URL de `…/config/SecurityConfig.java` cubren las tres zonas y `@PreAuthorize` en `AdminController` y `SupervisorController` repite el control en el método: defensa en profundidad, si alguien cambia una ruta el método sigue protegido |
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
| A-8 | `DELETE /api/clientes/{dni}`, `PUT` o `DELETE` real de crédito y de cobranza, CRUD de cuota, `GET /api/creditos/{id}/cuotas` | Romperían el historial o las cuotas ya generadas, o son redundantes con `CreditoResponse.cuotas` |
