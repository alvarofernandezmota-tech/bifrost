# Scripts de Bifrost

## Estructura de módulos

bifrost/
├─ bot.py # Punto de entrada del bot
├─ handlers/ # Comandos de Telegram
│ ├─ start.py # /start
│ ├─ help.py # /help
│ ├─ diario.py # /diario
│ └─ entrada.py # /entrada
├─ core/ # Lógica del diario
│ ├─ organizar.py # organizar_texto()
│ └─ bridge.py # escribir_entrada()
└─ utils/ # Utilidades
└─ auth.py # verificar_chat_autorizado()

text

## bot.py

**Propósito**: Punto de entrada principal del bot de Telegram.

**Funciones**:
- Inicia la aplicación de Telegram
- Registra los handlers desde el módulo `handlers`
- Carga variables de entorno y configura logging

**Uso**:
```bash
python3 bot.py
```

## handlers/ (comandos)

Ver [HANDLERS.md](HANDLERS.md) para documentación detallada de cada comando.

| Comando | Módulo | Función | Descripción |
|---------|--------|---------|-------------|
| `/start` | `handlers/start.py` | `comando_inicio()` | Mensaje de bienvenida |
| `/help` | `handlers/help.py` | `comando_ayuda()` | Muestra ayuda completa |
| `/diario <texto>` | `handlers/diario.py` | `comando_diario()` | Inserta texto en la entrada de hoy |
| `/entrada <fecha> <texto>` | `handlers/entrada.py` | `comando_entrada()` | Crea/actualiza entrada para una fecha |

## core/ (lógica del diario)

### core/organizar.py

**Propósito**: Inserta texto en la sección correcta de una entrada del diario.

**Funciones**:
- `organizar_texto(texto, ruta=None)` - Inserta texto en la entrada especificada o en la de hoy

**Uso desde Python**:
```python
from core.organizar import organizar_texto
organizar_texto("Texto a insertar")  # Usa entrada de hoy por defecto
```

**Usado por**: `comando_diario()` en `handlers/diario.py`

### core/bridge.py

**Propósito**: Funciones de escritura de entradas del diario.

**Funciones**:
- `escribir_entrada(fecha, texto)` - Crea o actualiza una entrada para una fecha específica

**Uso desde Python**:
```python
from core.bridge import escribir_entrada
escribir_entrada("2026-08-30", "Hoy fue un gran día")
```

**Usado por**: `comando_entrada()` en `handlers/entrada.py`

## utils/ (utilidades)

### utils/auth.py

**Propósito**: Funciones de autenticación y autorización.

**Funciones**:
- `verificar_chat_autorizado(update)` - Verifica que el mensaje viene del chat autorizado

**Usado por**: Todos los handlers en `handlers/`

## Dependencias

- `python-telegram-bot` - Librería oficial de Telegram Bot API
- `python-dotenv` - Carga variables de entorno desde `.env`

## Configuración

Copiar `.env.example` a `.env` y rellenar:
- `TELEGRAM_BOT_TOKEN` - Token obtenido de @BotFather
- `TELEGRAM_CHAT_ID` - ID del chat autorizado (obtenido con /getUpdates o bot de @userinfobot)
