# Instrucciones para Agentes AI

## Contexto del proyecto

Bifrost es un bot de Telegram para escribir y organizar entradas del diario personal.

## Estructura del código

bifrost/
├─ bot.py # Punto de entrada (inicia el bot)
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

## Flujo de ejecución

1. `bot.py` inicia la aplicación de Telegram
2. Registra los handlers desde `handlers/__init__.py`
3. Cada handler:
   - Verifica autorización con `utils/auth.py`
   - Llama a la función correspondiente en `core/`
4. `core/organizar.py` y `core/bridge.py` escriben en el sistema de archivos

## Reglas para modificar código

- **Nunca** modificar `.env` (contiene secretos)
- Usar `.env.example` como plantilla
- Los handlers solo llaman a funciones de `core/`, no escriben directamente en archivos
- Mantener imports relativos dentro del mismo módulo
- Documentar cambios en `docs/sesiones/`

## Comandos disponibles

| Comando | Handler | Función core |
|---------|---------|--------------|
| `/start` | `handlers/start.py` | - |
| `/help` | `handlers/help.py` | - |
| `/diario` | `handlers/diario.py` | `core.organizar.organizar_texto()` |
| `/entrada` | `handlers/entrada.py` | `core.bridge.escribir_entrada()` |
