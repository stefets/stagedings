#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

from fastapi import  WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        if websocket not in self.active_connections:
            print(f"Connecting: {websocket.client}")
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        try:
            if websocket in self.active_connections:
                print(f"Disconnecting: {websocket.client}")
                self.active_connections.remove(websocket)
        except:
            print("Tried to remove a connection that is not in the list.")

    async def broadcast(self, message: dict):
        print(f"Broadcasting to {len(self.active_connections)} connections")
        for websocket in self.active_connections[:]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"WebSocket error: {e} for {websocket.client}")
                self.disconnect(websocket)
