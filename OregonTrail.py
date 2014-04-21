#######################
# Oregon Trail Remake #
#######################

###########
# Imports #
###########

import pygame
import random
import eztext
import string
import copy
import colorsys
import pickle
import time

pygame.init()
clock = pygame.time.Clock()

#######################
# Beginning Variables #
#######################
#sampleDisease("Disease Name": (Chance to infect, Infectivity, Season, Health Change, (min recovery, max recovery))}
afflictions_dict = {"The Common Cold":  (10, 10, "winter", -2.5, (4, 10)),
                    "The Flu": (10, 10, "winter", -5.5, (9, 15)),
                    "Hunger": (0, 0, "none", -2, -1),
                    "Well Fed": (0, 0, "none", 2, -1)
                    }
passenger_list = []
afflictions_list = []
deceasedList = []
group_afflictions = []


resource_path = "Resources\\"
male_picture_list = ["maleface1", "maleface2", "maleface3", "maleface4", "maleface5"]
female_picture_list = ["maleface2"]  # Temporary until female faces are added

###########
# Classes #
###########


# Class used to create diseases
class AfflictionsClass():
    def __init__(self, name, chance_to_infect, infectivity, prime_season, health_change, recovery_time):
        self.name = name
        self.chance_to_infect = chance_to_infect
        self.infectivity = infectivity
        self.prime_season = prime_season
        self.health_change = health_change
        self.recovery_time = recovery_time

    # Sets equality to self.name
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        else:
            return False

    # Sets the inequality
    def __ne__(self, other):
        return not __eq__(self, other)


# Sprites used for the background
class BackgroundSprites(pygame.sprite.Sprite):
    def __init__(self, size, color, pos_x, pos_y, picture):
        pygame.sprite.Sprite.__init__(self)
        self.picture = picture
        self.image = pygame.image.load(resource_path+"Images\\"+self.picture+".png")
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


# Simple class used for river debris objects
class RiverDebris(pygame.sprite.Sprite):
    def __init__(self, size, pos_x, pos_y, random_gen, picture, river_pos):
        pygame.sprite.Sprite.__init__(self)
        self.picture = picture
        self.size = size
        self.river_pos = river_pos
        self.random_gen = random_gen
        self.preimage = pygame.image.load(resource_path+"Images\\"+self.picture+".png")
        self.image = pygame.transform.scale(self.preimage, (int(self.preimage.get_width()*self.size),
                                            int(self.preimage.get_height()*self.size)))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def update(self, riverres):
        self.rect.y += 1
        if self.rect.top > riverres[1]:
            self.rect.y = -self.image.get_height()
            self.rect.x = random.randint(self.random_gen[0], self.random_gen[1])


# The Passenger class
class Passenger():
    def __init__(self, name, age, gender, picture):
        self.name = name
        self.age = age
        self.gender = gender
        self.picture = picture
        self.afflictions = []
        self.health = 100
        self.food_divisions = 2
        self.status = "Healthy"

    def __str__(self):
        return self.name


# GUI tabs used in the Game.turn_menu
class PassengerTab(pygame.Surface):
    def __init__(self, position, size, passenger):
        pygame.Surface.__init__(self, size)
        self.position = position
        self.size = size
        self.passenger = passenger
        self.text_font = pygame.font.Font(None, 15)
        self.passenger_surface = pygame.Surface(self.size)
        self.rect = pygame.Rect(self.position, self.size)
        self.option_image = pygame.transform.scale(pygame.image.load(resource_path+"Images\\option_icon.png"), (20, 20))
        self.option_rect = self.option_image.get_rect()


# Vague option button used in the passenger_tabs in the turn menu
class OptionButton():
    def __init__(self, passenger_tab, option, size, hover):
        self.passenger_tab = passenger_tab
        self.option = option
        self.size = size
        self.hover = hover
        self.passenger = passenger_tab.passenger
        self.button_surface = pygame.Surface(self.size)
        if self.hover is not None and self.hover.option == self.option:
            self.button_surface.fill((200, 200, 200))
        else:
            self.button_surface.fill((255, 255, 255))
        self.button_rect = self.button_surface.get_rect()
        self.button_font = pygame.font.Font(None, 12)
        self.button_surface.blit(self.button_font.render(option, 1, (0, 0, 0)),
                                 (self.size[0]/2, self.size[1]/2))


# Displays the faces to select on character creation
class ShowFaces():
    def __init__(self, file_path, color=(0, 0, 0), x_pos=0, y_pos=100):
        self.file_path = file_path
        self.color = color
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.image = pygame.image.load(resource_path+"Images\\Faces\\"+self.file_path+".png")
        self.face_rect = self.image.get_rect()

    def update(self):
        self.face_rect.centerx = self.x_pos + self.image.get_width()/2
        self.face_rect.centery = self.y_pos + self.image.get_height()/2

    def create(self):
        self.image = pygame.image.load(resource_path+"Images\\Faces\\"+self.file_path+".png")
        self.face_rect = self.image.get_rect()
        self.update()


# Tombstone objects used to hold information about dead passengers
class Tombstones():
    def __init__(self, position, status, passenger, cause_of_death, tomb_width, tomb_height):
        self.position = position
        self.status = status
        self.passenger = passenger
        self.cause_of_death = cause_of_death
        self.x_pos = (-self.position * 40) + 1280
        self.y_pos = 500
        self.tomb_width = tomb_width
        self.tomb_height = tomb_height
        self.tomb_rect = pygame.Rect((self.x_pos, self.y_pos), (self.tomb_width, self.tomb_height))
        self.tomb_rect.centerx = self.x_pos
        self.tomb_rect.centery = self.y_pos + self.tomb_height / 2

    def update(self, move_value):
        self.x_pos += 2 * move_value
        self.tomb_rect.centerx += 2 * move_value


# Creates the shopping menu for each town
class Shop():
    def __init__(self, name, inventory, price_mod, group_inventory,
                 group_money, item_prices, position, blit_position, money):
        self.name_prefix = ["abner", "archer", "baker", "baxter", "booker",
                            "breaker", "bridger", "casper", "chester", "colter",
                            "dexter", "faulkner", "fielder", "fisher", "foster",
                            "grover", "gulliver", "homer", "hunter", "lander",
                            "leander", "luther", "miller", "palmer", "rancher",
                            "ranger", "rider", "ryker", "sayer", "thayer", "wheeler",
                            "dead man", "skeleton", "robber"]

        self.name_suffix = ["cave", "creek", "desert", "farm", "field", "forest",
                            "gulch", "hill", "lake", "mountain", "pass", "peak",
                            "plain", "pond", "ranch", "ravine", "rise" "river",
                            "rock", "stream", "swamp", "valley", "woods"]
        self.yvalue = 40
        self.group_inventory = group_inventory
        self.group_money = group_money
        self.price_mod = price_mod
        self.item_prices = item_prices
        self.inventory = inventory
        self.position = position
        self.blit_position = blit_position
        self.buy_button_list = []
        self.sell_button_list = []
        self.x_pos = (-self.position * 40) + 1280

        # Gui stuff #

        # Main Window
        self.shop_surface = pygame.Surface((500, 300))
        # Separator Line
        self.sep_line = pygame.Surface((self.shop_surface.get_width(), 10))
        self.sep_line.fill((0, 0, 0))
        # Inventory container box
        self.inv_container = pygame.Surface((self.shop_surface.get_width()-20,
                                             self.shop_surface.get_height()/2 - 35))
        self.inv_container.fill((255, 255, 255))
        # Font creation
        self.title_font = pygame.font.Font(None, 30)
        self.text_font = pygame.font.Font(None, 20)

        # Random name generation
        if name == "":
            self.name = string.capitalize(random.choice(self.name_prefix) + "'s " + random.choice(self.name_suffix))
            print self.name
        else:
            self.name = name
        # Random inventory generation
        if self.inventory == {}:
            inventory_random = copy.copy(self.group_inventory)
            for key in list(inventory_random.keys()):
                inventory_random[key] = random.randint(0, 10)
            inventory_random["Food"] *= 20
            self.inventory = inventory_random
            print self.inventory

        # Random money generation
        if money is None:
            self.money = random.randint(200, 500)
            print "Money: " + str(self.money)
        else:
            self.name = name
        self.render()

    # Used to get the surface created in self.render()
    def get_surface(self):
        self.render()
        return self.shop_surface

    # Updates the group_inv and group_money to blit in self.render
    def update(self, group_inv, group_m):
        self.group_inventory = group_inv
        self.group_money = group_m
        self.render()

    def move(self, move_value):
        self.x_pos += (2 * move_value)
        self.render()

    def render(self):
        self.yvalue = 40
        self.shop_surface.fill((133, 94, 66))
        self.shop_surface.blit(self.title_font.render(self.name + " - $"+str(self.money), 1, (0, 0, 255)), (10, 5))
        self.shop_surface.blit(self.inv_container, (10, 25))
        self.shop_surface.blit(self.inv_container, (10, self.shop_surface.get_height()/2 + 30))
        self.shop_surface.blit(self.text_font.render("Inventory", 1, (255, 0, 0)), (10, 25))
        self.shop_surface.blit(self.text_font.render("Amount", 1, (255, 0, 0)), (130, 25))
        self.shop_surface.blit(self.text_font.render("Price", 1, (255, 0, 0)), (200, 25))

        #Blit the shop's inventory
        for key in list(self.inventory.keys()):
            self.shop_surface.blit(self.text_font.render(key+":", 1, (0, 0, 0)), (10, self.yvalue))
            self.shop_surface.blit(self.text_font.render(str(self.inventory[key]), 1,
                                                        (0, 0, 0)), (150, self.yvalue))
            self.shop_surface.blit(self.text_font.render("$"+str(self.item_prices[key]*self.price_mod), 1,
                                                        (0, 0, 0)), (200, self.yvalue))
            if len(self.buy_button_list) < len(self.inventory.keys()):
                button_pos = tuple(map(sum, zip(self.blit_position, (250, self.yvalue))))
                self.buy_button_list.append(TransactionButton(transaction="buy",
                                                              item=key,
                                                              image_position=(250, self.yvalue),
                                                              rect_position=button_pos))
            self.yvalue += 30

        # Shows each button
        for button in self.buy_button_list:
            self.shop_surface.blit(button.image, button.image_position)

        self.shop_surface.blit(self.sep_line, (0, float(self.shop_surface.get_height())/2))

        self.shop_surface.blit(self.title_font.render("You - $"+str(self.group_money), 1, (0, 0, 255)),
                               (10, float(self.shop_surface.get_height()) / 2 + 10))
        self.shop_surface.blit(self.text_font.render("Inventory", 1, (255, 0, 0)),
                               (10, float(self.shop_surface.get_height()) / 2 + 30))
        self.shop_surface.blit(self.text_font.render("Amount", 1, (255, 0, 0)),
                               (130, float(self.shop_surface.get_height()) / 2 + 30))
        self.shop_surface.blit(self.text_font.render("Price", 1, (255, 0, 0)),
                               (200, float(self.shop_surface.get_height()) / 2 + 30))

        self.yvalue = (float(self.shop_surface.get_height())/2) + 45

        #Blit the player's inventory
        for key in list(self.group_inventory.keys()):
            self.shop_surface.blit(self.text_font.render(key+":", 1, (0, 0, 0)), (10, self.yvalue))
            self.shop_surface.blit(self.text_font.render(str(self.group_inventory[key]), 1,
                                                         (0, 0, 0)), (150, self.yvalue))
            self.shop_surface.blit(self.text_font.render("$"+str(self.item_prices[key]*self.price_mod), 1,
                                                        (0, 0, 0)), (200, self.yvalue))
            if len(self.sell_button_list) < len(self.inventory.keys()):
                button_pos = tuple(map(sum, zip(self.blit_position, (250, self.yvalue))))
                self.sell_button_list.append(TransactionButton(transaction="sell",
                                                               item=key,
                                                               image_position=(250, self.yvalue),
                                                               rect_position=button_pos))
            self.yvalue += 30

        for button in self.sell_button_list:
            self.shop_surface.blit(button.image, button.image_position)


# Used to create the Buy and Sell buttons in the Shop() class
class TransactionButton():
    def __init__(self, transaction, item, image_position, rect_position):
        self.transaction = transaction
        self.item = item
        self.image_position = image_position
        self.rect_position = rect_position
        self.filename = "buybutton.png"
        if self.transaction == "sell":
            self.filename = "sellbutton.png"
        self.image = pygame.transform.scale(pygame.image.load(resource_path+"Images\\"+self.filename), (25, 25))
        self.image_rect = pygame.Rect(self.rect_position, self.image.get_size())


