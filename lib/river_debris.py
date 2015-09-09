from pygame import sprite, image, transform

class RiverDebris(sprite.Sprite):
    """ Simple class used for river debris objects """

    def __init__(self, size, pos_x, pos_y, random_gen, picture, river_pos, resource_path):
        sprite.Sprite.__init__(self)
        self.picture = picture
        self.size = size
        self.river_pos = river_pos
        self.random_gen = random_gen
        self.preimage = image.load(resource_path+"Images/"+self.picture+".png")
        self.image = transform.scale(self.preimage, (int(self.preimage.get_width()*self.size),
                                     int(self.preimage.get_height()*self.size)))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def update(self, riverres):
        self.rect.y += 1
        if self.rect.top > riverres[1]:
            self.rect.y = -self.image.get_height()
            self.rect.x = random.randint(self.random_gen[0], self.random_gen[1])

