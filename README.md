# Bifrost

Bot de Telegram para escribir y organizar entradas del diario personal.

## Estado

✅ **Bot funcional** - Arranca y responde comandos
✅ **`/entrada` arreglado** (2026-09-04)
⚠️ **Pendiente** - Prueba real contra Telegram, servicio systemd en Madre y autorización por chat_id

## Estructura del repositorio

bifrost/
├─ bot.py # Punto de entrada del bot
├─ handlers/
│ ├─ _init_.py
│ ├─ diario.py # /diario → organizar_texto()
│ └─ entrada.py # /entrada → escribir_entrada()
├─ utils/
│ └─ auth.py # (pendiente de implementar)
├─ venv/ # Entorno virtual (NO commitear)
├─ .env # Token y chat_id (NO commitear)
├─ .env.example # Plantilla
├─ .gitignore
├─ AGENTS.md
├─ CONTEXT.md
├─ HANDLERS.md
├─ README.md
├─ SCRIPTS.md
└─ docs/
└─ sesiones/

text

## Dónde tiene que vivir este repo

**Importante:** bifrost no funciona clonado por su cuenta. Los handlers
buscan el diario cuatro niveles por encima de `handlers/`, así que el repo
tiene que estar en `midgaror/proyectos/bifrost`, que es donde lo pone el
submódulo. Clonado en otro sitio, los imports de `midgaror/diario/` fallan
al arrancar.

```bash
cd ~/GitHub/personal/midgaror     # o donde tengas midgaror
git submodule update --init --recursive
cd proyectos/bifrost
```

## Puesta en marcha, paso a paso

1. **Crear el bot en Telegram.** Habla con `@BotFather`, `/newbot`, y guarda
   el token que te da.

2. **Averiguar tu chat_id.** Escríbele algo a tu bot y luego:

   ```bash
   curl -s "https://api.telegram.org/bot<TU_TOKEN>/getUpdates" | grep -o '"id":[0-9-]*' | head -1
   ```

   Ese número va en `TELEGRAM_CHAT_ID` y es lo que hace que el bot te
   responda solo a ti. Sin él responde a cualquiera, y avisa por el log al
   arrancar.

