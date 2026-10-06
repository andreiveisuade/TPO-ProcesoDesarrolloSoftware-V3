#!/usr/bin/env bash
# Abre nvim con una tab por archivo cambiado (v2 a la izquierda, main a la derecha), en el orden de la presentación.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"
B=backend/src/main/java/com/uade/tpejemplo
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
VIM="$TMP/demo.vim"

cambios=(
  "M9 Strategy|$B/model/Credito.java $B/model/interfaces/CalculoDeCuota.java $B/model/plan/InteresSimple.java $B/model/plan/SistemaFrances.java $B/model/TipoPlan.java"
  "M7 Adapter|$B/service/TokenService.java $B/security/JwtUtil.java $B/security/JwtAuthFilter.java $B/security/UsuarioDetails.java"
  "M8+M2 EstadoCredito y agregado|$B/model/EstadoCredito.java $B/model/Credito.java $B/model/Cuota.java $B/service/impl/CreditoServiceImpl.java"
  "M4 permisos en backend (MVC)|$B/controller/CreditoController.java $B/model/Usuario.java $B/service/impl/CreditoServiceImpl.java"
  "M5 Handlers HTTP y Swagger/401|$B/exception/GlobalExceptionHandler.java $B/config/SecurityConfig.java $B/config/OpenApiConfig.java"
  "M1 Information Expert|$B/model/Cuota.java"
  "M3 Dashboard con numeros verdaderos|$B/service/impl/DashboardServiceImpl.java"
  "M6 Cuota.estaVencida|$B/model/Cuota.java"
  "M10 Dashboard para ADMIN|$B/config/SecurityConfig.java"
)

cat > "$VIM" <<'VIML'
set noswapfile hidden nofoldenable
set showtabline=2
function! TablineDemo()
  let s = ''
  for i in range(1, tabpagenr('$'))
    let s .= (i == tabpagenr() ? '%#TabLineSel#' : '%#TabLine#') . ' ' . get(gettabvar(i, ''), 'titulo', '') . ' '
  endfor
  return s . '%#TabLineFill#'
endfunction
set tabline=%!TablineDemo()
VIML

n=0
for cambio in "${cambios[@]}"; do
  titulo="${cambio%%|*}"
  for ruta in ${cambio#*|}; do
    [[ -f "$ruta" ]] || { echo "No existe: $ruta" >&2; exit 1; }
    n=$((n + 1))
    viejo="$TMP/$n-v2-$(basename "$ruta")"
    git show "v2:$ruta" > "$viejo" 2>/dev/null || : > "$viejo"
    cat >> "$VIM" <<VIML
$([[ $n -eq 1 ]] && echo "edit $viejo" || echo "tabedit $viejo")
let t:titulo = '$titulo: $(basename "$ruta")'
setlocal readonly nomodifiable
diffthis
vsplit $RAIZ/$ruta
diffthis
VIML
  done
done
echo "tabfirst" >> "$VIM"

if [[ "${1:-}" == "--headless" ]]; then
  nvim --headless -S "$VIM" +"echo tabpagenr('\$')" +qa
  echo
else
  nvim -S "$VIM"
fi