# Used to create rectangles around the affliction names in the Game.passenger_info() function
class AfflictionBox():
    def __init__(self, affliction, font, rect_position=(0, 0)):
        self.affliction = affliction
        self.rect_position = rect_position
        self.name = self.affliction.name
        self.font = font
        self.text_size = self.font.size(self.name)
        self.text_rect = pygame.Rect(self.rect_position, self.text_size)

    def update(self, rect_position):
        self.rect_position = rect_position
        self.text_rect.centerx = rect_position[0] + self.text_size[0]
        self.text_rect.centery = rect_position[1] + self.text_size[1]


# Creates buttons used in the Game menu_surface
class MenuButton():
    def __init__(self, image, image_size=(0, 0), rect_position=(0, 0), name=None):
        self.image = image
        self.rect_position = rect_position
        self.image_size = image_size
        self.name = name
        self.rect = pygame.Rect(self.rect_position, self.image_size)

    def update(self, rect_position, image_size):
        self.rect_position = rect_position
        self.image_size = image_size
        self.rect = pygame.Rect(self.rect_position, self.image_size)


# Creates buttons with rectangle attached for the logbook
class ScrollButton():
    def __init__(self, direction):
        self.direction = direction
        if self.direction == "up":
            self.image = pygame.image.load(resource_path+"Images\\uparrow.png")
        elif self.direction == "down":
            self.image = pygame.image.load(resource_path+"Images\\downarrow.png")
        self.rect = pygame.Rect((0, 0), self.image.get_size())

    def update(self, position):
        self.rect = pygame.Rect(position, self.image.get_size())


# Buffalo object used in the Hunting minigame
class Buffalo():
    def __init__(self, pos_x, pos_y, picture, size):
        self.picture = picture
        self.size = size
        self.max_health = 100 * self.size
        self.health = self.max_health
        self.preimage = pygame.image.load(resource_path+"Images\\"+self.picture+"_buffalo.png")
        self.image = pygame.transform.scale(self.preimage, (int(self.preimage.get_width()*self.size),
                                                            int(self.preimage.get_height()*self.size)))
        self.health_font = pygame.font.Font(None, 20)
        self.health_bar_container = pygame.Surface((int(75*self.size), int(12*self.size)))
        self.health_bar_shader = pygame.Surface((self.health_bar_container.get_width() + 6,
                                                 self.health_bar_container.get_height() + 6))
        self.health_number = self.health_font.render(str(self.health), 1, (0, 0, 0))
        self.health_bar_shader.fill((175, 175, 175))
        self.health_bar = pygame.Surface(self.health_bar_container.get_size())
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
        self.rect = pygame.Rect((0, 0), self.image.get_size())
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.status = "alive"
        self.target_y = pos_y

    def update(self):
        # Checks the health and updates the health bar
        self.preimage = pygame.image.load(resource_path+"Images\\"+self.status+"_buffalo.png")
        self.image = pygame.transform.scale(self.preimage, (int(self.preimage.get_width()*self.size),
                                                            int(self.preimage.get_height()*self.size)))
        #Create health bar + shader + container
        self.health_bar_container = pygame.Surface((int(75*self.size), int(12*self.size)))
        self.health_number = self.health_font.render(str(int(self.health)), 1, (255, 255, 255))
        self.health_bar_shader = pygame.Surface((self.health_bar_container.get_width() + 6,
                                                 self.health_bar_container.get_height() + 6))
        self.health_bar_shader.fill((175, 175, 175))
        if self.health <= 0:
            self.health_bar = pygame.Surface((0, 0))
        else:
            self.health_bar = pygame.Surface((int(self.health_bar_container.get_width()/self.max_health*self.health),
                                              self.health_bar_container.get_height()))
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
            self.rect.x += float(3 - self.size)
            if self.rect.y != self.target_y:
                if self.rect.y < self.target_y:
                    self.rect.y += float(3 - self.size)
                elif self.rect.y > self.target_y:
                    self.rect.y -= float(3 - self.size)
            return self.rect.center


# The random event class
class Event():
    def __init__(self, max_pos, name=None, pos=-1):
        self.good_or_bad = random.choice([-1, 1])
        self.surface = pygame.Surface((0, 0))
        self.random_events = [self.river, self.house]
        self.name = name
        self.pos = pos
        self.event_name = ""
        if self.name is not None:
            if self.name == "river":
                self.river()
            elif self.name == "house":
                self.house()
            self.event_pos = self.pos
        else:
            self.event = random.choice(self.random_events)()
            self.event_pos = random.randint(5, max_pos - 5)
        self.x_pos = (-self.event_pos * 40) + 1280

    def river(self):
        self.surface = pygame.Surface((100, 400))
        self.surface.fill((30, 144, 255))
        self.event_name = "river"

    def house(self):
        self.surface = pygame.image.load(resource_path + "Images\\house.png")
        self.event_name = "house"

    def update(self):
        self.x_pos += 2


# Used to create interactive buttons in the RiverOptionMenu
class RiverOptionButton():
    def __init__(self, option, size, hover, pos):
        self.option = option
        self.size = size
        self.hover = hover
        self.size = size
        self.surface = pygame.Surface(self.size)
        self.pos = pos
        if self.hover:
            self.surface.fill((200, 200, 200))
        else:
            self.surface.fill((255, 255, 255))
        self.rect = pygame.Rect(self.pos, self.size)
        self.button_font = pygame.font.Font(None, 25)
        self.surface.blit(self.button_font.render(self.option, 1, (0, 0, 0)),
                         (5, self.size[1]/2 - self.button_font.size("Lorem Ipsum")[1]/2))

    def update(self, hover):
        if hover:
            self.surface.fill((200, 200, 200))
        else:
            self.surface.fill((255, 255, 255))
        self.rect = pygame.Rect(self.pos, self.size)
        self.button_font = pygame.font.Font(None, 25)
        self.surface.blit(self.button_font.render(self.option, 1, (0, 0, 0)),
                         (5, self.size[1]/2 - self.button_font.size("Lorem Ipsum")[1]/2))

# Unused class to create small random events
class MiniEvent():
    def __init__(self):
        self.events = {self.lose_wheel: 0.1, self.find_food: 1.5}

        for event in self.events:
            if round(random.uniform(0, 100), 1) == self.events[event]:
                return event()

    def lose_wheel(self):
        return {"The wagon hit a large hole and lost a wheel!": {"Wheel": -1}}

    def find_food(self):
        rand_amount = random.randint(1, 50)
        prompts = ["You come across an abandoned wagon and find [" + str(rand_amount) + "] Food.",
                    "You find an unattended crop of potatoes. You're able to harvest [" + str(rand_amount) + "] Food."]
        return {random.choice(prompts): {"Food": rand_amount}}
