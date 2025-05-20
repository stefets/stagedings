#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

'''
    Main service, driving the scene and osc context
'''


from .osc import OscService
from .scene import SceneService


class ManagerService:
    def __init__(self, config) -> None:
        self.scene_service = SceneService()
        self.osc_service = OscService(config, self.scene_service)

    async def is_dirty(self):
        return self.osc_service.dirty

    async def set_dirty(self, value):
        self.osc_service.dirty = value

    async def is_running(self):
        return self.osc_service.running

    async def next_scene(self):
        self.osc_service.server.next_scene()

    async def next_subscene(self):
        self.osc_service.server.next_subscene()

    async def prev_scene(self):
        self.osc_service.server.prev_scene()

    async def prev_subscene(self):
        self.osc_service.server.prev_subscene()

    async def panic(self):
        self.osc_service.server.panic()

    async def restart(self):
        self.osc_service.server.restart()

    async def query(self):
        self.osc_service.server.query()

    async def quit(self):
        self.osc_service.server.quit()

    async def switch_scene(self, value):
        self.osc_service.server.switch_scene(value)

    async def switch_subscene(self, value):
        self.osc_service.server.switch_subscene(value)


