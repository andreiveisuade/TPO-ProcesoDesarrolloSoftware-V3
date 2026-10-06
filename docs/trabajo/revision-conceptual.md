# Revisión conceptual de V3 contra el material de la cátedra (T48)

Medido contra `CLASE_09_Patrones_mvc_strategy_adapter.pdf` y `CLASE_10_ADOO_Repaso_GRASP_SOLID_Adapter_Strategy.pdf` (CLASE_10 repasa GRASP y SOLID de CLASE_05 y CLASE_07), más la convención de `bitacora-tpo.md`. Rutas relativas a `backend/src/main/java/com/uade/tpejemplo/`. Solo lectura: no se tocó código.

## 1. Strategy (M9): CUMPLE, con un matiz que conviene cerrar

| Rol (slide 35/36 de CLASE_10) | V3 | Veredicto |
|---|---|---|
| Strategy (interfaz con una firma) | `model/interfaces/CalculoDeCuota.importeCuota(...)` | CUMPLE |
| ConcreteStrategies | `model/plan/InteresSimple`, `model/plan/SistemaFrances`; no se conocen entre sí | CUMPLE |
| Context "tiene referencia a la interface Strategy" (CLASE_09) | `model/Credito` guarda `TipoPlan tipoPlan` y llega a la estrategia con `tipoPlan.calculo()` en el constructor | PARCIAL: la referencia es indirecta |
| Quién elige | el que otorga: `CreditoRequest.tipoPlan` → `Credito.nuevo(...)` | CUMPLE ("el cliente tiene que conocer las estrategias", slide 38: `TipoPlan` las enumera) |
| `setEstrategia` | no existe | CORRECTO |

- **El enum `TipoPlan` no rompe el patrón.** Es la forma de configurar la estrategia de manera persistible: JPA no puede guardar una interfaz, sí un `@Enumerated`. El Context no hace `if/switch` por tipo (la regla de Polymorphism, slide 10), así que la variación queda protegida. Hace de registro de estrategias, no de Context.
- **Sin `setEstrategia` está bien.** CLASE_09 dice "permite configurar en momento de ejecución"; en V3 se configura en ejecución, al otorgar (lo elige el usuario en el `<select>`). Cambiarlo después alteraría cuotas ya emitidas y el importe persistido (`importeCuota`). El `setEstrategia` del diagrama es la forma de inyectar, no un requisito; el reporte ya lo defiende (`reporte-v3.html`, preguntas de defensa).
- **Matiz que un profe puede marcar:** en el diagrama de clases el Context tiene `- estrategia: IEstrategia` y delega en un método propio. En `Credito` no hay ni campo ni método de tipo `CalculoDeCuota`: la delegación ocurre una vez, dentro del constructor, a través del enum. **Cambio mínimo:** un método privado `private CalculoDeCuota calculo() { return tipoPlan.calculo(); }` en `Credito`, usado por el constructor, y en el diagrama `m9-despues.puml` dibujar `Credito --> CalculoDeCuota` (vía `TipoPlan`). Así el diagrama muestra la flecha Context → Strategy de la slide. Alternativa más "de manual" (campo `@Transient CalculoDeCuota` rehidratado con `@PostLoad`) agrega código sin uso real: no lo recomiendo.
- **Sistema francés como segunda ConcreteStrategy:** justificado. Es exactamente "misma acción, distintos algoritmos" (CLASE_09) y OCP (slide 37: una estrategia nueva es una clase más + una constante del enum, sin tocar `Credito`). Con una sola estrategia el patrón sería sobre-ingeniería (slide 38). **Ojo:** `bitacora-tpo.md` registra que se descartó el 15/09 (Regulo). El reporte lo dice en la portada ("Revierte V2: sistema francés descartado el 15/09"); falta que la ficha de M9 explique por qué se revierte (antes se buscaba solo la convención interfaz+clase, ahora el tema de la iteración es Strategy y necesita dos algoritmos reales).
- **Detalle de OCP:** agregar una estrategia obliga a tocar `TipoPlan` (agrega una constante). Es la modificación aceptada en un registro de estrategias; si lo preguntan, el Context y las otras estrategias quedan cerrados.

## 2. Adapter (M7)

### `JwtUtil` sobre jjwt: PARCIAL, hoy es un wrapper de llamadas estáticas

| Rol (slide 26/28 de CLASE_10) | V3 | Veredicto |
|---|---|---|
| Target / ITarget | `service/TokenService` | CUMPLE |
| Cliente que solo conoce el Target | `service/impl/AuthServiceImpl`, `security/JwtAuthFilter` | CUMPLE (nadie importa `JwtUtil`) |
| Adapter que implementa el Target | `security/JwtUtil implements TokenService` | CUMPLE |
| Adapter "contiene" al Adaptado (`- adaptado: Adaptado`, composición 1 a 1) | no: guarda `String secret` y `long expirationMs`, y en cada llamada usa `Jwts.builder()` / `Jwts.parser()...build()` estáticos y rearma la `SecretKey` | VIOLA la forma Object Adapter |