# Main Game class
class Game():
    def __init__(self):
        # GUI Elements
        self.game_window = pygame.display.set_mode((1280, 800))
        self.game_surface = pygame.Surface((self.game_window.get_size())).convert()
        self.game_surface.fill((135, 206, 250))
        self.game_window.blit(self.game_surface,  (0, 0))
        self.shape_group = pygame.sprite.Group()
        self.turn_menu_surface_offsetx = self.game_window.get_width() * (100./1280)
        self.turn_menu_surface_offsety = self.game_window.get_height() * (100./720)
        self.turn_menu_surface = pygame.Surface((0, 0))
        self.exit_button = pygame.image.load(resource_path+"Images\\exit.png")
        self.exit_button_rect = self.exit_button.get_rect()
        self.exit_button_rect.centerx = self.game_window.get_width() - self.exit_button.get_width() / 2
        self.exit_button_rect.centery = self.exit_button.get_height()/2
        self.tomb_image = pygame.image.load(resource_path+"Images\\tombstone.png")
        self.town_image = pygame.image.load(resource_path+"Images\\town.png")
        self.road = pygame.Surface((self.game_window.get_width(), self.game_window.get_height() / 3))
        self.road.fill((139, 69, 19))
        self.shop_blit_position = (self.game_window.get_width() - self.game_window.get_width()*(2./5),
                                   self.game_window.get_height()*(1./8))
        self.info_menu_blit_position = (200, 200)
        self.menu_bar = pygame.Surface((0, 0))
        self.logbook_render_pos = (200, 200)
        self.logbook_up_rect = pygame.Rect(0, 0, 0, 0)
        self.logbook_down_rect = pygame.Rect(0, 0, 0, 0)
        self.food_menu_up_rect = pygame.Rect(0, 0, 0, 0)
        self.food_menu_down_rect = pygame.Rect(0, 0, 0, 0)
        self.food_menu_blit_pos = (400, 200)
        self.random_blit = []
        self.canvas = pygame.Surface((400, 300))
        self.undos = []
        self.redos = []

        # Values
        self.days_since_start = 0
        self.day = 0
        self.year = 1850
        self.season = ""
        self.mouse_x = 0
        self.mouse_y = 0
        self.turn_passenger_list = []
        self.change_list = []
        self.num_passengers = 3
        self.num_events = 10
        self.game_length = 100
        # Actual Oregon Trail length is 2,000 miles
        self.group_pos = 0
        self.group_inventory = {"Horses": 1,
                                "Spare Wheels": 2,
                                # Because the first turn takes away food,
                                # we give extra so you start with the intended amount
                                "Food": 52*self.num_passengers}
        self.move_value = self.group_inventory["Horses"]
        self.group_money = 200
        self.item_prices = {"Horses": 150,
                            "Spare Wheels": 40,
                            "Food": 1}
        self.option_list = ["Kill", "Info", "Food", "Paint"]
        self.option_button_list = []
        self.logbook = []
        self.logbook_dict = {}
        self.menu_list = ["logbook", "settings"]
        self.menu_button_list = []
        self.in_town = None
        self.output_text = []
        self.painting = False
        #Creating and storing towns
        self.town_list = [Shop(name="Starting Town", inventory={}, price_mod=1,
                               group_inventory=self.group_inventory,
                               group_money=self.group_money,
                               item_prices=self.item_prices,
                               position=1,
                               blit_position=self.shop_blit_position,
                               money=None)]
        self.affliction_button_list = []
        for x in range(2):
            random_mod = round(random.uniform(0.1, 2.0), 3)
            calculate_pos = True
            while calculate_pos:
                random_pos = random.randint(6, 100)
                print random_pos
                for town in self.town_list:
                    if abs(random_pos - town.position) >= 0:
                        self.town_list.append(Shop(name="", inventory={}, price_mod=random_mod,
                                                   group_inventory=self.group_inventory,
                                                   group_money=self.group_money,
                                                   item_prices=self.item_prices,
                                                   position=random_pos,
                                                   blit_position=self.shop_blit_position,
                                                   money=None))
                        print"Town created at "+str(random_pos)
                        calculate_pos = False
                        break

        # Reading the tombstone file
        try:
            with open("tombstone.dat", "rb") as file_name:
                self.tombstone_list = pickle.load(file_name)
                for tomb in self.tombstone_list:
                    tomb.status = "Old"
        except (EOFError, IOError):
            print"Error opening Tombstone.dat, pickling an empty list.."
            with open("tombstone.dat", "wb") as file_name:
                self.tombstone_list = []
                pickle.dump([], file_name)

        # Add the random events
        for x in range(self.num_events):
            self.random_blit.append(Event(max_pos=self.game_length))
        for event in self.random_blit:
            print "["+str(event.good_or_bad)+"] Event " + str(event.event_name) + " created at: " + str(event.event_pos)

    # Loops through main Game functions
    def begin_play(self):
        while True:
            clock.tick(30)
            self.run_background()
            self.calculations()
            self.turn_menu()

    # Menu that pops up after every day
    def turn_menu(self):
        x_value = 20
        y_value = 45
        in_turn_menu = True
        pygame.font.init()
        self.turn_passenger_list = []
        next_day = pygame.image.load(resource_path+"Images\\nextday.png")
        self.turn_menu_surface = pygame.Surface((500, 75 * len(passenger_list) + next_day.get_height()+75))
        self.turn_menu_surface.fill((175.5, 175.5, 175.5))
        next_day_rect = pygame.Rect((0, 0), next_day.get_size())
        next_day_rect.centerx = (self.turn_menu_surface.get_width() + self.turn_menu_surface_offsetx
                                 - next_day.get_width()/2)
        next_day_rect.centery = (self.turn_menu_surface.get_height() + self.turn_menu_surface_offsety
                                 - next_day.get_height()/2)
        font = pygame.font.Font(None, 28)
        status_font = pygame.font.Font(None, 24)
        log_range = [0, 45]
        times_hunted = 0

        # Create a tab for each passenger
        for passenger in passenger_list:
            self.turn_passenger_list.append(PassengerTab(position=(x_value+5, y_value+5), size=(450, 75),
                                                         passenger=passenger))
            y_value += 80

        # Checks for input and re-renders the turn menu (and friends)
        selected_option_menu = None
        option_hover = None
        mouse_rect = pygame.Rect(0, 0, 0, 0)
        tombstone_hover = None
        selected_info_menu = None
        show_logbook = False
        show_food_menu = None
        event_result = None

        # Checks if it's time for a random event, and runs it before the turn menu
        for event in self.random_blit:
            if event.event_name == "river":
                if self.group_pos == event.event_pos - 1:
                    event_result = self.river
            elif event.event_name == "house":
                if self.group_pos == event.event_pos:
                    event_result = self.house(event)

        # Main while loop for the turn menu
        while in_turn_menu:
            clock.tick(30)
            events = pygame.event.get()
            # Creates a surface tab for each passenger
            for surface in self.turn_passenger_list:
                surface.fill((255, 255, 255))
                status_color = (0, 255, 0)

                health_bar_container = pygame.Surface((75, 25))
                health_bar_container.fill((0, 0, 0))
                surface.blit(health_bar_container, (surface.get_width() - health_bar_container.get_width() - 5,
                                                    surface.get_height() - health_bar_container.get_height() - 5))
                health_bar = pygame.Surface((int(surface.passenger.health/100.*health_bar_container.get_width()), 25))

                pass_pic_container = pygame.Surface((75, 75))
                pass_pic_container.fill((255, 255, 255))
                pass_pic = pygame.image.load(resource_path+"\\Images\\Faces\\"+surface.passenger.picture+".png")
                pass_pic = pygame.transform.scale(pass_pic, (70, 70))

                # Calculates the bar color based on health. Green -> Yellow -> Red
                if surface.passenger.health >= 50:
                    health_color = (float((100-surface.passenger.health)*2/100.*255), 255, 0)
                else:
                    health_color = (255, float(surface.passenger.health*2/100.*255), 0)
                health_bar.fill(health_color)

                # Calculate the complementary color of the health bar for visibility
                health_text_hls = colorsys.rgb_to_hls(health_color[0]/255, health_color[1]/255, health_color[2]/255)

                health_text_rgb = colorsys.hls_to_rgb(float(((health_text_hls[0]*360)+180) % 360)/360,
                                                      health_text_hls[1],
                                                      health_text_hls[2])

                health_text_color = tuple(map(lambda e: e*255, health_text_rgb[0:3]))

                # Local blitting
                pass_pic_container.blit(pass_pic, (2.5, 2.5))
                surface.blit(pass_pic_container, (0, 0))
                surface.blit(font.render(surface.passenger.name, 0, (0, 0, 255)), (75, 10))
                surface.blit(health_bar, (surface.get_width() - health_bar_container.get_width() - 5,
                                          surface.get_height() - health_bar_container.get_height() - 5))

                surface.blit(font.render(str(surface.passenger.health), 1, health_text_color),
                             (surface.get_width() - (health_bar_container.get_width()) + 12,
                              surface.get_height() - (health_bar_container.get_height()) - 3))
                surface.blit(status_font.render("Status: ", 1, (0, 0, 0)),
                             (75, surface.get_height() - 25))

                # Setting the status color
                if surface.passenger.status == "Unhealthy":
                    status_color = (255, 0, 0)
                surface.blit(status_font.render(str(surface.passenger.status), 1, status_color),
                             (140, surface.get_height() - 25))
                surface.blit(surface.option_image, (surface.passenger_surface.get_width() -
                                                    surface.option_image.get_width(), 0))
                surface.option_rect.x = surface.passenger_surface.get_width() + self.turn_menu_surface_offsetx
                surface.option_rect.y = self.turn_menu_surface_offsety + \
                    surface.position[1] - surface.option_image.get_height()/2
                self.turn_menu_surface.blit(surface, surface.position)

            # Global blitting
            self.game_surface.fill((135, 206, 250))
            self.game_window.blit(self.game_surface, (0, 0))
            self.game_window.blit(self.road, (0, float(self.game_window.get_height()) -
                                              float(self.game_window.get_height()) / 3))
            for event in self.random_blit:
                if event.event_name == "river":
                    self.game_window.blit(event.surface, (event.x_pos, (float(self.game_window.get_height()) -
                                                                        float(self.game_window.get_height()) / 3)))
            self.shape_group.draw(self.game_window)
            self.turn_menu_surface.blit(next_day, (self.turn_menu_surface.get_width() - next_day.get_width(),
                                                   self.turn_menu_surface.get_height() - next_day.get_height()))

            self.turn_menu_surface.blit(font.render(str("Day: "+str(self.days_since_start)), 0, (0, 0, 0)),
                                                   (5, 5))
            self.turn_menu_surface.blit(font.render("Position: "+str(self.group_pos), 1, (0, 0, 0)),
                                                   (5, 5 + font.size("Day")[1]))
            self.turn_menu_surface.blit(font.render("Food: "+str(self.group_inventory["Food"]), 0, (0, 0, 0)),
                                                   (5, self.turn_menu_surface.get_height() - font.size('Food')[1]*2))
            self.turn_menu_surface.blit(font.render("Go Hunting", 0, (0, 0, 0)),
                                                   (5, self.turn_menu_surface.get_height()-font.size("Go Hunting")[1]))
            hunting_rect = pygame.Rect((self.turn_menu_surface_offsetx, (self.turn_menu_surface.get_height() +
                                                                         self.turn_menu_surface_offsety -
                                                                         font.size("Go Hunting")[1]*2)),
                                       font.size("Go Hunting"))
            # Displays random events
            for event in self.random_blit:
                if event.event_name == "house":
                    self.game_window.blit(event.surface, (event.x_pos, 500))

            # Blitting towns
            for town in self.town_list:
                if self.group_pos == town.position:
                    self.game_window.blit(town.get_surface(), self.shop_blit_position)
                    self.in_town = town
                town.blit_position = self.shop_blit_position
                self.game_window.blit(self.town_image, (town.x_pos - self.town_image.get_width() / 2,
                                                        self.game_window.get_height()/2 +
                                                        self.town_image.get_height()/2))
                self.game_window.blit(font.render(town.name, 1, (0, 0, 255)),
                                      (town.x_pos - self.town_image.get_width() / 2,
                                       (self.game_window.get_height()/2 + self.town_image.get_height()/2)+40))

            # Blitting tombstones
            for tombstone in self.tombstone_list:
                if tombstone.status == "Old":
                    self.game_window.blit(self.tomb_image, (tombstone.x_pos - self.tomb_image.get_width() / 2,
                                                            tombstone.y_pos))
            # Large event loop to create interactivity while in the Turn Menu
            for event in events:
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos
                    mouse_rect = pygame.Rect(self.mouse_x, self.mouse_y, 1, 1)
                # Exit
                if event.type == pygame.MOUSEBUTTONDOWN and self.exit_button_rect.collidepoint(
                        self.mouse_x, self.mouse_y):
                    pygame.quit()
                    quit()

                # Next Day button
                if event.type == pygame.MOUSEBUTTONDOWN and next_day_rect.collidepoint(self.mouse_x, self.mouse_y):
                    in_turn_menu = False
                    break

                # Checks if the mouse is over the tombstone and if cursor is in turn menu
                if mouse_rect.collidelist([x.tomb_rect for x in self.tombstone_list]) != -1:
                    if not mouse_rect.colliderect(self.turn_menu_surface.get_rect()):
                        tombstone_hover = self.tombstone_list[mouse_rect.collidelist(
                            [x.tomb_rect for x in self.tombstone_list])]
                    break
                else:
                    tombstone_hover = None

                # Option Button
                if mouse_rect.collidelist([x.option_rect for x in self.turn_passenger_list]) != -1 and \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    if selected_option_menu is None:
                        selected_option_menu = self.turn_passenger_list[mouse_rect.collidelist(
                            [x.option_rect for x in self.turn_passenger_list])]
                        break
                    else:
                        selected_option_menu = None
                        self.option_button_list = []

                # Buttons in menu list
                if mouse_rect.collidelist([button.rect for button in self.option_button_list]) != -1:
                    option_hover = self.option_button_list[mouse_rect.collidelist(
                        [button.rect for button in self.option_button_list])]
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if option_hover.option == "Kill":
                            self.kill_passenger(option_hover.passenger_tab.passenger)
                            option_hover = None
                            selected_option_menu = None
                            self.option_button_list = []
                            in_turn_menu = False
                            self.turn_menu()
                        elif option_hover.option == "Info":
                            if selected_info_menu is None:
                                selected_info_menu = self.passenger_info(option_hover.passenger_tab.passenger,
                                                                         self.info_menu_blit_position)
                                break
                            else:
                                selected_info_menu = None
                        elif option_hover.option == "Food":
                            if show_food_menu is None:
                                show_food_menu = option_hover.passenger_tab.passenger
                            else:
                                show_food_menu = None
                        elif option_hover.option == "Paint":
                            self.go_painting(option_hover.passenger_tab.passenger)
                            option_hover = None
                            selected_option_menu = None
                            self.option_button_list = []
                else:
                    option_hover = None

                #Buying and selling from the Shop
                if self.in_town is not None:
                    # Buying
                    if mouse_rect.collidelist([button.image_rect for button in self.in_town.buy_button_list]) != -1:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            the_button = self.in_town.buy_button_list[
                                mouse_rect.collidelist([button.image_rect for button in self.in_town.buy_button_list])]
                            if self.in_town.inventory[the_button.item] > 0:
                                if self.group_money > self.in_town.item_prices[the_button.item]:
                                    self.group_money -= self.in_town.item_prices[the_button.item]
                                    self.in_town.money += self.in_town.item_prices[the_button.item]
                                    self.group_inventory[the_button.item] += 1
                                    self.in_town.inventory[the_button.item] -= 1
                                else:
                                    self.output_text.append("You don't have enough money for [" + the_button.item + "]")
                            else:
                                self.output_text.append(self.in_town.name + " is out of [" + the_button.item + "]")
                    # Selling
                    elif mouse_rect.collidelist([button.image_rect for button in self.in_town.sell_button_list]) != -1:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            the_button = self.in_town.sell_button_list[
                                mouse_rect.collidelist([button.image_rect for button in self.in_town.sell_button_list])]
                            if self.in_town.money > self.in_town.item_prices[the_button.item]:
                                if self.group_inventory[the_button.item] > 0:
                                    self.group_money += self.in_town.item_prices[the_button.item]
                                    self.in_town.money -= self.in_town.item_prices[the_button.item]
                                    self.group_inventory[the_button.item] -= 1
                                    self.in_town.inventory[the_button.item] += 1
                                else:
                                    self.output_text.append("You are out of [" + the_button.item + "]")
                            else:
                                self.output_text.append(self.in_town.name + " can't afford [" + the_button.item + "]")
                    self.move_value = self.group_inventory["Horses"]
                    self.in_town.update(self.group_inventory, self.group_money)
                    self.in_town.render()

                # Menu bar collisions
                if event.type == pygame.MOUSEBUTTONDOWN and mouse_rect.collidelist(
                        [menu_button.rect for menu_button in self.menu_button_list]) != -1:
                    clicked_menu_button = self.menu_button_list[mouse_rect.collidelist(
                        [menu_button.rect for menu_button in self.menu_button_list])]
                    if clicked_menu_button.name == "logbook":
                        show_logbook = not show_logbook
                    elif clicked_menu_button.name == "settings":
                        self.output_text.append("There are no settings.")

                # Logbook scroll buttons
                if show_logbook:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.logbook_up_rect.collidepoint((self.mouse_x, self.mouse_y)):
                            if log_range[0] > 0:
                                map(lambda lr: lr-1, log_range[0:2])
                        elif self.logbook_down_rect.collidepoint((self.mouse_x, self.mouse_y)):
                            map(lambda lr: lr+1, log_range[0:2])

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            if log_range[0] > 0:
                                    map(lambda lr: lr-1, log_range[0:2])
                        elif event.key == pygame.K_DOWN:
                            map(lambda lr: lr+1, log_range[0:2])

                # Food menu buttons
                if show_food_menu is not None and event.type == pygame.MOUSEBUTTONDOWN:
                    if self.food_menu_down_rect.collidepoint((self.mouse_x, self.mouse_y)):
                        if show_food_menu.food_divisions > 0:
                            show_food_menu.food_divisions -= 1
                        else:
                            self.output_text.append("You can't have less than 0 food!")
                    elif self.food_menu_up_rect.collidepoint((self.mouse_x, self.mouse_y)):
                        if show_food_menu.food_divisions < 5:
                            show_food_menu.food_divisions += 1
                        else:
                            self.output_text.append("You can't have more than 5 food!")

                # Hunting Function
                if hunting_rect.collidepoint((self.mouse_x, self.mouse_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    self.confirmation_window(self.go_hunting(times_hunted), "okay")
                    times_hunted += 1

            # Blit the tombstone hovered over, if any.
            if tombstone_hover is not None:
                self.tombstone_info(tombstone_hover)

            # Done blitting to the surface, can blit it to the window
            self.game_window.blit(self.turn_menu_surface, (100, 100))

            # Blit the selected option menu, if any.
            if selected_option_menu is not None:
                self.option_button_list = []
                the_option_menu = self.option_menu(selected_option_menu, option_hover)
                self.game_window.blit(the_option_menu,
                                      (selected_option_menu.position[0] + selected_option_menu.size[0] +
                                       the_option_menu.get_width(),
                                       selected_option_menu.position[1]+the_option_menu.get_height()))
            if selected_info_menu is not None:
                self.game_window.blit(selected_info_menu, self.info_menu_blit_position)

            if show_food_menu is not None:
                self.game_window.blit(self.show_food_menu(show_food_menu), self.info_menu_blit_position)

            if show_logbook:
                self.game_window.blit(self.show_logbook(range(log_range[0], log_range[1]), self.logbook_render_pos),
                                      self.logbook_render_pos)

            self.turn_menu_surface.fill((175, 175, 175))
            # Shows the output box
            output_box = self.show_output_box()
            self.game_window.blit(output_box, (self.game_window.get_width() - output_box.get_width(),
                                               self.game_window.get_height() - output_box.get_height() - 200))
            self.game_window.blit(self.build_menu_bar(), (0, 0))
            self.game_window.blit(self.exit_button, (self.game_window.get_width()-self.exit_button.get_width(), 0))
            if event_result is not None:
                self.output_text.append(event_result)
                event_result = None
            pygame.display.flip()

    # Moves the background
    def run_background(self):
        keep_moving = True
        move_counter = 0
        font = pygame.font.Font(None, 28)
        self.output_text = []
        while keep_moving:
            clock.tick(30)
            if move_counter > 20:
                keep_moving = False
            self.game_surface.fill((135, 206, 250))
            self.game_window.blit(self.game_surface, (0, 0))
            self.game_window.blit(self.road, (0, float(self.game_window.get_height()) -
                                              float(self.game_window.get_height()) / 3))
            self.shape_group.update(self)
            self.shape_group.draw(self.game_window)

            # Displays random events
            for event in self.random_blit:
                event.update()
                if event.event_name == "river":
                    self.game_window.blit(event.surface, (event.x_pos, (float(self.game_window.get_height()) -
                                                                        float(self.game_window.get_height()) / 3)))
                elif event.event_name == "house":
                    self.game_window.blit(event.surface, (event.x_pos, 500))

            # Displays towns
            for town in self.town_list:
                town.move(self.move_value)
                self.game_window.blit(self.town_image, (town.x_pos - self.town_image.get_width() / 2,
                                                        self.game_window.get_height()/2 +
                                                        self.town_image.get_height()/2))
                self.game_window.blit(font.render(town.name, 1, (0, 0, 255)),
                                      (town.x_pos - self.town_image.get_width() / 2,
                                       (self.game_window.get_height()/2 + self.town_image.get_height()/2)+40))
                town.update(self.group_inventory, self.group_money)

            # Displays tombstones
            for tombstone in self.tombstone_list:
                tombstone.update(self.move_value)
                if tombstone.status == "Old":
                    self.game_window.blit(self.tomb_image, (tombstone.x_pos - self.tomb_image.get_width() / 2,
                                                            tombstone.y_pos))

            self.game_window.blit(self.build_menu_bar(), (0, 0))
            pygame.display.flip()
            move_counter += self.move_value
        pygame.display.flip()

    # All of the calculations needed each turn
    def calculations(self):
        # Changes time and position
        self.day += 1
        self.days_since_start += 1
        self.group_pos += self.move_value
        self.change_list = []
        self.logbook = []

        # Is it a new year?
        if self.day == 366:
            self.year += 1
            self.day = 1

        # Season calculations
        if 1 <= self.day <= 80 or 356 <= self.day <= 365:
            self.season = "Winter"
        elif 81 <= self.day <= 171:
            self.season = "Spring"
        elif 172 <= self.day <= 262:
            self.season = "Summer"
        elif 263 <= self.day <= 355:
            self.season = "Autumn"

        for town in self.town_list:
            if self.group_pos == town.position:
                self.change_list.append("You've arrived at "+town.name)

        for passenger in passenger_list:
            total_hp_change = 0.5
            passenger.status = "Healthy"

            # Sloppy food calculations

            if self.group_inventory["Food"] >= passenger.food_divisions:
                self.group_inventory["Food"] -= passenger.food_divisions
            else:
                passenger.food_divisions = 0

            for x in ("Hunger", "Well Fed"):
                for y in passenger.afflictions:
                    if x == y.name:
                        passenger.afflictions.remove(y)

            if passenger.food_divisions < 2:
                for affliction in afflictions_list:
                    if affliction.name == "Hunger":
                        copy_aff = copy.copy(affliction)
                        copy_aff.health_change = -3 + (1.5*passenger.food_divisions)
                        passenger.afflictions.append(copy_aff)
                        self.change_list.append(passenger.name + " is hungry!")
                        break
            elif passenger.food_divisions > 2:
                for affliction in afflictions_list:
                    if affliction.name == "Well Fed":
                        copy_aff = copy.copy(affliction)
                        copy_aff.health_change = -3 + (1.5*passenger.food_divisions)
                        passenger.afflictions.append(copy_aff)
                        break

            # Calculates recovery time
            for affliction in passenger.afflictions:
                affliction.recovery_time -= 1
                if affliction.name != "Well Fed":
                    passenger.status = "Unhealthy"
                if affliction.recovery_time == 0:
                    passenger.afflictions.remove(affliction)
                    group_afflictions.remove(affliction)
                    self.change_list.append(passenger.name + " has recovered from " + str(affliction.name))
                else:
                    total_hp_change += affliction.health_change

            if total_hp_change != 0:
                gain_or_loss = "lost "
                if total_hp_change > 0:
                    gain_or_loss = "gained "
                passenger.health += total_hp_change

                if passenger.health < 0:
                    passenger.health = 0
                elif passenger.health > 100:
                    passenger.health = 100

                if passenger.health != 100:
                    self.change_list.append(passenger.name + " has " + gain_or_loss +
                                            str(abs(total_hp_change)) +
                                            " health for a total of " +
                                            str(passenger.health))

            # Did they dead?
            if passenger.health <= 0:
                self.kill_passenger(passenger)
                break

            # Here be the dragons. Calculates chance to infect.
            for affliction in afflictions_list:
                modifier = 0
                if affliction in group_afflictions and affliction not in passenger.afflictions:
                    modifier += affliction.infectivity
                if affliction not in passenger.afflictions:
                    rand_chance = round(random.uniform(0, 100), 2)
                    if rand_chance <= affliction.chance_to_infect + modifier:
                        rand_duration = random.randint(affliction.recovery_time[0],  affliction.recovery_time[1])
                        copy_affliction = copy.copy(affliction)
                        passenger.afflictions.append(copy_affliction)
                        for x in passenger.afflictions:
                            if x.name == affliction.name:
                                x.recovery_time = rand_duration
                                self.change_list.append(str(passenger.name) + " has contracted " +
                                                        str(affliction.name) + " for " + str(rand_duration)+" days.")
                        group_afflictions.append(affliction)

        # Returns and saves all of the things that happened this turn
        if len(passenger_list) != 0:
            t = "-"*50
            self.logbook.append(t)
            self.logbook.append("Day : "+str(self.days_since_start)+", "+self.season+" of "+str(self.year))
            if len(self.change_list) == 0:
                self.logbook.append("Nothing happened.")
            else:
                for change in self.change_list:
                    self.logbook.append(change)
            self.logbook.append(t)
        self.logbook_dict[self.days_since_start] = self.logbook

    # Character Creation
    def char_create(self):
        prompt_list = ["First Name", "Last Name", "Age", "Gender"]
        confirm_button = pygame.image.load(resource_path+"Images\\confirmbutton.png")
        confirm_button_rect = confirm_button.get_rect()
        confirm_button_rect.centerx = confirm_button.get_width()*1.5
        confirm_button_rect.centery = confirm_button.get_height()*1.5
        # Loops once for each passenger in self.num_passengers
        for x in range(self.num_passengers):
            entering_text = True
            text_prompt_counter = 0
            text_entry_responses = []
            text_entry = eztext.Input(maxlength=10,  color=(0, 0, 255),  prompt=prompt_list[text_prompt_counter]+":  ")
            male_female_words = {("m", "male", "guy", "man", "boy"): "Male",
                                 ("f", "female", "gal", "woman", "girl"): "Female"}
            # Character creation loop
            while entering_text:
                clock.tick(30)
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.MOUSEMOTION:
                        self.mouse_x, self.mouse_y = event.pos
                    if event.type == pygame.MOUSEBUTTONDOWN and self.exit_button_rect.collidepoint(
                            self.mouse_x, self.mouse_y):
                        pygame.quit()
                        quit()
                    if (event.type == pygame.MOUSEBUTTONDOWN and confirm_button_rect.collidepoint(
                            self.mouse_x, self.mouse_y) or
                            (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN)):
                        is_error = False

                        # First Name
                        if text_prompt_counter == 0:
                            if not all([x in string.letters for x in text_entry.value]) or text_entry.value == "_":
                                is_error = True

                        # Last Name
                        elif text_prompt_counter == 1:
                            if not all([x in string.letters for x in text_entry.value]) or text_entry.value == "_":
                                is_error = True

                        # Age
                        elif text_prompt_counter == 2:
                            if not all([x in string.digits for x in text_entry.value]) or text_entry.value == "_":
                                is_error = True

                        # Gender
                        elif text_prompt_counter == 3:
                            c = 0
                            if not all([x in string.letters for x in text_entry.value]) or text_entry.value == "_":
                                is_error = True
                            else:
                                for m_f in male_female_words:
                                    if text_entry.value in male_female_words[m_f]:
                                        text_entry.value = male_female_words[m_f]
                                        break
                                    c += 1
                                    print str(c),
                                if c >= 2:
                                    print "Counter Error"
                                    is_error = True

                        # Move on to picking a face
                        if text_prompt_counter < 4 and not is_error:
                            text_entry_responses.append(text_entry.value)
                            if text_prompt_counter != 3:
                                text_prompt_counter += 1
                                text_entry = eztext.Input(maxlength=10,  color=(0, 0, 255),
                                                          prompt=prompt_list[text_prompt_counter]+":  ")
                                print str(text_prompt_counter)
                            else:
                                # Create the passenger
                                passenger_list.append(Passenger(name=text_entry_responses[0] + " " +
                                                                text_entry_responses[1],
                                                                age=text_entry_responses[2],
                                                                gender=text_entry_responses[3],
                                                                picture=self.pick_face(text_entry_responses[3])))
                                entering_text = False

                        else:
                            print"Invalid Entry for "+prompt_list[text_prompt_counter]

                self.game_surface.fill((135, 206, 250))
                self.game_window.blit(self.game_surface, (0, 0))
                self.game_window.blit(self.exit_button,  (self.game_window.get_width()-self.exit_button.get_width(), 0))
                self.game_window.blit(confirm_button,  (100, 50))

                # Blits the text_entry only if it exists
                # Prevents errors because we use "del" on the text_entry earlier
                if "text_entry" in locals() and entering_text:
                    text_entry.update(events)
                    text_entry.draw(self.game_window)
                pygame.display.flip()

        self.game_surface.fill((135, 206, 250))
        self.game_window.blit(self.game_surface, (0, 0))
        pygame.display.flip()
        self.begin_play()

    # Section to pick a face
    def pick_face(self, gender):
        # Section for picking a face
        cur_face = "%empty"
        picking = True
        confirm_button = pygame.image.load(resource_path+"Images\\confirmbutton.png")
        confirm_button_rect = confirm_button.get_rect()
        confirm_button_rect.centerx = confirm_button.get_width()*1.5
        confirm_button_rect.centery = confirm_button.get_height()*1.5
        face_list = []

        picture_list = male_picture_list
        if gender == "Female":
            picture_list = female_picture_list

        # Creates and displays the faces
        for path, counter in zip(picture_list, range(len(picture_list))):
            face_list.append(ShowFaces(file_path=path,
                                       x_pos=(picture_list.index(path) * 100 + 50), y_pos=100))
            face_list[counter].create()

        # Face picking loop
        while picking:
            clock.tick(30)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos

                # Exit
                if event.type == pygame.MOUSEBUTTONDOWN and self.exit_button_rect.collidepoint(
                        self.mouse_x, self.mouse_y):
                    pygame.quit()
                    quit()

                # If a mouse button is clicked, or the enter button is hit
                if (event.type == pygame.MOUSEBUTTONDOWN) or \
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):

                    # If the user clicks, and it's not on the confirm button
                    if event.type == pygame.MOUSEBUTTONDOWN and not confirm_button_rect.collidepoint(
                            self.mouse_x, self.mouse_y):

                        # If the user clicks on a face, move all faces and set cur_face
                        for face in face_list:
                            if face.face_rect.collidepoint(self.mouse_x, self.mouse_y):
                                for replace in face_list:
                                    if replace != face:
                                        replace.y_pos = 200
                                    else:
                                        replace.y_pos = 100
                                    replace.update()
                                cur_face = str(face.file_path)
                                break

                    # If the user clicks "confirm" or hits enter
                    elif (event.type == pygame.MOUSEBUTTONDOWN and
                            confirm_button_rect.collidepoint(self.mouse_x, self.mouse_y)) or \
                            (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):

                        if cur_face == "":
                            print"There's no face selected!"
                        elif cur_face == "%empty":
                            cur_face = ""
                        else:
                            return cur_face

            self.game_surface.fill((135, 206, 250))
            self.game_window.blit(self.game_surface, (0, 0))
            self.game_window.blit(self.exit_button, (self.game_window.get_width() - self.exit_button.get_width(), 0))
            self.game_window.blit(confirm_button, (100, 50))
            for face in face_list:
                self.game_window.blit(face.image, (face.x_pos, face.y_pos))
            pygame.display.flip()

    # Creates the title screen
    def title_screen(self):
        play_button_col = (0, 0, 255)
        in_title_screen = True
        title = True
        while in_title_screen:
            self.game_surface.fill((135, 206, 250))
            play_font = pygame.font.Font(None,  36)
            play_text = play_font.render("Play",  1,  (10,  10,  10))
            play_text_pos = play_text.get_rect()
            play_text_pos.centerx = self.game_window.get_rect().centerx
            play_text_pos.centery = self.game_window.get_rect().centery
            if title:
                play_button = pygame.draw.rect(self.game_surface,  play_button_col,
                                               (self.game_window.get_width()/2-100,
                                                self.game_window.get_height()/2-25, 200, 50))

            self.game_window.blit(self.game_surface, (0, 0))
            self.game_window.blit(self.exit_button,  (self.game_window.get_width()-self.exit_button.get_width(), 0))
            self.game_window.blit(play_text,  play_text_pos)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Darken the play button
                    if title and play_button.collidepoint(self.mouse_x, self.mouse_y):
                        play_button_col = (0, 0, 175)
                    # Quit
                    if self.exit_button_rect.collidepoint(self.mouse_x, self.mouse_y):
                        pygame.quit()
                        quit()

                if event.type == pygame.MOUSEBUTTONUP:
                    # Reset the color of the play button
                    play_button_col = (0, 0, 255)

                    # Break out of the loop and continue to char_create()
                    if title and play_button.collidepoint(self.mouse_x, self.mouse_y):
                        self.game_surface.fill((135, 206, 250))
                        self.game_window.blit(self.game_surface, (0, 0))
                        title = False
                        in_title_screen = False
            pygame.display.flip()
        self.char_create()

    # Render the tombstone information to self.game_window
    def tombstone_info(self, tombstone):
        tomb_surface = pygame.Surface((200, 300))
        tomb_surface.fill((175, 175, 175))
        font = pygame.font.Font(None, 18)
        blit_x = 0
        face_image = pygame.image.load(resource_path + "Images\\Faces\\" + tombstone.passenger.picture + ".png")
        tomb_surface.blit(face_image, (tomb_surface.get_width()/2 - face_image.get_width()/2, 10))
        tomb_surface.blit(font.render("Name: %s" % tombstone.passenger.name, 1, (0, 0, 0)), (5, 110))
        tomb_surface.blit(font.render("Age : %s" % tombstone.passenger.age, 1, (0, 0, 0)), (5, 120))
        tomb_surface.blit(font.render("Cause of Death: %s" % tombstone.cause_of_death, 1, (0, 0, 0)), (5, 130))
        tomb_surface.blit(font.render("Position: %s" % tombstone.position, 1, (0, 0, 0)), (5, 140))

        if tombstone.x_pos + tombstone.tomb_width <= self.game_window.get_width() - tomb_surface.get_width():
            blit_x = tombstone.x_pos + tombstone.tomb_width
        elif tombstone.x_pos + tombstone.tomb_width >= self.game_window.get_width() - tomb_surface.get_width():
            blit_x = tombstone.x_pos - tomb_surface.get_width()
        self.game_window.blit(tomb_surface, (blit_x, tombstone.y_pos - tombstone.tomb_height))

    # Creates and blits the Menu Bar
    def build_menu_bar(self):
        self.menu_bar = pygame.Surface((35*len(self.menu_list) + 10, 34))
        self.menu_bar.fill((175, 175, 175))
        self.menu_bar.set_alpha(200)
        self.menu_button_list = []
        x_value = 5

        # Creates the menu buttons
        for path in self.menu_list:
            self.menu_button_list.append(MenuButton(image=resource_path+"Images\\"+path+".png",
                                                    name=path))
        # Manipulates and positions the menu buttons
        for button in self.menu_button_list:
            button_image = pygame.transform.scale(pygame.image.load(button.image), (32, 32))
            position = x_value, (self.menu_bar.get_height() - button_image.get_height())/2
            self.menu_bar.blit(button_image, position)
            button.update(position, button_image.get_size())
            x_value += button_image.get_width() + 5
        return self.menu_bar

    # Function to kill passengers
    def kill_passenger(self, passenger):
        passenger_list.remove(passenger)
        deceasedList.append(passenger)
        death_cause = "Unknown Causes"

        # Checks for the first negative affliction and blames it for the death
        for affliction in passenger.afflictions:
            if affliction.health_change < 0:
                death_cause = affliction.name
                break
        append_tomb = Tombstones(position=self.group_pos, status="New",
                                 passenger=passenger, cause_of_death=death_cause,
                                 tomb_width=self.tomb_image.get_width(),
                                 tomb_height=self.tomb_image.get_height())
        self.tombstone_list.append(append_tomb)
        print "Creating tombstone at position: " + str(self.group_pos)

        # Saving the tombstone to the file
        try:
            # Builds a temporary list with everything in tombstone.dat and adds the new tombstone
            with open("tombstone.dat", "rb") as file_name:
                temp_list = pickle.load(file_name)
                temp_list.append(append_tomb)

            # Writes over the tombstone.dat with the new tombstone added
            with open("tombstone.dat", "wb") as file_name:
                pickle.dump(temp_list, file_name)

        # Error handling
        except (EOFError, IOError) as error:
            print"Error occurred when saving to tombstone.dat. No tombstones will be saved."
            print"Error: "+error

        self.change_list.append(passenger.name+" has died.")
        # Checks if it's game over
        if len(passenger_list) == 0:
            print"They're all dead,  Jim."
            self.game_over()

    # Creates the option menu for the turn_menu_surface
    def option_menu(self, passenger_tab, hover):
        pygame.font.init()
        option_offset = 20./6.5
        option_menu_surface = pygame.Surface((100+option_offset*2,
                                              option_offset + (20 + option_offset)*len(self.option_list)))
        option_menu_surface.fill((100, 100, 100))
        y_value = option_offset

        # Checks if the option buttons have already been made, and makes them if they haven't
        if len(self.option_button_list) != len(self.option_list):
            for option in self.option_list:
                self.option_button_list.append(OptionButton(passenger_tab=passenger_tab,
                                                            option=option,
                                                            size=(100, 20),
                                                            hover=hover))

        # Positions the option buttons and creates their rectangle
        for button in self.option_button_list:
            option_menu_surface.blit(button.button_surface, (option_offset, y_value))
            button.rect = pygame.Rect((passenger_tab.position[0] +
                                       passenger_tab.size[0] + option_menu_surface.get_width() + option_offset,
                                       passenger_tab.position[1] + y_value + option_menu_surface.get_height()),
                                      button.size)
            y_value += button.size[1] + option_offset
        return option_menu_surface

    # Function to show detailed information about passengers
    def passenger_info(self, passenger, blit_pos):
        border_offset = float(15)
        info_font = pygame.font.Font(None, 30)
        x_value = 0
        self.affliction_button_list = []
        for affliction in passenger.afflictions:
            self.affliction_button_list.append(AfflictionBox(affliction=affliction,
                                                             font=info_font))
        passenger_info_filler_surface = pygame.Surface((400 + border_offset, 200 + border_offset))
        passenger_info_filler_surface.fill((0, 255, 0))
        passenger_info_surface = pygame.Surface((400, 200))
        passenger_info_surface.fill((255, 255, 255))
        passenger_picture = pygame.image.load(resource_path + "Images\\Faces\\" + passenger.picture + ".png")
        passenger_info_surface.blit(passenger_picture, (0, 0))

        # Blit Name
        passenger_info_surface.blit(info_font.render("Name: ", 1, (255, 0, 0)),
                                    (passenger_picture.get_width() + 5, float(passenger_picture.get_height())/10))
        passenger_info_surface.blit(info_font.render(passenger.name, 1, (0, 0, 255)),
                                    (passenger_picture.get_width() + 5 + info_font.size("Name: ")[0],
                                     float(passenger_picture.get_height())/10))
        # Blit Age
        passenger_info_surface.blit(info_font.render("Age: "+str(passenger.age), 1, (255, 0, 0)),
                                    (passenger_picture.get_width() + 5, float(passenger_picture.get_height())/2))
        passenger_info_surface.blit(info_font.render(str(passenger.age), 1, (0, 0, 255)),
                                    (passenger_picture.get_width() + 5 + info_font.size("Age: ")[0],
                                     float(passenger_picture.get_height())/2))
        # Blit Gender
        passenger_info_surface.blit(info_font.render("Gender: ", 1, (255, 0, 0)),
                                    (passenger_picture.get_width()*2, float(passenger_picture.get_height()/2)))
        passenger_info_surface.blit(info_font.render(passenger.gender, 1, (0, 0, 255)),
                                    ((passenger_picture.get_width()*2) + info_font.size("Gender: ")[0],
                                     float(passenger_picture.get_height()/2)))
        # Blit Afflictions
        passenger_info_surface.blit(info_font.render("Afflictions: ", 1, (255, 0, 0)),
                                    (0, passenger_picture.get_height() + passenger_picture.get_height()/10))
        x_value += info_font.size("Afflictions: ")[0]

        # Blits "None" if they have to afflictions
        if len(self.affliction_button_list) == 0:
            passenger_info_surface.blit(info_font.render("None", 1, (0, 0, 255)),
                                        (x_value, passenger_picture.get_height() + passenger_picture.get_height()/10))

        # Otherwise write as many affliction names as we can
        else:
            for affliction_button in self.affliction_button_list:
                # Checks if the next affliction name can fit without going off the edges
                if x_value + affliction_button.text_size[0] < passenger_info_surface.get_width():
                    passenger_info_surface.blit(info_font.render(affliction_button.name, 1, (0, 0, 255)),
                                                (x_value,
                                                 passenger_picture.get_height() +
                                                 passenger_picture.get_height()/10))
                    affliction_button.update((x_value + blit_pos[0],
                                              blit_pos[1] + passenger_picture.get_height() +
                                              passenger_picture.get_height()/10))
                    x_value += affliction_button.text_size[0]
                # If it can't, we've blitted as many as we can
                else:
                    break

        passenger_info_filler_surface.blit(passenger_info_surface, (border_offset/2, border_offset/2))
        return passenger_info_filler_surface

    # Function to show the full logbook
    def show_logbook(self, line_range, render_pos):
        offset = 5
        logbook_border = pygame.Surface((410, 510))
        logbook_surface = pygame.Surface((400, 500))
        logbook_surface.fill((255, 255, 255))
        text = pygame.font.Font(None, 15)
        char_height = text.size("LOREM IPSUM")[1]
        y_value = char_height + 1
        cur_line = 0

        # Blits everything within the visibility range
        for key in self.logbook_dict.keys():
            for line in self.logbook_dict[key]:
                if cur_line in line_range:
                    logbook_surface.blit(text.render(line, 1, (0, 0, 255)), (1, y_value))
                    y_value += char_height + 1
                cur_line += 1

        up_image = pygame.image.load(resource_path+"Images\\uparrow.png")
        down_image = pygame.image.load(resource_path+"Images\\downarrow.png")
        logbook_surface.blit(up_image, (logbook_surface.get_width() - up_image.get_width(), 0))
        self.logbook_up_rect = pygame.Rect((render_pos[0] + logbook_surface.get_width() - up_image.get_width(),
                                            render_pos[1]), up_image.get_size())

        logbook_surface.blit(down_image, (logbook_surface.get_width() - down_image.get_width(),
                                          logbook_surface.get_height() - down_image.get_height()))

        self.logbook_down_rect = pygame.Rect((render_pos[0] + logbook_surface.get_width() - down_image.get_width(),
                                              render_pos[1] + logbook_surface.get_height() - down_image.get_height()),
                                             down_image.get_size())
        logbook_border.blit(logbook_surface, (offset, offset))
        return logbook_border

    # A vague confirmation window, used to present messages to the player
    def confirmation_window(self, message, selection):
        pygame.key.set_repeat(0, 0)
        in_confirm_window = True
        confirm_outline = pygame.Surface((210, 110))
        confirm_window = pygame.Surface((200, 100))
        confirm_window.fill((255, 255, 255))

        okay_button_rect = pygame.Rect((0, 0), (0, 0))
        yes_button_rect = pygame.Rect((0, 0), (0, 0))
        no_button_rect = pygame.Rect((0, 0), (0, 0))

        # Global position used to place the rectangles
        pos = (self.game_window.get_width()/2 - confirm_window.get_width()/2,
               self.game_window.get_height()/2 - confirm_window.get_height()/2)
        font = pygame.font.Font(None, 20)
        text = []

        pixel_selection = ([pos[0], pos[0]+confirm_outline.get_width()],
                           [pos[1], pos[1]+confirm_outline.get_height()])

        # Keeps track of what the window looked like so we can draw it again after the confirm window is gone
        saved_state = pygame.PixelArray(self.game_window)[pixel_selection[0][0]:pixel_selection[0][1],
                                                          pixel_selection[1][0]:pixel_selection[1][1]].make_surface()

        # If the box is meant to be a box with "Okay" as the only option, or a box with text-entry
        if selection == "okay" or selection == "text_entry":
            okay_button = pygame.transform.scale(pygame.image.load(resource_path + "Images\\okay_button.png"), (50, 25))
            okay_button_pos = (self.game_window.get_width()/2 - okay_button.get_width()/2,
                               self.game_window.get_height()/2 + okay_button.get_height())
            okay_button_rect = pygame.Rect(okay_button_pos, (okay_button.get_size()))

            confirm_window.blit(okay_button, (confirm_window.get_width()/2 - okay_button.get_width()/2,
                                              confirm_window.get_height() - okay_button.get_height()))

            # Text-entry specific stuff
            if selection == "text_entry":
                entry_box = pygame.Surface((confirm_window.get_width() - 10, 40))
                entry_box.fill((255, 255, 255))
                confirm_window.blit(entry_box, (5, confirm_window.get_height()/2 - entry_box.get_height()))

        # If the box is meant to be a box with "Yes" or "No" as the options
        elif selection == "yesno":
            yes_button = pygame.transform.scale(pygame.image.load(resource_path + "Images\\yes_button.png"), (50, 25))
            yes_button_pos = (self.game_window.get_width()/2 - yes_button.get_width() + 5,
                              self.game_window.get_height()/2 + yes_button.get_height() + 5)
            yes_button_rect = pygame.Rect(yes_button_pos, (yes_button.get_size()))

            no_button = pygame.transform.scale(pygame.image.load(resource_path + "Images\\no_button.png"), (50, 25))
            no_button_pos = (self.game_window.get_width()/2 + 5,
                             self.game_window.get_height()/2 + no_button.get_height() + 5)
            no_button_rect = pygame.Rect(no_button_pos, (no_button.get_size()))

            confirm_window.blit(yes_button, (confirm_window.get_width()/2 - yes_button.get_width() + 5,
                                             confirm_window.get_height() - yes_button.get_height()))
            confirm_window.blit(no_button, (confirm_window.get_width()/2 + 5,
                                            confirm_window.get_height() - no_button.get_height()))

        # Places the text with wrap-around provided by self.length_splitter()
        y_value = 0
        for l in self.length_splitter(font, message, confirm_window.get_width()):
            confirm_window.blit(font.render(l, 1, (255, 0, 0)), (0, y_value))
            y_value += font.size(l)[1]

        confirm_outline.blit(confirm_window, (5, 5))
        self.game_window.blit(confirm_outline, pos)
        pygame.display.flip()
        is_shift = False

        # Main loop to wait for user-input
        while in_confirm_window:
            # Fill the entry_box with white, but only if it's a text-entry window
            if selection == "text_entry":
                entry_box.fill((255, 255, 255))

            events = pygame.event.get()
            # Main event loop for the confirm_window
            for event in events:
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Quit
                    if self.exit_button_rect.collidepoint(self.mouse_x, self.mouse_y):
                        in_confirm_window = False
                        pygame.quit()
                        break
                    # Exit the confirm window
                    if okay_button_rect.collidepoint(self.mouse_x, self.mouse_y):
                        if selection == "text_entry":
                            return "".join(text), saved_state, pos
                        return True

                    # Returns True or False based on which option is chosen
                    if yes_button_rect.collidepoint(self.mouse_x, self.mouse_y):
                        return True
                    elif no_button_rect.collidepoint(self.mouse_x, self.mouse_y):
                        return False

                # Checks for the text-entry window
                if event.type == pygame.KEYDOWN and selection == "text_entry":
                    # Keeps track of if the shift button is pressed
                    if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        is_shift = True
                    # Remove the last thing in text if the backspace is pressed
                    if event.key == pygame.K_BACKSPACE:
                        if len(text) > 0:
                            text.pop()
                    else:
                        # Tries to add the key that got pressed, fails if it can't be converted using chr()
                        try:
                            if is_shift:
                                text.append(chr(event.key).upper())
                            else:
                                text.append(chr(event.key))
                        except ValueError:
                            print "Error: [" + str(event.key) + "] out of chr() range."
                # Shift button is no longer being pressed
                if event.type == pygame.KEYUP and selection == "text_entry":
                    if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        is_shift = False

            # Renders the text if it's a text-entry window
            if selection == "text_entry":
                entry_box.blit(font.render("".join(text), 1, (255, 0, 0)), (0, 0))
                confirm_window.blit(entry_box, (5, confirm_window.get_height()/2 - entry_box.get_height()+10))
            confirm_outline.blit(confirm_window, (5, 5))
            self.game_window.blit(confirm_outline, pos)
            pygame.display.flip()

    @staticmethod
    # Used to split text up into lines that will fit the surface
    def length_splitter(font, text, maxlength):
        ret_list = []
        explode = text.split()
        t_str = ""
        while len(explode) > 0:
            if font.size(t_str + explode[0])[0] > maxlength:
                ret_list.append(t_str)
                t_str = ""
            else:
                t_str += explode.pop(0) + " "
                if len(explode) == 0:
                    ret_list.append(t_str)
        return ret_list

    # Creates a surface that shows the changes for that day
    def show_output_box(self):
        offset = 5
        output_border = pygame.Surface((310, 160))
        output_box = pygame.Surface((300, 150))
        output_box.fill((255, 255, 255))
        text = pygame.font.Font(None, 15)
        char_height = text.size("LOREM IPSUM")[1]
        y_value = -char_height

        # Adds it to the logbook first
        if len(self.output_text) < len(self.logbook_dict[self.days_since_start]):
            t_lst = [x for x in self.logbook_dict[self.days_since_start]]
            for e in t_lst:
                for l in self.length_splitter(text, e, 300):
                    self.output_text.append(l)

        # Then creates the output box
        for output in self.output_text:
            out_y = output_box.get_height()-(char_height*len(self.output_text))+y_value
            output_box.blit(text.render(output, 1, (0, 0, 255)), (0, out_y))
            y_value += char_height
        output_border.blit(output_box, (offset, offset))
        return output_border

    # Shows the menu to display and edit food for each passenger
    def show_food_menu(self, passenger):
        offset = 5
        food_menu_surface_border = pygame.Surface((310, 110))
        food_menu_surface = pygame.Surface((300, 100))
        food_menu_surface.fill((255, 255, 255))
        text = pygame.font.Font(None, 20)
        up_image = pygame.transform.scale(pygame.image.load(resource_path+"Images\\uparrow.png"), (25, 25))
        down_image = pygame.transform.scale(pygame.image.load(resource_path+"Images\\downarrow.png"), (25, 25))
        food_menu_surface.blit(text.render(passenger.name, 1, (0, 0, 255)), (10, food_menu_surface.get_height()/4))
        food_menu_surface.blit(text.render("Food Division: ", 1, (255, 0, 0)), (10, food_menu_surface.get_height()/2))
        food_menu_surface.blit(text.render(str(passenger.food_divisions), 1, (0, 0, 255)),
                               (10 + text.size("Food Division: ")[0], food_menu_surface.get_height()/2))
        food_menu_surface.blit(text.render("Change from food: ", 1, (255, 0, 0)),
                               (10, food_menu_surface.get_height() * 3/4))
        food_menu_surface.blit(text.render(str(-3 + (1.5 * passenger.food_divisions)), 1, (0, 0, 255)),
                               (10 + text.size("Change from food: ")[0], food_menu_surface.get_height() * 3/4))

        food_menu_surface.blit(up_image, (food_menu_surface.get_width() - up_image.get_width(), 0))
        self.food_menu_up_rect = pygame.Rect((food_menu_surface.get_width() - up_image.get_width() +
                                              self.info_menu_blit_position[0], self.info_menu_blit_position[1]),
                                             up_image.get_size())

        food_menu_surface.blit(down_image, (food_menu_surface.get_width() - down_image.get_width(),
                                            food_menu_surface.get_height() - down_image.get_height()))
        self.food_menu_down_rect = pygame.Rect((food_menu_surface.get_width() - down_image.get_width() +
                                                self.info_menu_blit_position[0], self.info_menu_blit_position[1] +
                                                food_menu_surface.get_height() - down_image.get_height()),
                                               down_image.get_size())
        food_menu_surface_border.blit(food_menu_surface, (offset, offset))
        return food_menu_surface_border

    # Hunting minigame function
    def go_hunting(self, times):
        buffalo_list = []
        hunting = True
        shoot_countdown = 0
        food_yield = 0
        self.game_surface.fill((0, 255, 0))
        self.game_window.blit(self.game_surface, (0, 0))
        countdown_text = pygame.font.Font(None, 35)
        counter_text = pygame.font.Font(None, 50)
        cooldown_background = pygame.Surface((300, 50))
        cooldown_bar = pygame.Surface((300, 50))
        cooldown_bar.fill((255, 0, 0))
        crosshair = pygame.image.load(resource_path + "Images\\crosshair.png")
        gun_shot = pygame.transform.scale(pygame.image.load(resource_path + "Images\\bloodsplatter.png"), (20, 20))
        ref_buffalo = pygame.image.load(resource_path + "Images\\alive_buffalo.png")
        gun_shot_group = {}
        pygame.mouse.set_visible(False)

        # Function used to determine the maximum buffalo that can appear
        val_funct = 20.46096855 / (1+0.0011517959*2.71828**(2.996546379*times))
        the_max = min(20, max(0, int(val_funct)))

        # Create buffalos and give them random values
        for n in range(random.randint(0, the_max)):
            random_size = random.uniform(0.5, 1.5)
            random_y = random.randint(ref_buffalo.get_height(), (self.game_window.get_height() * 3/4))
            random_x = random.randint(-self.game_window.get_width()/2, self.game_window.get_width()/2)
            buffalo_list.append(Buffalo(pos_x=random_x, pos_y=random_y, picture="alive", size=random_size))

        # Creates an entry in gun_shot_group for every buffalo
        for b in buffalo_list:
            gun_shot_group[b] = []

        # Main hunting minigame loop
        while hunting:
            clock.tick(60)
            events = pygame.event.get()
            cooldown_bar = pygame.Surface((shoot_countdown*2, 50))
            cooldown_background.fill((0, 0, 0))
            cooldown_bar.fill((255, 0, 0))
            cooldown_background.blit(cooldown_bar, (0, 0))
            background_color = (0, 255, 0)
            self.game_surface.fill(background_color)
            self.game_window.blit(self.game_surface, (0, 0))

            # Counts the number of buffalo killed
            counter = 0
            for check in buffalo_list:
                if check.status == "dead":
                    counter += 1
            # The main loop ends when they're all either killed or off the screen
            hunting = not len(buffalo_list) == counter

            for buffalo in buffalo_list:
                buffalo.update()
                self.game_window.blit(buffalo.image, (buffalo.rect.x,
                                                      buffalo.rect.y))
                self.game_window.blit(buffalo.health_bar_shader, ((buffalo.rect.x + buffalo.image.get_width()/2) -
                                                                  buffalo.health_bar_shader.get_width()/2,
                                                                  buffalo.rect.y))
                # Blit gunshots
                for g in gun_shot_group[buffalo]:
                    self.game_window.blit(gun_shot, (buffalo.rect.x + g[0], buffalo.rect.y + g[1]))

                # Remove buffalos if they're off the screen
                if buffalo.rect.left > self.game_window.get_width():
                    buffalo_list.remove(buffalo)

                # Random Y-axis movements
                if buffalo.rect.y == buffalo.target_y:
                    if random.randint(1, 200) == 1:
                        buffalo.target_y = int(random.randint(ref_buffalo.get_height(),
                                                              (self.game_window.get_height() * 3/4)))

                # Main event loop
                for event in events:
                    if event.type == pygame.MOUSEMOTION:
                        self.mouse_x, self.mouse_y = event.pos
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Quit
                        if self.exit_button_rect.collidepoint(self.mouse_x, self.mouse_y):
                            hunting = False
                        # Main shot detection
                        if shoot_countdown <= 0:
                            if buffalo.rect.collidepoint(self.mouse_x, self.mouse_y):
                                if buffalo.image.get_at((self.mouse_x - buffalo.rect.x,
                                                         self.mouse_y - buffalo.rect.y)) != (0, 0, 0, 0):
                                    print buffalo.image.get_at((self.mouse_x - buffalo.rect.x,
                                                                self.mouse_y - buffalo.rect.y))
                                    if buffalo.status != "dead":
                                        # Subtracts a random amount of health and then check if they're dead
                                        buffalo.health -= random.randint(40, 130)
                                        if buffalo.health <= 0:
                                            buffalo.health = 0
                                            buffalo.status = "dead"
                                            food_yield += buffalo.value
                                    shoot_countdown = 150
                                    # Add a gunshot to the buffalo
                                    gun_shot_group[buffalo].append(((self.mouse_x -
                                                                     gun_shot.get_width()/2) - buffalo.rect.x,
                                                                    (self.mouse_y -
                                                                     gun_shot.get_height()/2) - buffalo.rect.y))
                        break

            # Main blitting block
            self.game_window.blit(cooldown_background, (self.game_window.get_width()/2 -
                                                        cooldown_background.get_width()/2,
                                                        self.game_window.get_height() - 100))
            self.game_window.blit(self.exit_button, (self.game_window.get_width() -
                                                     self.exit_button.get_width(), 0))
            self.game_window.blit(countdown_text.render(str(round(float(shoot_countdown)/clock.get_fps(), 1)), 1,
                                                        (0, 0, 255)),
                                  (self.game_window.get_width()/2 - countdown_text.size(str(shoot_countdown))[0],
                                   self.game_window.get_height() - 100))
            self.game_window.blit(counter_text.render(str(counter), 1, (0, 0, 255)), (0, 0))
            self.game_window.blit(crosshair, (self.mouse_x - crosshair.get_width()/2,
                                              self.mouse_y - crosshair.get_height()/2))
            if shoot_countdown > 0:
                crosshair = pygame.image.load(resource_path + "Images\\crosshair_cooldown.png")
                shoot_countdown -= 1
            else:
                crosshair = pygame.image.load(resource_path + "Images\\crosshair.png")
            pygame.display.flip()

        # End of the hunt stuff
        pygame.mouse.set_visible(True)
        self.group_inventory["Food"] += int(food_yield)
        return "You brought back " + str(int(food_yield)) + " food!"

    # Function called when a river event is met
    @property
    def river(self):
        font = pygame.font.Font(None, 25)
        options = ["Attempt to wade through the river.",
                   "Attempt to float across the river."]

        # Random ferry generation
        is_ferry = random.randint(0, 10) >= 4
        ferry_price = None
        if is_ferry:
            ferry_price = random.randint(50, 150)
            options.append("Purchase a ferry ride across the river. [$" + str(ferry_price) + "]")

        in_menu = True
        font_height = font.size("LOREM IPSUM")[1]
        mouse_rect = pygame.Rect((0, 0), (0, 0))
        box_hover = None
        option = None
        random_risk = random.randint(1, 10000)
        # River menu loop
        while in_menu:
            y_value = font_height
            object_list = []
            option_box = pygame.Surface((400, 300))
            option_box.fill((255, 255, 255))
            option_box_container = pygame.Surface((option_box.get_width() + 10, option_box.get_height() + 10))
            # Global offset used to position rectangles
            global_offset = (self.game_window.get_width() -
                             option_box_container.get_width())/2, \
                            (self.game_window.get_height() -
                             option_box_container.get_height())/2
            # Create a RiverOptionButton object for each item in the options list
            for opt in options:
                opt_pos = (global_offset[0] + 3, global_offset[1] + y_value)
                create_bool = box_hover is not None and box_hover.option == opt
                object_list.append(RiverOptionButton(option=opt, size=(option_box.get_width(), font_height*3),
                                                     hover=create_bool, pos=opt_pos))
                y_value += font_height*3

            # Interactvity for the River menu
            events = pygame.event.get()
            for event in events:
                # Mouse movement
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos
                    mouse_rect = pygame.Rect((self.mouse_x, self.mouse_y), (1, 1))

                # Exit button
                if self.exit_button_rect.collidepoint(self.mouse_x, self.mouse_y):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        in_menu = False
                        break

                # Hover coloring and option selection
                if mouse_rect.collidelist([x.rect for x in object_list]) != -1:
                    box_hover = object_list[mouse_rect.collidelist([x.rect for x in object_list])]

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if box_hover.option in options:
                            if box_hover.option == "Attempt to wade through the river.":
                                option = "wade"
                                print"You want to wade through the river."
                            elif box_hover.option == "Attempt to float across the river.":
                                option = "float"
                                print"You want to float across the river."
                            elif box_hover.option == "Purchase a ferry ride across the river. [$"+str(ferry_price)+"]":
                                option = "ferry"
                                print"You want to purchase a ride."
                            in_menu = False
                        else:
                            print"Somehow an invalid argument."
                else:
                    box_hover = None

            # Shades in the option being hovered over
            if box_hover is not None:
                box_hover.update(True)

            for obj in object_list:
                obj_pos = (obj.pos[0] - global_offset[0], obj.pos[1] - global_offset[1])
                option_box.blit(obj.surface, obj_pos)

            # Main blitting block
            option_box_container.blit(option_box, (5, 5))
            self.game_surface.fill((175, 175, 175))
            self.game_window.blit(self.game_surface, (0, 0))
            self.game_window.blit(option_box_container, ((self.game_window.get_width() -
                                                         option_box_container.get_width())/2,
                                                         (self.game_window.get_height() -
                                                         option_box_container.get_height())/2))
            self.game_window.blit(self.exit_button, (self.game_window.get_width() - self.exit_button.get_width(), 0))
            pygame.display.flip()

        # Variables defined before handling the options
        river_surface = pygame.Surface((self.game_window.get_width() * 5/8, self.game_window.get_height()))
        river_surface.fill((30, 144, 255))
        river_pos = (self.game_window.get_width() * 1.5/8, 0)

        wagon = pygame.image.load(resource_path + "Images\\wagon.png")
        wagon_pos = [self.game_window.get_width() * 6.5/8, self.game_window.get_height()/2]

        river_random = (self.game_window.get_width() * 1.5/8, (self.game_window.get_width() * 6.5/8)-wagon.get_width())

        pygame.key.set_repeat(10, 10)
        river_debris_group = []

        # Creates buttons for the river option menu
        for num in range(random.randint(1, 10)):
            random_x = random.randint(river_random[0], river_random[1])
            random_y = random.randint(0, self.game_window.get_height())
            random_size = round(random.uniform(0.5, 1.5), 1)
            river_debris_group.append(RiverDebris(size=random_size,
                                                  pos_x=random_x,
                                                  pos_y=random_y,
                                                  random_gen=river_random,
                                                  picture="river_debris",
                                                  river_pos=river_pos[0]))

        # Loop for the wading animation
        while option == "wade":
            if wagon_pos[0] < (self.game_window.get_width() * 1.5/8) - wagon.get_width() or \
               wagon_pos[1] > self.game_window.get_height() + wagon.get_height():
                self.confirmation_window("YOU MADE IT ACROSS SAFELY", "okay")
                return "YOU MADE IT ACROSS SAFELY"
            if random.randint(1, random_risk) == 1:
                self.confirmation_window("YOU WERE INUNDATED BY WATER", "okay")
                return "YOU WERE INUNDATED BY WATER"

            wagon_pos[0] -= 1
            self.game_surface.fill((139, 69, 19))
            self.game_window.blit(self.game_surface, (0, 0))
            self.game_window.blit(river_surface, river_pos)
            self.game_window.blit(wagon, tuple(wagon_pos))
            self.game_window.blit(self.exit_button, (self.game_window.get_width() - self.exit_button.get_width(), 0))
            pygame.display.flip()

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos
                if self.exit_button_rect.collidepoint((self.mouse_x, self.mouse_y)):
                    option = None

        # Loop for the floating minigame
        while option == "float":
            wagon_rect = pygame.Rect(tuple(wagon_pos), wagon.get_size())
            if wagon_pos[0] < (self.game_window.get_width() * 1.5/8) - wagon.get_width() or \
               wagon_pos[1] > self.game_window.get_height() + wagon.get_height():
                self.confirmation_window("YOU MADE IT ACROSS SAFELY", "okay")
                return "YOU MADE IT ACROSS SAFELY"

            if wagon_rect.collidelist([x.rect for x in river_debris_group]) != -1:
                self.confirmation_window("YOU CRASHED!", "okay")
                return "YOU CRASHED!"

            self.game_surface.fill((139, 69, 19))
            self.game_window.blit(self.game_surface, (0, 0))
            river_surface.fill((30, 144, 255))
            self.game_window.blit(river_surface, river_pos)

            # Updates and moves the river debris
            for deb in river_debris_group:
                self.game_window.blit(deb.image, (deb.rect.x, deb.rect.y))
                deb.update(river_surface.get_size())

            self.game_window.blit(wagon, tuple(wagon_pos))
            self.game_window.blit(self.exit_button, (self.game_window.get_width() - self.exit_button.get_width(), 0))
            wagon_pos[1] += 0.1
            pygame.display.flip()

            # Event loop checking for keypresses
            events = pygame.event.get()
            keys = pygame.key.get_pressed()
            for event in events:
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos
                if self.exit_button_rect.collidepoint((self.mouse_x, self.mouse_y)):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        option = None
                if event.type == pygame.KEYDOWN:
                    if keys[pygame.K_a]:
                        wagon_pos[0] -= 1
                    if keys[pygame.K_s]:
                        wagon_pos[1] += 1
                    if keys[pygame.K_w]:
                        wagon_pos[1] -= 1

        # Checks if the group can afford a ferry, and ferries them across if they can
        if option == "ferry":
            if self.group_money >= ferry_price:
                self.group_money -= ferry_price
                self.confirmation_window("You purchased a ride across for $" + str(ferry_price), "okay")
                return "You purchased a ride across for $" + str(ferry_price)
            else:
                self.confirmation_window("You don't have enough money to hire a ferry.", "okay")

    def house(self, event):
        item_changed = {}
        # List of dictionaries, both positive and negative, used to inform the user of inventory changes
        gain_loss_phrases = [{"You found": " in the house.",
                              "You scavenged": " from the house",
                              "Found": " in the house.",
                              "You came across": " near the house."},
                             {"Bandits stole": " from the wagon.",
                              "You were ambushed by bandits and lost": ".",
                              "You were attacked by thieves who stole": " from you.",
                              "You came back to the wagon to find": "missing."}]
        rand_phrase = random.choice(gain_loss_phrases[event.good_or_bad].keys())
        change_report = rand_phrase
        amount_items = random.randint(1, len(self.group_inventory))
        # Randomly selects the items to gain or lose
        for n in range(amount_items):
            the_item = self.group_inventory.keys()[n]
            amount_changed = random.randint(0, self.group_inventory[the_item])
            item_changed[the_item] = amount_changed * event.good_or_bad

        # Changes the inventory and modifies the change_report with the items
        for i in item_changed.keys():
            self.group_inventory[i] += item_changed[i]
            change_report += (str(", ["+str(abs(item_changed[i]))+" "+str(i)+"]"))
        change_report += " " + str(gain_loss_phrases[event.good_or_bad][rand_phrase])
        self.confirmation_window(change_report, "okay")
        return change_report

    # Used in paint_bucket to return all neighbors of a given pixel
    def get_neighbors(self, pixel):
        neighbors = []
        if pixel[0] > 2:
            neighbors.append((pixel[0] - 2, pixel[1]))
        if pixel[0] < self.canvas.get_width() - 2:
            neighbors.append((pixel[0] + 2, pixel[1]))
        if pixel[1] > 2:
            neighbors.append((pixel[0], pixel[1] - 2))
        if pixel[1] < self.canvas.get_height() - 2:
            neighbors.append((pixel[0], pixel[1] + 2))
        return neighbors

    # Used in go_painting to flood fill a section of canvas
    def paint_bucket(self, pixel, color, fill_color, g_pos):
        show_steps = False
        checked = [pixel]
        array = pygame.PixelArray(self.canvas)
        while len(checked) > 0:
            pix = checked.pop(0)
            if show_steps:
                array = pygame.PixelArray(self.canvas)

            # Replaces a 4x4 grid around the pixel with the selected color
            if array[pix] == self.canvas.map_rgb(color):
                array[pix[0]-1:pix[0]+2, pix[1]-1:pix[1]+2].replace(color, fill_color)
                for n in self.get_neighbors(pix):
                    if n not in checked:
                        checked.append(n)
            # Used during development to visualize the flood_fill
            if show_steps:
                del array
                self.game_window.blit(self.canvas, g_pos)
                pygame.display.flip()

    # Returns true if the surfaces are the same, false if they are not
    @staticmethod
    def compare_surface(s1, s2):
        # Uses PixelArrays to walk through each pixel and compare them
        s1pa = pygame.PixelArray(s1)
        s2pa = pygame.PixelArray(s2)
        for x, y in zip(s1pa, s2pa):
            for a, b in zip(x, y):
                if a != b:
                    return False
        return True

    # Sloppy function used to go painting with a canvas
    # Marked for a re-write
    def go_painting(self, passenger):
        g_pos = (0, 100)
        self.canvas.fill((255, 255, 255))
        line_start = (0, 0)
        line_end = (0, 0)

        paint_menu_bar = pygame.Surface((self.canvas.get_width(), 30))
        paint_menu_bar.fill((175, 175, 175))

        paint_colors = {"red": (pygame.Rect((0, 0), (10, 10)), (255, 0, 0)),
                        "green": (pygame.Rect((0, 0), (10, 10)), (0, 255, 0)),
                        "blue": (pygame.Rect((0, 0), (10, 10)), (0, 0, 255)),
                        "yellow": (pygame.Rect((0, 0),  (10, 10)), (255, 255, 0)),
                        "lightblue": (pygame.Rect((0, 0),  (10, 10)), (0, 255, 255)),
                        "black": (pygame.Rect((0, 0), (10, 10)), (0, 0, 0)),
                        "white": (pygame.Rect((0, 0), (10, 10)), (255, 255, 255))}

        brush_sizes = {"small": (pygame.Rect((0, 0), (10, 10)), 2),
                       "medium": (pygame.Rect((0, 0), (10, 10)), 5),
                       "large": (pygame.Rect((0, 0), (10, 10)), 8)}

        text_fonts = {"small": (pygame.Rect((0, 0), (10, 10)), 5),
                      "medium": (pygame.Rect((0, 0), (10, 10)), 10),
                      "large": (pygame.Rect((0, 0), (10, 10)), 15)}

        paint_menu_colors_rect = pygame.Rect((0, 0), (30, 30))
        paint_menu_pulldown = pygame.Surface((50, 50))
        paint_menu_pulldown.fill((175, 175, 175))

        paint_menu_sizes_rect = pygame.Rect((0, 0), (50, 30))
        paint_menu_sizes_pulldown = pygame.Surface((50, 50))
        paint_menu_sizes_pulldown.fill((175, 175, 175))

        paint_menu_text_rect = pygame.Rect((0, 0), (30, 30))
        paint_menu_text_pulldown = pygame.Surface((50, 50))

        x_value = 5
        y_value = 5
        for color in paint_colors:
            the_sur = pygame.Surface((10, 10))
            the_sur.fill(paint_colors[color][1])
            paint_menu_pulldown.blit(the_sur, (x_value, y_value))
            paint_colors[color] = (pygame.Rect((g_pos[0] + x_value,
                                                g_pos[1] + y_value), (10, 10)),
                                   paint_colors[color][1])
            x_value += 15
            if x_value == 50:
                x_value = 5
                y_value += 15

        x_value = 5
        y_value = 5
        for size in brush_sizes:
            the_sur = pygame.Surface((10, 10))
            the_sur.fill((255, 255, 255))
            calc_pos = (int(the_sur.get_width()/2 - brush_sizes[size][1]/2),
                        int(the_sur.get_height()/2 - brush_sizes[size][1]/2))
            pygame.draw.circle(the_sur, (0, 0, 0), calc_pos, brush_sizes[size][1]/2)
            paint_menu_sizes_pulldown.blit(the_sur, (x_value, y_value))
            brush_sizes[size] = (pygame.Rect((g_pos[0] + x_value,
                                              g_pos[1] + y_value), (10, 10)),
                                 brush_sizes[size][1])
            x_value += 15
            if x_value == 50:
                x_value = 5
                y_value += 15

        x_value = 5
        y_value = 5
        for font in text_fonts:
            fnt = pygame.font.Font(None, text_fonts[font][1])
            the_sur = pygame.Surface((10, 10))
            the_sur.fill((255, 255, 255))
            the_sur.blit(fnt.render("T", 1, (0, 0, 0)), (0, 0))
            paint_menu_text_pulldown.blit(the_sur, (x_value, y_value))
            text_fonts[font] = (pygame.Rect((g_pos[0] + x_value,
                                             g_pos[1] + y_value), (10, 10)),
                                text_fonts[font][1])
            x_value += 15
            if x_value == 50:
                x_value = 5
                y_value += 15

        paint_menu_bar_buttons = {"color_select": (paint_menu_colors_rect,
                                                   paint_menu_pulldown,
                                                   resource_path+"Images\\Paint\\color_select.png"),
                                  "brush_sizes": (paint_menu_sizes_rect,
                                                  paint_menu_sizes_pulldown,
                                                  resource_path+"Images\\Paint\\brush_sizes.png"),
                                  "text_tool": (paint_menu_text_rect,
                                                paint_menu_text_pulldown,
                                                resource_path+"Images\\Paint\\text.png")}

        menu_x = 5
        for b in paint_menu_bar_buttons:
            paint_menu_bar.blit(pygame.transform.scale(pygame.image.load(paint_menu_bar_buttons[b][2]), (30, 30)),
                                (menu_x, 0))
            paint_menu_bar_buttons[b] = (pygame.Rect((menu_x + g_pos[0], g_pos[1]-paint_menu_bar.get_height()),
                                                     (paint_menu_bar.get_height(), paint_menu_bar.get_height())),
                                         paint_menu_bar_buttons[b][1],
                                         paint_menu_bar_buttons[b][2])
            menu_x += 35

        self.painting = True
        show_pulldown = None
        show_pulldown_rect = pygame.Rect((0, 0), (0, 0))
        canvas_rect = pygame.Rect(g_pos, self.canvas.get_size())
        cur_width = 5
        cur_color = (255, 0, 0)
        place_text = None
        is_ctrl = False
        pygame.mouse.set_visible(False)
        # Sets the undos list to initially include the blank canvas
        self.undos.append(self.canvas.copy())

        # Main painting loop
        while self.painting:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.MOUSEMOTION:
                    line_end = event.pos
                    if pygame.mouse.get_pressed() == (1, 0, 0) and place_text is None:
                        # Draws a line for as long as left mouse button is down and not placing text
                        if not show_pulldown_rect.collidepoint(line_end) and canvas_rect.collidepoint(line_end):
                            pygame.draw.line(self.canvas, cur_color, (line_start[0]-g_pos[0], line_start[1]-g_pos[1]),
                                             (line_end[0]-g_pos[0], line_end[1]-g_pos[1]), cur_width)
                    line_start = line_end
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL:
                        is_ctrl = True

                    # If the user undos something, remove the last thing in self.undos and put it in self.redos
                    if event.key == pygame.K_z and is_ctrl:
                        if len(self.undos) > 1:
                            self.redos.append(self.undos.pop())
                            self.canvas = self.undos[-1].copy()
                            break
                    # If the user redos something, move the last thing in self.redos over to self.undos
                    if event.key == pygame.K_r and is_ctrl:
                        if len(self.redos) > 0:
                            self.undos.append(self.redos.pop())
                            self.canvas = self.undos[-1].copy()
                            break
                # Keeps track of the ctrl key used for shortcuts
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LCTRL:
                        is_ctrl = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.exit_button_rect.collidepoint(line_end):
                        self.painting = False
                        break
                    # Checks if any of the buttons in the paint_menu_bar are clicked
                    for button in paint_menu_bar_buttons:
                        if paint_menu_bar_buttons[button][0].collidepoint(line_end):
                            if show_pulldown == paint_menu_bar_buttons[button][1]:
                                show_pulldown = None
                                show_pulldown_rect = pygame.Rect((0, 0), (0, 0))
                            else:
                                show_pulldown = paint_menu_bar_buttons[button][1]
                                show_pulldown_rect = pygame.Rect(g_pos, show_pulldown.get_size())

                    # If we're placing text, call the confirmation_window and use it as a text-entry
                    if place_text is not None and not show_pulldown_rect.collidepoint(line_end):
                        entry_output = self.confirmation_window("Please enter text: ", "text_entry")
                        self.canvas.blit(place_text.render(entry_output[0], 1, cur_color),
                                         (line_end[0]-g_pos[0], line_end[1]-g_pos[1]))
                        self.game_window.blit(entry_output[1], entry_output[2])
                        line_end = (0, 0)
                        pygame.display.flip()
                        place_text = None

                    # Colors
                    if show_pulldown == paint_menu_pulldown:
                        for c in paint_colors:
                            if paint_colors[c][0].collidepoint(line_end):
                                cur_color = paint_colors[c][1]

                    # Brush Size
                    elif show_pulldown == paint_menu_sizes_pulldown:
                        for s in brush_sizes:
                            if brush_sizes[s][0].collidepoint(line_end):
                                cur_width = brush_sizes[s][1]

                    # Font
                    elif show_pulldown == paint_menu_text_pulldown:
                        for t in text_fonts:
                            if text_fonts[t][0].collidepoint(line_end):
                                place_text = pygame.font.Font(None, text_fonts[t][1])

                    # Flood filling
                    if pygame.mouse.get_pressed() == (0, 0, 1) and not show_pulldown_rect.collidepoint(line_end):
                        if g_pos[0] <= line_end[0] <= g_pos[0]+self.canvas.get_width()-cur_width:
                            self.paint_bucket((line_end[0]-g_pos[0], line_end[1]-g_pos[1]),
                                              self.canvas.get_at((line_end[0]-g_pos[0], line_end[1]-g_pos[1])),
                                              cur_color, g_pos)

            # Saves a copy of the canvas if it's different than the last thing in self.undos
            if not any(pygame.key.get_pressed()) and not any(pygame.mouse.get_pressed()):
                if not self.compare_surface(self.undos[-1], self.canvas):
                    self.undos.append(self.canvas.copy())
                    self.redos = []
                    print len(self.redos)

            self.game_window.blit(self.exit_button, (self.game_window.get_width() - self.exit_button.get_width(), 0))
            self.game_window.blit(self.canvas, g_pos)
            self.game_window.blit(paint_menu_bar, (g_pos[0], g_pos[1]-paint_menu_bar.get_height()))

            if show_pulldown is not None:
                self.game_window.blit(show_pulldown, g_pos)

            cursor = pygame.Surface((cur_width, cur_width))
            cursor.fill(cur_color)

            # Only show the cursor if it's on the canvas and not on an option menu
            if g_pos[0] <= line_end[0] <= g_pos[0]+self.canvas.get_width()-cur_width and place_text is None:
                if g_pos[1] <= line_end[1] <= g_pos[1]+self.canvas.get_height()-cur_width:
                    if not show_pulldown_rect.collidepoint(line_end):
                        self.game_window.blit(cursor, line_end)
                        pygame.mouse.set_visible(False)
                    else:
                        pygame.mouse.set_visible(True)
                else:
                    pygame.mouse.set_visible(True)
            else:
                pygame.mouse.set_visible(True)

            pygame.display.flip()

        pygame.mouse.set_visible(True)
        # Prompt asking the user to save their painting or not
        if self.confirmation_window("Save this painting by [" + passenger.name + "] to your inventory?", "yesno"):
            try:
                pygame.image.save(self.canvas,
                                  resource_path + "Saved Paintings\\"+passenger.name+str(time.time())+".png")
                self.confirmation_window("Painting saved successfully.", "okay")
                print "Painting saved successfully"
            except IOError as e:
                self.confirmation_window("Error saving painting.", "okay")
                print "Error saving painting to [" + \
                      resource_path + "Saved Paintings\\"+passenger.name+str(time.time())+".png" + "]: " + str(e)

    @staticmethod
    def game_over():
        pygame.quit()
        quit()

#############
# Functions #
#############


def main():
    the_game = Game()
    random_y = 0

    # Creates 200 random objects for the background
    for counter in xrange(201):
        rand_choice = random.choice(["cloud", "tree"])
        if rand_choice == "cloud":
            random_y = random.randint(0, 100)
        elif rand_choice == "tree":
            random_y = random.randint(the_game.game_window.get_height() - the_game.game_window.get_height() / 3 - 45,
                                      the_game.game_window.get_height() - the_game.game_window.get_height() / 3 - 5)

        random_x = random.randint(-100, the_game.game_window.get_width()-11)
        the_game.shape_group.add(BackgroundSprites(size=10,  color=(255, 0, 0),
                                                   pos_x=random_x, pos_y=random_y, picture=rand_choice))

    # Generates the afflictions from the afflictions_dict
    for affliction in afflictions_dict:
        stats = afflictions_dict[affliction]
        afflictions_list.append(AfflictionsClass(name=affliction, chance_to_infect=stats[0], infectivity=stats[1],
                                                 prime_season=stats[2], health_change=stats[3], recovery_time=stats[4]))

    the_game.title_screen()

################
# Running Main #
################
if __name__ == "__main__":
    main()
