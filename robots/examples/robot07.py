from robot import Robot

from math import copysign

class TheRobot(Robot):
    '''Strategy:
        Stay near the middle of the field,
        Move if being attacked.
    '''
    
    def initialize(self):
        self.health = 100
        self._flee = 15
        self._goto = 0
        self._moveto_choices = [7, 7, -7, -7]
        self._turnto_choices = [0, 90, 180, -90]

    def respond(self):
        self.scan_and_fire()

        # Move away if damaged
        health = self.sensors['HEALTH']
        if health != self.health and not self._flee:
            self._flee = 30
            self._goto += 1
            self._goto = self._goto % 4

        self.health = health

        self.turnto()
        self.moveto()

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
        a = self._turnto_choices[self._goto]
        err = -self.closest_turn(a)
        if self._flee:
            gain = 50
        else:
            gain = 1.5
        self.torque(-gain * err)

    def moveto(self):
        # Move to the position set in self._moveto

        moveto = self._moveto_choices[self._goto%4]

        pos = self.sensors['POS']

        if self._flee:
            maxspeed = 100
            gain = -16
            self._flee -= 1
        else:
            maxspeed = 50
            gain = 6

        coord = pos[self._goto%2]
        sign = [-1, -1, 1, 1][self._goto%4]
        error = coord - moveto
        force = max(min(maxspeed, sign * gain * error), -maxspeed)
        self.force(force)

    def scan_and_fire(self):
        # Move the turret around, look for stuff and shoot it

        self.turret(-75)
        self.ping()

        kind, angle, dist = self.sensors['PING']
        if kind in 'r':
            if dist > 4:
                # Try not to blast yourself
                self.fire(dist)
            else:
                self.fire()
