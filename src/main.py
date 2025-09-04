#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

import os
import json
import asyncio
from core.control import Controller
from core.connection import ConnectionManager

from fastapi import Request, FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

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
        version="1.0.0",
        description=description,
        routes=app.routes,
        openapi_version="3.1.0",
        summary="An UI and API for mididings community version"
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
controller = Controller(configuration["osc_server"])

# WebSocket connection manager
connection_manager = ConnectionManager()

# Load environment variables
load_dotenv()

async def mididings_context_update():
    await controller.set_dirty(False)
    await connection_manager.broadcast(
        {"action": "mididings_context_update", "payload": controller.scene_controller.payload}
    )

# UI enpoints
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(name="index.html", context={"request": request})


@app.get("/ui", response_class=HTMLResponse, include_in_schema=False)
async def ui(request: Request):
    ws_host = os.getenv("STAGEDINGS_WS_HOST", "localhost")
    return templates.TemplateResponse(
        name="ui.html" if controller.scene_controller.scenes else "no_context.html",
        context={
            "request": request,
            "ws_host": ws_host,
        },
    )

# Navigation endpoints
# -----
@app.post("/api/scenes/{sceneId}/subscenes/{subsceneId}/activate", 
    description="Switch to the given scene and subscene number.", 
    summary="Switch to the given scene and subscene number.", 
    tags=["Navigation"], responses={204: {"description": "No content"}}
)
async def switch_scene(sceneId: int, subsceneId: int):
    await controller.switch_scene(sceneId)
    await controller.switch_subscene(subsceneId)
    return Response(status_code=204)

# -----
@app.post("/api/scenes/{sceneId}/activate", 
    description="Switch to the given scene number.", 
    summary="Switch to the given scene number.", 
    tags=["Navigation"], responses={204: {"description": "No content"}}
)
async def switch_scene(sceneId: int):
    await controller.switch_scene(sceneId)
    return Response(status_code=204)

# -----
@app.post("/api/subscenes/{subsceneId}/activate", 
    description="Switch to the given subscene number.", 
    summary="Switch to the given subscene number.", 
    tags=["Navigation"], responses={204: {"description": "No content"}}
)
async def switch_subscene(subsceneId: int):
    await controller.switch_subscene(subsceneId)
    return Response(status_code=204)

# -----
@app.post("/api/scenes/prev", description="Switch to the previous scene.",
    summary="Switch to the previous scene.", tags=["Navigation"], responses={204: {"description": "No content"}}
)
async def prev_scene():
    await controller.prev_scene()
    return Response(status_code=204)

# -----
@app.post("/api/scenes/next", description="Switch to the next scene.", 
         summary="Switch to the next scene.", tags=["Navigation"], responses={204: {"description": "No content"}}
)
async def next_scene():
    await controller.next_scene()
    return Response(status_code=204)

# -----
@app.post("/api/subscenes/prev", description="Switch to the previous subscene.", 
         summary="Switch to the previous subscene.", 
         tags=["Navigation"], responses={204: {"description": "No content"}}
)
async def prev_subscene():
    await controller.prev_subscene()
    return Response(status_code=204)

# -----
@app.post("/api/subscenes/next", description="Switch to the next subscene.", 
         summary="Switch to the next subscene.", tags=["Navigation"], responses={204: {"description": "No content"}}
)
async def next_subscene():
    await controller.next_subscene()
    return Response(status_code=204)    

# System endpoints
# -----
@app.post("/api/system/panic", description="Send all-notes-off on all channels and on all output ports.", 
         summary="Send all-notes-off on all channels and on all output ports.", 
         tags=["System"], responses={204: {"description": "No content"}})
async def panic():
    await controller.panic()
    return Response(status_code=204)

# -----
@app.post("/api/system/quit", description="Terminate mididings.", summary="Terminate mididings.", 
         tags=["System"], responses={204: {"description": "No content"}}
)
async def quit():
    await controller.quit()
    return Response(status_code=204)

# -----
@app.post("/api/system/restart", description="Restart mididings.", summary="Restart mididings.", 
         tags=["System"], responses={204: {"description": "No content"}}
)
async def restart():
    await controller.restart()
    return Response(status_code=204)

# -----
@app.post("/api/system/query", description="Send config, current scene/subscene to all notify ports.", 
         summary="Send config, current scene/subscene to all notify ports.", 
         tags=["System"], responses={204: {"description": "No content"}}
)
async def query():
    await controller.query()
    return Response(status_code=204)

""" Websocket handler """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while websocket in connection_manager.active_connections:
            # Send status periodic task
            await connection_manager.broadcast(
                {"action": "on_start" if await controller.is_running() else "on_exit"}
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

            if await controller.is_dirty():
                await delegates["mididings_context_update"]()

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)        
    except asyncio.exceptions.CancelledError:
        print("asyncio CancelledError exception")
    except Exception as e:
        print(f"Unexpected WebSocket error: {e}")
        connection_manager.disconnect(websocket)        
    finally:
        print("exit")


async def on_quit(websocket: WebSocket = None):
    await connection_manager.broadcast(
        {
            "action": "on_terminate",
        }
    )


async def on_connect(websocket: WebSocket = None):
    await controller.set_dirty(True)


delegates = {

    "on_connect": on_connect,

    "quit": controller.quit,
    "panic": controller.panic,
    "query": controller.query,
    "restart": controller.restart,

    "next_scene": controller.next_scene,
    "prev_scene": controller.prev_scene,
    "next_subscene": controller.next_subscene,
    "prev_subscene": controller.prev_subscene,

    "switch_scene": controller.switch_scene,
    "switch_subscene": controller.switch_subscene,

    "mididings_context_update": mididings_context_update,
    
}
