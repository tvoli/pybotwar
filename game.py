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


import subprocess
from subprocess import PIPE
import time
import random
import os

import logging
logger = logging.getLogger('PybotwarLogger')

import viewselect
view = viewselect.get_view_module()

import world
from world import box2d

import stats
import util
import conf


class Game(object):
    def __init__(self, testmode=False, tournament=None):
        self.testmode = testmode
        self.tournament = tournament

        self.models = {}
        self.procs = {}
        self.results = {}
        self.timeouts = {}
        self.rnd = 0

        self.w = world.World()
        self.cl = world.CL()
        self.w.w.contactListener = self.cl
        self.cl.w = self.w

    def run(self):
        self.load_robots()
        if not self.nrobots:
            self.finish()
            return

        while ((self.testmode and not self.tournament)
                    or len(self.procs) > 1) and not self.w.v.quit:
            if self.rnd > 60 * conf.maxtime:
                break
            self.tick()
        self.finish()

    def robot_module_file(self, robot):
        for d in util.get_robot_dirs():
            fname = '%s.py' % robot
            fpath = os.path.join(d, fname)
            if os.path.exists(fpath):
                return os.path.abspath(fpath)
        return None

    def load_robots(self):
        robots = conf.robots
        for robot in robots:
            robotname = robot
            while robotname in self.w.robots:
                robotname += '_'
            rfile = self.robot_module_file(robot)
            if rfile is None:
                continue
            print 'STARTING', robotname, rfile
            proc = subprocess.Popen([conf.subproc_python,
                                        conf.subproc_main,
                                        robot, rfile, robotname,
                                        str(int(self.testmode))],
                                        stdin=PIPE, stdout=PIPE)
            try:
                result = proc.stdout.readline().strip()
            except IOError:
                result = 'FAIL'

            if result == 'START':
                print 'STARTED'
                model = self.w.makerobot(robot, robotname)
                self.models[robotname] = model
                self.procs[robotname] = proc
                self.timeouts[robotname] = 0
            elif result in ['ERROR', 'END']:
                print 'ERROR!'
            else:
                print 'FAIL', result

        self.nrobots = len(self.models)
        self.t0 = int(time.time())

    def tick(self):
        procs = self.procs
        nrobots = self.nrobots
        timeouts = self.timeouts
        w = self.w
        rnd = self.rnd
        result = ''

        items = self.models.items()
        random.shuffle(items)
        for robotname, model in items:
            if robotname not in self.procs:
                continue

            proc = procs[robotname]

            if model._enable_debug is None:
                pass
            elif model._enable_debug:
                line = 'DEBUG\n'
                proc.stdin.write(line)
                model._enable_debug = None
                continue
            else:
                line = 'NODEBUG\n'
                proc.stdin.write(line)
                model._enable_debug = None
                continue

            health = model.health
            body = model.body
            pos = body.position
            possens = '%s;%s' % (int(pos.x), int(pos.y))
            tur = model.get_turretangle()
            ping = '%s;%s;%s' % (model._pingtype,
                                    model._pingangle,
                                    model._pingdist)
            gyro = model.gyro()
            heat = int(model._cannonheat)
            loading = int(model._cannonreload)
            pinged = int(model._pinged == rnd - 1)
            line = 'TICK:%s|HEALTH:%s|POS:%s|TUR:%s|PING:%s|GYRO:%s|HEAT:%s|LOADING:%s|PINGED:%s\n' % (rnd, health, possens, tur, ping, gyro, heat, loading, pinged)
            #print robotname, line

            if not model.alive:
                model._outlasted = nrobots - len(procs)
                del procs[robotname]
                print 'DEAD robot', robotname, 'health is 0'
                proc.stdin.flush()
                proc.stdin.close()
                proc.stdout.close()
                proc.kill()
                time.sleep(0.1)
                model._commands = {'INACTIVE':'DEAD'}
                continue

            proc.stdin.write(line)
            try:
                result = proc.stdout.readline().strip()
            except IOError:
                print 'ERROR with', robotname
                continue

            if result == 'TIMEOUT':
                timeouts[robotname] += 1
                if timeouts[robotname] > 5:
                    del procs[robotname]
                    print 'REMOVED robot', robotname, 'due to excessive timeouts'
                    proc.stdin.flush()
                    proc.stdin.close()
                    proc.stdout.close()
                    proc.kill()

            elif result == 'END':
                del procs[robotname]
                print 'FINISHED: robot', robotname
                proc.stdin.flush()
                proc.stdin.close()
                proc.stdout.close()
                proc.kill()

            elif result == 'ERROR':
                del procs[robotname]
                print 'ERROR: robot', robotname
                proc.stdin.flush()
                proc.stdin.close()
                proc.stdout.close()
                proc.kill()

            else:
                timeouts[robotname] = 0


            #print 'RR', result, 'RR'
            commands = {}
            try:
                props = result.split('|')
                for prop in props:
                    kind, val = prop.split(':')
                    try:
                        vconv = int(val)
                    except ValueError:
                        pass
                    else:
                        val = vconv
                    commands[kind] = val
            except ValueError:
                continue

            #print 'KV', kind, val
            #print 'R', model, 'R', result, 'R'
            #print 'R', robotname, 'T', '%s -> %.3f' % (model._turretangletarget, model.turretjoint.angle)

            model._commands = commands or {'INACTIVE':result}

            for kind, val in commands.items():
                if kind == 'FORCE':
                    # Make sure force is not more than 100% or less than -100%
                    val = min(val, 100)
                    val = max(-100, val)
                    force = conf.maxforce * val/100.0
                    localforce = box2d.b2Vec2(val, 0)
                    worldforce = body.GetWorldVector(localforce)
                    body.ApplyForce(worldforce, pos, True)
                elif kind == 'TORQUE':
                    # Make sure torque is not more than 100% or less than -100%
                    val = min(val, 100)
                    val = max(-100, val)
                    torque = conf.maxtorque * val/100.0
                    body.ApplyTorque(torque, True)
                elif kind == 'FIRE':
                    if val == '_':
                        # no fire
                        pass
                    elif val == 'X':
                        # non-exploding shell
                        w.makebullet(robotname)
                    else:
                        # exploding shell
                        ticks = int(60 * val / conf.bulletspeed)
                        w.makebullet(robotname, ticks)
                elif kind == 'PING':
                    if val:
                        kind, angle, dist = w.makeping(robotname, rnd)
                        if kind is not None:
                            model._pingtype = kind[0]
                            model._pingangle = angle
                            model._pingdist = int(dist)
                elif kind == 'TURRET':
                    val = min(val, 100)
                    val = max(-100, val)
                    torque = conf.turret_maxMotorSpeed * val/100.0
                    model.turretcontrol(torque)

        w.step()

        if not rnd%60:
            print '%s seconds (%s real)' % (rnd/60, int(time.time())-self.t0)
        self.rnd += 1

    def enable_debug(self):
        items = self.models.items()
        for robotname, model in items:
            model._enable_debug = True

    def disable_debug(self):
        items = self.models.items()
        for robotname, model in items:
            model._enable_debug = False

    def finish(self, update_stats=True):
        print 'FINISHING'
        if hasattr(self, '_FINISHED'):
            print 'ALREADY FINISHED'
            return
        self._FINISHED = True

        models = self.models
        testmode = self.testmode
        nrobots = self.nrobots
        procs = self.procs
        tournament = self.tournament

        alive = [model for model in models.values() if model.alive]
        if not testmode and len(alive)==1:
            model = alive[0]
            print 'WINNER:', model.name
            winner = model
            model._outlasted = nrobots-1
        elif not testmode:
            winner = None
            if self.rnd >= conf.maxtime*60:
                print 'Battle stopped after maximum time:', conf.maxtime, 'seconds.'
            else:
                print 'Battle stopped after', int(self.rnd/60), 'seconds.'
            print 'STILL ALIVE:'
            for model in alive:
                print '   ', model.name
        else:
            print 'Test mode ended'
            winner = None

        for robotname, model in models.items():
            print robotname, 'caused', model._damage_caused, 'damage'
            if robotname in procs:
                line = 'FINISH\n'
                proc = procs[robotname]
                proc.stdin.write(line)
                proc.stdin.flush()
                proc.stdin.close()
                proc.stdout.close()
                del procs[robotname]

            if winner is None and model.alive:
                model._outlasted = nrobots - len(alive)

            if model == winner:
                win = 1
            else:
                win = 0

            if update_stats and not testmode:
                stats.update(model.kind, win, nrobots-1, model._outlasted,
                                model._damage_caused, model._kills)

            if update_stats and tournament is not None:
                stats.tournament_update(tournament,
                                            model.kind, model.name, win,
                                            nrobots-1, model._outlasted,
                                            model._damage_caused,
                                            model._kills)
