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

## Dark theme

La paleta vive en un solo lugar, `frontend/src/index.css`, como variables CSS (custom properties) con nombre semántico: dicen para qué se usan, no qué color son. Los estilos inline de `pages/*.jsx` y `components/Navbar.jsx` ya no tienen colores escritos a mano, solo `var(--...)`.

| Variable | Uso |
|---|---|
| `--color-bg` | Fondo de la página |
| `--color-surface`, `--color-surface-alt` | Cards, inputs; encabezado y hover de tablas, tags |
| `--color-text`, `--color-text-muted`, `--color-heading` | Texto, rótulos y secundarios, títulos |
| `--color-border`, `--color-border-strong` | Separadores; bordes de inputs |
| `--color-primary`, `--color-on-primary`, `--color-link` | Botones principales y texto sobre ellos; links |
| `--color-success`, `--color-danger`, `--color-warning`, `--color-info`, `--color-accent` (+ `-bg` / `-solid`) | Estados: badges VIGENTE/CANCELADO/ANULADO, cuotas Pagada/Vencida/Pendiente, errores, botón Anular, badges de rol |
| `--color-nav-*` | Barra de navegación |
| `--color-shadow` | Sombras de cards |

**Por qué `prefers-color-scheme`:** el oscuro es el default y `@media (prefers-color-scheme: light)` redefine las mismas variables para quien tiene el sistema en claro. Respeta la preferencia del usuario sin botón, sin estado en React y sin librerías: cambiar de tema es solo cambiar valores de variables. Sin `!important`.

**Contraste:** todo texto cumple WCAG AA (≥ 4.5:1). En oscuro: badges de estado 7.3–7.6, cuotas 7.7–9.6, texto secundario 7.1, texto blanco sobre botones y badges sólidos 5.0–5.6.

Capturas en oscuro: `capturas/dark/` ([login](capturas/dark/login.png), [register](capturas/dark/register.png), [clientes](capturas/dark/clientes.png), [créditos](capturas/dark/creditos.png), [cobranzas](capturas/dark/cobranzas.png), [dashboard](capturas/dark/dashboard.png), [admin](capturas/dark/admin.png), [permisos](capturas/dark/permisos.png)).
