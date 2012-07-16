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


import sqlite3
import os
import hashlib
import conf
import util


dbversion = 4
dbversion_reset = dbversion


def fullpath():
    if conf.dbfile.startswith('~'):
        fname = os.path.expanduser(conf.dbfile)
    else:
        fname = os.path.join(conf.base_dir, conf.dbfile)

    fname = os.path.abspath(fname)
    head, tail = os.path.split(fname)
    if not os.path.exists(head):
        fname = '/:::NONEXISTANT:::'

    return fname


def dbopen():
    global dbversion
    if dbversion == ':memory:':
        return

    global conn
    fname = fullpath()

    newdb = not os.path.exists(fname)

    try:
        conn = sqlite3.connect(fname)
        if newdb:
            print 'New stats database file started'
    except sqlite3.OperationalError:
        print 'Cannot open database file. Working in :memory:'
        conn = sqlite3.connect(':memory:')
        dbversion = ':memory:'

    conn.row_factory = sqlite3.Row
    global c
    c = conn.cursor()

    if dbversion == ':memory:' or newdb:
        initialize()


def dbclose(restart=False):
    global dbversion
    if restart or dbversion != ':memory:':
        conn.close()
    if restart:
        dbversion = dbversion_reset

def trywrite():
    dbopen()
    q = '''
    UPDATE trywrite SET tw=1;
    '''
    try:
        c.execute(q)
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        return False

    return True

def dbcheck():
    fname = fullpath()
    print 'Checking', fname
    if fname != '/:::NONEXISTANT:::' and not os.path.exists(fname):
        dbopen()

    if not dbcheckver():
        print 'ERROR: Database version mismatch.'
        return False

    if not trywrite():
        print 'Cannot write to database. Working in :memory:'
        global dbversion
        global conn
        global c
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        dbversion = ':memory:'
        initialize()

    return True

def dbcheckver():
    dbopen()
    q = '''SELECT count(*)
            FROM sqlite_master
            WHERE type='table' AND
                name='dbversion'
        '''
    c.execute(q)
    r = c.fetchone()
    if not r[0]:
        # No dbversion table exists
        retval = 0
    else:
        q = '''SELECT n
                FROM dbversion'''
        c.execute(q)
        r = c.fetchone()
        ver = r[0]
        retval = ver == dbversion

    dbclose()
    return retval

def dbremove():
    fname = fullpath()
    if os.path.exists(fname):
        print 'Removing', fname
        os.remove(fname)

def initialize():
    'Create empty database'

    schemadef = '''\

CREATE TABLE dbversion (
    n integer
);

CREATE TABLE robot_stats (
    program_name text,
    fingerprint text,
    matches integer,
    wins integer,
    opponents integer,
    kills integer,
    damage_caused integer
);

CREATE TABLE tournament_stats (
    tournament datetime,
    program_name text,
    fingerprint text,
    matches integer,
    wins integer,
    opponents integer,
    kills integer,
    damage_caused integer
);

CREATE TABLE trywrite (
    tw integer
);

    '''

    dbopen()
    conn.executescript(schemadef)
    conn.commit()

    q = '''INSERT INTO dbversion
            VALUES (:n)
    '''
    n = dbversion
    c.execute(q, locals())
    conn.commit()

    print 'Stats database initialized'

    if dbversion != ':memory:':
        dbclose()



def fingerprint(name):
    fname = '%s.py' % name
    rdirs = util.get_robot_dirs()
    for d in rdirs:
        pth = os.path.join(d, fname)
        if os.path.exists(pth):
            break

    m = hashlib.md5()
    for line in file(pth):
        m.update(line)

    return m.hexdigest()

def robot_exists(name, fp):
    q = '''\
    SELECT *
    FROM robot_stats
    WHERE program_name=:name AND
            fingerprint=:fp
    '''
    c.execute(q, locals())
    r = c.fetchall()
    return bool(r)

def add_robot(name, fp):
    q = '''\
    INSERT INTO robot_stats
        (program_name,
            fingerprint,
            matches,
            wins,
            opponents,
            kills,
            damage_caused)
        VALUES
            (:name,
                :fp,
                0,
                0,
                0,
                0,
                0)
    '''
    try:
        c.execute(q, locals())
        conn.commit()
    except sqlite3.OperationalError:
        conn.rollback()

