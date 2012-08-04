from robot import Robot

class TheRobot(Robot):
    '''Strategy:
        Drive around real fast,
        Don't run in to anything,
        Shoot stuff that gets in the way.
    '''

    def initialize(self):
        self._spinning = False

    def respond(self):
        if self._spinning:
            self.spin()

        self.ping()
        self.ping_react()

        self.turret_forward()

    def turret_forward(self):
        'keep the turret pointed straight ahead.'

        tur = self.sensors['TUR']
        if tur:
            gain = 10
            self.turret(-gain * tur)

    def spin(self, n=None):
        # Spin for n ticks, then stop

        self.force(0)
        self.torque(100)

        if n is not None:
            self._spinning = True
            self._spin_n = n
        else:
            self._spin_n -= 1
            if self._spin_n <= 0:
                self._spinning = False

    def ping_react(self):
        kind, angle, dist = self.sensors['PING']

        if kind == 'w' and not self._spinning:
            # Pinged a wall
            if dist < 8:
                self.spin(30)

            elif dist > 20:
                self.force(100)
                self.torque(0)

            else:
                self.force(60)
                self.torque(0)

        elif kind == 'r':
            # Pinged a robot
            self.fire()

            if dist < 5:
                self.force(-10)
            else:
                self.force(10)
                self.torque(10)
