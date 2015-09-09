from pygame import sprite, image

class BackgroundSprites(sprite.Sprite):
    """ Sprites used for the background """

    def __init__(self, size, color, pos_x, pos_y, picture, resource_path):
        sprite.Sprite.__init__(self)
        self.picture = picture
        self.image = image.load(resource_path+"Images/"+self.picture+".png")
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        self.size = size
        self.color = color

    def update(self, thegame):
        if self.rect.right > thegame.game_window.get_width()+100:
            self.rect.left = random.randint(-150, -100)
            if self.picture == "cloud":
                random_y = random.randint(0, 100)
            elif self.picture == "tree":
                random_y = random.randint(thegame.game_window.get_height() - thegame.game_window.get_height() / 3 - 45,
                                          thegame.game_window.get_height() - thegame.game_window.get_height() / 3 - 5)
            else:
                random_y = 0
            self.rect.centery = random_y
        self.rect.centerx += 2 * thegame.move_value

