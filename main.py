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


import time

try:
    import conf
except ImportError:
    import util
    util.makeconf()

    import stats
    stats.dbcheck()

    raise SystemExit


import util
try:
    util.setup_conf()
except ImportError:
    print 'Trying to use Qt settings per conf.py'
    print 'but unable to import PyQt4 modules.'
    print
    print 'Check PyQt4 installation, or change conf.py'
    print 'to have use_qt_settings = False'

    raise SystemExit


import viewselect

def check_pybox2d_version():
    pybox2d_error = False
    try:
        import pkg_resources
        pkg_resources.require('Box2D==%s'%conf.pybox2d_version)
    except ImportError:
        pass
    except pkg_resources.VersionConflict:
        pass

    try:
        import Box2D
    except ImportError:
        pybox2d_error = True
    else:
        if not Box2D.__version__ == conf.pybox2d_version:
            pybox2d_error = True

    if pybox2d_error:
        print 'Unable to import PyBox2D'
        print 'requires version', conf.pybox2d_version
        print
        print 'If running with Qt interface, try clearing Qt settings with:'
        print 'python main.py -S'
        raise SystemExit

def setup_logging(level='info'):
    import logging
    import logging.handlers
    logger = logging.getLogger('PybotwarLogger')
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(
              'appdebug.log', maxBytes=1000000, backupCount=3)
    logger.addHandler(handler)

def run_supertournament(nbattles):
    robots = conf.robots
    nrobots = len(robots)
    import datetime
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    from itertools import combinations
    combos = []
    for n in range(2, nrobots+1):
        combos.extend(combinations(robots, n))
    import sys
    py = sys.executable
    main = os.path.abspath(__file__)
    cmd = '%s %s -t "%s" -g -n %s --robots %s'
    for combo in combos:
        rstr = ' '.join(combo)
        cmdstr = cmd % (py, main, dt, nbattles, rstr)
        print cmdstr
        os.system(cmdstr)

if __name__ == '__main__':
    import sys
    import os

    os.chdir(os.path.split(os.path.abspath(__file__))[0])

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-T', '--testmode', dest='testmode',
                    action='store_true', default=False,
                    help='run in test mode')
    parser.add_argument('-t', '--tournament', dest='tournament',
                    nargs='?', const=True, default=False,
                    help='run a tournament')
    parser.add_argument('-n', '--battles', dest='nbattles',
                    action='store', type=int, default=5,
                    help='number of battles in tournament')
    parser.add_argument('--supertournament', dest='supertournament',
                    action='store_true', default=False,
                    help='run a supertournament')
    parser.add_argument('-g', '--no-graphics', dest='nographics',
                    action='store_true', default=False,
                    help='non graphics mode')
    parser.add_argument('-Q', '--pyqt-graphics', dest='pyqtgraphics',
                    action='store_true', default=False,
                    help='enable PyQt interface')
    parser.add_argument('-P', '--pygsear-graphics', dest='pygseargraphics',
                    action='store_true', default=False,
                    help='enable Pygsear interface')
    parser.add_argument('-D', '--upgrade-db', dest='upgrade_db',
                    action='store_true', default=False,
                    help='upgrade database (WARNING! Deletes database!)')
    parser.add_argument('-S', '--reset-qt-settings', dest='qtreset',
                    action='store_true', default=False,
                    help='reset Qt settings')
    parser.add_argument('-B', '--app-debug', dest='appdebug',
                    action='store_true', default=False,
                    help='enable app debug log')
    parser.add_argument('--robots', dest='robots', nargs='+',
                    metavar='ROBOT',
                    help='list of robots to load')

    options = parser.parse_args()

    testmode = options.testmode
    tournament = options.tournament
    nbattles = options.nbattles
    supertournament = options.supertournament
    nographics = options.nographics
    pyqtgraphics = options.pyqtgraphics
    pygseargraphics = options.pygseargraphics
    upgrade_db = options.upgrade_db
    qtreset = options.qtreset
    appdebug = options.appdebug
    robots = options.robots

    if robots is not None:
        conf.robots = robots

    gmodes = nographics + pyqtgraphics + pygseargraphics

    if appdebug:
        setup_logging()

    if gmodes > 1:
        print 'must select ONE of -g, -Q, or -P'
        import sys
        sys.exit(0)

    if tournament and supertournament:
        print 'must select one of --tournament or --supertournament'
        import sys
        sys.exit(0)
    elif supertournament:
        run_supertournament(nbattles)
        import sys
        sys.exit(0)

    elif nographics:
        viewselect.select_view_module('none')
    elif pyqtgraphics:
        viewselect.select_view_module('pyqt')
    elif pygseargraphics:
        viewselect.select_view_module('pygame')
    else:
        # default view type is PyQt
        pyqtgraphics = True
        viewselect.select_view_module('pyqt')

view = viewselect.get_view_module()

from game import Game

import world

import stats


def dbcheck():
    if not stats.dbcheck():
        print 'Run pytbotwar with -D switch to upgrade database.'
        print 'WARNING: This will delete your current database!'
        import sys
        sys.exit(0)


def reset_qt_settings():
    from PyQt4 import QtCore
    QtCore.QCoreApplication.setOrganizationName('pybotwar.googlecode.com')
    QtCore.QCoreApplication.setOrganizationDomain('pybotwar.googlecode.com')
    QtCore.QCoreApplication.setApplicationName('pybotwar')
    settings = QtCore.QSettings()
    settings.clear()
    print 'Qt settings cleared.'
    import sys
    sys.exit(0)


def runmain():
    if qtreset:
        reset_qt_settings()
        
    check_pybox2d_version()

    if upgrade_db:
        print 'Upgrading Database'
        stats.dbremove()
        stats.dbopen()
        return

    dbcheck()

    stats.dbopen()

    global tournament
    global nbattles
    if not pyqtgraphics and not tournament:
        tournament = True
        nbattles = 1

    if tournament and pyqtgraphics:
        print 'When using PyQt interface, run tournaments from GUI.'

    elif tournament:
        if tournament is True:
            import datetime
            dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            dt = tournament
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
            print line[1], ':', line[4], 'wins', ':', line[6], 'outlasted', ':', line[7], 'dmg caused', ':', line[8], 'kills'

    elif pyqtgraphics:
        import qt4view
        qt4view.run(testmode)

    else:
        game = Game(testmode)
        game.run()

    stats.dbclose()

    if not tournament:
        stats.dbopen()
        stats.top10()


    # Clean up log directory if not in test mode
    logdir = os.path.join(conf.base_dir, conf.logdir)

    if not testmode and os.path.exists(logdir):
        for f in os.listdir(logdir):
            fpath = os.path.join(logdir, f)
            try:
                os.remove(fpath)
            except OSError:
                pass


if __name__ == '__main__':
    try:
        runmain()
    except KeyboardInterrupt:
        pass

