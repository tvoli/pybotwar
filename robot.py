# Copyright 2009-2014 Lee Harr
#
# This file is part of pybotwar.
#     http://pybotwar.googlecode.com/
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

from util import defaultNonedict

import conf


class Robot(object):
    def __init__(self, name):
        self._p__name = name

        self._p__overtime_count = 0

        self.sensors = defaultNonedict()

        self._p__steps = []

        self._p__err = False
        self._p__finished = False
        self.force(0)
        self.torque(0)
        self._p__fire = '_'
        self._p__ping = 0
        self._p__turret_speed = 0

        self._p__logfile = None
        self._p__log = None

    def initialize(self):
        '''Set up the robot before it starts running.
            Must complete in < 1 second (by default).

        '''

        pass

    def respond(self):
        '''User code goes here. Called 60 times per second (default).

        Must complete in < 0.015 seconds (default).

        Most robots will override the respond() method with their
            own code.

            This default method looks for a series of steps in
            self._steps (could be set up in the initialize() method)

            self._steps is a list of 3-tuples:
                (# of repetitions, function, parameters)

        '''

        self.force(0)
        self.torque(0)

        if self._p__steps:
            nextstep = self._p__steps[0]
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
                self._p__steps.pop(0)

            #self.log(f)
            #self.log(p)
            f(*p)

    def forsteps(self, steps, f, *p):
        '''for use with the default respond() method.

        This will add an entry to self._steps using the passed
            # of ticks, function, and function parameters.

        '''

        self._p__steps.append([steps, f, p])

    def forseconds(self, seconds, f, *p):
        'Converts seconds to steps, then calls forsteps()'

        steps = int(seconds*60.0)
        self.forsteps(steps, f, *p)

    def forever(self, f, *p):
        '''for use with the default respond() method

        Sets a function and parameters to be called non-stop.

        '''

        self.forsteps(0, f, *p)

    def err(self):
        'Put the robot in to an error state.'

        self._p__err = True

    def finished(self):
        'Signal that the robot code is finished and exit.'

        self._p__finished = True

    def force(self, n):
        'Between -100 and 100, percent of max fwd/bk force'
        self._p__force = int(n)

    def torque(self, n):
        'between -100 and 100, percent of max rt/lt torque'
        self._p__torque = int(n)

    def fire(self, dist=None):
        '''Launch a shell from the cannon.

        If dist is None, the shell will continue until it hits a wall,
            a robot, or another bullet.

        If dist is given, the shell will travel that distance and then
            explode.

        '''

        if dist is None:
            self._p__fire = 'X'
        else:
            self._p__fire = int(dist)

    def ping(self):
        'Send out a sonar/radar pulse'
        self._p__ping = 1

    def turret(self, speed):
        '''Set the speed of the turret. Positive values turn the
            turret clockwise, negative values counter-clockwise.

        Values between -100 < speed < 100 are allowed.

        The turret does have inertia, so the speed is a requested
            speed and the turret will take some time to come up
            to the requested speed (or to stop, if speed = 0).
        '''
        
        self._p__turret_speed = int(speed)

    def log(self, *msgs):
        'Write a message to the log file.'

        if self._p__logfile is not None:
            msgstrs = map(str, msgs)
            m = ', '.join(msgstrs)
            msg = '%s: %s' % (self._p__name, m)
            self._p__logfile.write(msg)
            self._p__logfile.write('\n')
            self._p__logfile.flush()

    def start_logging(self):
        self._p__log = True

    def stop_logging(self):
        self._p__log = False

    @property
    def response(self):
        if self._p__err:
            return 'ERROR'

        if self._p__log is None:
            pass
        elif self._log:
            self._p__log = None
            return 'LOG'
        else:
            self._p__log = None
            return 'NOLOG'

        if self._p__finished:
            return 'END'
        else:
            r = 'FORCE:%s|TORQUE:%s|FIRE:%s|PING:%s|TURRET:%s' % (self._p__force,
                                                self._p__torque,
                                                self._p__fire, self._p__ping,
                                                self._p__turret_speed)
            self._p__fire = '_'
            self._p__ping = 0

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
