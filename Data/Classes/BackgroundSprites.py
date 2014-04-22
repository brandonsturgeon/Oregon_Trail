import pygame
import random
class BackgroundSprites(pygame.sprite.Sprite): 
    def __init__(self, size, color, pos_x, pos_y, picture): 
        pygame.sprite.Sprite.__init__(self)
        self.picture = picture
        self.image = pygame.image.load(resource_path+"Images\\"+self.picture+".jpg")
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        self.size = size
        self.color = color
        
    def update(self, thegame): 
        if self.rect.right > thegame.game_window.get_width()+100: 
            self.rect.left = random.randint(-100, -30)
            if self.picture == "cloud": 
                random_y = random.randint(0, 100)
            elif self.picture == "tree": 
                random_y = random.randint(600, thegame.game_window.get_height())
            else:
                random_y = 0
            self.rect.centery = random_y
        self.rect.centerx += 2
