# Contexto y Decisiones de Arquitectura

## Propósito

Bifrost es un bot de Telegram que permite escribir entradas del diario personal mediante comandos de texto.

## Decisiones de arquitectura

### 1. Estructura modular

**Decisión**: Separar código en módulos independientes (`handlers/`, `core/`, `utils/`)

**Razón**:
- Cada handler en archivo independiente para facilitar mantenimiento
- Lógica del diario (`core/`) separada de la interfaz de Telegram (`handlers/`)
- Reutilizable desde otros scripts (ej: `midgaror/diario/`)

### 2. Un único lugar de verdad

**Decisión**: La lógica del diario vive en `bifrost/core/`, no en `midgaror/diario/`

**Razón**:
- Evita duplicación de código
- El bot y los scripts de terminal usan las mismas funciones
- Más fácil de mantener y testear

### 3. Seguridad por chat autorizado

**Decisión**: Verificar `TELEGRAM_CHAT_ID` en cada comando

**Razón**:
- Previene que otros usuarios usen el bot
- Simple de implementar y mantener
- Suficiente para uso personal

### 4. Documentación en la raíz

**Decisión**: Mantener README, CONTEXT, AGENTS, HANDLERS, SCRIPTS en la raíz

**Razón**:
- Estándar de GitHub
- Fácil acceso desde la página principal del repo
- Separa documentación de código

## Relación con midgaror

- `bifrost` es un submódulo de `midgaror`
- `midgaror/diario/` puede importar funciones de `bifrost/core/`
- El diario se escribe en `midgaror/diario/personal/YYYY/MM-mes/YYYY-MM-DD.md`

## Dependencias

- `python-telegram-bot` - Bot de Telegram
- `python-dotenv` - Variables de entorno

## Estado actual

✅ Estructura modular completada
✅ Documentación alineada
⏳ Pendiente: pruebas funcionales del bot
