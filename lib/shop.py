from pygame import Surface, font
from copy import copy
from random import randint, choice
from string import capitalize

from transaction_button import TransactionButton

# Constants
SHOP_NAME_PREFIX = ["abner", "archer", "baker", "baxter", "booker",
                    "breaker", "bridger", "casper", "chester", "colter",
                    "dexter", "faulkner", "fielder", "fisher", "foster",
                    "grover", "gulliver", "homer", "hunter", "lander",
                    "leander", "luther", "miller", "palmer", "rancher",
                    "ranger", "rider", "ryker", "sayer", "thayer", "wheeler",
                    "dead man", "skeleton", "robber"]
SHOP_NAME_SUFFIX = ["cave", "creek", "desert", "farm", "field", "forest",
                    "gulch", "hill", "lake", "mountain", "pass", "peak",
                    "plain", "pond", "ranch", "ravine", "rise" "river",
                    "rock", "stream", "swamp", "valley", "woods"]
# Creates the shopping menu for each town
class Shop():
    def __init__(self, name, inventory, price_mod, group_inventory,
                 group_money, item_prices, position, blit_position, money, resource_path):
        self.yvalue = 40
        self.group_inventory = group_inventory
        self.group_money = group_money
        self.price_mod = price_mod
        self.item_prices = item_prices
        self.inventory = inventory
        self.position = position
        self.blit_position = blit_position
        self.resource_path = resource_path
        self.buy_button_list = []
        self.sell_button_list = []
        # TODO: figure out what these magic numbers mean
        self.x_pos = (-self.position * 40) + 1280

        # Gui stuff #

        # Main Window
        self.shop_surface = Surface((500, 300)).convert()
        # Separator Line
        self.sep_line = Surface((self.shop_surface.get_width(), 10)).convert()
        self.sep_line.fill((0, 0, 0))
        # Inventory container box
        self.inv_container = Surface((self.shop_surface.get_width()-20,
                                             self.shop_surface.get_height()/2 - 35)).convert()
        self.inv_container.fill((255, 255, 255))
        # Font creation
        self.title_font = font.Font(None, 30)
        self.text_font = font.Font(None, 20)

        # Random name generation
        if name == "":
            self.name = capitalize(choice(SHOP_NAME_PREFIX) + "'s " + choice(SHOP_NAME_SUFFIX))
        else:
            self.name = name
        # Random inventory generation
        if self.inventory == {}:
            # TODO: The shop should have random items, not just what the group currently has
            inventory_random = copy(self.group_inventory)

            # Assign a random value between 1,10 to each inventory item
            for key in list(inventory_random.keys()):
                inventory_random[key] = randint(0, 10)

            # Inflate food count
            inventory_random["Food"] *= 20
            self.inventory = inventory_random

        # Random money generation
        if money is None:
            self.money = randint(200, 500)
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
                                                              rect_position=button_pos,
                                                              resource_path=self.resource_path))
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
                                                               rect_position=button_pos,
                                                               resource_path=self.resource_path))
            self.yvalue += 30

        for button in self.sell_button_list:
            self.shop_surface.blit(button.image, button.image_position)

