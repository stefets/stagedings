#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

'''
    OSC service
'''


from mididings.live.osc_control import LiveOSC


class OscService:
    def __init__(self, config, scene_service):

        self.server = LiveOSC(
            self, config["control_port"], config["listen_port"])

        self.dirty = False
        self.running = False

        self.scene_service = scene_service

        self.server.start()
        self.server.query()

    ''' LiveOSC callbacks '''

    '''Data offset'''

    def set_data_offset(self, data_offset):
        self.scene_service.data_offset = data_offset

    '''Scenes dictionary'''

    def set_scenes(self, scenes):
        self.scene_service.set_scenes(scenes)

    '''This is the last OSC operation from /query'''

    def set_current_scene(self, cur_scene, cur_subscene):
        self.scene_service.set_current_scene(cur_scene, cur_subscene)

        self.dirty = True
        self.running = True

    def on_start(self):
        ''' Engine start '''
        self.running = True

    def on_exit(self):
        ''' Engine stopped '''
        self.running = False
