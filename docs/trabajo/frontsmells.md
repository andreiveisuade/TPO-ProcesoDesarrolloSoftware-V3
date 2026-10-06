# T42 frontsmells: smells chicos del front

Rama `pendientes-front`. Origen del detalle: `docs/trabajo/smells.md` en `4713828^`.

## DF2. Archivos y exports sin uso (commit dfa2c12)
- Problema: `frontend/src/App.css` y `frontend/src/assets/react.svg` (restos de Vite) sin importar; acción `clearError` exportada y nunca despachada en `store/slices/{clientes,creditos,cobranzas,auth}Slice.js`.
- Cambio: se borran los dos archivos y los cuatro `clearError`.
- Por qué: código muerto que confunde al leer.
- Consecuencias: `getCliente` y `getCredito` ya NO están sin uso (`pages/Clientes.jsx`, `pages/Creditos.jsx` los llaman), así que se dejan.

## BSF4. Roles como strings sueltos (commit d9b0b8f)
- Problema: `'ADMIN'`/`'SUPERVISOR'` comparados a mano en Navbar, Dashboard, PanelAdmin, GestorPermisos y las rutas.
- Cambio: `frontend/src/utils/roles.js` exporta `ROLES` y se usa en todos esos lugares.
- Por qué: un typo en un string no falla, y el rol queda definido en un solo lugar.
- Consecuencias: ninguna de comportamiento.

## BSF2. Rutas protegidas duplicadas (commit a085f66)
- Problema: `AdminRoute.jsx` y `SupervisorRoute.jsx` idénticas salvo el rol; `PanelAdmin.jsx` y `GestorPermisos.jsx` repetían el chequeo que ya hace la ruta.
- Cambio: `components/RoleRoute.jsx` (`roles`, `children`) usado en `App.jsx`; se quitan los chequeos y el estilo `center` en las dos páginas.
- Por qué: una guarda única en vez de dos copias y un chequeo por capa.
- Consecuencias: `pages/Dashboard.jsx` conserva su chequeo porque su ruta es solo `PrivateRoute` (admite dos roles).

## BSF5. Acceso a la API inconsistente (commit f5c8d05)
- Problema: `dashboardSlice.js` y `permisosSlice.js` llamaban `api.get` directo; `api/admin.js` y `api/supervisor.js` envolvían en async/await lo que el resto hace en una línea; `cobranzasSlice.js` leía `err.response?.data?.mensajes`, forma que `apiClient.js` nunca produce.
- Cambio: `api/dashboard.js` (`getEstadisticas`), `getUsuariosAdmin` en `api/admin.js`, wrappers en una línea, `rejectWithValue(err.message)` en cobranzas.
- Por qué: las slices solo hablan con `src/api/*`.
- Consecuencias: ninguna de comportamiento (ese camino ya caía siempre en `err.message`).

## BSF6. Ternarios anidados en el render (commit 0e3284e)
- Problema: `pages/Creditos.jsx` resolvía color y texto de la cuota con dos ternarios anidados repetidos, y el plan con un ternario en una línea.
- Cambio: `ESTADO_CUOTA` + `estadoCuota(c)` y `descripcionPlan(cr)` en `Creditos.jsx`.
- Por qué: el render queda legible y el estado vive en una tabla.
- Consecuencias: mismos textos y colores.
