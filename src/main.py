#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

import os
import json
from typing import Union
from threading import Lock
from services.live import LiveContext

from fastapi import FastAPI
app = FastAPI()

"""  Configuration """

filename = os.path.join('static', 'config.json')
with open(filename) as FILE:
    configuration = json.load(FILE)

thread = None
thread_lock = Lock()    

''' Mididings and OSC context '''
live_context = LiveContext(
    configuration["osc_server"])

'''
    Api routes
'''


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/next_scene")
def api_next_scene():
    next_scene()
    return '', 204


@app.get("/prev_scene")
def api_prev_scene():
    prev_scene()
    return '', 204


@app.get("/next_subscene")
def api_next_subscene():
    next_subscene()
    return '', 204


@app.get("/prev_subscene")
def api_prev_subscene():
    prev_subscene()
    return '', 204


@app.get("/switch_scene/{id}")
def api_switch_scene(id : int):
    switch_scene(id)
    return '', 204


@app.get("/switch_subscene/{id}")
def api_switch_subscene(id : int):
    switch_subscene(id)
    return '', 204


@app.get("/quit")
def api_quit():
    quit()
    return '', 204


@app.get("/panic")
def api_panic():
    panic()
    return '', 204


@app.get("/restart")
def api_restart():
    restart()
    return '', 204

''' Websockets event routes '''


''' API calls  '''

def mididings_context_update():
    live_context.set_dirty(False)


def quit():
    live_context.quit()


def panic():
    live_context.panic()


def query():
    live_context.query()


def restart():
    live_context.restart()


def next_subscene():
    live_context.next_subscene()


def next_scene():
    live_context.next_scene()


def prev_subscene():
    live_context.prev_subscene()


def prev_scene():
    live_context.prev_scene()


def switch_scene(id : int):
    live_context.switch_scene(id)


def switch_subscene(id : int):
    live_context.switch_subscene(id)