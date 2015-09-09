class Passenger():
    """ The Passenger Class """
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
