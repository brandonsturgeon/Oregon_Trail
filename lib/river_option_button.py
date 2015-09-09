from pygame import Surface, Rect, font

# Used to create interactive buttons in the RiverOptionMenu
class RiverOptionButton():
    def __init__(self, option, size, hover, pos):
        self.option = option
        self.size = size
        self.hover = hover
        self.size = size
        self.surface = Surface(self.size).convert()
        self.pos = pos
        if self.hover:
            self.surface.fill((200, 200, 200))
        else:
            self.surface.fill((255, 255, 255))
        self.rect = Rect(self.pos, self.size)
        self.button_font = font.Font(None, 25)
        self.surface.blit(self.button_font.render(self.option, 1, (0, 0, 0)),
                         (5, self.size[1]/2 - self.button_font.size("Lorem Ipsum")[1]/2))

    def update(self, hover):
        if hover:
            self.surface.fill((200, 200, 200))
        else:
            self.surface.fill((255, 255, 255))
        self.rect = Rect(self.pos, self.size)
        self.button_font = font.Font(None, 25)
        self.surface.blit(self.button_font.render(self.option, 1, (0, 0, 0)),
                         (5, self.size[1]/2 - self.button_font.size("Lorem Ipsum")[1]/2))

