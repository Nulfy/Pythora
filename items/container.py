from items.object import Object


class Container(Object):

    contents: list[Object] = []
    max_mass: int = None

    def __init__(self, name, take, mass, damage, max_mass, contents):
        super().__init__(name, take, mass, damage)
        self.max_mass = max_mass
        self.contents = contents

    def get_damage(self):
        n = super().get_damage()
        for o in self.contents:
            n += o.get_mass()
        return n

    def get_mass(self):
        n = super().get_mass()
        for o in self.contents:
            n += o.get_mass()
        return n

    def get_self_mass(self):
        real_mass = self.get_mass() - super().get_mass()
        return real_mass if real_mass > 0 else 0

    def get_contents(self):
        return self.contents

    def get_max_mass(self):
        return self.max_mass
