from pydantic import BaseModel
from typing import List, Optional

class SceneBase(BaseModel):
    id: int
    name: str


class SubScene(SceneBase):
    pass


class Scene(SceneBase):
    subscenes: List[SubScene] = []