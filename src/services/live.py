#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later


'''
    This module is the equivalent of the mididings.live.livedings.LiveDings
'''


import liblo
from mididings.live.osc_control import LiveOSC


class LiveContext:
    def __init__(self, options) -> None:
        self.scene_context = SceneContext()
        self.server = OscContext(options, self.scene_context)

    def is_dirty(self) -> bool:
        return self.server.dirty

    async def set_dirty(self, value) -> None:
        self.server.dirty = value

    async def is_running(self) -> bool:
        return self.server.running

    async def next_scene(self) -> None:
        self.server.osc.next_scene()

    async def next_subscene(self) -> None:
        self.server.osc.next_subscene()

    async def prev_scene(self) -> None:
        self.server.osc.prev_scene()

    async def prev_subscene(self) -> None:
        self.server.osc.prev_subscene()

    async def panic(self) -> None:
        self.server.osc.panic()

    async def restart(self) -> None:
        self.server.osc.restart()

    async def query(self):
        self.server.osc.query()

    async def quit(self) -> None:
        self.server.osc.quit()

    async def switch_scene(self, value) -> None:
        self.server.osc.switch_scene(value)

    async def switch_subscene(self, value) -> None:
        self.server.osc.switch_subscene(value)


class OscContext:
    def __init__(self, options, scene_context):

        self.osc = LiveOSC(
            self, options["control_port"], options["listen_port"])

        self.dirty = False
        self.running = False

        self.scene_context = scene_context

        self.osc.start()
        self.osc.query()

    ''' LiveOSC callbacks '''

    '''Data offset'''

    def set_data_offset(self, data_offset):
        self.scene_context.data_offset = data_offset

    '''Scenes dictionary'''

    def set_scenes(self, scenes):
        self.scene_context.set_scenes(scenes)

    '''This is the last OSC operation from /query'''

    def set_current_scene(self, cur_scene, cur_subscene):
        self.scene_context.set_current_scene(cur_scene, cur_subscene)

        self.dirty = True
        self.running = True

    def on_start(self):
        ''' Engine start '''
        self.running = True

    def on_exit(self):
        ''' Engine stopped '''
        self.running = False


class SceneContext:
    def __init__(self) -> None:
        self.data_offset = -1
        self.scenes = []
        self.payload = None  # For the UI

    def find(self, id):
        return next(
            (candidate for candidate in self.scenes if candidate.id == id), None)

    def set_scenes(self, scenes):
        ''' Dictionary (int scene_id: tuple(str scene_name, list subscenes))'''
        self.scenes = []
        for key, scene_item in scenes.items():
            scene = Scene(key, scene_item[0])
            index = 0
            for subscene_name in scene_item[1]:
                index += 1
                scene.subscenes.append(SubScene(index, subscene_name))

            self.scenes.append(scene)

    def set_current_scene(self, cur_scene, cur_subscene):
        '''Build a friendly dict for the javascript'''
        items = []
        for scene in self.scenes:
            item = {
                "id": scene.id,
                "name": scene.name,
                "current": scene.id == cur_scene
            }

            subitems = []
            for subscene in scene.subscenes:
                subitem = {
                    "id": subscene.id,
                    "name": subscene.name,
                    "current": subscene.id == cur_subscene
                }
                subitems.append(subitem)

            item["subscenes"] = subitems

            items.append(item)

        self.payload = {"items": items}


class SceneBase:
    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name


class Scene(SceneBase):
    def __init__(self, id, name) -> None:
        super().__init__(id, name)
        self.subscenes = []


class SubScene(SceneBase):
    def __init__(self, id, name) -> None:
        super().__init__(id, name)
