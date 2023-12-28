from typing import Union

from fastapi import FastAPI

app = FastAPI()


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


@app.get("/switch_scene/<int:id>")
def api_switch_scene(id):
    switch_scene(id)
    return '', 204


@app.get("/switch_subscene/<int:id>")
def api_switch_subscene(id):
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


''' API calls  '''


def quit():
    pass #live_context.quit()


def panic():
    pass #live_context.panic()


def query():
    pass #live_context.query()


def restart():
    pass #live_context.restart()


def next_subscene():
    pass #live_context.next_subscene()


def next_scene():
    pass #live_context.next_scene()


def prev_subscene():
    pass #live_context.prev_subscene()


def prev_scene():
    pass #live_context.prev_scene()


def switch_scene(id):
    pass #live_context.switch_scene(id)


def switch_subscene(id):
    pass #live_context.switch_subscene(id)    