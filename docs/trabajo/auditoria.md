# Auditoría T10 — iteración 3 (main@61b7f74 vs v2)

Revisión de solo lectura. Alcance: `git diff v2..main -- backend frontend`, `docs/trabajo/m*.md`, consigna, tablero. Rama `api-swagger` ignorada.

## BLOQUEANTE

### B1. No existe el diagrama de clases V3
- Evidencia: la consigna pide tres elementos (diagrama + código + lista de mejoras), consigna-iteracion3.md §1. `docs/reporte/` está vacío; en `docs/trabajo/` solo hay `mN-despues.puml` parciales por mejora. No hay tarea en el tablero que lo produzca.
- Además el profe evalúa diagramación normalizada (tres compartimentos, relaciones tipadas, ninguna clase suelta).
- Arreglo mínimo: un `.puml` completo de V3 (sobre el de V2 de `docs-v0`/reporte) que sume `CalculoDeCuota`, `InteresSimple`, `SistemaFrances`, `TipoPlan`, `EstadoCredito`, `TokenService`, la relación `Credito 1--* Cuota` navegable, y los métodos nuevos de `Credito`/`Cuota`/`IPermisos`. Asignarlo como tarea en el tablero.

### B2. No existe la lista de mejoras consolidada (documento de entrega)
- Evidencia: solo hay 10 `m*.md` sueltos; `docs/reporte/` vacío. La defensa del 13/10 gira sobre la lista de mejoras hechas y pendientes (consigna §1 y §3), con timeline V0→V1→V2→V3 (AGENTS.md).
- Arreglo mínimo: T6 fase 2 — un reporte que liste M1..M10 con Strategy y Adapter primero, pendientes explícitos (403 sin token, N+1 residual, dashboard por estado, etc.) y el timeline.

### B3. M2 no está documentada ni declarada como absorbida
- Evidencia: no existe `m2.md`. El tablero dice "M2 se implementa sola solo si M8 no entra (M8 la absorbe)". El cambio real está: `Credito.tieneCobranzas()` ahora ignora cobranzas anuladas (`Credito.java` `cuotas.stream().anyMatch(Cuota::estaPagada)` + `Cuota.java:65`), pero `m8.md` no lo cuenta como el cierre de M2.
- Arreglo mínimo: una línea en `m8.md` (Solución/Por qué): "absorbe M2: un crédito cuyas cobranzas están todas anuladas ya puede anularse". En la lista de mejoras, M2 → "cubierta por M8".

## IMPORTANTE

### I1. `M4.md` muestra código que ya no existe en main
- Evidencia: `docs/trabajo/M4.md:44` muestra `credito.anular(cobranzaRepository.existeCobranzaDelCredito(id));` como "Solución". En main (`CreditoServiceImpl.java` `anularCredito`) es `credito.anular();` y `existeCobranzaDelCredito` fue borrado del repositorio por M8. Si el profe compara doc con código en vivo, choca.
- Arreglo mínimo: actualizar el bloque "Solución" de M4 al código de main, o aclarar "código al momento de M4, luego modificado por M8".

### I2. Carga de cobranzas por efecto lateral (query cuyo resultado se descarta)
- Evidencia: `CreditoServiceImpl.buscarCredito` llama `cuotaRepository.buscarPorCredito(id);` sin usar el resultado, y `listarPorCliente` hace `cuotaRepository.buscarPorCliente(dniCliente);` igual. Funciona solo porque el persistence context de la transacción hidrata `Cuota.cobranzas` de las mismas instancias. Leído en frío parece código muerto; un compañero lo borra y `estaPagada()` tira `LazyInitializationException` (o hace N+1 dentro de la tx).
- Pregunta del profe probable: "¿esa línea para qué está?".
- Arreglo mínimo: o explicarlo en `m8.md` (Consecuencias), o reemplazar por un `JOIN FETCH` único (`LEFT JOIN FETCH c.cuotas cu LEFT JOIN FETCH cu.cobranzas` — ojo con MultipleBagFetchException si ambas son `List`; ahí convertir a `Set` o dejar como está y documentarlo). Lo más barato: documentar.