def update(name, win, opponents, kills, damage_caused):
    fp = fingerprint(name)
    if robot_exists(name, fp):
        q = '''\
        UPDATE robot_stats
        SET matches = matches + 1,
            wins = wins + :win,
            opponents = opponents + :opponents,
            kills = kills + :kills,
            damage_caused = damage_caused + :damage_caused
        WHERE
            program_name = :name AND
            fingerprint = :fp
        '''
        win = int(win) # turn True/False in to 1/0
        try:
            c.execute(q, locals())
            conn.commit()
        except sqlite3.OperationalError:
            conn.rollback()

    else:
        add_robot(name, fp)
        update(name, win, opponents, kills, damage_caused)


def tournament_robot_exists(tournament, name, fp):
    q = '''\
    SELECT *
    FROM tournament_stats
    WHERE tournament = :tournament AND
            program_name = :name AND
            fingerprint = :fp
    '''
    c.execute(q, locals())
    r = c.fetchall()
    return bool(r)

def add_tournament_robot(tournament, name, fp):
    q = '''\
    INSERT INTO tournament_stats
        (tournament,
            program_name,
            fingerprint,
            matches,
            wins,
            opponents,
            kills,
            damage_caused)
        VALUES
            (:tournament,
                :name,
                :fp,
                0,
                0,
                0,
                0,
                0)
    '''
    try:
        c.execute(q, locals())
        conn.commit()
    except sqlite3.OperationalError:
        conn.rollback()

def tournament_update(tournament, kind, name, win, opponents, kills,
                                                        damage_caused):
    fp = fingerprint(kind)
    win = int(win) # turn True/False in to 1/0
    if tournament_robot_exists(tournament, name, fp):
        q = '''\
        UPDATE tournament_stats
        SET matches = matches + 1,
            wins = wins + :win,
            opponents = opponents + :opponents,
            kills = kills + :kills,
            damage_caused = damage_caused + :damage_caused
        WHERE
            tournament = :tournament AND
            program_name = :name AND
            fingerprint = :fp
        '''
        try:
            c.execute(q, locals())
            conn.commit()
        except sqlite3.OperationalError:
            conn.rollback()

    else:
        add_tournament_robot(tournament, name, fp)
        tournament_update(tournament, kind, name, win, opponents, kills, damage_caused)

def tournament_results(tournament):
    q = '''
    SELECT *
    FROM tournament_stats
    WHERE tournament = :tournament
    ORDER BY
        wins DESC,
        kills DESC

    '''

    c.execute(q, locals())
    r = c.fetchall()
    return r


def top10():
    q = '''
    SELECT
        program_name,
        fingerprint,
        matches,
        wins,
        opponents,
        kills,
        damage_caused

    FROM robot_stats
    ORDER BY
        wins DESC,
        kills DESC

    '''

    c.execute(q, locals())
    results = c.fetchall()

    print 'Top 10 List:'
    if dbversion == ':memory:':
        fname = dbversion
    else:
        fname = fullpath()
    print '(%s)' % fname

    er = list(enumerate(results[:10]))
    len_name = max(len(l[0]) for n, l in er)
    len_wins = max(len(str(l[3])) for n, l in er)
    len_def = max(len(str(l[5])) for n, l in er)
    len_dmg = max(len(str(l[6])) for n, l in er)

    for n, line in er:
        wpct = round(float(line[3]) / line[2], 3)
        opct = round(float(line[5]) / line[4], 3)
        print '{0:2} :: {1:{len_name}} : {2:{len_wins}} wins ({5:.3f}) : {3:{len_def}} defeated ({6:.3f}) : {4:{len_dmg}} dmg caused'.format(
            n+1, line[0], line[3], line[5], line[6], wpct, opct,
            len_name = len_name,
            len_wins = len_wins,
            len_def = len_def,
            len_dmg = len_dmg)

def get_robot_stats(sort='wpct'):
    q = '''
    SELECT
        program_name,
        fingerprint,
        matches,
        wins,
        CAST(wins AS REAL)/matches AS wpct,
        opponents,
        kills,
        CAST(kills AS REAL)/opponents opct,
        damage_caused

    FROM robot_stats
    ORDER BY %s DESC
    ''' % sort

    c.execute(q, locals())
    results = c.fetchall()

    return results

def get_tournament_stats(dt, sort='wpct DESC'):
    q = '''
    SELECT
        program_name,
        fingerprint,
        matches,
        wins,
        CAST(wins AS REAL)/matches AS wpct,
        opponents,
        kills,
        CAST(kills AS REAL)/opponents opct,
        damage_caused

    FROM tournament_stats
    WHERE tournament=:dt
    ORDER BY %s
    ''' % sort

    c.execute(q, locals())
    results = c.fetchall()

    return results


if __name__ == '__main__':
    dbopen()
    top10()
