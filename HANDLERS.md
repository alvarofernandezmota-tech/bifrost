# Handlers de Bifrost

Un handler traduce el mensaje de Telegram a una llamada a midgaror y la
respuesta a texto. **Ninguna lógica vive aquí** (ADR-009): lo que decide qué
se guarda y cómo está en `midgaror/diario/`, con sus pruebas.

Todos siguen el mismo patrón: `AYUDA` con los usos, `try` alrededor de la
llamada, `ValueError` → `⚠️ <mensaje>` (error del usuario, se le dice qué
escribir), cualquier otra excepción → log completo y `❌ Error:` (fallo
nuestro). Lo que escribe sube con `sincronizar()`, y la confirmación se acorta
con `utils/respuestas.breve()`.

---

## `/diario <texto>`

**Módulo**: `handlers/diario.py` → `organizar_texto()` de
`midgaror/diario/organizar_diario.py`

Inserta el texto en «Qué ha pasado hoy» de la entrada de hoy, con la hora
delante, sin pisar lo que ya hubiera.

---

## `/entrada <AAAA-MM-DD> <texto>`

**Módulo**: `handlers/entrada.py` → `escribir_entrada()` de
`midgaror/diario/bifrost_bridge.py`

Lo mismo, en el día que se diga. Crea la entrada si no existe.

---

## *(texto sin comando)*

**Módulo**: `handlers/texto.py` → lo mismo que `/diario`

Se registra **el último** en `bot.py`, con `filters.TEXT & ~filters.COMMAND`,
así que los comandos mandan. Escribir sin comando es lo normal: es como se usa
el bot el 90 % de las veces.

Pero `~filters.COMMAND` **no** quiere decir «no empieza por `/`»: quiere decir
«Telegram no lo marcó como `bot_command`». Un comando pegado con formato de
código llega marcado como `code` y cae aquí. Por eso el handler rechaza todo
lo que empiece por `/` con un aviso, y lo devuelve para poder reenviarlo. La
alternativa —escribirlo en el diario— es tragarse un comando en silencio, que
es lo que pasó el 2026-09-05 treinta veces seguidas.

---

## `/siento`, `/aprendo` y `/plan`

**Módulo**: `handlers/secciones.py` → `organizar_texto(..., seccion=...)` de
`midgaror/diario/organizar_diario.py`

| Mensaje | Va a | Cómo se ve |
|---|---|---|
| `/siento contento, he dormido bien` | `## Cómo me siento` | con la hora delante |
| `/aprendo lo de filters.COMMAND` | `## Avances / aprendizajes` | como viñeta |
| `/plan seguir con el portfolio` | `## Para mañana` | como viñeta |

**Por qué existen.** De las cuatro secciones de la plantilla, «Qué ha pasado
hoy» está rellena el 100 % de los días y las otras tres entre el 30 y el
40 %. La diferencia no es la disciplina: es que en la primera escribe el bot
y en las otras hay que abrir un editor (ADR-012, apartado 5).

**Por qué `/plan` y no `/mañana`.** Los comandos de Telegram solo admiten
`a-z`, `0-9` y `_`: con eñe no llegan marcados como comando.

La hora o la viñeta no las decide este handler: están en
`organizar_diario.SECCIONES`, con el resto de la lógica.

---

## `/tarea` y `/tareas`

**Módulo**: `handlers/tarea.py` → `midgaror/diario/tareas/tareas.py`

| Mensaje | Qué hace |
|---|---|
| `/tarea comprar el pan` | apunta una tarea sin fecha |
| `/tarea médico mañana a las 10` | apunta con fecha: la saca del texto con `fechas.py` |
| `/tarea empezar 3` | la pone en proceso (`◐`) |
| `/tarea hecha 3` · `/tarea reabrir 3` | la cierra o la devuelve a pendiente |
| `/tarea editar 3 comprar pan y leche` | le cambia el texto (y la fecha, si el texto nuevo la trae) |
| `/tarea aplazar 3 el lunes por la tarde` | le cambia solo la fecha |
| `/tarea borrar 3` | la retira; no se elimina, los ids no se reutilizan |
| `/tareas` | en proceso, pendientes por fecha (`⚠️ vencida` las pasadas) y últimas hechas |

