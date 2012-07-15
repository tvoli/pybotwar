# Copyright 2009-2012 Lee Harr
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

from PyQt4 import QtCore, QtGui, uic

import stats
import conf

uidir = 'data/ui'


ss = dict(
    # Robot subprocess
    subprocess = dict(subproc_python = 's+',
                        subproc_main = 's+',
                        init_timeout = 'f',
                        tick_timeout = 'f',
    ),

    # Files
    files = dict(base_dir = 's+',
                    more_robot_dirs = 'sa+',
                    logdir = 's+',
                    template = 's+X',
                    lineups = 's+',
                    dbfile = 's+',
    ),

    # Physics
    physics = dict(pybox2d_version = 's+X',

                ## robot
                maxforce = 'f+',
                maxtorque = 'f+',
                robot_density = 'f+',
                robot_linearDamping = 'f+',
                robot_angularDamping = 'f+',
                robot_friction = 'f+',
                robot_restitution = 'f+',

                ## cannon
                cannon_reload_ticks = 'i+',
                cannon_maxheat = 'i+',
                cannon_heating_per_shot = 'i+',
                cannon_cooling_per_tick = 'f+',
                overheat_fire_reload_penalty = 'i',
                unloaded_fire_reload_penalty = 'i',

                ## turret
                turret_maxMotorTorque = 'f+',
                turret_maxMotorSpeed = 'f+',
                turret_gain = 'f+',

                ## bullet
                bulletspeed = 'f+',
                bullet_density = 'f+',
    ),

    # Rules
    rules = dict(
                ## game end
                maxtime = 'i',
                maxhealth = 'i',
                remove_dead_robots = 'b+',

                ## damage
                direct_hit_damage = 'i',
                explosion_radii = 'fa+3',
                explosion_damage = 'ia+3',
                collision_damage_start = 'i',
                collision_damage_factor = 'f',

                ## cannon
                cannon_reload_ticks = 'i',
                cannon_maxheat = 'i',
                cannon_heating_per_shot = 'i',
                cannon_cooling_per_tick = 'f',
                overheat_fire_reload_penalty = 'i',
                unloaded_fire_reload_penalty = 'i',
    ),
)



def setup_qt_settings():
    QtCore.QCoreApplication.setOrganizationName('pybotwar.googlecode.com')
    QtCore.QCoreApplication.setOrganizationDomain('pybotwar.googlecode.com')
    QtCore.QCoreApplication.setApplicationName('pybotwar')
    settings = QtCore.QSettings()
    settings.sync()
    setup_sections()

def setup_sections():
    for section, items in ss.items():
        setup_section(section, items)

def setup_section(section, items):
    '''read settings from QSettings and store in conf module'''

    for name, kind in items.items():
        setup_one(section, name, kind)

def read_value(setting, kind):
    ok = True
    if kind.startswith('s'):
        v = str(setting.toString())
    elif kind.startswith('i'):
        v, ok = setting.toInt()
    elif kind.startswith('f'):
        v, ok = setting.toFloat()
    elif kind.startswith('b'):
        v = setting.toBool()
    #print 'R', name, kind, v, ok
    return v, ok

def read_array(k, name, kind):
    'read an array-type from QSettings and return it as a list'

    settings = QtCore.QSettings()

    ok = True
    v = []
    for n in range(settings.beginReadArray(k)):
        settings.setArrayIndex(n)
        setting = settings.value(name)
        vi, ok = read_value(setting, kind)
        if not ok:
            #print '++', name, n, vi
            break
        v.append(vi)
    settings.endArray()

    ns = kind[-1]
    if ns.isdigit():
        n = int(ns)
        v = v[:n]

    return v

def setup_one(section, name, kind):
    settings = QtCore.QSettings()

    k = '%s/%s' % (section, name)

    ok = True
    if 'a' in kind:
        v = read_array(k, name, kind)
    else:
        setting = settings.value(k)
        v, ok = read_value(setting, kind)

    if '+' in kind and not v:
        ok = False

    if not ok:
        #print '!!', name,
        v = getattr(conf, name)
        #print 'loading', v
        if 'a' not in kind:
            settings.setValue(k, v)
        else:
            settings.beginWriteArray(k)
            for n in range(len(v)):
                settings.setArrayIndex(n)
                vi = v[n]
                settings.setValue(name, vi)
            settings.endArray()
            
    else:
        #print 'ok %s = %s' % (name, v)
        setattr(conf, name, v)

def save_robots(robots):
    settings = QtCore.QSettings()
    settings.beginWriteArray('files/robots')
    for i, val in enumerate(robots):
        settings.setArrayIndex(i)
        settings.setValue('robot', val)
    settings.endArray()

def load_robots():
    settings = QtCore.QSettings()
    robots = []
    for n in range(settings.beginReadArray('files/robots')):
        settings.setArrayIndex(n)
        setting = settings.value('robot')
        v = str(setting.toString())
        robots.append(v)
    if robots:
        conf.robots = robots
        

