# bifrost — Agent instructions

## Contexto
bifrost es un bot Telegram que expone funciones de `diario.py` (midgaror) como comandos `/hoy`, `/leer`, etc.

## Reglas
- No reimplementar lógica de `diario.py`. Bifrost solo llama a funciones ya probadas en midgaror.
- Toda función nueva se prueba primero en terminal en midgaror, luego se expone como comando.
- Documentar cada comando en README.md.
