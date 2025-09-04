#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

'''
    Main controller, driving the scene and osc controllers
'''


from .osc import OscController
from .scene import SceneController


class Controller:
    def __init__(self, config) -> None:
        self.scene_controller = SceneController()
        self.osc_controller = OscController(config, self.scene_controller)

    async def is_dirty(self):
        return self.osc_controller.dirty

    async def set_dirty(self, value):
        self.osc_controller.dirty = value

    async def is_running(self):
        return self.osc_controller.running

    async def next_scene(self):
        self.osc_controller.server.next_scene()

    async def next_subscene(self):
        self.osc_controller.server.next_subscene()

    async def prev_scene(self):
        self.osc_controller.server.prev_scene()

    async def prev_subscene(self):
        self.osc_controller.server.prev_subscene()

    async def panic(self):
        self.osc_controller.server.panic()

    async def restart(self):
        self.osc_controller.server.restart()

    async def query(self):
        self.osc_controller.server.query()

    async def quit(self):
        self.osc_controller.server.quit()

    async def switch_scene(self, value):
        self.osc_controller.server.switch_scene(value)

    async def switch_subscene(self, value):
        self.osc_controller.server.switch_subscene(value)


