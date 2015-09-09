from pygame import Rect

class MenuButton():
    """ Creates buttons used in the Game menu_surface """
    def __init__(self, image, image_size=(0, 0), rect_position=(0, 0), name=None):
        self.image = image
        self.rect_position = rect_position
        self.image_size = image_size
        self.name = name
        self.rect = Rect(self.rect_position, self.image_size)

    def update(self, rect_position, image_size):
        self.rect_position = rect_position
        self.image_size = image_size
        self.rect = Rect(self.rect_position, self.image_size)
