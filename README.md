# Bifrost

Bot de Telegram para escribir y organizar entradas del diario personal.

## Estado

✅ **Estructura modular completada** - Documentación y código alineados

## Estructura del repositorio

bifrost/
├─ bot.py # Punto de entrada del bot (inicia Telegram app)
├─ handlers/ # Comandos de Telegram
│ ├─ _init_.py # Exporta todos los handlers
│ ├─ start.py # Handler: /start
│ ├─ help.py # Handler: /help
│ ├─ diario.py # Handler: /diario
│ └─ entrada.py # Handler: /entrada
├─ core/ # Lógica del diario
│ ├─ _init_.py # Exporta funciones principales
│ ├─ organizar.py # Función: organizar_texto()
│ └─ bridge.py # Función: escribir_entrada()
├─ utils/ # Utilidades
│ ├─ _init_.py
│ └─ auth.py # Función: verificar_chat_autorizado()
├─ .env # Variables de entorno (NO commitear)
├─ .env.example # Plantilla de variables
├─ .gitignore
├─ AGENTS.md # Instrucciones para agentes AI
├─ CONTEXT.md # Contexto y decisiones de arquitectura
├─ HANDLERS.md # Documentación de cada handler
├─ README.md # Este archivo
├─ SCRIPTS.md # Documentación de módulos y funciones
└─ docs/
└─ sesiones/
└─ YYYY/MM-mes/
└─ YYYY-MM-DD.md # Registro de sesiones de desarrollo

text

## Índices y conexiones

### Módulos principales

| Módulo | Archivos | Propósito |
|--------|----------|-----------|
| `handlers/` | `start.py`, `help.py`, `diario.py`, `entrada.py` | Comandos de Telegram |
| `core/` | `organizar.py`, `bridge.py` | Lógica del diario |
| `utils/` | `auth.py` | Autenticación y autorización |

### Flujo de datos

Telegram (mensaje)
↓
bot.py (Application.run_polling)
↓
handlers/ (comando_*)
↓
utils/auth.py (verificar_chat_autorizado)
↓
core/ (organizar_texto / escribir_entrada)
↓
Sistema de archivos (diario en midgaror/diario/personal/)

text

### Dependencias entre módulos

bot.py
└─ imports → handlers/_init_.py
├─ handlers/start.py
├─ handlers/help.py
├─ handlers/diario.py → core/organizar.py
└─ handlers/entrada.py → core/bridge.py

handlers/diario.py
└─ imports → utils/auth.py
core/organizar.py

handlers/entrada.py
└─ imports → utils/auth.py
core/bridge.py

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

| Comando | Handler | Descripción | Ejemplo |
|---------|---------|-------------|---------|
| `/start` | `handlers/start.py` | Mensaje de bienvenida | `/start` |
| `/help` | `handlers/help.py` | Muestra ayuda completa | `/help` |
| `/diario <texto>` | `handlers/diario.py` | Inserta texto en "Qué ha pasado hoy" | `/diario Fui a caminar` |
| `/entrada <fecha> <texto>` | `handlers/entrada.py` | Crea/actualiza entrada para una fecha | `/entrada 2026-08-30 Gran día` |

## Documentación

| Archivo | Propósito |
|---------|-----------|
| [README.md](README.md) | Vista general, estructura, instalación |
| [SCRIPTS.md](SCRIPTS.md) | Documentación de módulos y funciones |
| [HANDLERS.md](HANDLERS.md) | Documentación detallada de cada comando |
| [CONTEXT.md](CONTEXT.md) | Contexto y decisiones de arquitectura |
| [AGENTS.md](AGENTS.md) | Instrucciones para agentes AI |
| [docs/sesiones/](docs/sesiones/) | Registro de sesiones de desarrollo |

## Pruebas

```bash
# 1. Asegurar que .env tiene token y chat_id válidos
cat .env

# 2. Ejecutar el bot
python3 bot.py

# 3. En Telegram, enviar:
/start       # Debería responder con mensaje de bienvenida
/help        # Debería mostrar ayuda
/diario Prueba desde Telegram  # Debería guardar en el diario
```

## Relación con midgaror

Este repositorio es un submódulo de [midgaror](https://github.com/alvarofernandezmota-tech/midgaror), el repo raíz del sistema personal.

### Conexión con el diario

- `core/organizar.py` y `core/bridge.py` escriben en `midgaror/diario/personal/YYYY/MM-mes/YYYY-MM-DD.md`
- Los handlers de Telegram llaman a estas funciones para guardar las entradas
- La ruta base del diario se calcula relativamente desde la ubicación de los scripts

### Uso desde midgaror

Los scripts en `midgaror/diario/` pueden importar funciones de `bifrost/core/` para mantener un único lugar de verdad:

```python
# En midgaror/diario/algun_script.py
import sys
from pathlib import Path

BIFROST = Path(__file__).parent.parent / "proyectos" / "bifrost"
sys.path.insert(0, str(BIFROST))

from core.organizar import organizar_texto
organizar_texto("Texto desde midgaror")
```
