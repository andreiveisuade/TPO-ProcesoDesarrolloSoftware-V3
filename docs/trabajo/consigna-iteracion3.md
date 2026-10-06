# Consigna — Iteración 3 (entrega 13/10/2026)

Fuentes: grabación clase 10 (06/10, min 0-25, whisper con mucho ruido hasta ~08:30), resumen clase 9, slides `CLASE_09_Patrones_mvc_strategy_adapter.pdf`. Las citas son textuales de la transcripción (con sus errores de whisper; entre corchetes, la lectura probable).

## 1. Qué se entrega, formato y cuándo

- **Tres elementos**, los mismos que pidió para la entrega final en clase 9: **diagrama de clases actualizado + código + lista de mejoras/cambios** (hechos y pendientes).
  - [16:48] "necesito los tres elementos como entrega de la iteración de tres."
  - [19:25] "en el 11 tienen la entrega, de nuevo, la entrega son los tres elementos"
- **Dónde:** carpeta de Teams creada por el profe para la entrega de la iteración, bajo **Clase 11** (la estaba renombrando en vivo: [17:09] "Esta es la clase 10. La clase 11, ahora la modifico. [17:14] Acá tienen la entrega de la iteración.").
- **Cuándo:** antes del martes 13/10. [17:33] "Antes del martes que viene, entregan estos 3 elementos".
- **Formato:** no lo especificó. Mantenemos el de iteraciones anteriores: un zip por grupo (desde `git archive`) con código, diagrama y documento de mejoras.
- **Ese día (13/10):** defensa oral sobre la lista de mejoras. [17:39] "vamos a hablar sobre las iteraciones, principalmente sobre esta lista de mejoras, lo que vieron mejorar."
- **Foco temático:** [16:32] "Ahora, para la próxima, solo nos enfocamos en estos dos patrones." Por contexto (slides clase 9) son **Strategy y Adapter**; MVC queda como base ya vista: [16:42] "Si mucho avanzaste en el otro, en MVC, no pasa nada".
- Iteraciones anteriores: si falta algo de la anterior, revisarlo [17:46]. Una vez defendida, la iteración queda cerrada [18:52-18:58].

## 2. Criterios de evaluación

- **No hay segundo parcial escrito**: la nota sale de las iteraciones. [15:54] "Con las iteraciones yo pretendo, por grupo, poner la segunda nota." / [17:54] "La fecha de parcial[...] va a ser que le ponga una nota de todas las iteraciones que realizamos."
- **Asistencia de todos** a las iteraciones, cuenta en la nota individual. [18:08] "tienen que venir a las iteraciones" / [18:18] "Eso influye en esa nota individual."
- **Diagramación normalizada** (lección del parcial 1, aplica al diagrama de la entrega): cada clase con sus tres compartimentos (nombre, atributos, métodos), relaciones tipadas, ninguna clase suelta. [09:41] "las clases no tenían los tres elementos fundamentales. [09:49] Atributo, método [...] o las relaciones no están definidas [...] [09:57] O la clase queda suelta." / [11:25] "el hecho de diagramar mal en este tipo de materias no hay chance." Faltar algunos métodos se flexibiliza si se explica el uso de patrones [11:13-11:22].
- **Explicar por qué se aplica cada patrón** (básico pero razonado) [13:12-13:20].
- Materia tipo taller: se evalúan las entregas, no la presencia en el taller [20:53-21:01].
- No se pide aplicar todo: [23:23] "La idea no es aplicar todo, pero la idea sí es modificar y mejorar mejor nuestros proyectos."

## 3. Reporte y bitácora

- La **lista de mejoras** es el centro de la defensa [17:39]. Clase 9: la lista final debe incluir cambios hechos y pendientes, "no solo los del repositorio".
- Sugirió armar un documento tipo "SharePoint del proyecto" siguiendo el esquema del apunte, **patrón por patrón**: qué problema resuelve, qué reglas se aplican, qué consecuencias tiene [22:32-22:51]. Encaja con nuestro formato Patrón → Problema → Solución → Por qué; conviene agregar **Consecuencias**.
- No mencionó la bitácora explícitamente en este tramo (min 0-25).

