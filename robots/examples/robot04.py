from robot import Robot

class TheRobot(Robot):
    '''Strategy:
        Get in to a corner,
        Look around and shoot stuff,
        Try to remember where stuff was, so you can shoot it real good.
    '''
    
    def initialize(self):
        # Try to get in to a corner
        self.forseconds(5, self.istep, self.force, 50)
        self.forseconds(0.9, self.istep, self.force, -10)
        self.forseconds(0.7, self.istep, self.torque, 100)
        self.forseconds(6, self.istep, self.force, 50)

        # Then look around and shoot stuff
        self.forever(self.scanfire)


        self._turret_target_angle = 180
        self._turretdirection = 1
        self._pingfoundrobot = None

    def istep(self, func, val):
        '''Utility function used by initialize.

        Keep the turret moving to its target angle with turret_track()

        Then, call the requested function with the given value.

        These are set up in the forseconds() calls in initialize.
        '''

        self.turret_track()
        func(val)

    def closest_turn(self, from_angle, to_angle):
        '''return the smallest angle to turn to get from from_angle
            to to_angle.

        should never return turn < -180 or turn > 180

        '''

        target = to_angle % 360
        current = from_angle % 360
        turn = target - current
        if turn > 180:
            turn -= 360
        elif turn < -180:
            turn += 360
        return turn

    def turret_to(self, angle):
        '''Set turret target angle to angle.
        '''
        self._turret_target_angle = angle

    def turret_track(self):
        '''Keep the turret moving towards its target angle.
        Should be called repeatedly (probably every tick).
        '''
        current = self.sensors['TUR']
        target = self._turret_target_angle
        error = -self.closest_turn(current, target)
        gain = 5.0
        self.turret(-gain * error)

    def scanfire(self):
        self.turret_track()
        self.ping()

        sensors = self.sensors
        kind, angle, dist = sensors['PING']
        tur = sensors['TUR']

        if self._pingfoundrobot is not None:
            # has pinged a robot previously
            if angle == self._pingfoundrobot:
                # This is where we saw the robot previously
                if kind == 'r':
                    # Something is still there, so shoot it
                    self.fire()
                elif kind == 'w':
                    # No robot there now
                    self._pingfoundrobot = None
            elif kind == 'r':
                # This is not where we saw something before,
                #   but there is a robot at this location also
                self.fire()
                self._pingfoundrobot = angle
                self.turret_to(angle)
            else:
                # No robot where we just pinged. So go back to
                #   where we saw a robot before.
                self.turret_to(self._pingfoundrobot)

        elif kind == 'r':
            # pinged a robot
            # shoot it
            self.fire()
            # keep the turret here, and see if we can get it again
            self._pingfoundrobot = angle
            self.turret_to(angle)

        else:
            # No robot pinged, and have not seen a robot yet
            #   so move the turret and keep looking
            if self._turretdirection == 1:
                if tur < 180:
                    self.turret_to(180)
                else:
                    self._turretdirection = 0
            elif self._turretdirection == 0:
                if tur > 90:
                    self.turret_to(90)
                else:
                    self._turretdirection = 1
