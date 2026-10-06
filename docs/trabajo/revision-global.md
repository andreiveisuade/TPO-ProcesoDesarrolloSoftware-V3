# Revisión global V3 (T30, 06/10/2026)

Base: `main@aaed9b5`. Solo lectura sobre código y entregables.

## Resultado de ejecución

| Chequeo | Resultado |
|---|---|
| `cd backend && mvn -q test` | exit=0, 25 tests (suma de `target/surefire-reports`) |
| `cd frontend && npm run build` | exit=0 |
| `bash docs/demo.sh --headless` | exit=0, 23 tabs, ninguna ruta faltante |
| `git archive HEAD \| tar -t` | sin `docs/trabajo`, `target/`, `node_modules/`, `dist/`, `.classpath`, `.project`, `.factorypath`, `.idea`, `.DS_Store` |
| `git log v2..main` con claude/co-authored/anthropic/generated | 0 |
| Clases y métodos citados en `docs/entrega/lista-mejoras.md` | todos existen en `backend/src/main/java/com/uade/tpejemplo/` |
| Clases de `docs/diagramas/clases-v3.puml` | todas existen en el código |
| Javadoc en `backend/src/main/java` | 0 |

## Checklist de la consigna (`docs/trabajo/consigna-iteracion3.md`)

| Pide | Dónde | Estado |
|---|---|---|
| Diagrama de clases actualizado | `docs/diagramas/clases-v3.puml` + `clases-v3-general.svg`, `clases-v3-modelo.svg` | OK |
| Código | `backend/`, `frontend/` (tests y build verdes) | OK |
| Lista de mejoras hechas y pendientes | `docs/entrega/lista-mejoras.md` | OK |
| Foco Strategy | M9: `model/interfaces/CalculoDeCuota.java`, `model/plan/InteresSimple.java`, `model/plan/SistemaFrances.java`, `model/Credito.java` | OK |
| Foco Adapter | M7: `service/TokenService.java`, `security/JwtUtil.java`, `security/UsuarioDetails.java` | OK |
| Diagrama normalizado (3 compartimentos, relaciones, nada suelto) | `docs/diagramas/clases-v3.puml` | OK (DTOs, repos y config omitidos a propósito, ver I3) |
| Por qué de cada patrón, esquema problema / regla / consecuencia | `docs/reporte/reporte-v3.html` M1..M10 | OK |
| GRASP/SOLID de fondo en M7 y M9 (veredicto §4) | reporte: Indirection, Pure Fabrication, Protected Variations, Polymorphism, Object Adapter, sobre-ingeniería, `setEstrategia` presentes | OK |
| Diagramas por mejora | `docs/reporte/puml/m*-antes/despues.svg` | OK |
| Timeline V0 → V3 | reporte, sección "Timeline" | OK |
| Formato zip desde `git archive` | `.gitattributes` excluye `docs/trabajo` | PARCIAL (ver B1) |
| Ubicación MVC de cada clase | reporte "MVC en Spring Boot", paquetes del diagrama general | OK |
| Asistencia de todos a la defensa | fuera del repo | n/a |

## BLOQUEANTE

**B1. El reporte y el manual enlazan e incrustan archivos de `docs/trabajo/`, que no entra al zip.**
Evidencia: `docs/reporte/reporte-v3.html` tiene `src="../trabajo/capturas/{dark,ui-antes,ui-despues}/*.png"` (6 imágenes) y links a `../trabajo/{api,smoke,tests,ui,verificacion-final,visual}.md` y `../trabajo/capturas/final/`; `docs/manual/index.html` linkea `../trabajo/{api,smoke,tests,ui,verificacion-final,visual}.md` y `ui.md#dark-theme`. En el zip la sección "Capturas de la UI" queda con imágenes rotas y ~16 links muertos.
Arreglo mínimo: mover las 6 capturas usadas a `docs/reporte/capturas/` (o incrustarlas como data URI desde `docs/reporte/build/build.py`) y sacar o convertir en texto los links a `../trabajo/*.md`. Alternativa: dejar de excluir los `.md` puntuales de `docs/trabajo` en `.gitattributes`. Verificar con `git archive HEAD | tar -x -C /tmp/x` y abrir el HTML.

## IMPORTANTE

**I1. Orden del reporte: Strategy y Adapter aparecen 7.º y 9.º.** La consigna pone el foco en esos dos patrones y la lista de mejoras abre con M1..M6 de bugs. `docs/demo.sh` ya los pone primero; el reporte (`docs/reporte/reporte-v3.html`, "Mejoras al dominio") y `docs/entrega/lista-mejoras.md` no. Arreglo: sin renumerar, agregar un párrafo inicial "Foco de la iteración: M9 Strategy y M7 Adapter" con link a cada sección, o reordenar las filas de la tabla.

