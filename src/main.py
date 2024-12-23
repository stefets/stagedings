#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

import os
import json
import asyncio
from services.logic import LogicService

from fastapi import Request, FastAPI, WebSocket, WebSocketDisconnect
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


"""
    REST API endpoints
"""


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(name="index.html", context={"request": request})


@app.get("/ui", response_class=HTMLResponse)
async def ui(request: Request):
    return templates.TemplateResponse(
        name="ui.html" if logic.scene_context.scenes else "no_context.html",
        context={"request": request},
    )


@app.get("/api/", status_code=204)
async def api(action: str, payload: int = 0):
    if action in mididings_actions:
        (
            await mididings_actions[action]()
            if payload == 0
            else await mididings_actions[action](payload)
        )
    return ""


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

            if await logic.is_dirty():
                await logic_actions["mididings_context_update"]()

            try:
                # Handle incoming messages from the client
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.125)
                action = data["action"]

                if action in mididings_actions:
                    (
                        await mididings_actions[action]()
                        if not "payload" in data
                        else await mididings_actions[action](int(data["payload"]))
                    )

                if action in logic_actions:
                    await logic_actions[action](websocket)

            except asyncio.TimeoutError:
                # No message received during the timeout, continue the loop
                pass
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except asyncio.exceptions.CancelledError:
        print("------------------------CancelledError")
    finally:
        print("exit")


async def on_quit(websocket: WebSocket):
    await manager.broadcast(
        {
            "action": "on_terminate",
        }
    )


async def on_connect(websocket: WebSocket):
    await logic.set_dirty(True)


mididings_actions = {
    "quit": logic.quit,
    "panic": logic.panic,
    "query": logic.query,
    "restart": logic.restart,
    "next_scene": logic.next_scene,
    "prev_scene": logic.prev_scene,
    "switch_scene": logic.switch_scene,
    "next_subscene": logic.next_subscene,
    "prev_subscene": logic.prev_subscene,
    "switch_subscene": logic.switch_subscene,
    "get_mididings_context": mididings_context_update,
}


logic_actions = {
    "on_connect": on_connect,
    "quit": on_quit,
    "mididings_context_update": mididings_context_update,
}
