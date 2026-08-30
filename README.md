# Bifrost

Bot de Telegram para escribir y organizar entradas del diario personal.

## Estado

✅ **Bot funcional** - Arranca y responde comandos
⚠️ **Pendiente** - Refactorizar `organizar_diario.py` para manejar marcadores

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

## Instalación

```bash
# Clonar
git clone https://github.com/alvarofernandezmota-tech/bifrost.git
cd bifrost

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install python-telegram-bot python-dotenv

# Copiar .env
cp .env.example .env
# Editar con tu token y chat_id
```

## Uso

```bash
# Activar venv
source venv/bin/activate

# Ejecutar bot
python3 bot.py
```

## Comandos

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida |
| `/help` | Muestra ayuda |
| `/diario <texto>` | Inserta texto en "Qué ha pasado hoy" (usa `midgaror/diario/organizar_diario.py`) |
| `/entrada <fecha> <texto>` | Crea/actualiza entrada (usa `midgaror/diario/bifrost_bridge.py`) |

## Problemas conocidos

- `organizar_diario.py` no maneja bien entradas con marcadores `=======` existentes
- Solución pendiente: refactorizar o cambiar flujo

## Documentación

- [HANDLERS.md](HANDLERS.md) - Documentación de cada handler
- [SCRIPTS.md](SCRIPTS.md) - Documentación de scripts
- [CONTEXT.md](CONTEXT.md) - Contexto y decisiones
- [AGENTS.md](AGENTS.md) - Instrucciones para agentes AI
- [docs/sesiones/](docs/sesiones/) - Registro de sesiones
