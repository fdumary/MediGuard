# MediGuard FastAPI entrypoint. Wires up the REST routes, the live WebSocket
# feed, and CORS so the React frontend can talk to this backend.

from contextlib import asynccontextmanager
from pathlib import Path
import json

from dotenv import load_dotenv

# Ensure environment variables are loaded regardless of current working directory
_backend_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=_backend_dir / ".env")
load_dotenv(dotenv_path=_backend_dir.parent / ".env")
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.websocket import manager
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="MediGuard API", description="Complete Patient Safety Platform", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


async def handle_websocket_connection(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial confirmation so the client knows the feed is active
        await websocket.send_json({
            "type": "connection_established",
            "status": "connected",
            "message": "Live feed connected",
        })
        while True:
            raw_text = await websocket.receive_text()
            if raw_text == "ping":
                await websocket.send_text("pong")
            else:
                try:
                    msg = json.loads(raw_text)
                    if msg.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                except Exception:
                    pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@app.websocket("/ws")
async def websocket_ws(websocket: WebSocket):
    await handle_websocket_connection(websocket)


@app.websocket("/api/ws")
async def websocket_api_ws(websocket: WebSocket):
    await handle_websocket_connection(websocket)


@app.get("/")
async def root():
    return {"message": "MediGuard API is running", "status": "online"}
