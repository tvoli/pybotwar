import random
from robot import Robot


class TheRobot(Robot):
    def initialize(self):
        self.rounds = random.randrange(10000, 20000)

        self._state = 'FORWARD'
        self._fwdfor_ticks = None
        self._rightfor_ticks = None
        self._unstick_freq = 12
        self._unstickfor_ticks = None

    def respond(self):
        t = self.sensors['TICK']

        if t > self.rounds:
            self.finished()

        self.controller()

    def controller(self):
        self.shoot()

        if self._state == 'FORWARD':
            if self._fwdfor_ticks is not None:
                self.fwdfor()
            else:
                self._state = 'RIGHT'
                self.rightfor(0.8)

        elif self._state == 'RIGHT':
            if self._rightfor_ticks is not None:
                self.rightfor()
            else:
                self._unstick_freq -= 1
                if self._unstick_freq < 0:
                    self._state = 'UNSTICK'
                    self.unstickfor(1.6)
                else:
                    self._state = 'FORWARD'
                    self.fwdfor(1)

        elif self._state == 'UNSTICK':
            if self._unstickfor_ticks is not None:
                self._unstick_freq = 12
                self.unstickfor()
            else:
                self._state = 'FORWARD'
                self.fwdfor(1)

    def shoot(self):
        if not random.randrange(30):
            self.fire()

    def fwdfor(self, s=None):
        if s is None:
            t = self._fwdfor_ticks
            t -= 1
        else:
            t = 60 * s

        if t > 0:
            self.force(100)
        else:
            t = None
            self.force(0)

        self._fwdfor_ticks = t
        return t

    def rightfor(self, s=None):
        if s is None:
            t = self._rightfor_ticks
            t -= 1
        else:
            t = 60 * s

        if t > 0:
            self.torque(100)
        else:
            t = None
            self.torque(0)

        self._rightfor_ticks = t
        return t

    def unstickfor(self, s=None):
        if s is None:
            t = self._unstickfor_ticks
            t -= 1
        else:
            self.log('unstick!')
            t = 60 * s

        if t > 0:
            self.force(-60)
            self.torque(-100)
        else:
            t = None
            self.force(0)
            self.torque(0)

        self._unstickfor_ticks = t
        return t
