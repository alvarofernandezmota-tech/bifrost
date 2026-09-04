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

**Decisión**: `/diario` escribe en hoy, `/entrada` en la fecha que se le diga

**Razón** (actualizada 2026-09-04):
- La razón original era que `organizar_diario.py` fallaba con marcadores
  existentes, así que `/entrada` escribía "sin organizar". Ese fallo ya no
  existe: los `=======` son separadores del autor, no un problema de formato.
- Los dos comandos usan hoy el mismo camino de escritura, dentro de la
  sección "Qué ha pasado hoy". Lo único que cambia es el día de destino.
- `/entrada` estuvo roto desde el principio: pasaba una fecha que
  `escribir_entrada` no aceptaba.

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
✅ `/entrada` arreglado y probado (2026-09-04)
⚠️ Pendiente: prueba real contra Telegram, servicio systemd en Madre y autorización por chat_id
