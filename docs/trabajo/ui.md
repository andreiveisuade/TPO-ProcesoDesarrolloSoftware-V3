# T25 — Mejoras chicas de presentación (front)

Solo se muestran campos que el backend ya devuelve (`CreditoResponse`, `CuotaResponse`, `CobranzaResponse`, `DashboardStatsResponse`, `ErrorResponse`). Sin librerías nuevas; el formateo vive en una sola util: `frontend/src/utils/formato.js`.

| Mejora | Por qué ayuda | Archivo | Antes | Después |
|---|---|---|---|---|
| Importes con moneda es-AR (`$ 120.000,00`) | `$120000` y `$55081.29` no se leen; separador de miles y coma decimal como en Argentina | `utils/formato.js`, `pages/Creditos.jsx`, `pages/Cobranzas.jsx`, `pages/Dashboard.jsx` | [créditos](capturas/ui-antes/03-creditos.png), [dashboard](capturas/ui-antes/05-dashboard.png) | [créditos](capturas/ui-despues/03-creditos.png), [dashboard](capturas/ui-despues/05-dashboard.png) |
| Fechas `dd/mm/aaaa` y columna Fecha en cobranzas (`fechaCobranza`) | ISO `2026-07-01` no es el formato local; la fecha de cobro ya venía y no se mostraba | `pages/Creditos.jsx`, `pages/Cobranzas.jsx` | [cobranzas](capturas/ui-antes/04-cobranzas.png) | [cobranzas](capturas/ui-despues/04-cobranzas.png) |
| Crédito: badge de estado (VIGENTE/CANCELADO/ANULADO), datos rotulados (deuda, plan y tasa, otorgado, total, cuota, saldo), "x de n cuotas pagadas" e importe por cuota | Antes era una sola línea con guiones; ahora cada dato tiene rótulo y el estado se ve de un vistazo | `pages/Creditos.jsx` | [créditos](capturas/ui-antes/03-creditos.png) | [créditos](capturas/ui-despues/03-creditos.png) |
| Todos los `mensajes` del `ErrorResponse` | Con varios errores de validación solo se veía el primero | `api/apiClient.js` | — | — |
| Tabla de clientes con padding y alineación | Quedaba centrada y apretada, distinta a la de cobranzas | `pages/Clientes.jsx` | [clientes](capturas/ui-antes/02-clientes.png) | [clientes](capturas/ui-despues/02-clientes.png) |

Capturas completas (login, clientes, créditos, cobranzas, dashboard, admin, permisos): `capturas/ui-antes/` y `capturas/ui-despues/`. Datos de prueba cargados vía API sobre la H2 en memoria.
