# T36 — creator (O6 + O7)

Rama `creator-dashboard`.

## O6 — Creator completo

- **Problema.** `Credito.nuevo` devolvía un crédito sin cuotas; `CreditoServiceImpl.crear` tenía que llamar a `generarPlanDeCuotas()` y `cuotaRepository.saveAll(...)`. Si se olvidaba, el crédito quedaba VIGENTE con saldo 0 para siempre.
- **Cambio.** `model/Credito.java`: el constructor llama a `generarPlanDeCuotas()` (ahora privado) y `cuotas` tiene `cascade = CascadeType.PERSIST`. `model/interfaces/ICredito.java`: sale `generarPlanDeCuotas`. `service/impl/CreditoServiceImpl.java#crear`: guarda solo el crédito. Tests (`CreditoTest`, `CuotaTest`, `CobranzaTest`) usan `getCuotas()`.
- **Por qué.** Creator: el crédito contiene y agrega sus cuotas, así que las crea. El agregado nace completo y el service no conoce su estructura interna.
- **Consecuencias.** El fetch no cambia: las lecturas siguen con `buscarConCuotas`/`buscarTodosConCuotas` + precarga de cobranzas (sin N+1 ni LazyInitializationException con open-in-view en false).
- **Commit.** d89d62d

## O7 — Saldo pendiente y monto vencido en el dashboard

- **Problema.** El dashboard no mostraba mora ni saldo (A-02 y A-05 de los requerimientos v0); había que entrar crédito por crédito.
- **Cambio.** `dto/response/DashboardStatsResponse.java`: `saldoPendiente` y `montoVencido`. `service/impl/DashboardServiceImpl.java#obtenerEstadisticasGenerales`: suma `Credito.saldo()` y las cuotas `Cuota.estaVencida()` de los créditos no anulados, sobre la carga que ya hacía. `frontend/src/pages/Dashboard.jsx`: dos tarjetas con el mismo estilo.
- **Por qué.** Information Expert: la regla de saldo y de vencimiento vive en el modelo; una query la duplicaría.
- **Consecuencias.** Sin queries nuevas. Sin estado EN_MORA ni punitorios.
- **Commit.** ver `git log` (commit O7).
