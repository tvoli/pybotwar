import random
from math import pi

from robot import Robot

class TheRobot(Robot):
    '''Strategy:
        Drive around blindly in several different patterns,
        Shoot stuff.

    This robot shows an unusual style of coding using "generators"
        which makes programs that require sequential steps somewhat
        easier to write,
        
        but strategically this one is a complete mess.
    '''
    
    def initialize(self):
        self.ctrlr = self.controller()

    def respond(self):
        try:
            self.ctrlr.next()
        except StopIteration:
            self.finished()

    def controller(self):
        'Set up a generator to keep state between calls.'

        while True:
            for t in self.setturret(): yield
            for t in self.square(): yield
            for t in self.patrol(): yield
            for t in self.unstick(): yield

    def setturret(self):
        # Turn the turret at a random speed
        speed = random.randrange(40, 80)
        direction = random.choice([-1, 1])
        speed = direction * speed
        self.turret(speed)
        yield

    def square(self):
        # Go in a square
        for side in range(4):
            for t in self.fwdfor(2): yield
            for t in self.rightfor(1.0): yield

    def patrol(self):
        # Go back and forth in a line
        for side in range(2):
            for t in self.fwdfor(3): yield
            for t in self.rightfor(1.9): yield

    def unstick(self):
        # Try to get unstuck if up against a wall
        self.log('test unstick log')
        for t in self.fwdfor(-1): yield
        for t in self.rightfor(-1.5): yield

    def pingfire(self):
        self.ping()
        kind, angle, dist = self.sensors['PING']
        if kind == 'r':
            self.fire()

    def fwdfor(self, s):
        '''Move forward for s seconds, or
            or if s is < 0 move backwards for -s seconds, or
            if s is None, keep going in an already started move.
        '''

        force = 50
        if s < 0:
            s = -s
            force = -force

        ticks = 60 * s

        while ticks > 0:
            self.force(force)
            self.pingfire()
            yield ticks
            ticks -= 1
        else:
            self.force(0)

    def rightfor(self, s):
        '''Turn right for s seconds, or
            if s < 0 turn left for -s seconds, or
            if is is None, keep turning in an already started direction.
        '''

        torque = 100
        if s < 0:
            s = -s
            torque = -torque

        ticks = 60 * s

        while ticks > 0:
            self.torque(torque)
            self.pingfire()
            yield ticks
            ticks -= 1
        else:
            self.torque(0)

