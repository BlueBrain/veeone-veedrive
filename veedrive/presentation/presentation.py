import json
import uuid


class Scene:
    def __init__(self, name, topics: [], theme="default"):
        self._id = str(uuid.uuid1())
        self.name = name
        self.topics = topics
        self.theme = theme

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Topic:
    def __init__(self, name, windows, layout="default"):
        self.name = name
        self.windows = windows
        self.layout = layout


class Window:
    def __init__(
        self,
        source=None,
        dimensions=None,
        size=None,
        selected=None,
        aspect=None,
        mode=None,
    ):
        self.source = source
        self.dimensions = dimensions
        self.size = size
        self.selected = selected
        self.aspect = aspect
        self.mode = mode

    def dumps(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def create_from_json(jsonObject):
        window = Window()
        for var in jsonObject:
            window.__setattr__(var, jsonObject[var])
        return window
