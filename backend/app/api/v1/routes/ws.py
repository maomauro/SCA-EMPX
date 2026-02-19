"""
WebSocket /ws/events — broadcast de eventos de acceso en tiempo real.

Permite que el frontend reciba notificaciones instantáneas sin hacer polling.
Cada cliente que se conecta queda suscrito a todos los eventos que emita
la aplicación mientras la conexión esté activa.

Mensajes emitidos por el servidor::

    {"type": "connected",  "message": "SCA-EMPX WebSocket activo"}
    {"type": "acceso",     "data": {id_persona, nombres, tipo_acceso, similitud, fecha}}
    {"type": "registro_completado", "data": {id_persona, nombres, n_embeddings}}
    {"type": "pong"}

Mensajes aceptados del cliente::

    "ping"  → el servidor responde con {"type": "pong"} (keepalive)
"""
import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Gestiona las conexiones WebSocket activas y distribuye mensajes.

    Mantiene una lista de sockets conectados y se encarga de enviar
    mensajes a todos ellos (broadcast), eliminando automáticamente las
    conexiones que fallen durante el envío.

    Attributes:
        active: Lista de WebSockets con conexión activa.
    """
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        """Acepta la conexión WebSocket y la registra en la lista activa.

        Args:
            ws: Instancia WebSocket de FastAPI pendiente de aceptar.
        """
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        """Elimina un WebSocket de la lista de conexiones activas.

        Es seguro llamarlo aunque el socket ya no esté en la lista.

        Args:
            ws: Instancia WebSocket a desregistrar.
        """
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, payload: dict[str, Any]):
        """Envía un mensaje JSON a todos los clientes conectados.

        Si el envío a un cliente falla (conexión caída), ese socket se
        elimina de la lista sin interrumpir el broadcast al resto.

        Args:
            payload: Diccionario serializable a JSON con el evento a emitir.
        """
        msg = json.dumps(payload, default=str)
        dead = []
        for ws in self.active:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


@router.websocket("/events")
async def websocket_events(ws: WebSocket):
    """Endpoint WebSocket que gestiona la conexión de un cliente.

    Al conectarse envía un mensaje de confirmación y queda en escucha
    activa. Responde a mensajes ``"ping"`` con ``"pong"`` para mantener
    viva la conexión. Cuando el cliente se desconecta, el socket se
    elimina limpiamente de ``ConnectionManager``.

    Args:
        ws: Instancia WebSocket inyectada por FastAPI.
    """
    await manager.connect(ws)
    try:
        await ws.send_text(json.dumps({"type": "connected", "message": "SCA-EMPX WebSocket activo"}))
        while True:
            try:
                data = await asyncio.wait_for(ws.receive_text(), timeout=25)
                if data == "ping":
                    await ws.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                pass  # keepalive
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(ws)
