from robot import Robot

class TheRobot(Robot):
    '''Strategy:
        Circle around the center,
        Home in on any found robot and shoot it.
    '''
    
    def initialize(self):
        self._foundrobotangle = None

    def respond(self):
        self.turret_forward()
        self.ping()
        kind, angle, distance = self.sensors['PING']
        gyro = self.sensors['GYRO']

        if self._foundrobotangle is not None:
            if gyro == self._foundrobotangle and kind != 'r':
                self._foundrobotangle = None
            else:
                self.turnby(self._foundrobotangle - gyro)
            
        if kind == 'r':
            self.fire(distance+2) # Add a bit since always moving back
            self._foundrobotangle = gyro
            self.force(20)
            self.turnby(-10)
        elif self._foundrobotangle is not None:
            self.turnby()
        elif kind == 'w' and distance==35:
            # Stuck against the wall.
            self.force(100)
            self.turnby(100)
        elif kind == 'w' and distance<10:
            self.force(-45)
            self.turnby(15)
        elif kind == 'w':
            self.force(-30)
            self.turnby(20)
        else:
            self.turnby()

        self.log(self._foundrobotangle, gyro, kind)

    def turret_forward(self):
        'keep the turret pointed straight ahead.'

        tur = self.sensors['TUR']
        if tur:
            gain = 10
            self.turret(-gain * tur)

    def turnedby(self, before, now):
        '''given 2 angles return the angle between.

        Meant to be called rapidly (like every tick), so should
            never return an angle > 180 or < -180

        '''

        angle = now - before
        if angle > 180:
            angle = 360 - angle
        elif angle < -180:
            angle = -(360 + angle)
        return angle

    def turnby(self, a=None):
        'turn by the angle given, or if a is None, continue turning.'
        if a is not None:
            self.turntarget = a
            self.turnedsofar = 0
            self.current_angle = self.sensors['GYRO']
            angle_error = a
        elif self.turntarget is None:
            self.torque(0)
            return True
        else:
            previous_angle = self.current_angle
            self.current_angle = self.sensors['GYRO']
            turned = self.turnedby(previous_angle, self.current_angle)
            self.turnedsofar += turned
            angle_error = self.turnedsofar - self.turntarget

        gain = 1.5
        torque = -gain * angle_error
        self.torque(torque)

        if angle_error == 0:
            self.turntarget = None
            return True
        else:
            return False
