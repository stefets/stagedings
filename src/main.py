#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

import os
import json
import asyncio
from services.logic import LogicService

from fastapi import Request, FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, payload):
        for connection in self.active_connections:
            await connection.send_json(payload)


manager = ConnectionManager()

"""  Configuration """

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

config = os.path.join("static", "config.json")
with open(config) as FILE:  
    configuration = json.load(FILE)


""" Mididings and OSC context """
logic = LogicService(configuration["osc_server"])


async def mididings_context_update():
    await logic.set_dirty(False)
    await manager.broadcast(
        {"action": "mididings_context_update", "payload": logic.scene_context.payload}
    )


@app.get("/", tags=["UI"], response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(name="index.html", context={"request": request})


@app.get("/ui", tags=["UI"], response_class=HTMLResponse)
async def ui(request: Request):
    return templates.TemplateResponse(
        name="ui.html" if logic.scene_context.scenes else "no_context.html",
        context={"request": request},
    )


# Endpoints (router)
@app.get("/api/panic", tags=["Control"], responses={204: {"description": "No content"}})
async def panic():
    await logic.panic()
    return Response(status_code=204)

@app.get("/api/query", tags=["Control"], responses={204: {"description": "No content"}})
async def query():
    await logic.query()
    return Response(status_code=204)

@app.get("/api/quit", tags=["Control"], responses={204: {"description": "No content"}})
async def quit():
    await logic.quit()
    return Response(status_code=204)

@app.get("/api/restart", tags=["Control"], responses={204: {"description": "No content"}})
async def restart():
    await logic.restart()
    return Response(status_code=204)

#
# Navigation endpoints
#
@app.get("/api/next_scene", tags=["Navigation"], responses={204: {"description": "No content"}})
async def next_scene():
    await logic.next_scene()
    return Response(status_code=204)    


@app.get("/api/prev_scene", tags=["Navigation"], responses={204: {"description": "No content"}})
async def prev_scene():
    await logic.prev_scene()
    return Response(status_code=204)

@app.get("/api/switch_scene/{id}", tags=["Navigation"], responses={204: {"description": "No content"}})
async def switch_scene_endpoint(id: int):
    await logic.switch_scene(id)
    return Response(status_code=204)

@app.get("/api/next_subscene", tags=["Navigation"], responses={204: {"description": "No content"}})
async def next_subscene():
    await logic.next_subscene()
    return Response(status_code=204)    

@app.get("/api/prev_subscene", tags=["Navigation"], responses={204: {"description": "No content"}})
async def prev_subscene():
    await logic.prev_subscene()
    return Response(status_code=204)

@app.get("/api/switch_subscene/{id}", tags=["Navigation"], responses={204: {"description": "No content"}})
async def switch_subscene_endpoint(id: int):
    await logic.switch_subscene(id)
    return Response(status_code=204)


""" Websocket handler """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send status periodic task
            await manager.broadcast(
                {"action": "on_start" if await logic.is_running() else "on_exit"}
            )

            try:
                # Handle incoming messages from the client
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                action = data["action"]

                if action in delegates:
                    (
                        await delegates[action]()
                        if not "payload" in data
                        else await delegates[action](int(data["payload"]))
                    )

            except asyncio.TimeoutError:
                # No message received during the timeout, continue the loop
                pass

            if await logic.is_dirty():
                await delegates["mididings_context_update"]()

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except asyncio.exceptions.CancelledError:
        print("------------------------CancelledError")
    finally:
        print("exit")


async def on_quit(websocket: WebSocket = None):
    await manager.broadcast(
        {
            "action": "on_terminate",
        }
    )


async def on_connect(websocket: WebSocket = None):
    await logic.set_dirty(True)


delegates = {

    "on_connect": on_connect,

    "quit": logic.quit,
    "panic": logic.panic,
    "query": logic.query,
    "restart": logic.restart,

    "next_scene": logic.next_scene,
    "prev_scene": logic.prev_scene,
    "next_subscene": logic.next_subscene,
    "prev_subscene": logic.prev_subscene,

    "switch_scene": logic.switch_scene,
    "switch_subscene": logic.switch_subscene,

    "mididings_context_update": mididings_context_update,
    
}
