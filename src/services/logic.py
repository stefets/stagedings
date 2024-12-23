#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

'''
    Main service, driving the scene and osc context
'''


from .osc import OscLogic
from .scene import SceneLogic


class LogicService:
    def __init__(self, config) -> None:
        self.scene_context = SceneLogic()
        self.osc_context = OscLogic(config, self.scene_context)

    async def is_dirty(self):
        return self.osc_context.dirty

    async def set_dirty(self, value):
        self.osc_context.dirty = value

    async def is_running(self):
        return self.osc_context.running

    async def next_scene(self):
        self.osc_context.server.next_scene()

    async def next_subscene(self):
        self.osc_context.server.next_subscene()

    async def prev_scene(self):
        self.osc_context.server.prev_scene()

    async def prev_subscene(self):
        self.osc_context.server.prev_subscene()

    async def panic(self):
        self.osc_context.server.panic()

    async def restart(self):
        self.osc_context.server.restart()

    async def query(self):
        self.osc_context.server.query()

    async def quit(self):
        self.osc_context.server.quit()

    async def switch_scene(self, value):
        self.osc_context.server.switch_scene(value)

    async def switch_subscene(self, value):
        self.osc_context.server.switch_subscene(value)

