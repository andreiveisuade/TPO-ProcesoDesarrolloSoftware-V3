# Repo V3 (local)

Árbol base: `git archive 45e228c` del repo Arreglos (main@45e228c = V2). `diff -rq` contra un segundo archive: idéntico, sin basura de IDE.

## Commits y tag
- `6a0ca8f` V2: punto de partida (Arreglos main@45e228c), tag `v2`
- segundo commit: docs/reporte/, docs/trabajo/, docs/README.md, este archivo

`.gitignore` ya cubría target/, node_modules/, .idea/, .vscode/, .classpath, .project, .settings/; no se tocó.

## Credenciales en el árbol (*.properties, *.yml)
- `backend/src/main/resources/application.properties:7` `spring.datasource.password=` (vacío)
- `backend/src/main/resources/application.properties:22` `jwt.secret=clave-super-secreta-de-al-menos-32-caracteres-uade2026` (ya público en Arreglos, TPO-009; no se toca)
