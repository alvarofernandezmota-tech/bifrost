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

### 3. Autorización por filtro, no por comprobación en cada handler

**Decisión**: el filtro de chats autorizados se aplica al registrar los
`CommandHandler`, no dentro de cada handler.

**Razón**:
- Un handler nuevo no puede olvidarse de comprobar el permiso: o se registra
  con el filtro o no se registra.
- Los no autorizados no reciben respuesta, que es lo que interesa: contestar
  confirma que el bot existe.
- Sin `TELEGRAM_CHAT_ID` el filtro es `None` y el bot responde a todos, como
  antes. Actualizar no rompe una instalación existente; el aviso del log es
  lo que empuja a configurarlo.

### 4. Entorno virtual

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

✅ Bot funcional y probado contra Telegram (2026-09-04)
✅ Documentación completa
✅ `/entrada` arreglado
✅ Autorización por chat_id (`utils/auth.py`)
✅ Unidad de systemd escrita (`systemd/bifrost.service`)
⚠️ Pendiente: instalarla en Madre y usar el bot 1-2 semanas (fase 2b)
