from pygame import Surface, font

class OptionButton():
    """ Vague option button used in the passenger_tabs in the turn menu """
    def __init__(self, passenger_tab, option, size, hover):
        self.passenger_tab = passenger_tab
        self.option = option
        self.size = size
        self.hover = hover
        self.passenger = passenger_tab.passenger
        self.button_surface = Surface(self.size).convert()
        if self.hover is not None and self.hover.option == self.option:
            self.button_surface.fill((200, 200, 200))
        else:
            self.button_surface.fill((255, 255, 255))
        self.button_rect = self.button_surface.get_rect()
        self.button_font = font.Font(None, 12)
        self.button_surface.blit(self.button_font.render(option, 1, (0, 0, 0)),
                                 (self.size[0]/2, self.size[1]/2))

