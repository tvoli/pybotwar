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
from threading import Thread
from time import sleep

_overtime_count = 0

def loop(r, i):
    data = i.split('|')
    sensors = {}
    for d in data:
        k, v = d.split(':')

        if ';' in v:
            # Some sensors send multiple values, separated by semicolon
            v = v.split(';')
            vconv = []
            for vv in v:
                try:
                    vvconv = int(vv)
                except:
                    vvconv = vv

                vconv.append(vvconv)

        else:
            try:
                vconv = int(v)
            except:
                vconv = v

        sensors[k] = vconv

    timeout = 0.015

    user_thread = Thread(target=get_response, args=(r, sensors))
    response = None
    user_thread.start()

    user_thread.join(timeout)
    if user_thread.isAlive():
        global _overtime_count
        _overtime_count += 1
        response = 'TIMEOUT'
        if _overtime_count > 10:
            os.kill(os.getpid(), 9)
    else:
        _overtime_count = 0

    return response or r.response

def get_response(r, sensors):
    try:
        r.sensors = sensors
        r.respond()
    except:
        r.err()
        raise

def communicate(r):
    while True:
        line = sys.stdin.readline().strip()
        if line == 'FINISH':
            break

        o = loop(r, line)
        if o is not None:
            oline = '%s\n' % (str(o))
            sys.stdout.write(oline)
            sys.stdout.flush()
        else:
            oline = 'END\n'
            sys.stdout.write(oline)
            sys.stdout.flush()
            break


if __name__ == '__main__':
    import sys
    sys.path.append('robots')
    sys.path.append('robots/examples')

    if len(sys.argv) != 3:
        raise SystemExit
    else:
        modname = sys.argv[1]
        robotname = sys.argv[2]

    try:
        mod = __import__(modname)
    except:
        # robot failed to load properly
        oline = 'ERROR\n'
        sys.stdout.write(oline)
        sys.stdout.flush()
    else:
        r = mod.TheRobot(robotname)
        oline = 'START\n'
        sys.stdout.write(oline)
        sys.stdout.flush()
        communicate(r)
