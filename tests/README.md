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

No se usa el `python-telegram-bot` de verdad a propósito:

- Lo que hay que probar es **nuestro** código, no el de la librería.
- Las pruebas corren en cualquier sitio, sin instalar nada.
- Y sobre todo: así se puede simular **lo que Telegram hace de verdad**,
  como mandar un mensaje que empieza por `/` sin marcarlo como
  `bot_command`. Eso es exactamente lo que rompió el bot el 2026-09-05.

`sincronizar()` también se sustituye: haría `git commit` y `git push`. Si un
handler nuevo se olvida en esa lista, su prueba falla con un aviso de que el
fichero está fuera del repo, así que la red no se toca ni por accidente.

## Qué se cubre

| Fichero | Qué prueba |
|---|---|
| `test_tarea.py` | las siete acciones de `/tarea`, el orden de `/tareas` y los cinco errores de uso |
| `test_cita.py` | alta, choque de horario, todo el día, mover, cancelar y `/agenda` día y semana |
| `test_habito.py` | sí/no, valor del 1 al 10, otra fecha, y que el número y el sí/no conviven en los totales |
| `test_diario.py` | que cada comando escribe **en su sección y solo en la suya**, y que el texto libre **no se traga comandos** |
| `test_hoy.py` | que junta las cuatro partes, que **no escribe nada** y que el recorte no se come el resto |
| `test_menu.py` | que el menú de «/» y los `CommandHandler` no se separen; lee `bot.py` con `ast`, sin arrancar el bot |

## Lo que estas pruebas NO dicen

Y conviene tenerlo claro, porque es donde estuvo el fallo del 2026-09-05:

- Que **Telegram** marque un mensaje como comando.
- Que lo desplegado en Madre sea este código (`git pull`, submódulo, reinicio).
- Que el token valga y el chat esté autorizado.
- Que `sincronizar` empuje de verdad a GitHub.
- Que el menú aparezca en el móvil.
- Que **se use**. Eso lo dicen los 15 días.

Las pruebas quitan la repetición, no la primera vez.