## 4. Análisis del apunte (ADOO, Repaso Integrador GRASP · SOLID · Adapter · Strategy, clase 10)

Archivo: `01_Material_de_Clase/CLASE_10_ADOO_Repaso_GRASP_SOLID_Adapter_Strategy.pdf` (40 láminas).

**Qué dice.** Tres bloques: GRASP (9 patrones, láminas 4-14), SOLID (5 principios, 15-22) y dos patrones GoF, Adapter (24-31) y Strategy (32-38), con una comparación (39) y un mapa integrador (40). Tesis: GRASP es micro-decisión (a qué clase va cada responsabilidad), SOLID es criterio de auditoría del resultado, y los patrones de diseño nacen de aplicar ambos, no son una teoría aparte. Advierte que SOLID aplicado sin criterio es sobre-ingeniería.

**Estructura con la que documenta.**
- GRASP: una lámina por patrón con tres bloques fijos, *¿Qué problema resuelve?* / *Regla de asignación* / *Consecuencia*. Es el esquema que el profe pidió replicar.
- SOLID: enunciado + antes (violación) / después (corrección) + GRASP relacionado.
- Adapter y Strategy (más larga): problema, intención + analogía, diagrama de clases, código Java, fundamentos (qué GRASP y qué SOLID hay detrás), ventajas / desventajas / cuándo usarlo, casos reales.

**Adapter.**
- Roles: Cliente, Target (`ITarget`, la interfaz que el cliente espera), Adapter (implementa Target y contiene al Adaptado), Adaptado (clase existente que no se puede tocar). El Cliente solo conoce el Target; el Adaptado no sabe que el Adapter existe.
- Variante: Object Adapter (composición). Class Adapter necesita herencia múltiple y en Java no es viable.
- Cuándo: hay que integrar código de terceros o legacy **que no podés modificar**. Si se puede tocar la clase origen, es más simple modificarla.
- Errores típicos: usarlo cuando se puede cambiar la clase; acumular decenas de Adapters sobre un mismo subsistema (la pregunta real es si falta una Facade); olvidar mantenerlo sincronizado si el Adaptado cambia seguido; que el Target siga exponiendo tipos del Adaptado.
- Fundamentos: GRASP Indirection, Pure Fabrication, Protected Variations; SOLID SRP, OCP.

**Strategy.**
- Roles: Contexto (guarda la estrategia y delega), Estrategia (interfaz), EstrategiaConcreta A/B/C. Se cambia en runtime (`setEstrategia`); es composición, no herencia. Las estrategias no se conocen entre sí (a diferencia de State, donde sí conocen la transición).
- Cuándo: una misma tarea con varios algoritmos intercambiables; señal de alarma, un `switch(tipoDeAlgoritmo)` que crece con cada caso. Se diseña desde el inicio junto al Contexto.
- Errores típicos: aplicarlo con dos algoritmos que casi nunca cambian (sobre-ingeniería); que el Contexto siga decidiendo el algoritmo con `if/switch`; que el cliente no sepa qué estrategias existen para elegir; confundirlo con State.
- Fundamentos: GRASP Polymorphism, Protected Variations; SOLID OCP, DIP.

**Qué GRASP/SOLID repasa.** GRASP completo: Information Expert, Creator, Controller, Low Coupling, High Cohesion, Polymorphism, Pure Fabrication, Indirection, Protected Variations. SOLID completo, con su correlato: SRP-High Cohesion, OCP-Protected Variations, LSP-Polymorphism, ISP-Low Coupling, DIP-Indirection/Protected Variations.

