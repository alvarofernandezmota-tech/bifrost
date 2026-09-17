#!/usr/bin/env bash
# ¿Cómo está el bot? Todo lo que hace falta saber, en una palabra:
#
#     ./estado.sh
#
# Existe porque la noche del 2026-09-17 se fueron dos horas en preguntas que
# esto contesta en dos segundos: si el servicio vive, si el paquete que dice
# que falta está instalado de verdad, en qué commit corre, y si el
# clasificador está encendido o simplemente dormido.
#
# La clave: **no imprime ni un valor del .env**, solo los nombres. Un
# diagnóstico que hay que censurar antes de enseñarlo no se enseña, y
# entonces no sirve. Este se puede pegar en un chat entero.

set -uo pipefail
cd "$(dirname "$0")" || exit 1

verde() { printf '\033[32m%s\033[0m\n' "$1"; }
rojo()  { printf '\033[31m%s\033[0m\n' "$1"; }

echo "═══ bifrost ═══"

# ---- el servicio -------------------------------------------------------
#
# `is-active` distingue tres cosas que importan y que a ojo se confunden:
# active (vivo), failed (arrancó y se cayó) e inactive (parado a propósito).
estado=$(systemctl is-active bifrost 2>/dev/null || true)
case "$estado" in
  active) verde "servicio:  active" ;;
  "")     rojo  "servicio:  la unidad no existe (¿es un servicio de usuario?)" ;;
  *)      rojo  "servicio:  $estado"
          echo "           lo último del log:"
          journalctl -u bifrost -n 6 --no-pager 2>/dev/null | sed 's/^/           /'
          ;;
esac

# ---- el código ---------------------------------------------------------
echo "código:    $(git log --oneline -1 2>/dev/null || echo '¿no es un repo?')"
sucio=$(git status --porcelain 2>/dev/null | wc -l)
[ "$sucio" -gt 0 ] && rojo "           ⚠️  $sucio fichero(s) sin commitear"

# ---- la configuración --------------------------------------------------
#
# Nombres, nunca valores. Y se avisa de las líneas que dotenv NO va a
# entender: eso fue exactamente lo que tiró el bot el 2026-09-18 —una `x` y
# unos espacios delante de TELEGRAM_BOT_TOKEN, metidos sin querer en un
# editor— y el error solo decía «no encontrado».
echo "variables:"
if [ -f .env ]; then
  while IFS= read -r linea; do
    case "$linea" in
      ""|\#*) continue ;;
      [A-Za-z_]*=*) echo "  ${linea%%=*}" ;;
      *) rojo "  ⚠️  línea que dotenv NO entiende: «$(echo "$linea" | cut -c1-40)…»" ;;
    esac
  done < .env
else
  rojo "  no hay .env (cópialo de .env.example)"
fi

# ---- los paquetes ------------------------------------------------------
PY=venv/bin/python
[ -x "$PY" ] || PY=python3
echo "paquetes:  (con $PY)"
# Cada import, en SU PROPIO proceso. No es manía: un paquete compilado que
# no cuadra con este Python no lanza un ImportError, **mata al interprete**
# (un panic de Rust, un fallo de segmentacion). Con los cuatro en el mismo
# proceso, el primero que revienta se lleva por delante las otras tres
# comprobaciones y esto no imprime nada — justo cuando mas falta hace.
#
# Y se prueba a IMPORTARLOS, no a buscarlos con pip: `pip` decia
# «Successfully installed faster-whisper» mientras el import moria por una
# dependencia que ese paquete no declara. Media hora, el 2026-09-17.
comprobar() {
  local modulo="$1" para_que="$2" salida
  salida=$("$PY" -c "
import sys, traceback
try:
    __import__('$modulo')
# BaseException y no Exception: un paquete compilado que no cuadra tira un
# pyo3_runtime.PanicException, que NO hereda de Exception. Con \`except
# Exception\` se escapaba y esto no llegaba a decir quién había fallado.
except BaseException as error:
    culpable = (getattr(error, 'name', '') or '').split('.')[0]
    if not culpable:
        # Sin .name (un panic, un error de tipo): el culpable es el último
        # módulo de la traza, que es el que estaba importándose al reventar.
        marcos = traceback.extract_tb(error.__traceback__)
        culpable = marcos[-1].filename.split('/site-packages/')[-1] \
            .split('/dist-packages/')[-1].split('/')[0] if marcos else '$modulo'
    if culpable == '$modulo':
        print('falta' if isinstance(error, ImportError) else
              'no carga: ' + type(error).__name__)
    else:
        print('no carga: falla «' + culpable + '»')
    sys.exit(1)
" 2>/dev/null)
  case $? in
    0) printf '  ok     %-16s (%s)\n' "$modulo" "$para_que" ;;
    *) [ -n "$salida" ] || salida="revienta al importarse"
       rojo "$(printf '  FALLA  %-16s (%s) — %s' "$modulo" "$para_que" "$salida")"
       rojo "$(printf '         para verlo entero:  %s -c \"import %s\"' "$PY" "$modulo")" ;;
  esac
}

comprobar telegram        "el bot"
comprobar dotenv          "leer el .env"
comprobar anthropic       "entender lo que escribes"
comprobar faster_whisper  "las notas de voz"

# ---- lo que está encendido ---------------------------------------------
#
# Esto es lo que más se olvida: la función está desplegada y dormida porque
# falta una línea, y nada falla. No hay error que mirar.
#
# La clave se mide, no se enseña: solo su longitud. Un sitio vacío y un sitio
# con el hueco puesto («sk-ant-PON-AQUI-LA-TUYA») fallan igual de silenciosos,
# pero se arreglan distinto, así que se distinguen. Una clave de verdad pasa
# de largo de los 40 caracteres; el hueco se queda muy corto.
clave=$(sed -n 's/^ANTHROPIC_API_KEY=//p' .env 2>/dev/null | tail -1)
if [ -z "$clave" ]; then
  echo "cerebro:   apagado — sin ANTHROPIC_API_KEY todo va al diario"
elif [ "${#clave}" -lt 40 ]; then
  rojo "cerebro:   apagado — ANTHROPIC_API_KEY está puesta pero mide ${#clave} caracteres:"
  rojo "           es el hueco de ejemplo, no una clave. Todo va al diario."
else
  verde "cerebro:   encendido (clasifica tarea/hábito/cita/apunte)"
fi
if "$PY" -c "import faster_whisper" >/dev/null 2>&1; then
  verde "voz:       lista"
else
  echo   "voz:       apagada — sin faster-whisper las notas de voz fallan"
fi