class Settings(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        uifile = 'settings.ui'
        uipath = os.path.join(uidir, uifile)
        SClass, _ = uic.loadUiType(uipath)
        self.ui = SClass()
        self.ui.setupUi(self)
        self.load_current()

    def load_current(self):
        'read settings from QSettings and store in settings form'

        settings = QtCore.QSettings()
        self.settings = settings
        
        for section, items in ss.items():
            self.load_section(section, items)

    def load_section(self, section, items):
        for name, kind in items.items():
            self.load_one(section, name, kind)

    def load_var(self, var, kind, val):
        if 'X' in kind:
            return

        o = getattr(self.ui, var)

        if 'i' in kind:
            o.setValue(val)
        elif 'b' in kind:
            o.setChecked(val)
        elif 'f' in kind:
            if val == int(val):
                o.setText(str(int(val)))
            else:
                sval = '%.3f' % val
                o.setText(sval)
        else:
            o.setText(val)

    def load_one(self, section, name, kind):
        settings = self.settings

        k = '%s/%s' % (section, name)
        #print 'O', k,

        if 'a' not in kind:
            setting = settings.value(k)
            val, ok = read_value(setting, kind)
            if not ok:
                val = getattr(conf, var)
                #print val
            #else:
                #print 'ok'
            self.load_var(name, kind, val)
        else:
            v = read_array(k, name, kind)
            #print k, v
            for n, val in enumerate(v):
                var = name + str(n+1)
                self.load_var(var, kind, val)

    def browse(self):
        d = QtGui.QFileDialog.getExistingDirectory(
                self,
                'Set Robot dir',
                self.robotdir.text())
        self.robotdir.setText(d)

    def accept(self):
        self.set_current()
        QtGui.QDialog.accept(self)

    def set_current(self):
        for section, items in ss.items():
            self.set_section(section, items)

    def set_section(self, section, items):
        for name, kind in items.items():
            self.set_one(section, name, kind)

    def get_from_form(self, var, kind):
        if 'X' in kind:
            return None

        o = getattr(self.ui, var)

        if 'i' in kind:
            retval = o.value()
        elif 'b' in kind:
            retval = o.isChecked()
        elif 'f' in kind:
            retval = float(str(o.text()))
        else:
            retval = str(o.text())

        return retval

    def set_one(self, section, name, kind):
        if 'X' in kind:
            return

        settings = self.settings

        k = '%s/%s' % (section, name)
        #print 'S', k

        if 'a' not in kind:
            oldval = getattr(conf, name)
            val = self.get_from_form(name, kind)
            settings.setValue(k, val)
            setattr(conf, name, val)
            if val != oldval:
                special = '_changed_%s' % name
                if hasattr(self, special):
                    getattr(self, special)(val, oldval)

        else:
            matching = []
            for e in dir(self.ui):
                if e.endswith('_browse'):
                    continue
                if e.startswith(name):
                    matching.append(e)
            vals = []
            settings.beginWriteArray(k)
            for i, e in enumerate(matching):
                settings.setArrayIndex(i)
                val = self.get_from_form(e, kind)
                settings.setValue(name, val)
                vals.append(val)
                #print 'A', e, val
            settings.endArray()
            setattr(conf, name, vals)


    def browse_for_directory(self):
        button = str(self.sender().objectName())
        #print 'browsing directory', button
        base = button[:-7] # remove _browse
        txt = str(getattr(self.ui, base).text())
        if base == 'base_dir':
            if os.path.isabs(conf.base_dir):
                curdir, _ = os.path.split(conf.base_dir)
            else:
                curdir = conf.base_dir
        else:
            curdir = conf.base_dir

        #print 'CD', os.getcwd(), curdir, os.path.exists(curdir)
        curdir = os.path.abspath(curdir)

        dirpath = QtGui.QFileDialog.getExistingDirectory(
                            self,
                            'Choose folder',
                            curdir)
        dirpath = str(dirpath)
        base_dir_abs = os.path.abspath(conf.base_dir)
        common = os.path.commonprefix((dirpath, base_dir_abs))
        #print 'C', common
        if common == base_dir_abs:
            dirpath = os.path.relpath(dirpath, base_dir_abs)
            #print 'CC', dirpath

        getattr(self.ui, base).setText(dirpath)

    def browse_for_file(self):
        button = str(self.sender().objectName())
        #print 'browsing file', button
        base = button[:-7] # remove _browse
        txt = str(getattr(self.ui, base).text())
        d, f = os.path.split(txt)
        if os.path.isabs(txt):
            fdir, fname = d, f
        else:
            fdir = os.path.join(conf.base_dir, d)
        fdir = os.path.abspath(fdir)
        fpath = QtGui.QFileDialog.getOpenFileName(
                            self,
                            'Choose file',
                            fdir)
        fpath = str(fpath)
        base_dir_abs = os.path.abspath(conf.base_dir)
        common = os.path.commonprefix((fpath, base_dir_abs))
        #print 'C', common
        if common == base_dir_abs:
            fpath = os.path.relpath(fpath, base_dir_abs)
            #print 'CC', fpath

        getattr(self.ui, base).setText(fpath)

    def _changed_base_dir(self, val, oldval):
        stats.dbclose(restart=True)
        if not stats.dbcheck():
            QtGui.QMessageBox.warning(self, 'DB Version Mismatch', 'Database version mismatch.')
        stats.dbopen()

        import shutil
        #print 'ONV', oldval, conf.template, val
        shutil.copy(os.path.join(oldval, conf.template), val)

    def _changed_dbfile(self, val, oldval):
        stats.dbclose(restart=True)
        if not stats.dbcheck():
            QtGui.QMessageBox.warning(self, 'DB Version Mismatch', 'Database version mismatch.\nUpgrade database with -D switch.\n\nReverted to previous value.')
            conf.dbfile = oldval
            self.settings.setValue('files/dbfile', oldval)
            stats.dbclose(restart=True)
            stats.dbcheck()
        stats.dbopen()

    def reject(self):
        QtGui.QDialog.reject(self)

    def reset_to_defaults(self):
        settings = QtCore.QSettings()
        settings.clear()
        reload(conf)
        setup_sections()
        self.load_current()
