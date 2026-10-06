# Guía de lectura de V3 (~45 min)

Repo: `03_Trabajos_Practicos/TPO_Grupo07/V3`. Antes, leé los hallazgos en `docs/trabajo/revision-global.md` (5 min).

## 1. Reporte, 15 min — `docs/reporte/reporte-v3.html`

- Timeline V0 → V3: que cuente bien la reversión de interfaces (V1 las colapsa, V2 las restituye).
- M9 Strategy y M7 Adapter primero: roles, código antes/después, GRASP/SOLID, cuándo usarlo, consecuencias. Es lo que defiende la nota.
- M1..M6, M8, M10 de pasada: cada una con su hueco concreto (TPO-NNN).
- "Capturas de la UI": hoy linkean a `docs/trabajo/` (B1).
- Decidir: arreglo de B1 (mover capturas o incrustarlas) y si se reordena para abrir con M9/M7 (I1).

## 2. Lista de mejoras, 7 min — `docs/entrega/lista-mejoras.md`

- Es el centro de la defensa: chequeá que cada fila la puedas explicar en 30 segundos.
- Fila M7: nombrar jjwt como Adaptado (I4). Pendiente "M9" que choca con la M9 hecha (N1).
- Decidir: qué pendientes se prometen para el 27/10 (O6, O7, H1).

## 3. Diagrama, 8 min — `docs/diagramas/clases-v3-general.svg` y `clases-v3-modelo.svg`

- General: Vista / Controlador / Modelo, con `TokenService` → `JwtUtil`.
- Modelo: `Credito` ◇ `CalculoDeCuota` ← `InteresSimple`, `SistemaFrances`; tres compartimentos en todas.
- Decidir: agregar la nota de clases omitidas (I3).

## 4. Demo, 10 min — `bash docs/demo.sh`

- nvim con diff v2 | main por archivo, en el orden de la presentación (M9, M7, M8, M4, M5...).
- Practicá el recorrido M9 y M7 completo; ensayá quién dice qué.
- Levantar la app (`README.md`) y hacer: otorgar crédito francés, cobrar, anular como supervisor, dashboard como admin. Evitar anular dos veces la misma cobranza (H1).

## 5. Manual, 5 min — `docs/manual/index.html`

- Cómo se levanta y qué hace cada rol; links a `docs/trabajo/` rotos en el zip (B1).
- Decidir: si el manual va en la entrega o solo el README.

Al terminar: arreglos de B1 + los IMPORTANTE que elijas, `git archive` → `diff -rq` y subir a Teams (Clase 11) antes del 13/10.
