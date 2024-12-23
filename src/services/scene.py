#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later


'''
    Scene logic
'''


class SceneLogic:
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
            scene = SceneDto(key, scene_item[0])
            index = 0
            for subscene_name in scene_item[1]:
                index += 1
                scene.subscenes.append(SubSceneDto(index, subscene_name))

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


class SceneBaseDto:
    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name


class SceneDto(SceneBaseDto):
    def __init__(self, id, name) -> None:
        super().__init__(id, name)
        self.subscenes = []


class SubSceneDto(SceneBaseDto):
    def __init__(self, id, name) -> None:
        super().__init__(id, name)