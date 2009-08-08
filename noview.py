class Fake(object):
    def setpos(self, pos):
        pass

    def set_rotation(self, ang):
        pass

    def kill(self):
        pass

    def step(self, n=None):
        pass


class Robot(Fake):
    def __init__(self, pos, ang):
        pass


class Turret(Fake):
    def __init__(self, pos, ang):
        pass

class RobotInfo(Fake):
    def __init__(self, n, name):
        self.health = Fake()


class Bullet(Fake):
    def __init__(self, pos):
        pass


class Wall(Fake):
    def __init__(self, pos, size):
        pass


class Sprites(Fake):
    def add(self, sprite, level=None):
        pass

class Arena(Fake):
    def __init__(self):
        self.sprites = Sprites()
        self.quit = False

    def step(self):
        pass
