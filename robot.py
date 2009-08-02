# Copyright 2009 Lee Harr
#
# This file is part of pybotwar.
#
# Pybotwar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pybotwar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pybotwar.  If not, see <http://www.gnu.org/licenses/>.


import os
import random
from time import sleep


class Robot(object):
    def __init__(self, name):
        self.name = name

        self._overtime_count = 0

        self._steps = []

        self._err = False
        self._finished = False
        self.force(0)
        self.torque(0)
        self._fire = 0
        self._ping = 0
        self._turretangle = 0

        if os.path.exists('log'):
            self.logfile = open('log', 'a')
        else:
            self.logfile = None

        self.initialize()

    def initialize(self):
        pass

    def respond(self):
        self.force(0)
        self.torque(0)

        if self._steps:
            nextstep = self._steps[0]
            steps = nextstep[0]
            f = nextstep[1]
            p = nextstep[2]

            if steps == 0:
                # loop forever
                pass
            elif steps > 1:
                nextstep[0] -= 1
            else:
                # 1 right now. Don't decrease to zero. Remove this one.
                self._steps.pop(0)

            #self.log(f)
            #self.log(p)
            f(*p)

    def forsteps(self, steps, f, *p):
        self._steps.append([steps, f, p])

    def forseconds(self, seconds, f, *p):
        steps = int(seconds*60.0)
        self.forsteps(steps, f, *p)

    def forever(self, f, *p):
        self.forsteps(0, f, *p)

    def err(self):
        self._err = True

    def finished(self):
        self._finished = True

    def force(self, n):
        'Between -100 and 100, percent of max fwd/bk force'
        self._force = n

    def torque(self, n):
        'between -100 and 100, percent of max rt/lt torque'
        self._torque = n

    def fire(self):
        self._fire = 1

    def ping(self):
        'Send out a sonar/radar pulse'
        self._ping = 1

    def turret(self, angle):
        self._turretangle = angle

    def log(self, *msgs):
        if self.logfile is not None:
            msgstrs = map(str, msgs)
            m = ', '.join(msgstrs)
            msg = '%s: %s' % (self.name, m)
            self.logfile.write(msg)
            self.logfile.write('\n')
            self.logfile.flush()

    @property
    def response(self):
        if self._err:
            return 'ERROR'
        if self._finished:
            return 'END'
        else:
            r = 'FORCE:%s|TORQUE:%s|FIRE:%s|PING:%s|TURRET:%s' % (self._force,
                                                    self._torque,
                                                    self._fire, self._ping,
                                                    self._turretangle)
            self._fire = 0
            self._ping = 0

            return r

    def test005(self):
        sleep(0.005)

    def test01(self):
        sleep(0.01)

    def test01a(self):
        sleep(0.01001)

    def test1(self):
        sleep(0.1)

    def test2(self):
        sleep(0.2)

    def testrand(self):
        t = random.randrange(1, 10) / 1000.
        sleep(t)
