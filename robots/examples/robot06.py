from robot import Robot

class TheRobot(Robot):
    def initialize(self):
        self.health = 100
        self._movefor = 0
        self._moveforce = 0
        self._turnto = 0

    def respond(self):
        self.turnto()

        health = self.sensors['HEALTH']
        if health != self.health:
            self.health = health
            self._movefor = 60 #ticks
            self._moveforce = 100
            self._turnto += 90

        if self._movefor:
            self._movefor -= 1
            self.force(self._moveforce)
        else:
            self.force(0)

    def turnto(self):
        gyro = self.sensors['GYRO']

        gain = 0.5
        error = gyro - self._turnto
        torque = -gain * error

        self.torque(torque)
