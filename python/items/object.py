class Object:

    name: str = None
    take: bool = None
    mass: int = None
    damage: int = None

    def __init__(self, name, take, mass, damage):
        self.name = name
        self.take = take
        self.mass = mass
        self.damage = damage

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_mass(self):
        return self.mass

    def get_damage(self):
        return self.damage

    def get_take(self):
        return self.take