### I3. `IPermisos` duplica getters (slop)
- Evidencia: `model/Permisos.java` agrega `permiteAnularCredito()`/`permiteAnularCobranza()` que devuelven exactamente lo mismo que los existentes `isPuedeAnularCredito()`/`isPuedeAnularCobranza()` (usados en `AuthResponse.java:26`, `UsuarioResponse.java:24`). Dos métodos idénticos en la interfaz.
- Arreglo mínimo: borrar los nuevos y usar `isPuedeAnular*()` en `CreditoServiceImpl`/`CobranzaServiceImpl`, o defender el nombre de dominio y deprecar los `is*` (más trabajo, no vale la pena). Actualizar M4.md.

### I4. `tasaInteres` cambia de semántica según el plan y la UI lo muestra igual
- Evidencia: `InteresSimple` interpreta % total; `SistemaFrances` % mensual (`SistemaFrances.java` `i = tasa/100` por período). El `<select>` lo aclara al crear, pero el listado (`Creditos.jsx` línea `Deuda: ${cr.deudaOriginal} + {cr.tasaInteres}% = ${cr.totalADevolver}`) presenta la tasa como si fuera simple; para francés "10.000 + 5% = 13.xxx" no cierra. Además `CreditoResponse` no expone `tipoPlan`, así que el front no puede distinguirlo.
- Arreglo mínimo: sumar `tipoPlan` a `CreditoResponse` y mostrarlo en el listado. Sin eso, en la demo en vivo un crédito francés se lee como error de cálculo.

### I5. Strategy: el profe va a preguntar "¿quién elige la estrategia?" y "¿dónde está el setEstrategia?"
- Estado: defendible. Roles correctos (Context `Credito`, Strategy `CalculoDeCuota`, concretas en `model/plan`), dos algoritmos reales, sin `if/switch` en el Contexto (lo resuelve el enum `TipoPlan`).
- Flancos: (a) el Contexto no guarda la estrategia sino el enum y llama `tipoPlan.calculo()` en cada uso — hay que explicar que es porque se persiste (JPA no persiste una interfaz); (b) no hay cambio en runtime: el plan se fija al otorgar, a propósito (cambiarlo alteraría cuotas ya emitidas); (c) "¿dos algoritmos no es sobre-ingeniería?" — respuesta: el francés es el sistema real de préstamos y reabre la decisión del 15/09 (m9.md ya lo dice).
- Falta en `m9.md` (lo pidió el análisis del apunte, consigna §4): GRASP/SOLID de fondo (Polymorphism, Protected Variations, DIP; hoy solo OCP), "cuándo usarlo", diagrama, y los puntos (a) y (b). Sin encabezado `## Patrón` (usa negrita), inconsistente con el resto.

### I6. Adapter: el apunte dice "usalo cuando NO podés tocar la clase"
- Estado: Adapter 1 (`JwtUtil implements TokenService`) es defendible solo si se presenta como "adaptamos jjwt", no "adaptamos JwtUtil"; `m7.md` ya pone jjwt como Adaptee, bien. Adapter 2 (`UsuarioDetails`) es el ejemplo más limpio: `Usuario` es nuestro pero no queremos que el dominio dependa de Spring Security; `UserDetails` es el Target que no controlamos.
- Pregunta incómoda: "`TokenService` vive en `service/` pero su única implementación está en `security/` y la firma recibe `UserDetails`: ¿el Target no está acoplado al framework?". Respuesta: sí, está anotado en Consecuencias; el próximo paso sería `esValido(String token, String username)`.
- Otra: "¿una interfaz con una sola implementación?" Respuesta: DIP + testeo; el apunte lo marca como costo aceptable.
- Falta en `m7.md`: GRASP/SOLID completos (Indirection, Pure Fabrication, Protected Variations, SRP, OCP), variante Object Adapter (por composición sobre jjwt), diagrama, costo de mantenerlo si jjwt cambia.

### I7. Archivos sin trackear
- Evidencia: `git status` → `?? docs/trabajo/api-propuesta.md`, `?? docs/trabajo/smoke.md`. `smoke.md` es la evidencia de que todo funciona (22 OK); si no se commitea, se pierde y no entra al `git archive`.
- Arreglo mínimo: commitear `smoke.md`; `api-propuesta.md` va con la rama `api-swagger` (T9), no en main.

