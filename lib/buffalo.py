from pygame.transform import scale
from pygame import image, font, Surface, Rect

class Buffalo():
    """ Buffalo object used in the Hunting minigame """
    def __init__(self, pos_x, pos_y, picture, size):
        self.picture = picture
        self.size = size
        self.max_health = 100 * self.size
        self.health = self.max_health
        self.preimage = image.load(resource_path+"Images/"+self.picture+"_buffalo.png")
        self.image = scale(self.preimage, (int(self.preimage.get_width()*self.size),
                                                            int(self.preimage.get_height()*self.size)))
        self.health_font = font.Font(None, 20)
        self.health_bar_container = Surface((int(75*self.size), int(12*self.size))).convert()
        self.health_bar_shader = Surface((self.health_bar_container.get_width() + 6,
                                                 self.health_bar_container.get_height() + 6)).convert()
        self.health_number = self.health_font.render(str(self.health), 1, (0, 0, 0))
        self.health_bar_shader.fill((175, 175, 175))
        self.health_bar = Surface(self.health_bar_container.get_size()).convert()
        self.health_color = ()
        if self.health >= 50:
                    self.health_color = (float((self.max_health-self.health)*2/self.max_health*255), 255, 0)
        else:
            self.health_color = (255, float(self.health*2/self.max_health*255), 0)
        try:
            self.health_bar.fill(self.health_color)
        except TypeError:
            self.health_bar.fill((0, 0, 0))
        self.health_bar_container.blit(self.health_bar, (0, 0))
        self.value = 20 * self.size
        self.rect = Rect((0, 0), self.image.get_size())
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.status = "alive"
        self.target_y = pos_y

    def update(self):
        # Checks the health and updates the health bar
        self.preimage = image.load(resource_path+"Images/"+self.status+"_buffalo.png")
        self.image = scale(self.preimage, (int(self.preimage.get_width()*self.size),
                                                            int(self.preimage.get_height()*self.size)))
        #Create health bar + shader + container
        self.health_bar_container = Surface((int(75*self.size), int(12*self.size))).convert()
        self.health_number = self.health_font.render(str(int(self.health)), 1, (255, 255, 255))
        self.health_bar_shader = Surface((self.health_bar_container.get_width() + 6,
                                                 self.health_bar_container.get_height() + 6)).convert()
        self.health_bar_shader.fill((175, 175, 175))
        if self.health <= 0:
            self.health_bar = Surface((0, 0)).convert()
        else:
            self.health_bar = Surface((int(self.health_bar_container.get_width()/self.max_health*self.health),
                                              self.health_bar_container.get_height())).convert()
            # Set the color of the health_bar_container Red->Yellow->Red based on HP
            if self.health >= 50:
                self.health_color = (float((self.max_health-self.health)*2/self.max_health*255), 255, 0)
            else:
                self.health_color = (255, float(self.health*2/self.max_health*255), 0)

            # Band-aid solution
            # It tends to crash here when self.health_color isn't a valid RGB for some reason
            try:
                self.health_bar.fill(self.health_color)
            except TypeError:
                self.health_bar.fill((0, 0, 0))
            self.health_bar_container.blit(self.health_bar, (0, 0))
        self.health_bar_container.blit(self.health_number, (self.health_bar_container.get_width()/2 -
                                                            self.health_number.get_width()/2,
                                                            self.health_bar_container.get_height()/2 -
                                                            self.health_number.get_height()/2))
        self.health_bar_shader.blit(self.health_bar_container, (3, 3))

        # Defines movement
        if self.status == "alive":
            # If buffalo is alive, move them until they reach their target X and Y positions
            # TODO: this logic should be reworked
            self.rect.x += float(3 - self.size)
            if self.rect.y != self.target_y:
                if self.rect.y < self.target_y:
                    self.rect.y += float(3 - self.size)
                elif self.rect.y > self.target_y:
                    self.rect.y -= float(3 - self.size)
            return self.rect.center


