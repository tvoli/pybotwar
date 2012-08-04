from robot import Robot

class TheRobot(Robot):
    '''Strategy:
        Look around and shoot stuff,
        Move if attacked.
    '''
    
    def initialize(self):
        self.health = 100
        self._movefor = 0
        self._moveforce = 0
        self._turnto = 0

    def respond(self):
        self.turnto()
        self.scan_and_fire()

        # Move away if damaged
        health = self.sensors['HEALTH']
        if health != self.health and not self._movefor:
            self._movefor = 45 #ticks
            self._moveforce = 100
            self._turnto += 90
        self.health = health

        if self._movefor:
            self._movefor -= 1
            self.force(self._moveforce)
        else:
            self.force(0)

    def closest_turn(self, a):
        '''return the smallest angle to turn to get to absolute angle a

        should never return turn < -180 or turn > 180

        '''

        target = a % 360
        current = self.sensors['GYRO']
        turn = target - current
        if turn > 180:
            turn -= 360
        elif turn < -180:
            turn += 360
        return turn

    def turnto(self):
        # Turn to angle set in self._turnto

        gain = 2.5
        error = -self.closest_turn(self._turnto)
        torque = -gain * error

        self.torque(torque)

    def scan_and_fire(self):
        # Move the turret around, look for stuff and shoot it

        self.turret(50)
        self.ping()

        kind, angle, dist = self.sensors['PING']
        if kind in 'r':
            if dist > 4:
                # Try not to blast yourself
                self.fire(dist)
            else:
                self.fire()
