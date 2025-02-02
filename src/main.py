#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

import os
import json
import asyncio
from services.manager import ManagerService
from services.connection import ConnectionManager

from fastapi import Request, FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.openapi.utils import get_openapi

description = """
### You will be able to:

* **Navigating Scenes and Subscenes**
* **Control mididings**
"""

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = get_openapi(
        title="stagedings",
        version="0.0.1",
        summary="The UI & API for mididings community version",
        description=description,
        routes=app.routes,
        openapi_version="3.0.0",
    )
    app.openapi_schema["info"]["x-logo"] = {
        "url": "https://avatars.githubusercontent.com/u/121540801?s=400&u=2d3daf12927631aecd807b2d6dfb90652cc22ae8&v=4"
    }
    return app.openapi_schema

app.openapi = custom_openapi    


"""  Configuration """

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

config = os.path.join("static", "config.json")
with open(config) as FILE:  
    configuration = json.load(FILE)


# Mididings and OSC context
manager = ManagerService(configuration["osc_server"])

# WebSocket connection manager
connection_manager = ConnectionManager()

async def mididings_context_update():
    await manager.set_dirty(False)
    await connection_manager.broadcast(
        {"action": "mididings_context_update", "payload": manager.scene_service.payload}
    )

# UI enpoints
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(name="index.html", context={"request": request})


@app.get("/ui", response_class=HTMLResponse, include_in_schema=False)
async def ui(request: Request):
    return templates.TemplateResponse(
        name="ui.html" if manager.scene_service.scenes else "no_context.html",
        context={"request": request},
    )

# Navigation endpoints
@app.get("/switch_scene", summary="Switch to the given scene number.", tags=["Navigation"], responses={204: {"description": "No content"}})
async def switch_scene(id: int):
    await manager.switch_scene(id)
    return Response(status_code=204)

@app.get("/switch_subscene", summary="Switch to the given subscene number.", tags=["Navigation"], responses={204: {"description": "No content"}})
async def switch_subscene(id: int):
    await manager.switch_subscene(id)
    return Response(status_code=204)

@app.get("/prev_scene", summary="Switch to the previous scene.", tags=["Navigation"], responses={204: {"description": "No content"}})
async def prev_scene():
    await manager.prev_scene()
    await dele
    return Response(status_code=204)

@app.get("/next_scene", summary="Switch to the next scene.", tags=["Navigation"], responses={204: {"description": "No content"}})
async def next_scene():
    await manager.next_scene()
    return Response(status_code=204)    

@app.get("/prev_subscene", summary="Switch to the previous subscene.", tags=["Navigation"], responses={204: {"description": "No content"}})
async def prev_subscene():
    await manager.prev_subscene()
    return Response(status_code=204)

@app.get("/next_subscene", summary="Switch to the next subscene.", tags=["Navigation"], responses={204: {"description": "No content"}})
async def next_subscene():
    await manager.next_subscene()
    return Response(status_code=204)    

# Control endpoints
@app.get("/panic", summary="Send all-notes-off on all channels and on all output ports.", tags=["Control"], responses={204: {"description": "No content"}})
async def panic():
    await manager.panic()
    return Response(status_code=204)

@app.get("/quit", summary="Terminate mididings.", tags=["Control"], responses={204: {"description": "No content"}})
async def quit():
    await manager.quit()
    return Response(status_code=204)

@app.get("/restart", summary="Restart mididings.", tags=["Control"], responses={204: {"description": "No content"}})
async def restart():
    await manager.restart()
    return Response(status_code=204)

@app.get("/query", summary="Send config, current scene/subscene to all notify ports.", tags=["Control"], responses={204: {"description": "No content"}})
async def query():
    await manager.query()
    return Response(status_code=204)

""" Websocket handler """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            # Send status periodic task
            await connection_manager.broadcast(
                {"action": "on_start" if await manager.is_running() else "on_exit"}
            )

            try:
                # Handle incoming messages from the client
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                action = data["action"]

                if action in delegates:
                    (
                        await delegates[action]()
                        if not "id" in data
                        else await delegates[action](int(data["id"]))
                    )

            except asyncio.TimeoutError:
                # No message received during the timeout, continue the loop
                pass

            if await manager.is_dirty():
                await delegates["mididings_context_update"]()

    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except asyncio.exceptions.CancelledError:
        print("------------------------CancelledError")
    finally:
        print("exit")


async def on_quit(websocket: WebSocket = None):
    await connection_manager.broadcast(
        {
            "action": "on_terminate",
        }
    )


async def on_connect(websocket: WebSocket = None):
    await manager.set_dirty(True)


delegates = {

    "on_connect": on_connect,

    "quit": manager.quit,
    "panic": manager.panic,
    "query": manager.query,
    "restart": manager.restart,

    "next_scene": manager.next_scene,
    "prev_scene": manager.prev_scene,
    "next_subscene": manager.next_subscene,
    "prev_subscene": manager.prev_subscene,

    "switch_scene": manager.switch_scene,
    "switch_subscene": manager.switch_subscene,

    "mididings_context_update": mididings_context_update,
    
}