## MENOR

### m1. Nombres de archivos de docs inconsistentes
- `M4.md` / `M4-despues.puml` en mayúscula; el resto `mN.md`. Falta `m2.md`, `m4-*`, `m8-despues` existe pero el tablero dice que los diagramas de M8 de fase 1 tenían el de M7 (rehacer).
- Arreglo: `git mv M4.md m4.md` y `M4-despues.puml m4-despues.puml`.

### m2. Plantilla de docs no uniforme
- `m1.md`, `m3.md`, `m5.md` no tienen sección `## Consecuencias` (la consigna §3 pide sumarla). `m3.md` no tiene `## Patrón`. Algunos encabezados dicen "Problema (código antes)", otros "Problema".
- Arreglo: agregar Patrón/Consecuencias faltantes; un párrafo cada una.

### m3. Handler de `AuthenticationException` no cubre el caso que el tablero espera
- Evidencia: `GlobalExceptionHandler.handleAuth` solo atrapa excepciones que lleguen al dispatcher (p. ej. `BadCredentialsException` del login vía `AuthServiceImpl`). Una request sin token la corta el filtro de Spring Security antes → sigue siendo 403 (pendiente ya anotado en el tablero). `m5.md` no debería prometer 401 para "sin token".
- Arreglo: confirmar que `m5.md` no lo prometa; listar el `AuthenticationEntryPoint` como pendiente (o lo resuelve T9).

### m4. Comentario obsoleto en `Dashboard.jsx`
- Evidencia: `frontend/src/pages/Dashboard.jsx` conserva `// Solo disparamos la petición si el usuario es supervisor` y ahora incluye ADMIN.
- Arreglo: borrar o corregir la línea.

### m5. `SistemaFrances.totalADevolver` = cuota redondeada × n
- Evidencia: `SistemaFrances.java` `importeCuota(...).multiply(n)`. Correcto y consistente con las cuotas emitidas (todas iguales), pero la última cuota no ajusta centavos; con `InteresSimple` pasa lo mismo y V2 ya lo documentaba como aceptable. Cálculo verificado: fórmula `C·i/(1-(1+i)^-n)` bien, tasa 0 cubierta.
- Arreglo: ninguno; mencionarlo en Consecuencias de m9 si preguntan.

### m6. `@NotNull` + `columnDefinition` con default en `tipo_plan`
- Evidencia: `Credito.java` `columnDefinition = "varchar(20) default 'INTERES_SIMPLE'"`. Necesario por `ddl-auto=update` con datos previos; atado a H2/SQL genérico. Aceptable; se defiende como migración mínima.

### m7. Sin tests nuevos
- Evidencia: `backend/src/test` solo tiene `TpEjemploApplicationTests.java`. `m9.md` dice "cada fórmula se testea aislada" pero no hay ningún test. No es requisito de la consigna, pero el doc promete algo que no existe.
- Arreglo: suavizar a "se puede testear aislada", o un test de 10 líneas para `SistemaFrances` (10.000, 5%, 12 → 1.128,25).

## Proceso

- Commits: mensajes en español, imperativo, con TPO-NNN donde aplica. Sin atribución a IA (verificado `git log v2..main --format=%B`). Bien.
- Ramas/worktrees: solo `main` y `api-swagger` (en curso, ignorada). No quedan ramas `m*` ni worktrees colgados.
- main local adelantado a `origin/main`: tablero dice "sin push". Pendiente push (confirmar con Andrei).
- Faltan para la entrega: diagrama V3 (B1), reporte/lista (B2), zip desde `git archive` + `diff -rq`, subida a Teams carpeta Clase 11 antes del 13/10, re-smoke tras los arreglos.

## Convenciones

- `XService` + `impl` respetado; `TokenService` en `service/` con impl en `security/JwtUtil` rompe la simetría (la impl no está en `service/impl`). Defendible (es infraestructura), pero decirlo.
- `CalculoDeCuota` en `model/interfaces` sin prefijo `I` (el resto: `ICredito`, `ICuota`, `IPermisos`). Inconsistencia de nombres; renombrar a `ICalculoDeCuota` o justificar que es un rol de patrón y no la interfaz de una entidad.