La slide 27 dice que en Java "solo Object Adapter es viable" y que el Adapter **contiene una instancia del Adaptado**. CLASE_09 es más laxa ("guardan referencia **o hacen uso** de las clases adaptadas"), así que por CLASE_09 pasa, pero el reporte afirma "Object Adapter (por composición)" y para `JwtUtil` eso hoy no es cierto: es más cercano a un Facade de métodos estáticos.

**Cambio mínimo:** construir el Adaptado una vez y guardarlo en campos finales.

```java
private final SecretKey key;
private final JwtParser parser;
private final long expirationMs;

public JwtUtil(@Value("${jwt.secret}") String secret, @Value("${jwt.expiration-ms}") long expirationMs) {
    this.key = Keys.hmacShaKeyFor(secret.getBytes());
    this.parser = Jwts.parser().verifyWith(key).build();
    this.expirationMs = expirationMs;
}
```

`extraerClaim` pasa a usar `parser.parseSignedClaims(token)` y `generarToken` firma con `key`. Queda `- parser: JwtParser` como el `- adaptado` del diagrama, y el `m7-despues.puml` dibuja la composición `JwtUtil *-- JwtParser`. Mismo comportamiento, los tests de token siguen valiendo. Bonus: deja de recalcular la clave en cada request.

### `UsuarioDetails`: CUMPLE, es el ejemplo de manual

`security/UsuarioDetails` implementa el Target de Spring (`UserDetails`), guarda `private final IUsuario usuario` (composición, Object Adapter) y traduce `getRol().autoridad()` → `GrantedAuthority`. El cliente (Spring Security, vía `UserDetailsServiceImpl`) nunca ve `Usuario`. Calca el `AdapterPagosExternos` de la slide 28. **Recomendación:** en la defensa abrir M7 con `UsuarioDetails` y después mostrar `JwtUtil`.

Matiz: aquí el "Adaptado" es una clase propia (`IUsuario`). CLASE_09 lo admite ("clases externas al dominio, **o no**"); lo que no se puede tocar es `UserDetails`, y es lo que justifica el patrón (no queremos que el modelo dependa de Spring Security).

## 3. Matriz GRASP y SOLID

| Principio | Dónde en V3 | Veredicto | Evidencia / arreglo |
|---|---|---|---|
| Information Expert | `model/Credito.estado()`, `saldo()`, `puedeAnularse()`; `model/Cuota.estaVencida()`; `Cuota.registrarCobranza` | CUMPLE | el servicio pregunta, no calcula (`DashboardServiceImpl` usa `Credito::saldo`, `Cuota::estaVencida`) |
| Creator | `Credito.generarPlanDeCuotas()` (el crédito contiene sus cuotas); `Cuota.registrarCobranza()` crea la `Cobranza` | CUMPLE | "quien lo contiene, lo crea" |
| Controller | `controller/*Controller` de caso de uso, delegan en `XService` | CUMPLE | ningún controller pasa de 76 líneas; no hay God Controller |
| Bajo acoplamiento | controllers → interfaces de servicio; clientes → `TokenService`; DTOs → `I*` del modelo | CUMPLE | `DashboardServiceImpl` depende de 4 repositorios: aceptable para un caso de uso de agregación |
| Alta cohesión | servicios por caso de uso; `JwtUtil` solo tokens | CUMPLE | |
| Polymorphism | `CalculoDeCuota` (sin `if` por plan) | CUMPLE | `Credito.estado()` usa `if` sobre flags, no sobre tipos: correcto |
| Pure Fabrication | repositorios, `XServiceImpl`, `JwtUtil`, `UsuarioDetails` | CUMPLE | |
| Indirection | `TokenService` entre `AuthServiceImpl` y jjwt; capa service entre controller y modelo | CUMPLE | |
| Protected Variations | `CalculoDeCuota` (fórmula), `TokenService` (librería JWT) | CUMPLE | |
| SRP | `Credito` (reglas del crédito), `JwtUtil`, servicios | CUMPLE | |
| OCP | nueva estrategia = clase + constante en `TipoPlan` | CUMPLE | ver §1, se toca el enum registro |
| LSP | `InteresSimple`/`SistemaFrances` intercambiables; `UsuarioDetails` no tira `UnsupportedOperationException` (deja los default de `UserDetails`) | CUMPLE | |
| ISP | `TokenService` con 3 métodos, todos usados; `CalculoDeCuota` con 1 | PARCIAL | `IRol` no tiene ningún consumidor como tipo (ya anotado en bitácora): la convención la exige, pero ningún cliente depende de ella. Defenderlo, no tocarlo |
| DIP | servicios inyectados por interfaz; `AuthServiceImpl` depende de `TokenService` | PARCIAL | `CobranzaServiceImpl.anularCobranza(Long, IUsuario)` bien; pero `TokenService` (abstracción de la capa service) se implementa en `security/`: correcto para DIP (el detalle depende de la abstracción). Única desviación es de convención, ver §4 |

