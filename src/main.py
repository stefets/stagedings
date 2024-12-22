#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

import os
import json
import time
import asyncio
from services.logic import LogicService

# from services.live import LiveContext
from fastapi import (
    Request,
    FastAPI,
    WebSocket,
    BackgroundTasks,
    WebSocketException,
    WebSocketDisconnect,
)
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

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

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
logic = None
logic = LogicService(configuration["osc_server"])


async def osc_observer_thread():
    while True:
        if await logic.is_dirty():
            await mididings_context_update()
        await manager.broadcast(
            {"action": "on_start" if await logic.is_running() else "on_exit"}
        )
        await asyncio.sleep(0.125)


async def mididings_context_update():
    await logic.set_dirty(False)
    await manager.broadcast({
        "action": "mididings_context_update",
        "payload" : logic.scene_context.payload
    })


async def get_mididings_context():
    await mididings_context_update()


'''
    REST API endpoints
'''


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(name="index.html", context={"request": request})


@app.get("/ui", response_class=HTMLResponse)
async def ui(request: Request, background_tasks: BackgroundTasks):
    if not background_tasks.tasks:
        print("Create observer")
        background_tasks.add_task(osc_observer_thread)

    return templates.TemplateResponse(
        name="ui.html" if logic.scene_context.scenes else "no_context.html",
        context={"request": request},
    )


"""
    REST API endpoints
"""


@app.get("/api/")
async def api(action: str, payload: int = 0):
    if action in mididings_actions:
        (
            await mididings_actions[action]()
            if payload == 0
            else await mididings_actions[action](payload)
        )
    return "", 204


""" Websockets handler """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()

            action = data["action"]

            if action in mididings_actions:
                (
                    await mididings_actions[action]()
                    if not "payload" in data
                    else await mididings_actions[action](int(data["payload"]))
                )

            if action in logic_actions:
                await logic_actions[action](websocket)

            if await logic.is_dirty():
                logic_actions["mididings_context_update"]

    except WebSocketDisconnect:
        await manager.disconnect(websocket)

    except asyncio.exceptions.CancelledError:
        print("------------------------CancelledError")

    finally:
        print("exit")


""" API calls  """


async def on_refresh(websocket: WebSocket):
    # This is mandatory to let time for mididings to process changes before re-render
    await asyncio.sleep(0.125)
    await manager.broadcast(
        {"action": "on_refresh", "payload": logic.scene_context.payload}
    )
    await logic.set_dirty(False)


async def on_quit(websocket: WebSocket):
    await websocket.send_json(
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
    "get_mididings_context" : get_mididings_context,
}


logic_actions = {
    "on_connect": on_connect,
    "on_refresh": on_refresh,
    "quit": on_quit,
    "mididings_context_update" : mididings_context_update
}
