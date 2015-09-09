from pygame import Rect

# Used to create rectangles around the affliction names in the Game.passenger_info() function
class AfflictionBox():
    def __init__(self, affliction, font, rect_position=(0, 0)):
        self.affliction = affliction
        self.rect_position = rect_position
        self.name = self.affliction.name
        self.font = font
        self.text_size = self.font.size(self.name)
        self.text_rect = Rect(self.rect_position, self.text_size)

    def update(self, rect_position):
        self.rect_position = rect_position
        self.text_rect.centerx = rect_position[0] + self.text_size[0]
        self.text_rect.centery = rect_position[1] + self.text_size[1]