**Cómo se aplica al dashboard.**
- Cada mejora del reporte V3 se documenta con la plantilla problema / regla / consecuencia, sumando antes/después de código y los GRASP/SOLID de fondo (el apunte los pone explícitos).
- Strategy: cálculo de cuota (`CalculoDeCuota`, `InteresSimple`, `SistemaFrances`, Contexto `Credito`), M9. Es el caso del apunte: el `if` por plan habría crecido con cada sistema nuevo.
- Adapter: `JwtUtil` detrás de `TokenService` (jjwt como Adaptado) y `UsuarioDetails` sobre `UserDetails` (Spring Security), M7.
- Alerta de defensa: el apunte dice "usalo cuando NO podés tocar la clase origen". `JwtUtil` es código nuestro; lo adaptado de verdad es jjwt. Hay que defenderlo así (protegemos al cliente de la librería, DIP), no como "adaptamos JwtUtil".

**Contraste de M7 y M9 con la estructura del apunte** (no se editaron).

| | M7 (Adapter) | M9 (Strategy) |
|---|---|---|
| Problema / solución / por qué / consecuencias | Cumple | Cumple |
| Roles | Cumple, tabla Target/Adapter/Adaptee/Client para las dos instancias | Cumple, tabla Context/Strategy/Concrete |
| Código antes/después | Cumple | Cumple |
| GRASP/SOLID de fondo | Falta: solo menciona DIP. Faltan Indirection, Protected Variations, Pure Fabrication, SRP, OCP | Falta: solo menciona OCP. Faltan Polymorphism, Protected Variations, DIP |
| Diagrama de clases | Falta | Falta |
| Cuándo usarlo / sobre-ingeniería | Falta: no justifica por qué Adapter si `JwtUtil` es propio; indicar variante Object Adapter | Falta: no dice por qué hay dos estrategias reales ni el riesgo de sobre-ingeniería; solo vale la pena porque el francés es real |
| Desventajas del apunte | Cumple casi todo: ya anota la interfaz con una sola implementación y el `UserDetails` en `esValido`; falta el costo de mantener el Adapter si jjwt cambia | Parcial: falta que el cliente debe conocer los planes (resuelto con el `select` y el enum, mencionarlo) |
| Cambio en runtime | n/a | Aclarar que `tipoPlan` queda fijo al otorgar (no hay `setEstrategia` en caliente) |

Veredicto: M7 y M9 tienen que cambiar, solo para agregar los fundamentos GRASP/SOLID, el diagrama de clases y la justificación de "cuándo usarlo". La estructura base ya cumple.

## 5. Contraste con M1..M10 (dominio.md §6)

Lo que pide la consigna y no cubrimos bien:
- **Strategy y Adapter son el foco**, no opcionales. Hoy Adapter está en P2 (y la mitad es "solo documentar") y **Strategy en P3 condicionado a Regulo**. Hay que subir ambos a P1: Strategy del cálculo de cuota (interés simple / sistema francés) con código real, y Adapter de `JwtUtil` detrás de interfaz propia, más `UsuarioDetails` documentado.
- **Diagrama de clases V3** con los tres compartimentos y las clases nuevas (interfaz Strategy, estrategias concretas, interfaz Adapter). No figura en M1..M10: falta como tarea.
- **Documento de mejoras patrón por patrón** con problema / reglas / consecuencias (esquema del apunte).
- Ubicación MVC de cada clase (tarea de clase 9) sigue vigente como base, aunque no sea foco.

Lo que sobra o hay que reenfocar:
- Las P1 de bugs (cobro de crédito anulado, cobranzas anuladas, números del dashboard, handlers 401/403/404/405) no son de Strategy/Adapter. Valen como mejoras, pero presentarlas como MVC/Information Expert secundarias; no dejar que se coman el tiempo de Strategy.
- Permisos en backend (P1, M): buen ejemplo MVC; mantener si entra, pero detrás de Strategy y Adapter.
- `EstadoCredito` + agregado (P2, M, riesgo N+1): candidato a pendiente para el 27/10.
- Dashboard para ADMIN (P3): sacarlo de esta iteración.
