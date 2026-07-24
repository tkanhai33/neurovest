import asyncio
from fastapi import APIRouter, WebSocket
from backend.app.core.cognitive_graph_state import graph_state

router = APIRouter()

connected = set()


@router.websocket("/ws/graph")
async def graph_ws(ws: WebSocket):
    await ws.accept()
    connected.add(ws)

    try:
        while True:
            await ws.send_json(graph_state.snapshot())
            await asyncio.sleep(0.5)

    except:
        connected.remove(ws)
