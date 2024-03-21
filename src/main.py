#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

import os
import json
import time
import asyncio
from typing import Union
from services.live import LiveContext
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

config = os.path.join('static', 'config.json')
with open(config) as FILE:
    settings = json.load(FILE)


''' Mididings and OSC context '''
live_context = LiveContext(
    settings["osc_server"])


async def osc_observer_thread():
    while True:
        await manager.broadcast({
                "action" : "on_start" if await live_context.is_running() else "on_exit"
        })
        await asyncio.sleep(0.125)


''' API Homepage '''
@app.get("/", response_class=HTMLResponse)
async def index(request : Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse(
        name="index.html", context=context
    )


''' Scene and subscene presentation'''
@app.get("/ui", response_class=HTMLResponse)
async def ui(request : Request, background_tasks: BackgroundTasks):
    context = {
        "request": request
    }

    if not background_tasks.tasks:
        print("Create observer")
        background_tasks.add_task(osc_observer_thread)

    return templates.TemplateResponse(
        name="ui.html" if live_context.scene_context.scenes else "no_context.html", context=context
    )

''' REST handler '''
@app.get("/api/")
async def api(action : str, payload : int = 0):
    if action in mididings_actions:
        await mididings_actions[action]() if payload == 0 else await mididings_actions[action](payload)
    return '', 204
    

''' Websockets handler '''
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()

            action = data['action']

            if action in mididings_actions:
                await mididings_actions[action]() if not "payload" in data else await mididings_actions[action](int(data['payload']))

            if action in logic_actions:
                await logic_actions[action](websocket)

            if live_context.is_dirty:
                await logic_actions["on_refresh"](websocket)

    except WebSocketDisconnect:
        await manager.disconnect(websocket)

    except asyncio.exceptions.CancelledError:
        print("------------------------CancelledError")

    finally:
        print("exit")


''' API calls  '''

async def on_refresh(websocket : WebSocket):
    time.sleep(0.125)   # This is mandatory to let time for mididings to process changes before re-render
    await manager.broadcast({
            "action" : "on_refresh",
            "payload" : live_context.scene_context.payload
    })
    await live_context.set_dirty(False)


async def on_quit(websocket : WebSocket):
    await websocket.send_json({
        "action" : "on_terminate",
    })


async def on_connect(websocket : WebSocket):
    await live_context.set_dirty(True)


mididings_actions = {
    "next_scene" : live_context.next_scene,
    "next_subscene" : live_context.next_subscene,
    "prev_scene" : live_context.prev_scene,
    "prev_subscene" : live_context.prev_subscene,
    "switch_scene" : live_context.switch_scene,
    "switch_subscene" : live_context.switch_subscene,
    "restart" : live_context.restart,
    "panic" : live_context.panic,
    "query" : live_context.query,
    "quit" : live_context.quit,
}


logic_actions = {
    "on_connect": on_connect,
    "on_refresh": on_refresh,
    "quit" : on_quit,
}
