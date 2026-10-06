# Config: perfiles dev/prod, CORS y consola H2 (S8, S9, TPO-008)

## Problema
- `backend/src/main/resources/application.properties` mezclaba config de desarrollo y única: consola H2 habilitada, `show-sql=true` y `ddl-auto=update` sobre H2 en memoria, sin forma de separar un entorno productivo.
- `backend/src/main/java/com/uade/tpejemplo/config/SecurityConfig.java` llamaba `.cors(Customizer.withDefaults())` sin ningún `CorsConfigurationSource`: la línea no hacía nada y sugería que CORS estaba resuelto.
- `/h2-console/**` estaba en `permitAll` y también en `web.ignoring()` (redundante). La consola da acceso total a la base sin autenticación (TPO-008).

## Cambio
- `application.properties`: queda lo común y `spring.profiles.default=dev`, así `mvn spring-boot:run` sin flags levanta dev.
- `application-dev.properties`: `create-drop`, `show-sql=true`, consola H2 en `/h2-console` (`jdbc:h2:mem:tpdb`, `sa`) y `app.cors.origin=http://localhost:5173`.
- `application-prod.properties`: consola H2 deshabilitada, `show-sql=false`, `ddl-auto=update` (no borra datos) y `app.cors.origin=${CORS_ORIGIN}`, obligatoria al activar prod.
- `SecurityConfig`: bean `CorsConfigurationSource` con un único origen (`app.cors.origin`) y se quitó `/h2-console/**` del `permitAll`.
- S6 (`@PreAuthorize` de `AdminController` y `SupervisorController`) no se tocó: queda como doble control de roles (reglas de URL + anotación), resuelto aparte.

## Por qué
- Un perfil por entorno evita que lo cómodo de la demo (consola, SQL en logs) llegue a prod.
- CORS declarado con origen explícito: en dev lo usa el front de Vite, en prod solo el origen configurado.
- Se mantiene `web.ignoring()` para `/h2-console/**`: con la consola deshabilitada en prod no expone nada y evita tocar el frame-options en dev.

## Consecuencias
- Verificado en el 8099: dev responde 200 en `/h2-console/` y devuelve `Access-Control-Allow-Origin` para `http://localhost:5173`; prod responde 404 en la consola, no loguea SQL, permite solo `CORS_ORIGIN` y rechaza `localhost:5173`.
- Roles por curl sin cambios (anon 401, admin 200/403, supervisor 403/200).
- `mvn -q test`: exit 0.
- Para prod: `CORS_ORIGIN=https://... mvn spring-boot:run -Dspring-boot.run.arguments=--spring.profiles.active=prod`. Sin `CORS_ORIGIN` la app no arranca.
- Con H2 en memoria `update` en prod igual no persiste entre reinicios: cuando haya base real alcanza con cambiar el datasource del perfil.
