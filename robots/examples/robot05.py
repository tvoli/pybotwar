from robot import Robot

class TheRobot(Robot):
    def initialize(self):
        self._spin = False

    def respond(self):
        if self._spin:
            self.spin()
        else:
            self.ping()
            self.ping_react(self.sensors['PING'])

    def spin(self, n=None):
        if n is not None:
            self._spin = True
            self._spin_n = n
        else:
            self.force(0)
            self.torque(100)

            self._spin_n -= 1
            if self._spin_n <= 0:
                self._spin = False

    def ping_react(self, ping):
        kind, angle, dist = ping

        if kind == 'w':
            if dist < 8:
                self.spin(30)

            elif dist > 20:
                self.force(100)
                self.torque(0)

            else:
                self.force(60)
                self.torque(0)

        elif kind == 'r':
            self.fire()

            if dist < 5:
                self.force(-10)
            else:
                self.force(10)
                self.torque(30)
