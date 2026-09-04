# Instrucciones para Agentes AI

## Contexto del proyecto

Bifrost es un bot de Telegram para escribir y organizar entradas del diario personal.

## Estado actual

✅ Bot funcional - Arranca y responde comandos
✅ `/entrada` arreglado (2026-09-04): pasaba una fecha que la funcion no aceptaba
✅ Probado contra Telegram real (2026-09-04): escribe en el diario
✅ Autorizacion por chat_id (2026-09-04): `utils/auth.py`
⚠️ Pendiente - Dejarlo como servicio de systemd en Madre

## Estructura

bifrost/
├─ bot.py # Punto de entrada
├─ handlers/
│ ├─ diario.py # /diario → organizar_texto()
│ └─ entrada.py # /entrada → escribir_entrada()
├─ utils/
│ └─ auth.py # filtro de chats autorizados (TELEGRAM_CHAT_ID)
├─ venv/ # (NO commitear)
└─ docs/sesiones/

text

## Scripts en midgaror/diario/

- `organizar_diario.py` → `organizar_texto(texto, fecha=None)`, unico camino de escritura
- `bifrost_bridge.py` → `escribir_entrada(texto, fecha=None)`, contrato con este bot (ADR-009)
- `diario.py` → rutas y plantilla del diario

## Problemas conocidos

- Ninguno abierto en el codigo. Los marcadores `=======` no eran un fallo:
  son separadores propios del autor entre ratos del dia, y `organizar_texto`
  escribe dentro de la seccion sin tocarlos.
- El bot corre en primer plano: falta la unidad de systemd (fase 2b).

## Reglas

- Nunca modificar `.env` (contiene secretos)
- Documentar cambios en `docs/sesiones/`
- Mantener imports de `midgaror/diario/` actualizados
