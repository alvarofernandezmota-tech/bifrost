# Handlers de Bifrost

Cada handler es un comando del bot de Telegram que responde a un `/comando`.

## Ubicación en el código

Todos los handlers están en `handlers/`:

- `handlers/start.py` → `/start`
- `handlers/help.py` → `/help`
- `handlers/diario.py` → `/diario`
- `handlers/entrada.py` → `/entrada`

---

## `/start` - Mensaje de bienvenida

**Módulo**: `handlers/start.py`

**Función**: `comando_inicio()`

**Propósito**: Saluda al usuario y muestra los comandos disponibles.

**Respuesta**:

👋 ¡Hola! Soy Bifrost, tu bot de diario personal.

Comandos disponibles:
/diario <texto> - Inserta texto en la entrada de hoy
/entrada <fecha> <texto> - Crea/actualiza entrada para una fecha
/start - Muestra este mensaje

text

**Código**: [`handlers/start.py`](handlers/start.py)

---

## `/help` - Mostrar ayuda

**Módulo**: `handlers/help.py`

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

**Código**: [`handlers/help.py`](handlers/help.py)

---

## `/diario <texto>` - Insertar texto en la entrada de hoy

**Módulo**: `handlers/diario.py`

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
1. Verifica que el chat está autorizado (`utils/auth.py`)
2. Valida que hay texto después del comando
3. Llama a `organizar_texto(texto)` de `core/organizar.py`
4. Devuelve la ruta del archivo guardado

**Código**: [`handlers/diario.py`](handlers/diario.py)

**Dependencias**:
- `utils/auth.verificar_chat_autorizado()`
- `core.organizar.organizar_texto()`

---

## `/entrada <fecha> <texto>` - Crear/actualizar entrada

**Módulo**: `handlers/entrada.py`

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
1. Verifica que el chat está autorizado (`utils/auth.py`)
2. Valida que hay fecha y texto después del comando
3. Llama a `escribir_entrada(fecha, texto)` de `core/bridge.py`
4. Devuelve la ruta del archivo guardado

**Código**: [`handlers/entrada.py`](handlers/entrada.py)

**Dependencias**:
- `utils/auth.verificar_chat_autorizado()`
- `core.bridge.escribir_entrada()`

---

## Funciones compartidas

### `utils/auth.verificar_chat_autorizado(update)`

**Módulo**: `utils/auth.py`

**Propósito**: Verifica que el mensaje viene del chat autorizado en `.env`.

**Uso**: Todos los handlers la llaman al inicio.

**Respuesta si no autorizado**:

❌ No estás autorizado para usar este bot.

text

**Código**: [`utils/auth.py`](utils/auth.py)

---

## Conexiones entre handlers

bot.py (punto de entrada)
│
└─ Application.run_polling()
│
├─ CommandHandler("start", comando_inicio)
│ └─ handlers/start.py
│
├─ CommandHandler("help", comando_ayuda)
│ └─ handlers/help.py
│
├─ CommandHandler("diario", comando_diario)
│ └─ handlers/diario.py
│ ├─ utils/auth.py (verificar_chat_autorizado)
│ └─ core/organizar.py (organizar_texto)
│
└─ CommandHandler("entrada", comando_entrada)
└─ handlers/entrada.py
├─ utils/auth.py (verificar_chat_autorizado)
└─ core/bridge.py (escribir_entrada)

text

Todos los handlers comparten:
- Configuración de entorno (`.env`)
- Logging
- Verificación de seguridad (`utils/auth.py`)
