from pygame import image

class ShowFaces():
    """ Displays the faces to select on character creation """
    def __init__(self, file_path, color=(0, 0, 0), x_pos=0, y_pos=100, resource_path=""):
        self.file_path = file_path
        self.color = color
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.resource_path = resource_path
        self.image = image.load(self.resource_path+"Images/Faces/"+self.file_path+".png")
        self.face_rect = self.image.get_rect()

    def update(self):
        self.face_rect.centerx = self.x_pos + self.image.get_width()/2
        self.face_rect.centery = self.y_pos + self.image.get_height()/2

    def create(self):
        self.image = image.load(self.resource_path+"Images/Faces/"+self.file_path+".png")
        self.face_rect = self.image.get_rect()
        self.update()
