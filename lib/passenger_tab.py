from pygame import Surface, Rect, transform, font, image

class PassengerTab(Surface):
    """ GUI tabs used in the Game.turn_menu """
    def __init__(self, position, size, passenger, resource_path):
        Surface.__init__(self, size)
        self.position = position
        self.size = size
        self.passenger = passenger
        self.text_font = font.Font(None, 15)
        self.passenger_surface = Surface(self.size).convert()
        self.rect = Rect(self.position, self.size)
        self.option_image = transform.scale(image.load(resource_path+"Images/option_icon.png"), (20, 20))
        self.option_rect = self.option_image.get_rect()

