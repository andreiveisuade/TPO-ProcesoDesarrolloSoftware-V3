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
| `model/CuotaTest` | `estaVencida()`, `estaPagada()`, cobranza anulada deja la cuota impaga, doble cobro, cobro sobre crédito anulado (M1), importe validado |
| `model/CobranzaTest` | fecha de hoy y anulación el mismo día |

Resultado: 24 tests nuevos + `contextLoads`, todos pasan. Sin bugs encontrados.

### Diferencias de centavos documentadas

- `InteresSimple`: la cuota se redondea a centavos, así que `cuotas x importeCuota` no siempre cierra con `totalADevolver`. 10.000 al 45% en 6: total 14.500,00, cuotas 6 x 2.416,67 = 14.500,02 (se cobran 2 centavos de más). Tasa 0, 1.000 en 3: 3 x 333,33 = 999,99 (1 centavo de menos).
- `SistemaFrances`: `totalADevolver` se define como `importeCuota x n`, así que cierra siempre con las cuotas; la diferencia queda contra el capital (tasa 0, 1.000 en 3 → 999,99).

## Qué queda sin cubrir

- Rechazo de `Cobranza.anular()` para una cobranza de otro día: la fecha la pone el constructor con `LocalDate.now()` y no hay setter ni `Clock` inyectable. No se agregó setter (regla del brief).
- `Permisos` / `IPermisos`: los está tocando la rama `fixes-auditoria`.
- Services, repositories y queries del dashboard.
- Controllers y códigos HTTP, seguridad (JWT, roles).
- Front.

## Próximos tests, en orden de prioridad

1. `@WebMvcTest` de los controllers con los códigos HTTP de M5 (`BusinessException` → 4xx, no encontrado → 404), con los services mockeados.
2. `@DataJpaTest` de las queries del dashboard (M3) sobre H2 con un set chico de créditos, cuotas vencidas y cobranzas anuladas.
3. Tests de `Permisos` una vez mergeada `fixes-auditoria`.
4. Seguridad: endpoint sin token → 401, rol sin permiso → 403 (`@WebMvcTest` + `spring-security-test`, que habría que agregar).
5. Inyectar un `Clock` en `Cobranza` para poder testear el rechazo de anulación de otro día (cambio de código, decidirlo antes).
