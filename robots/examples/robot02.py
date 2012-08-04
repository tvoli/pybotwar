from robot import Robot

class TheRobot(Robot):
    '''Strategy:
        Drive around the edge of the arena,
        Shoot whatever gets in the way.
    '''

    def respond(self):
        self.ping()
        self.turret_forward()
        self.ping_react()

    def turret_forward(self):
        'keep the turret pointed straight ahead.'

        tur = self.sensors['TUR']
        if tur:
            gain = 10
            self.turret(-gain * tur)

    def ping_react(self):
        kind, angle, dist = self.sensors['PING']

        if kind == 'w':
            # Pinged a wall

            if dist < 2:
                self.force(-30)
                self.torque(90)
            else:
                self.force(60)
                self.torque(0)

        elif kind in 'r':
            # Pinged a robot or a bullet

            self.fire()

            if dist < 5:
                self.force(-10)
            else:
                self.force(10)
                self.torque(0)
