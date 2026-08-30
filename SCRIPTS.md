# Scripts de Bifrost

## bot.py

**Propósito**: Script principal del bot de Telegram.

**Funciones**:
- Escucha comandos de Telegram
- Verifica que el chat esté autorizado
- Llama a `organizar_texto()` y `escribir_entrada()` según el comando

**Comandos**:
- `/start` - Mensaje de bienvenida
- `/help` - Muestra ayuda
- `/diario <texto>` - Inserta texto en la entrada de hoy
- `/entrada <fecha> <texto>` - Crea/actualiza entrada para una fecha

**Uso**:
```bash
python3 bot.py
```

## organizar_diario.py

**Propósito**: Inserta texto en la sección correcta de una entrada del diario.

**Funciones**:
- `organizar_texto(texto, ruta=None)` - Inserta texto en la entrada especificada o en la de hoy

**Uso desde terminal**:
```bash
python3 organizar_diario.py --input "Texto a insertar" --output /ruta/a/entrada.md
```

**Uso desde Python**:
```python
from organizar_diario import organizar_texto
organizar_texto("Texto a insertar")  # Usa entrada de hoy por defecto
```

## bifrost_bridge.py

**Propósito**: Funciones de escritura de entradas del diario.

**Funciones**:
- `escribir_entrada(fecha, texto)` - Crea o actualiza una entrada para una fecha específica

**Uso desde Python**:
```python
from bifrost_bridge import escribir_entrada
escribir_entrada("2026-08-30", "Hoy fue un gran día")
```

## Dependencias

- `python-telegram-bot` - Librería oficial de Telegram Bot API
- `python-dotenv` - Carga variables de entorno desde `.env`

## Configuración

Copiar `.env.example` a `.env` y rellenar:
- `TELEGRAM_BOT_TOKEN` - Token obtenido de @BotFather
- `TELEGRAM_CHAT_ID` - ID del chat autorizado (obtenido con /getUpdates o bot de @userinfobot)