3. **Entorno virtual y dependencias:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install python-telegram-bot python-dotenv
   ```

4. **Configurar el `.env`:**

   ```bash
   cp .env.example .env
   ```

   Rellena `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`. El `.env` no se
   commitea nunca: ya está en `.gitignore`.

5. **Probar la escritura sin el bot**, para separar los fallos del diario de
   los de Telegram:

   ```bash
   cd ../..                      # raíz de midgaror
   python3 diario/organizar_diario.py --input "prueba desde terminal"
   python3 diario/bifrost_bridge.py escribir "prueba con fecha" --fecha 2026-09-04
   git diff diario/personal/     # mirar qué ha escrito
   ```

   Si esto falla, el problema está en midgaror, no en el bot.

6. **Arrancar el bot en primer plano:**

   ```bash
   cd proyectos/bifrost
   source venv/bin/activate
   python3 bot.py
   ```

   Los mensajes de arranque salen por pantalla. Se para con `Ctrl+C`.

7. **Probar desde Telegram**, en este orden:

   | Mensaje | Qué debe pasar |
   |---------|----------------|
   | `/start` | Responde con la bienvenida |
   | `/help` | Responde con la ayuda |
   | `/diario probando hoy` | Escribe en la entrada de hoy y responde con la ruta |
   | `/entrada 2026-09-01 probando una fecha` | Escribe en la entrada de ese día |
   | `/entrada 01-09-2026 mal` | Responde que la fecha es inválida |
   | `/entrada 2026-09-01` | Responde con el uso correcto |

8. **Comprobar y guardar lo escrito**, desde la raíz de midgaror:

   ```bash
   git status diario/personal/
   git diff diario/personal/
   ```

   El bot escribe ficheros, no commitea. El commit lo haces tú.

## Uso diario

```bash
cd ~/GitHub/personal/midgaror/proyectos/bifrost
source venv/bin/activate
python3 bot.py
```

## Como servicio

Para que el bot no dependa de una terminal abierta. La unidad está en
[`systemd/bifrost.service`](systemd/bifrost.service).

**Antes de instalarla**, comprueba que las rutas del fichero coinciden con
las tuyas. Llevan `varopc` y `~/GitHub/personal/midgaror` escritos dentro:

```bash
grep -E "User=|WorkingDirectory=|ExecStart=|ReadWritePaths=" systemd/bifrost.service
```

Instalación:

```bash
sudo cp systemd/bifrost.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now bifrost
```

Comprobación:

```bash
systemctl status bifrost
journalctl -u bifrost -n 30 --no-pager
```

En el arranque debe aparecer `Bot en marcha` y, si tienes puesto el chat_id,
`Autorizacion activa para 1 chat(s)`. Si en su lugar sale el aviso de que
responde a cualquiera, te falta `TELEGRAM_CHAT_ID` en el `.env`.

### Comandos del día a día

```bash
sudo systemctl restart bifrost     # tras cambiar código o .env
sudo systemctl stop bifrost        # pararlo
journalctl -u bifrost -f           # ver el log en vivo
```

### Qué hace la unidad

- **Se reinicia solo** si el bot muere: la red se va, Telegram falla. Con un
  tope de 5 reinicios en 5 minutos, para que un error de configuración no
  entre en bucle.
- **El token no pasa por systemd.** Lo sigue leyendo `python-dotenv` del
  `.env`, así que no aparece en `systemctl show` ni en el volcado de la
  unidad.
- **Solo puede escribir en `diario/personal/`.** El resto del disco, incluido
  el resto del repo, lo ve de solo lectura.

### Dónde vive y qué toca

| Cosa | Dónde |
|------|-------|
| Código | `~/GitHub/personal/midgaror/proyectos/bifrost/` |
| Entorno virtual | `proyectos/bifrost/venv/` |
| Token y chat_id | `proyectos/bifrost/.env` (nunca se commitea) |
| Unidad | `/etc/systemd/system/bifrost.service` |
| Lo que escribe | `~/GitHub/personal/midgaror/diario/personal/AAAA/MM-mes/AAAA-MM-DD.md` |
| Logs | `journalctl -u bifrost` |
| Lógica del diario | `~/GitHub/personal/midgaror/diario/` (no está en este repo) |

El bot **escribe ficheros, no hace commit**. Las entradas viven en el disco
de Madre hasta que alguien las commitea a mano.

### Comprobar que no se muere

Instalarlo no demuestra nada. Estas cuatro pruebas sí, y son la fase 2b:

**1. Que resucita si lo matan**

```bash
sudo systemctl kill bifrost
sleep 15
systemctl status bifrost
```

Debe volver a estar `active (running)`, con un PID distinto. Si sale
`failed`, la unidad no está haciendo su trabajo.

**2. Que arranca solo al encender la máquina**

```bash
sudo reboot
# cuando vuelva:
systemctl is-enabled bifrost    # -> enabled
systemctl is-active bifrost     # -> active
```

Y lo que de verdad importa: escríbele por Telegram y comprueba que responde
sin que hayas tocado nada.

**3. Que aguanta un corte de red**

En una máquina a la que llegas por SSH, **no pares la red**: te quedas fuera.
La forma segura es esperar a que pase de verdad y mirarlo después:

```bash
systemctl show bifrost -p NRestarts
journalctl -u bifrost --since "1 day ago" | grep -iE "error|restart|network"
```

Si `NRestarts` sube solo, el bot se está muriendo por algo. Si sube y vuelve
solo, la unidad está cumpliendo.

**4. Que no se descuadra escribiendo**

Después de unos días de uso:

```bash
cd ~/GitHub/personal/midgaror
git status diario/personal/
git diff diario/personal/
```

Las entradas deben tener la hora delante y estar dentro de "Qué ha pasado
hoy", sin duplicados ni texto pegado al final del fichero.

### Qué anotar durante las dos semanas

La fase 2b pide uso real, y de eso salen datos. Vale con apuntar en la sesión
de trabajo, al final de cada semana:

- Cuántas veces se reinició (`NRestarts`) y por qué.
- Si alguna vez no respondió, y qué decía el log en ese momento.
- Si el formato de alguna entrada quedó raro.
- Cuántas veces lo usaste de verdad. Si la respuesta es "casi ninguna", eso
  también es un resultado, y más útil que cualquier mejora técnica.

### Cuidado al actualizar

Systemd arranca el bot con el Python del entorno virtual. Si rehaces el
`venv`, o si Arch sube de versión menor de Python y el entorno se queda
huérfano, el servicio deja de arrancar. Se ve claro en el log:

```bash
journalctl -u bifrost -n 20 --no-pager
```

Se arregla recreando el entorno y reiniciando el servicio.

## Comandos

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida |
| `/help` | Muestra ayuda |
| `/diario <texto>` | Escribe en la entrada de **hoy** (usa `midgaror/diario/organizar_diario.py`) |
| `/entrada <AAAA-MM-DD> <texto>` | Escribe en la entrada de **ese día** (usa `midgaror/diario/bifrost_bridge.py`) |

Los dos escriben dentro de la sección "Qué ha pasado hoy", con la hora
delante, sin pisar lo que ya hubiera. Lo único que cambia es el día.

## Seguridad

- **El token no se pega en ningún sitio.** Vive solo en el `.env`, que está en
  `.gitignore`. Si se filtra (un log pegado en un chat, una captura), se revoca
  desde `@BotFather` con `/revoke` y se pone el nuevo en el `.env`.
- Desde el 2026-09-04 el bot silencia el log de `httpx`, que imprimía la URL
  completa de cada petición, token incluido, unas seis veces por minuto.

## Autorización

`TELEGRAM_CHAT_ID` decide quién puede darle órdenes al bot. Acepta varios
separados por comas:

```
TELEGRAM_CHAT_ID=123456789
TELEGRAM_CHAT_ID=123456789,987654321
```

Los no autorizados **no reciben respuesta**. Es a propósito: contestarles
confirma que el bot existe.

Si la variable está vacía, el bot responde a todo el mundo, como antes, y lo
avisa en el log al arrancar. Se dejó así para no romper una instalación al
actualizar, pero es un aviso, no una opción recomendable: este bot escribe en
tu diario.

## Problemas conocidos

- Corre en primer plano: aún no es servicio de systemd (fase 2b del plan).

## Documentación

- [HANDLERS.md](HANDLERS.md) - Documentación de cada handler
- [SCRIPTS.md](SCRIPTS.md) - Documentación de scripts
- [CONTEXT.md](CONTEXT.md) - Contexto y decisiones
- [AGENTS.md](AGENTS.md) - Instrucciones para agentes AI
- [docs/sesiones/](docs/sesiones/) - Registro de sesiones
