from pygame import image, Rect

# Creates buttons with rectangle attached for the logbook
# TODO: is this even used?
class ScrollButton():
    def __init__(self, direction, resource_path):
        self.direction = direction
        if self.direction == "up":
            self.image = image.load(resource_path+"Images/uparrow.png")
        elif self.direction == "down":
            self.image = image.load(resource_path+"Images/downarrow.png")
        self.rect = Rect((0, 0), self.image.get_size())

    def update(self, position):
        self.rect = Rect(position, self.image.get_size())