**I2. Tests "25 = 24 de dominio + contexto" sin detalle en la lista.** `docs/entrega/lista-mejoras.md` fila Tests y `docs/manual/index.html:686` dicen 25 (coincide con surefire), pero `docs/trabajo/tests.md`, que tiene el desglose, no entra al zip. Arreglo: listar en el manual las clases de test (`CobranzaTest`, `CreditoTest`, `CuotaTest`, `plan/*`) en una línea.

**I3. El diagrama general omite DTOs, repositorios, excepciones y config (25 clases).** `docs/diagramas/clases-v3.puml` no tiene `CreditoRepository`, `GlobalExceptionHandler`, `SecurityConfig`, `CreditoResponse`, etc. El profe dijo "ninguna clase suelta" y flexibiliza faltantes solo si se explica. Arreglo: una nota en el diagrama ("se omiten DTOs, repositorios Spring Data y config; ver paquetes") y decirlo en la defensa.

**I4. M7 Adapter: el adaptado es jjwt, no `JwtUtil`.** La lista dice "JwtUtil detrás de TokenService" sin nombrar jjwt como Adaptee. El apunte advierte que si podés tocar la clase no es Adapter. Arreglo: en la fila M7 de `docs/entrega/lista-mejoras.md`, "Target `TokenService`, Adapter `JwtUtil`, Adaptado jjwt (`Jwts`)".

**I5. Pendiente H1 es un bug visible en vivo.** Anular dos veces una cobranza responde 204 (`model/Cobranza.java` `anular`). Si el profe lo prueba en la demo queda mal. Arreglo: una guarda de 2 líneas en `Cobranza.anular` + test, o no tocarlo en vivo.

## MENOR

- **N1.** Pendiente con ID `M9` en `docs/entrega/lista-mejoras.md` (tasa con unidad declarada) colisiona con la mejora hecha M9. Renombrar a `M9b` o `P-M9`.
- **N2.** `README.md` no menciona `docs/casos-de-uso/README.md` ni `docs/demo.sh`, ni cuántos tests hay. Agregar dos líneas.
- **N3.** `docs/manual/index.html` linkea `http://localhost:8080/swagger-ui.html`: correcto, pero aclarar "con el backend levantado" como en el README.
- **N4.** El zip incluye `docs/reporte/build/*.py` (generador del reporte). No molesta, pero es proceso; evaluar excluirlo en `.gitattributes`.
- **N5.** `docs/backlog.md` entra al zip y se linkea desde el reporte: revisar que no tenga notas internas antes de entregar.

## Preguntas probables del profe

| # | Pregunta | Respuesta corta | Dónde mostrarlo |
|---|---|---|---|
| 1 | ¿Dónde está el Strategy y por qué no es sobre-ingeniería? | Contexto `Credito`, estrategia `CalculoDeCuota`, concretas `InteresSimple` y `SistemaFrances`; son dos algoritmos reales que el negocio pide, y antes era un `if` por plan que crecía. OCP + Polymorphism. | `model/interfaces/CalculoDeCuota.java`, `model/Credito.java` constructor y `totalADevolver` |
| 2 | ¿Se puede cambiar la estrategia en runtime? | No: el plan queda fijo al otorgar el crédito (`TipoPlan`); no hay `setEstrategia` porque cambiar el plan de un crédito otorgado no tiene sentido de negocio. | `model/TipoPlan.java` |
| 3 | ¿Qué adapta el Adapter si `JwtUtil` es suyo? | Adapta jjwt (librería que no podemos tocar) al Target `TokenService`; los clientes (`JwtAuthFilter`, `AuthServiceImpl`) no ven tipos de jjwt. Object Adapter. DIP + Protected Variations. | `service/TokenService.java`, `security/JwtUtil.java` `extraerUsername`, `esValido` |
| 4 | ¿Y `UsuarioDetails`? | Adapta nuestro `Usuario` a `UserDetails` que exige Spring Security. | `security/UsuarioDetails.java` |
| 5 | ¿Dónde está MVC? | Vista React, Controlador `controller/*` + `GlobalExceptionHandler`, Modelo `service` + `model`. Ejemplo M4: el permiso se valida en el backend, no solo en la vista. | diagrama general, `controller/CreditoController.java` `anularCredito` |
| 6 | ¿Por qué `EstadoCredito` no es un State? | Es un valor derivado del saldo y la anulación, no cambia el comportamiento del crédito por estado (O9). | `model/EstadoCredito.java`, `model/Credito.java` `estado` |
| 7 | ¿Qué Information Expert aplicaron? | La cuota sabe si acepta un cobro (M1) y si está vencida (M6); el crédito sabe su saldo y si puede anularse (M8). | `model/Cuota.java` `registrarCobranza`, `estaVencida`; `model/Credito.java` `puedeAnularse` |
| 8 | ¿Qué quedó pendiente y por qué? | O6 plan en constructor (riesgo JPA), O7 saldo en dashboard, O8 pagos parciales, H1 doble anulación, tests web. Todo con motivo. | `docs/entrega/lista-mejoras.md` "Pendientes" |
