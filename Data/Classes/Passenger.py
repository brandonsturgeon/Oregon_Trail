class Passenger(): 
    
    
    def __init__(self, name, age, gender, health, afflictions,picture):
        self.name = name
        self.age = age
        self.gender = gender
        self.health = health
        self.afflictions = afflictions
        self.picture = picture

    def __str__(self): 
        return self.name
