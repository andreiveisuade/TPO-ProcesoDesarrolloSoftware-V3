# Dashboard de préstamos

Sistema interno de una financiera: clientes, créditos en cuotas (interés simple o sistema francés), cobranzas,
anulaciones y dashboard de supervisor. TPO de Proceso de Desarrollo de Software (UADE, 2C 2026, grupo 7),
iteración 3: MVC + patrones. El cambio respecto de V2 se ve con `git diff v2..main`.

## Levantarlo

Requiere JDK 21, Maven y Node.

```bash
cd backend && mvn spring-boot:run              # http://localhost:8080
cd frontend && npm install && npm run dev      # proxy /api → :8080
```

Usuarios de prueba (password = usuario): `admin`, `supervisor`, `user`.

Tests: `cd backend && mvn test` (26 tests).

## Documentación

- [Manual](docs/manual/index.html)
- [Reporte de la iteración 3](docs/reporte/reporte-v3.html)
- [Swagger](http://localhost:8080/swagger-ui.html) (con el backend levantado)
- [Lista de mejoras](docs/entrega/lista-mejoras.md)
- [Casos de uso](docs/casos-de-uso/README.md)
- Demo guiada: `bash docs/demo.sh`
- [Backlog](docs/backlog.md)
