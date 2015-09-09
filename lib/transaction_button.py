from pygame import transform, image, Rect

class TransactionButton():
    """ Used to create the Buy and Sell buttons in the Shop() class """
    def __init__(self, transaction, item, image_position, rect_position, resource_path):
        self.transaction = transaction
        self.item = item
        self.image_position = image_position
        self.rect_position = rect_position
        self.filename = "buybutton.png"
        if self.transaction == "sell":
            self.filename = "sellbutton.png"
        self.image = transform.scale(image.load(resource_path+"Images/"+self.filename), (25, 25))
        self.image_rect = Rect(self.rect_position, self.image.get_size())
