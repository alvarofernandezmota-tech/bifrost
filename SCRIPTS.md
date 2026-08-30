# Scripts de Bifrost

## bot.py

Punto de entrada del bot. Inicia la aplicación de Telegram y registra handlers.

**Dependencias**:
- `python-telegram-bot`
- `python-dotenv`

## handlers/

### handlers/diario.py

Importa `organizar_texto()` de `midgaror/diario/organizar_diario.py`.

**Problema**: Ese script no maneja bien marcadores `=======` existentes.

### handlers/entrada.py

Importa `escribir_entrada()` de `midgaror/diario/bifrost_bridge.py`.

**Ventaja**: Escribe sin organizar, más fiable.

## Scripts en midgaror/diario/

- `organizar_diario.py` → organiza texto en secciones
- `bifrost_bridge.py` → escribe sin organizar
- `diario.py` → funciones auxiliares (ruta_de_hoy, crear_desde_plantilla)
