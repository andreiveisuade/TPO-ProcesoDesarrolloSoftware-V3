# Dashboard de préstamos

Sistema interno de una financiera: clientes, créditos en cuotas (interés simple o sistema francés), cobranzas,
anulaciones y dashboard de supervisor.

TPO de **Proceso de Desarrollo de Software** — UADE, 2.º cuatrimestre 2026, grupo 7. Iteración 3: MVC + patrones
(entrega 13/10/2026).

## Estructura

| Carpeta | Qué es | Tecnología |
|---|---|---|
| `backend/` | API REST y reglas de negocio | Java 21, Spring Boot 3.4, JPA, H2, Spring Security + JWT |
| `frontend/` | Interfaz del personal | React 19, Redux Toolkit, Vite |
| [`docs/`](docs/README.md) | Manual, diagramas de clases, notas de cada mejora | PlantUML |

## Levantarlo

Requiere JDK 21, Maven y Node.

```bash
cd backend && mvn spring-boot:run              # http://localhost:8080
cd frontend && npm install && npm run dev      # proxy /api → :8080
```

Usuarios de prueba (password = usuario): `admin`, `supervisor`, `user`. Swagger: <http://localhost:8080/swagger-ui.html>.

## Documentación

- [Manual](docs/manual/index.html): actores, reglas R1..R18, casos de uso, MVC, patrones, seguridad, decisiones y pendientes.
- [`api.md`](docs/trabajo/api.md): mapa de endpoints.
- [`tests.md`](docs/trabajo/tests.md) y [`smoke.md`](docs/trabajo/smoke.md): cómo se verifica.
- [`docs/diagramas/`](docs/diagramas/): diagramas de clases V3.

## Pendiente

Ver [Pendientes y bugs](docs/manual/index.html#pendientes) en el manual.

## Convenciones

- Las reglas de negocio van en el modelo; el front solo oculta acciones.
- Cada mejora se documenta como Patrón → Problema → Solución → Por qué (`docs/trabajo/mN.md`).
- Si cambia una regla o un endpoint, se actualiza el manual o `api.md` en el mismo commit.
