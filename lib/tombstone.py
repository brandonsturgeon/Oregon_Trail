from pygame import Rect

class Tombstone():
    """ Tombstone objects used to hold information about dead passengers """
    def __init__(self, position, status, passenger, cause_of_death, tomb_width, tomb_height):
        self.position = position
        self.status = status
        self.passenger = passenger
        self.cause_of_death = cause_of_death
        self.x_pos = (-self.position * 40) + 1280
        self.y_pos = 500
        self.tomb_width = tomb_width
        self.tomb_height = tomb_height
        self.tomb_rect = Rect((self.x_pos, self.y_pos), (self.tomb_width, self.tomb_height))
        self.tomb_rect.centerx = self.x_pos
        self.tomb_rect.centery = self.y_pos + self.tomb_height / 2

    def update(self, move_value):
        self.x_pos += 2 * move_value
        self.tomb_rect.centerx += 2 * move_value

