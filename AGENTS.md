# Instrucciones para Agentes AI

## Contexto del proyecto

Bifrost es un bot de Telegram para escribir y organizar entradas del diario personal.

## Estado actual

✅ Bot funcional - Arranca y responde comandos
✅ `/entrada` arreglado (2026-09-04): pasaba una fecha que la funcion no aceptaba
⚠️ Pendiente - Probar contra Telegram real y dejarlo como servicio en Madre

## Estructura

bifrost/
├─ bot.py # Punto de entrada
├─ handlers/
│ ├─ diario.py # /diario → organizar_texto()
│ └─ entrada.py # /entrada → escribir_entrada()
├─ utils/
│ └─ auth.py # (pendiente)
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
- Falta autorizacion por chat_id (`utils/auth.py`).

## Reglas

- Nunca modificar `.env` (contiene secretos)
- Documentar cambios en `docs/sesiones/`
- Mantener imports de `midgaror/diario/` actualizados
