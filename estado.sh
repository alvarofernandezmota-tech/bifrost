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
  # Aqui ponia «(¿es un servicio de usuario?)», y apunta justo al reves:
  # bifrost es de SISTEMA (WantedBy=multi-user.target, instalado con sudo cp
  # en /etc/systemd/system). Medido el 2026-09-18: `systemctl --user status
  # bifrost` contesta «could not be found» y el de sistema lo da «active».
  # Esa pista mandaba a buscar donde no esta.
  "")     rojo  "servicio:  la unidad no existe en el gestor del sistema"
          rojo  "           ¿la instalaste?  sudo cp systemd/bifrost.service /etc/systemd/system/"
          rojo  "           y luego:         sudo systemctl daemon-reload && sudo systemctl enable --now bifrost" ;;
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
#
# Y hay DOS motores (ADR-022), así que no basta con mirar la clave: con
# `MIDGAROR_LLM=ollama` el cerebro está encendido sin ninguna clave, y
# mirando solo `ANTHROPIC_API_KEY` esto diría «apagado» con el bot
# funcionando. La lógica de aquí sigue a `entender.proveedor()`.
clave=$(sed -n 's/^ANTHROPIC_API_KEY=//p' .env 2>/dev/null | tail -1)
motor=$(sed -n 's/^MIDGAROR_LLM=//p' .env 2>/dev/null | tail -1 | tr '[:upper:]' '[:lower:]')

case "$motor" in
  no|off|ninguno|0)
    echo "cerebro:   apagado a mano (MIDGAROR_LLM=$motor). Todo va al diario." ;;
  ollama|local)
    # Ollama no necesita clave, pero sí necesita estar levantado y con el
    # modelo bajado. Las dos cosas fallan calladas, así que se comprueban.
    url=$(sed -n 's/^MIDGAROR_OLLAMA=//p' .env 2>/dev/null | tail -1)
    url=${url:-http://127.0.0.1:11434}
    quiere=$(sed -n 's/^MIDGAROR_LLM_MODELO=//p' .env 2>/dev/null | tail -1)
    quiere=${quiere:-qwen2.5:7b}
    if ! curl -fsS --max-time 3 "$url/api/tags" >/dev/null 2>&1; then
      rojo "cerebro:   APAGADO — MIDGAROR_LLM=$motor pero Ollama no contesta en $url"
      rojo "           ¿está instalado y corriendo?  systemctl status ollama"
    elif curl -fsS --max-time 3 "$url/api/tags" 2>/dev/null | grep -q "\"$quiere\""; then
      verde "cerebro:   encendido en LOCAL ($quiere, nada sale de esta máquina)"
    else
      rojo "cerebro:   APAGADO — Ollama va, pero no tiene el modelo «$quiere»"
      rojo "           bájalo con:  ollama pull $quiere"
    fi ;;
  anthropic|claude|"")
    if [ -z "$clave" ]; then
      echo "cerebro:   apagado — sin ANTHROPIC_API_KEY todo va al diario"
      echo "           (o pon MIDGAROR_LLM=ollama para usar un modelo local)"
    elif [ "${#clave}" -lt 40 ]; then
      rojo "cerebro:   apagado — ANTHROPIC_API_KEY está puesta pero mide ${#clave} caracteres:"
      rojo "           es el hueco de ejemplo, no una clave. Todo va al diario."
    else
      verde "cerebro:   encendido en la NUBE (Claude; el texto sale hacia la API)"
    fi ;;
  *)
    rojo "cerebro:   MIDGAROR_LLM=«$motor» no es un valor que se entienda."
    rojo "           Son: anthropic, ollama, no. Con esto va como si no hubiera nada." ;;
esac
# ---- el diario: donde se escribe, y si se escribe -----------------------
#
# Esta seccion faltaba, y su ausencia se noto el 2026-09-18: ese dia esto salia
# ENTERO EN VERDE mientras el backend del diario estaba en un sitio y los datos
# en otro. Un diagnostico que dice que el bot esta bien sin haber mirado si el
# diario se escribe no esta diciendo lo que parece.
#
# Y hay un detalle que obliga a hacerlo asi y no de la forma facil: MIDGAROR_DATOS
# **solo existe en la unidad**, no en una terminal (ADR-023). Leerla del entorno
# de este script da vacio SIEMPRE, y eso se leeria como «no esta configurada»
# cuando si lo esta. Hay que preguntarle a systemd.
echo "diario:"