Sin violaciones de GRASP/SOLID abiertas. La única debilidad conceptual real es la forma del Adapter de §2.

## 4. Convenciones de la cátedra

Convención (`bitacora-tpo.md`): una interfaz `I<Clase>` por clase de modelo en `model/interfaces/`; servicios `XService` + `service/impl/XServiceImpl`.

| Clase | Cumple | Comentario |
|---|---|---|
| `Cliente`, `Credito`, `Cuota`, `Cobranza`, `Usuario`, `Permisos`, `Rol` | Sí | |
| `model/EstadoCredito` (enum) | No tiene `IEstadoCredito` | Defendible: enum de valores sin comportamiento, ninguna interfaz tendría métodos. Decirlo en el reporte. |
| `model/TipoPlan` (enum) | No tiene `ITipoPlan` | Mismo argumento que `Rol`, que sí tiene `IRol`: o se agrega `ITipoPlan { CalculoDeCuota calculo(); }` por coherencia, o se declara la excepción. Recomiendo declarar la excepción para enums (y mencionar que `IRol` existe por pedido explícito). |
| `model/interfaces/CalculoDeCuota` | No usa prefijo `I` | Es la interfaz Strategy, no "la interfaz de una clase de modelo". Nombre de rol de patrón como en la slide (`EstrategiaDescuento`). Declararlo. |
| `model/plan/InteresSimple`, `SistemaFrances` | No tienen `I*` propio; su interfaz es `CalculoDeCuota` | Cumplen el espíritu (implementan una interfaz de `model/interfaces/`). |
| `service/TokenService` | Interfaz sí; impl **no** está en `service/impl/` ni se llama `TokenServiceImpl`: es `security/JwtUtil` | Desviación consciente: es el Adapter, el nombre de rol importa más. Declararlo o renombrar a `security/JwtTokenAdapter`. No mover a `service/impl` (mezcla infraestructura con casos de uso). |
| `AdminService`, `AuthService`, `ClienteService`, `CobranzaService`, `CreditoService`, `DashboardService` | Sí | |

Ninguna excepción a la convención está escrita hoy en el reporte. Hace falta un párrafo.

## 5. Mejoras de sistema en `docs/reporte/reporte-v3.html`

| Mejora | Dónde aparece hoy | Formato Problema → Solución → Práctica |
|---|---|---|
| Swagger | `#tecnologias` (qué es) y `#mvc` (contrato, 20 operaciones) | NO: falta el problema (no había contrato de la API, el front adivinaba los códigos) |
| Perfiles dev/prod, CORS, H2 | solo una línea del timeline (`e744600`) | NO |
| UI (formato moneda, fechas, badges, mensajes de validación) | capturas antes/después en "Capturas de la UI" | PARCIAL: hay antes/después visual, falta problema escrito y la práctica |
| Dark theme | 2 capturas + línea de timeline | NO |
| Casos de uso | sección `#casos` | CUMPLE como recorrido; no se presenta como mejora (UC06/UC09 nuevos, `/api/auth/me`) |

Falta una sección "Mejoras de sistema" (o filas S1..S5) con, para cada una: problema concreto en V2, solución (archivo/commit), práctica que aplica (MVC: contrato vista-controlador vía DTO para Swagger; configuración externalizada para perfiles; separación de presentación con variables CSS para dark theme; validación en la vista según CLASE_09 para la UI).

## CAMBIOS NECESARIOS

| # | Cambio | Tipo | Tamaño |
|---|---|---|---|
| 1 | `security/JwtUtil`: `SecretKey` y `JwtParser` como campos finales construidos en el constructor (Object Adapter real); actualizar `m7-despues.puml` con la composición | código + diagrama | S (~15 líneas) |
| 2 | `model/Credito`: método privado `calculo()` que devuelve la `CalculoDeCuota` y lo usa el constructor; `m9-despues.puml` con la flecha Context → Strategy | código + diagrama | XS (~3 líneas) |
| 3 | Ficha M9 del reporte: párrafo que explica por qué se revierte el descarte del sistema francés (15/09) | docs | XS |
| 4 | Reporte: párrafo de excepciones a la convención (`EstadoCredito`, `TipoPlan`, `CalculoDeCuota`, `TokenService`→`JwtUtil`) con su motivo | docs | S |
| 5 | Reporte: sección "Mejoras de sistema" con Problema → Solución → Práctica para Swagger, perfiles/CORS, UI, dark theme y casos de uso nuevos | docs | M |
| 6 | Ficha M7 del reporte: corregir "JwtUtil delega en la API de jjwt" por la composición del cambio 1, y presentar `UsuarioDetails` primero | docs | XS |
