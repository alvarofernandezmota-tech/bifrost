# Contexto y Decisiones de Arquitectura

## Propósito

Bifrost es un bot de Telegram que permite escribir entradas del diario personal mediante comandos.

## Decisiones de arquitectura

### 1. Handlers importan de midgaror/diario/

**Decisión**: Los handlers no duplican lógica, importan de `midgaror/diario/`

**Razón**:
- Un único lugar de verdad para la lógica del diario
- El bot y los scripts de terminal usan lo mismo
- Más fácil de mantener

### 2. Dos comandos separados

**Decisión**: `/diario` organiza, `/entrada` solo escribe

**Razón**:
- `organizar_diario.py` tiene problemas con marcadores existentes
- `bifrost_bridge.py` es más simple y fiable
- El usuario elige según necesite organizar o no

### 3. Entorno virtual

**Decisión**: `venv/` en la raíz, no se commitea

**Razón**:
- Aísla dependencias del bot
- No contamina el sistema
- `.gitignore` ya lo excluye

## Relación con midgaror

- `bifrost` es submódulo de `midgaror`
- Importa scripts de `midgaror/diario/`
- Escribe en `midgaror/diario/personal/`

## Estado actual

✅ Bot funcional
✅ Documentación completa
⚠️ Pendiente: refactorizar `organizar_diario.py`