# El entorno de VERDAD del servicio, no el de esta terminal. Se parte por
# espacios, que vale para rutas sin espacios —las de aqui no los tienen— y no
# necesita nada instalado.
entorno=$(systemctl show bifrost -p Environment --value 2>/dev/null | tr ' ' '\n')
del_servicio() { echo "$entorno" | sed -n "s/^$1=//p" | tail -1; }
del_env()      { sed -n "s/^$1=//p" .env 2>/dev/null | tail -1; }
# La unidad manda sobre el .env: es lo que systemd le pone al proceso.
backend=$(del_servicio DIARIO_BACKEND); [ -n "$backend" ] || backend=$(del_env DIARIO_BACKEND)
datos=$(del_servicio MIDGAROR_DATOS);   [ -n "$datos" ]   || datos=$(del_env MIDGAROR_DATOS)

case "${backend:-json}" in
  postgres)
    echo "  backend:  postgres"
    # psycopg no esta en requirements.txt: es opcional y solo hace falta con
    # este backend. Sin el, el primer /tarea se cae. Ya paso.
    if ! "$PY" -c "import psycopg" >/dev/null 2>&1; then
      rojo "  ⚠️  falta «psycopg» en $PY, y con backend=postgres el primer /tarea se cae"
      rojo "      instalalo AHI:  $PY -m pip install 'psycopg[binary]'"
      rojo "      (con «$PY -m pip», nunca «venv/bin/pip»: ese lleva otra ruta en el shebang)"
      url=""   # sin la libreria no hay nada que preguntarle a la base
    else
      url=$(del_servicio DIARIO_DATABASE_URL); [ -n "$url" ] || url=$(del_env DIARIO_DATABASE_URL)
    fi
    if [ -z "$url" ]; then
      # Sin psycopg ya se ha dicho arriba; aqui solo se avisa si la libreria
      # esta y lo que falta es la URL.
      "$PY" -c "import psycopg" >/dev/null 2>&1 && \
        rojo "  ⚠️  backend=postgres pero no hay DIARIO_DATABASE_URL en la unidad ni en el .env"
    else
      # La URL lleva contrasena: se usa, no se imprime. Solo sale el recuento.
      DIARIO_DATABASE_URL="$url" "$PY" - <<'EOF' 2>&1 | sed 's/^/  /'
import os, sys
try:
    import psycopg
    with psycopg.connect(os.environ["DIARIO_DATABASE_URL"]) as c:
        for tabla, col in (("tareas","creada"),("citas","creada"),
                           ("apuntes","fecha"),("habitos_registro","fecha")):
            n, ult = c.execute(f"select count(*), max({col})::text from {tabla}").fetchone()
            print(f"{tabla:18} {n:>5} filas   ultima: {ult or '—'}")
except Exception as e:
    print(f"NO CONECTA: {type(e).__name__}: {e}"); sys.exit(1)
EOF
    fi ;;
  json)
    echo "  backend:  json (ficheros)"
    if [ -z "$datos" ]; then
      echo "  carpeta:  la del repo (MIDGAROR_DATOS sin definir)"
    elif [ ! -d "$datos" ]; then
      rojo "  ⚠️  MIDGAROR_DATOS apunta a «$datos» y esa carpeta NO existe"
    else
      echo "  carpeta:  $datos"
      # El fallo que el ADR-016 llama «el mas caro posible»: sin la carpeta en
      # ReadWritePaths, el bot contesta como si nada y no escribe NADA.
      if ! systemctl show bifrost -p ReadWritePaths --value 2>/dev/null | grep -qF "$datos"; then
        rojo "  ⚠️  esa carpeta NO esta en ReadWritePaths de la unidad."
        rojo "      El bot contestara como si nada y no escribira nada (ADR-016)."
      fi
      ultimo=$(git -C "$datos" log -1 --format='%cr — %s' 2>/dev/null)
      if [ -z "$ultimo" ]; then
        rojo "  ⚠️  «$datos» no es un repo git, o no tiene ni un commit"
      else
        echo "  ultimo:   $ultimo"
      fi
    fi ;;
  *)
    rojo "  ⚠️  DIARIO_BACKEND=«$backend» no se entiende. Son: json, postgres." ;;
esac

if "$PY" -c "import faster_whisper" >/dev/null 2>&1; then
  verde "voz:       lista"
else
  echo   "voz:       apagada — sin faster-whisper las notas de voz fallan"
fi
