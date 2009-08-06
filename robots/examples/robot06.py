from robot import Robot
import random

class TheRobot(Robot):
    def initialize(self):
        self.health = 10
        self._movefor = 0
        self._moveforce = 0

    def respond(self):
        health = self.sensors['HEALTH']
        if health != self.health:
            self.health = health
            self._movefor = 60 #ticks
            self._moveforce = random.choice([-100, 100])

        if self._movefor:
            self._movefor -= 1
            self.force(self._moveforce)
        else:
            self.force(0)
