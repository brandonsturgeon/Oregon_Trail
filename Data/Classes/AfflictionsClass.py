class AfflictionsClass():
    def __init__(self, name, chance_to_infect, infectivity, prime_season, health_change, recovery_time): 
        self.name = name
        self.chance_to_infect = chance_to_infect
        self.infectivity = infectivity
        self.prime_season = prime_season
        self.health_change = health_change
        self.recovery_time = recovery_time

    def __eq__(self, other): 
        if isinstance(other, self.__class__): 
            return self.name == other.name
        else: 
            return False

    def __ne__(self, other): 
        return not __eq__(self, other)
