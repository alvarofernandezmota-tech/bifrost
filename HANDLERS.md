# Handlers de Bifrost

Cada handler es un comando del bot de Telegram que responde a un `/comando`.

## `/start` - Mensaje de bienvenida

**Función**: `comando_inicio()`

**Propósito**: Saluda al usuario y muestra los comandos disponibles.

**Respuesta**:

👋 ¡Hola! Soy Bifrost, tu bot de diario personal.

Comandos disponibles:
/diario <texto> - Inserta texto en la entrada de hoy
/entrada <fecha> <texto> - Crea/actualiza entrada para una fecha
/start - Muestra este mensaje

text

**Código**: `bot.py` líneas ~70-80

---

## `/help` - Mostrar ayuda

**Función**: `comando_ayuda()`

**Propósito**: Muestra ayuda detallada de cada comando.

**Respuesta**:

📖 Ayuda de Bifrost

/diario <texto>
Inserta texto en la sección 'Qué ha pasado hoy' de la entrada de hoy.

/entrada <fecha> <texto>
Crea o actualiza una entrada para la fecha especificada (YYYY-MM-DD).

/start - Mensaje de bienvenida
**/help** - Muestra esta ayuda

text

**Código**: `bot.py` líneas ~83-95

---

## `/diario <texto>` - Insertar texto en la entrada de hoy

**Función**: `comando_diario()`

**Propósito**: Inserta texto en la sección "Qué ha pasado hoy" de la entrada del día actual.

**Uso**:

/diario Fui a caminar 13km por Madrid

text

**Respuesta exitosa**:

✅ Texto guardado en: /ruta/a/diario/personal/2026/08-agosto/2026-08-30.md

text

**Respuesta de error**:

❌ Error: <mensaje de error>

text

**Flujo**:
1. Verifica que el chat está autorizado
2. Valida que hay texto después del comando
3. Llama a `organizar_texto(texto)` de `organizar_diario.py`
4. Devuelve la ruta del archivo guardado

**Código**: `bot.py` líneas ~35-50

---

## `/entrada <fecha> <texto>` - Crear/actualizar entrada

**Función**: `comando_entrada()`

**Propósito**: Crea o actualiza una entrada del diario para una fecha específica.

**Uso**:

/entrada 2026-08-30 Hoy fue un gran día

text

**Respuesta exitosa**:

✅ Entrada creada/actualizada en: /ruta/a/diario/personal/2026/08-agosto/2026-08-30.md

text

**Respuesta de error**:

❌ Error: <mensaje de error>

text

**Flujo**:
1. Verifica que el chat está autorizado
2. Valida que hay fecha y texto después del comando
3. Llama a `escribir_entrada(fecha, texto)` de `bifrost_bridge.py`
4. Devuelve la ruta del archivo guardado

**Código**: `bot.py` líneas ~53-68

---

## Funciones compartidas

### `verificar_chat_autorizado(update)`

**Propósito**: Verifica que el mensaje viene del chat autorizado en `.env`.

**Uso**: Todos los handlers la llaman al inicio.

**Respuesta si no autorizado**:

❌ No estás autorizado para usar este bot.

text

**Código**: `bot.py` líneas ~25-32

---

## Conexiones entre handlers

bot.py
├─ verificar_chat_autorizado() ← usado por todos los handlers
├─ comando_inicio() ← /start
├─ comando_ayuda() ← /help
├─ comando_diario() ← /diario
│ └─ llama a → organizar_texto() (organizar_diario.py)
└─ comando_entrada() ← /entrada
└─ llama a → escribir_entrada() (bifrost_bridge.py)

text

Todos los handlers están en `bot.py` y comparten:
- Configuración de entorno (`.env`)
- Logging
- Verificación de seguridad (chat autorizado)
