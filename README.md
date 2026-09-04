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

## Comandos

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida |
| `/help` | Muestra ayuda |
| `/diario <texto>` | Escribe en la entrada de **hoy** (usa `midgaror/diario/organizar_diario.py`) |
| `/entrada <AAAA-MM-DD> <texto>` | Escribe en la entrada de **ese día** (usa `midgaror/diario/bifrost_bridge.py`) |

Los dos escriben dentro de la sección "Qué ha pasado hoy", con la hora
delante, sin pisar lo que ya hubiera. Lo único que cambia es el día.

## Problemas conocidos

- Sin autorización todavía: `utils/auth.py` está pendiente, así que el bot
  responde a quien le escriba. No publiques el token.
- Corre en primer plano: aún no es servicio de systemd (fase 2b del plan).

## Documentación

- [HANDLERS.md](HANDLERS.md) - Documentación de cada handler
- [SCRIPTS.md](SCRIPTS.md) - Documentación de scripts
- [CONTEXT.md](CONTEXT.md) - Contexto y decisiones
- [AGENTS.md](AGENTS.md) - Instrucciones para agentes AI
- [docs/sesiones/](docs/sesiones/) - Registro de sesiones
