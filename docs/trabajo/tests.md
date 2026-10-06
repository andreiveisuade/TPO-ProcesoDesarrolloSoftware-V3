# Tests automáticos (TPO-011)

## Estado previo

`backend/src/test` solo tenía `TpEjemploApplicationTests.contextLoads()` (`@SpringBootTest`): verifica que el contexto levanta, nada de dominio. `mvn test` corría y pasaba. La verificación real era el smoke manual con curl (`smoke.md`).

## Qué se testea ahora

Tests unitarios de dominio puro, JUnit 5 + AssertJ (vienen en `spring-boot-starter-test`), sin contexto de Spring. Paquete espejo de `model`. Correr con `cd backend && mvn test`.

| Clase de test | Cubre |
|---|---|
| `model/plan/InteresSimpleTest` | total independiente de la cantidad de cuotas, redondeo de cuota, tasa 0, tasa con decimales (coeficiente a 4 decimales) |
| `model/plan/SistemaFrancesTest` | fórmula francesa con números a mano (1000 al 10% en 2 cuotas = 576,19), total = suma exacta de cuotas, tasa 0 |
| `model/CreditoTest` | plan de cuotas, VIGENTE → CANCELADO al pagar todo, ANULADO, `saldo()`, `puedeAnularse()`, doble anulación, anulación con cobranza vigente (M2) y con la única cobranza anulada (M8) |
| `model/CuotaTest` | `estaVencida()` (y con fecha fija: el día del vencimiento no está vencida, el siguiente sí), `estaPagada()`, cobranza anulada deja la cuota impaga, doble cobro, cobro sobre crédito anulado (M1), importe validado |
| `model/CobranzaTest` | fecha de hoy, anulación el mismo día, rechazo de anular una cobranza de otro día |
| `controller/CodigosHttpTest` | `@WebMvcTest` de `ClienteController` y `SupervisorController` con `SecurityConfig` y `JwtAuthFilter` reales y los servicios mockeados: 400 (validación de `@Size`, JSON roto, path variable de tipo incorrecto), 401 (sin token, token inválido), 403 (ADMIN contra `/api/supervisor`), 404 y 405 |

Resultado: 36 tests, todos pasan (`mvn -q test`, exit 0). Sin bugs encontrados.

### Validación de DTOs (I-2)

`@Size(max = 15)` en `dni` / `dniCliente`, `@Size(max = 255)` en `nombre` / `username`, `@Digits(8,2)` en `deudaOriginal`, `@Digits(3,2)` en `tasaInteres`, `@Digits(10,2)` en `importe`. Un valor fuera de rango ahora da 400 por `handleValidation` en vez de 500 o redondeo silencioso; lo cubre `dniDeMasDe15CaracteresDa400`.

### Fecha de hoy por parámetro

`Cobranza.anular(LocalDate hoy)` y `Cuota.estaVencida(LocalDate hoy)`; las versiones sin argumento delegan con `LocalDate.now()`, así que servicios y DTOs no cambian y no entra Spring en las entidades. Se eligió el parámetro y no un `Clock` porque alcanza para testear y no obliga a cambiar firmas de servicios ni el mapeo a DTO.

### Diferencias de centavos documentadas

- `InteresSimple`: la cuota se redondea a centavos, así que `cuotas x importeCuota` no siempre cierra con `totalADevolver`. 10.000 al 45% en 6: total 14.500,00, cuotas 6 x 2.416,67 = 14.500,02 (se cobran 2 centavos de más). Tasa 0, 1.000 en 3: 3 x 333,33 = 999,99 (1 centavo de menos).
- `SistemaFrances`: `totalADevolver` se define como `importeCuota x n`, así que cierra siempre con las cuotas; la diferencia queda contra el capital (tasa 0, 1.000 en 3 → 999,99).

## Qué queda sin cubrir

- `Permisos` / `IPermisos`: los está tocando la rama `fixes-auditoria`.
- Services, repositories y queries del dashboard.
- Controllers fuera de clientes y supervisor (los códigos los resuelve el mismo handler).
- Front.

## Próximos tests, en orden de prioridad

1. `@DataJpaTest` de las queries del dashboard (M3) sobre H2 con un set chico de créditos, cuotas vencidas y cobranzas anuladas.
2. Tests de `Permisos`.
