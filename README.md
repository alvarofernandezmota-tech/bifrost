# Bifrost

Bot de Telegram para escribir y organizar entradas del diario personal.

## Estructura del repositorio

bifrost/
├─ bot.py # Script principal del bot (comandos de Telegram)
├─ organizar_diario.py # Inserta texto en la sección correcta de una entrada
├─ bifrost_bridge.py # Funciones de escritura de entradas (escribir_entrada)
├─ SCRIPTS.md # Documentación de cada script
├─ .env # Token y chat_id (NO commitear, protegido por .gitignore)
├─ .env.example # Plantilla de variables de entorno
├─ .gitignore
├─ AGENTS.md # Instrucciones para agentes AI
├─ CONTEXT.md # Contexto del proyecto y decisiones de arquitectura
├─ README.md # Este archivo
└─ docs/
└─ sesiones/
└─ YYYY/MM-mes/
└─ YYYY-MM-DD.md # Registro de sesiones de desarrollo

text

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/alvarofernandezmota-tech/bifrost.git
cd bifrost

# Instalar dependencias
pip install python-telegram-bot python-dotenv

# Copiar plantilla de entorno
cp .env.example .env

# Editar .env con tu token y chat_id de Telegram
nano .env
```

## Uso

```bash
# Ejecutar el bot
python3 bot.py
```

## Comandos disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Mensaje de bienvenida | `/start` |
| `/help` | Muestra ayuda completa | `/help` |
| `/diario <texto>` | Inserta texto en "Qué ha pasado hoy" de la entrada de hoy | `/diario Fui a caminar` |
| `/entrada <fecha> <texto>` | Crea o actualiza entrada para una fecha | `/entrada 2026-08-30 Gran día` |

## Scripts

Ver [SCRIPTS.md](SCRIPTS.md) para documentación detallada de cada script.

## Documentación

- [CONTEXT.md](CONTEXT.md) - Contexto y decisiones de arquitectura
- [AGENTS.md](AGENTS.md) - Instrucciones para agentes AI
- [SCRIPTS.md](SCRIPTS.md) - Documentación de scripts
- [docs/sesiones/](docs/sesiones/) - Registro de sesiones de desarrollo

## Relación con midgaror

Este repositorio es un submódulo de [midgaror](https://github.com/alvarofernandezmota-tech/midgaror), el repo raíz del sistema personal. Los scripts de diario en `midgaror/diario/` pueden importar funciones de este repo para mantener un único lugar de verdad para el código.
