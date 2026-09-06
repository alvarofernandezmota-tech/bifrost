# tests/

Pruebas de los handlers de bifrost. Se corren igual que las de midgaror:

```bash
python3 -m unittest discover -s tests
```

Tardan menos de un décimo de segundo, **no necesitan red ni Telegram
instalado**, y no tocan ni el diario ni git.

## Cómo funciona

`dobles.py` instala un paquete `telegram` de mentira en `sys.modules` antes
de que se importe ningún handler, y `CasoBot` deja cada prueba con el diario
y los tres JSON vacíos en un directorio temporal.

Las rutas a `midgaror/diario/` **no se calculan aquí**: salen de
`utils/midgaror.py`, el mismo camino que usa el bot de verdad. Antes estaban
repetidas en este fichero y en los ocho handlers.

No se usa el `python-telegram-bot` de verdad a propósito:

- Lo que hay que probar es **nuestro** código, no el de la librería.
- Las pruebas corren en cualquier sitio, sin instalar nada.
- Y sobre todo: así se puede simular **lo que Telegram hace de verdad**,
  como mandar un mensaje que empieza por `/` sin marcarlo como
  `bot_command`. Eso es exactamente lo que rompió el bot el 2026-09-05.

`Mensaje.reply_text` **levanta `DemasiadoLargo` cuando el texto pasa de 4096
unidades UTF-16**, igual que Telegram. Sin eso, las pruebas de tamaño serían
tautológicas: `❌ Error: Message is too long` también cabe en 4096, así que
pasaban en verde con el bug puesto. Comprobado deshaciendo el arreglo.

`sincronizar()` también se sustituye: haría `git commit` y `git push`. Si un
handler nuevo se olvida en esa lista, su prueba falla con un aviso de que el
fichero está fuera del repo, así que la red no se toca ni por accidente.

`dobles.py` apaga el log con `logging.disable(CRITICAL)`, y eso deja `assertLogs`
y `assertNoLogs` sin poder decir la verdad: el primero falla siempre y el segundo
**pasa siempre**, aunque el aviso esté puesto. Una prueba que mire avisos tiene
que envolverse en `logs_visibles()`, que lo enciende dentro del `with`.

## Qué se cubre

| Fichero | Qué prueba |
|---|---|
| `test_tarea.py` | las siete acciones de `/tarea`, el orden de `/tareas` y los cinco errores de uso |
| `test_cita.py` | alta, choque de horario, todo el día, mover, cancelar y `/agenda` día y semana |
| `test_habito.py` | sí/no, valor del 1 al 10, otra fecha, y que el número y el sí/no conviven en los totales |
| `test_diario.py` | que cada comando escribe **en su sección y solo en la suya**, y que el texto libre **no se traga comandos** |
| `test_hoy.py` | que junta las cuatro partes, que **no escribe nada** y que el recorte no se come el resto |
| `test_limites.py` | que ningún comando se pase de los 4096 de Telegram: listas enormes, ecos del texto del usuario y el aviso de comando pegado |
| `test_menu.py` | que el menú de «/» y los `CommandHandler` no se separen; lee `bot.py` con `ast`, sin arrancar el bot |
| `test_auth.py` | quién puede darle órdenes al bot: cómo se lee `TELEGRAM_CHAT_ID` y que el aviso de «sin restricción» esté ahí |
| `test_botones.py` | el menú de botones entero: el teclado, la pregunta de cada botón, que la respuesta acabe **donde su comando**, y que un chat no autorizado no reciba nada |

## Lo que estas pruebas NO dicen

Y conviene tenerlo claro, porque es donde estuvo el fallo del 2026-09-05:

- Que **Telegram** marque un mensaje como comando.
- Que lo desplegado en Madre sea este código (`git pull`, submódulo, reinicio).
- Que el token valga y el chat esté autorizado.
- Que `sincronizar` empuje de verdad a GitHub.
- Que el menú aparezca en el móvil.
- Que **se use**. Eso lo dicen los 15 días.

Las pruebas quitan la repetición, no la primera vez.
