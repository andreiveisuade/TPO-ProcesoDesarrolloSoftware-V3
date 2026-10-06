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

## 4. Análisis del apunte (resumen de patrones subido a Teams, clase 10)

**Pendiente: el PDF no está en ~/Downloads (06/10).** Cuando Andrei lo baje: moverlo a `01_Material_de_Clase/CLASE_10_<nombre>.pdf` y completar esta sección.

Lo que se sabe por la grabación:
- Resumen de "todos los patrones que por lo menos vimos hasta ahora" [21:58-22:05]: GRASP primero, después SOLID [22:52-23:02], y anticipa los "patroncitos" de MVC para la próxima iteración [23:36-23:44].
- Estructura fija por patrón: problema que resuelve, reglas que se aplican, consecuencias [22:24-22:28].
- Ubicación: Teams, carpeta clase 10 [23:55].
- Aplicación al dashboard (a confirmar con el texto): usar ese esquema como plantilla de cada mejora del reporte V3.

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
