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


import subprocess
from subprocess import PIPE
import time

try:
    import conf
except ImportError:
    import util
    util.makeconf()

    import stats
    stats.dbcheck()

    raise SystemExit

import world
from world import box2d

import stats
stats.dbcheck()

import view


class Game(object):
    def __init__(self, testmode=False, tournament=None):
        self.testmode = testmode
        self.tournament = tournament

        self.models = {}
        self.procs = {}
        self.results = {}
        self.timeouts = {}

        self.w = world.World()
        self.cl = world.CL()
        self.w.w.SetContactListener(self.cl)
        self.cl.w = self.w

    def run(self):
        self.load_robots()
        self.t0 = int(time.time())
        self.rnd = 0
        while ((self.testmode and not self.tournament)
                    or len(self.procs) > 1) and not self.w.v.quit:
            if self.rnd > 60 * conf.maxtime:
                break
            self.tick()
        self.finish()

    def load_robots(self):
        robots = conf.robots
        for robot in robots:
            robotname = robot
            while robotname in self.w.robots:
                robotname += '_'
            print 'STARTING', robotname,
            proc = subprocess.Popen([conf.subproc_python,
                                        conf.subproc_main,
                                        robot, robotname,
                                        str(int(self.testmode))],
                                        stdin=PIPE, stdout=PIPE)
            result = proc.stdout.readline().strip()

            if result in ['ERROR', 'END']:
                print 'ERROR!'
            else:
                print 'STARTED'
                model = self.w.makerobot(robotname)
                self.models[robotname] = model
                self.procs[robotname] = proc
                self.timeouts[robotname] = 0

        self.nrobots = len(self.models)

    def tick(self):
        procs = self.procs
        nrobots = self.nrobots
        timeouts = self.timeouts
        w = self.w
        rnd = self.rnd
        result = ''

        for robotname, model in self.models.items():
            if robotname not in self.procs:
                continue

            health = model.health
            body = model.body
            pos = body.position
            possens = '%s;%s' % (int(pos.x*10), int(pos.y*10))
            tur = model.get_turretangle()
            ping = '%s;%s;%s' % (model._pingtype,
                                    model._pingangle,
                                    model._pingdist)
            gyro = model.gyro()
            heat = int(model._cannonheat)
            loading = int(model._cannonreload)
            line = 'TICK:%s|HEALTH:%s|POS:%s|TUR:%s|PING:%s|GYRO:%s|HEAT:%s|LOADING:%s\n' % (rnd, health, possens, tur, ping, gyro, heat, loading)
            #print robotname, line

            proc = procs[robotname]
            proc.stdin.write(line)
            result = proc.stdout.readline().strip()

            if not model.alive:
                model._kills = nrobots - len(procs)
                del procs[robotname]
                print 'DEAD robot', robotname, 'health is 0'
                proc.stdin.flush()
                proc.stdin.close()
                proc.stdout.close()
                proc.kill()
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
            #print 'R', robot, 'R', result, 'R'
            #print 'R', robotname, 'T', '%s -> %.3f' % (model._turretangletarget, model.turretjoint.GetJointAngle())

            for kind, val in commands.items():
                if kind == 'FORCE':
                    # Make sure force is not more than 100% or less than -100%
                    val = min(val, 100)
                    val = max(-100, val)
                    force = conf.maxforce * val/100.0
                    localforce = box2d.b2Vec2(val, 0)
                    worldforce = body.GetWorldVector(localforce)
                    body.ApplyForce(worldforce, pos)
                elif kind == 'TORQUE':
                    # Make sure torque is not more than 100% or less than -100%
                    val = min(val, 100)
                    val = max(-100, val)
                    torque = conf.maxtorque * val/100.0
                    body.ApplyTorque(torque)
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
                        kind, angle, dist = w.makeping(robotname)
                        if kind is not None:
                            model._pingtype = kind[0]
                            model._pingangle = angle
                            model._pingdist = int(dist)
                elif kind == 'TURRET':
                    model.set_turretangle(val)


        w.step()

        if not rnd%60:
            print '%s seconds (%s real)' % (rnd/60, int(time.time())-self.t0)
        self.rnd += 1


    def finish(self):
        print 'FINISHING'

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
            model._kills = nrobots-1
        else:
            winner = None

        for robotname, model in models.items():
            if robotname in procs:
                line = 'FINISH\n'
                proc = procs[robotname]
                proc.stdin.write(line)
                proc.stdin.flush()
                proc.stdin.close()
                proc.stdout.close()

            if winner is None and model.alive:
                model._kills = nrobots - len(alive)

            if model == winner:
                win = 1
            else:
                win = 0

            if not testmode:
                stats.update(model.name, win, nrobots-1, model._kills)

            if tournament is not None:
                stats.tournament_update(tournament, model.name, win,
                                                nrobots-1, model._kills)



if __name__ == '__main__':
    import sys
    import os

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-T", "--testmode", dest="testmode",
                    action="store_true", default=False,
                    help="run in test mode")
    parser.add_option("-t", "--tournament", dest="tournament",
                    action="store_true", default=False,
                    help="run a tournament")
    parser.add_option("-n", "--battles", dest="nbattles",
                    action="store", type='int', default=5,
                    help="number of battles in tournament")
    parser.add_option("-g", "--no-graphics", dest="nographics",
                    action="store_true", default=False,
                    help="non graphics mode")
    parser.add_option("-Q", "--pyqt-graphics", dest="pyqtgraphics",
                    action="store_true", default=False,
                    help="enable PyQt interface")

    (options, args) = parser.parse_args()

    testmode = options.testmode
    tournament = options.tournament
    nbattles = options.nbattles
    nographics = options.nographics
    pyqtgraphics = options.pyqtgraphics

    if testmode:
        if not os.path.exists(conf.logdir):
            print 'Log directory does not exist:', conf.logdir
            print 'test mode disabled'
            testmode = False

    if nographics:
        import noview
        world.view = noview

    if pyqtgraphics:
        import qt4view
        world.view = qt4view

    stats.dbopen()

    if tournament:
        import datetime
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print 'Beginning tournament with %s battles.' % nbattles
        for battle in range(nbattles):
            print 'Battle', battle+1
            game = Game(testmode, dt)
            game.run()
            world.Robot.nrobots = 0
            view.Robot.nrobots = 0

        results = stats.tournament_results(dt)
        print;print;print;
        print 'Tournament Results'
        print nbattles, 'battles between', len(results), 'robots'
        print
        for line in results:
            print line[1], ':', line[4], 'wins', line[6], 'robots defeated'

    else:
        game = Game(testmode)
        game.run()

    stats.dbclose()

    # Clean up log directory if not in test mode
    if not testmode and os.path.exists(conf.logdir):
        for f in os.listdir(conf.logdir):
            fpath = os.path.join(conf.logdir, f)
            os.remove(fpath)
