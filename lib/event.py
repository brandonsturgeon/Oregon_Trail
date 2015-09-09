from random import choice
from pygame import Surface, image

class Event():
    """ The random event class """
    def __init__(self, pos, name=None, resource_path=""):
        self.good_or_bad = choice([-1, 1])
        self.surface = Surface((0, 0)).convert()
        self.random_events = [self.river, self.house]
        self.name = name
        self.resource_path = resource_path
        self.pos = pos
        self.event_name = ""
        if self.name is not None:
            if self.name == "river":
                self.river()
            elif self.name == "house":
                self.house()
        else:
            self.event = choice(self.random_events)()
        self.event_pos = self.pos
        self.x_pos = (-self.event_pos * 40) + 1280

    def river(self):
        self.surface = Surface((100, 400)).convert()
        self.surface.fill((30, 144, 255))
        self.event_name = "river"

    def house(self):
        self.surface = image.load(self.resource_path + "Images/house.png")
        self.event_name = "house"

    def update(self, move_value):
        self.x_pos += 2 * move_value