Las acciones están en dos diccionarios, `SOLO_ID` y `CON_TEXTO`: añadir una
es añadir una línea, no otro `if`.

---

## `/cita` y `/agenda`

**Módulo**: `handlers/cita.py` → `midgaror/diario/agenda/agenda.py`

| Mensaje | Qué hace |
|---|---|
| `/cita médico mañana a las 10` | apunta una cita |
| `/cita mover 3 el lunes a las 17` | la cambia de día u hora |
| `/cita cancelar 3` | la retira |
| `/agenda` · `/agenda 2026-09-06` | las citas de un día |
| `/agenda semana` | los siete días desde hoy, agrupados por día |

**Una cita siempre lleva cuándo**; eso es lo que la separa de una tarea. Si el
texto no lo dice, se avisa y no se guarda nada. Sin hora, la cita es de todo
el día. Si el horario se pisa con otra, **se guarda igual y se avisa debajo**:
dos cosas a la misma hora pasan, y quien decide es Álvaro.

---

## `/habito` y `/habitos`

**Módulo**: `handlers/habito.py` → `midgaror/diario/habitos/habitos.py`

| Mensaje | Qué hace |
|---|---|
| `/habito deporte` · `/habito no meditar` | hecho o no hecho hoy |
| `/habito energia 7` | un valor del 1 al 10 en vez del sí o no |
| `/habito deporte 2026-09-03` | en otro día |
| `/habitos` · `/habitos semana` | el día, o la semana con totales y medias |

El número va suelto detrás del nombre; la fecha, detrás del número.

---

## `/hoy`

**Módulo**: `handlers/hoy.py` → `leer_entrada` + `agenda` + `tareas` + `habitos`

`/hoy [AAAA-MM-DD]` junta en un mensaje el diario del día, las citas, las
tareas y los hábitos. **Solo lee**: si no hay entrada, lo dice en vez de
crearla, y no sube nada. Si el mensaje entero no cabe, lo recorta
`utils/limites.py`, como cualquier otra respuesta del bot.

---

## El menú de comandos

`bot.py` publica la lista `MENU` con `setMyCommands` al arrancar
(`post_init=registrar_menu`): es lo que sale al pulsar «/» en el chat. Un
comando nuevo se añade ahí y aparece solo. Si Telegram no contesta, se
registra el fallo y **el bot arranca igual**: quedarse sin bot por no poder
pintar una lista sería peor.

---

## El límite de Telegram

**Todo lo que sale del bot pasa por `responder(update, texto)`**
(`utils/respuestas.py`). Es un punto único a propósito: había 47 llamadas
sueltas a `reply_text`, cualquiera podía pasarse de los 4096 de Telegram, y
algunas ni siquiera estaban dentro de un `try` — así que el error no llegaba
al usuario, se quedaba en el log.

`utils/limites.py` mide en **unidades UTF-16, como hace Telegram**, no con
`len()`: `📅` mide 1 para Python y 2 para Telegram, y hay una banda real
donde `len()` dice que cabe y Telegram lo rechaza. Recorta por **líneas
enteras** y dice cuántas faltan (`… y 92 líneas más`), porque una tarea
cortada por la mitad pierde su id, que es el asa para actuar sobre ella. Y
conserva las primeras, que el dominio ya ordena por urgencia.

Medido el 2026-09-05, antes del arreglo: `/hoy` reventaba con **29 tareas
pendientes**, `/tareas` con 81, `/agenda semana` con 126 citas y
`/habitos semana` con 68 hábitos. Cuando pasaba, el bot contestaba
`❌ Error: Message is too long` y ese comando quedaba inservible hasta
limpiar la lista.
