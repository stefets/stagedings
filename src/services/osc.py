#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

'''
    OSC service
'''


import liblo
from mididings.live.osc_control import LiveOSC


class OscLogic:
    def __init__(self, config, scene_context):

        self.server = LiveOSC(
            self, config["control_port"], config["listen_port"])

        self.dirty = False
        self.running = False

        self.scene_context = scene_context

        self.server.start()
        self.server.query()

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
