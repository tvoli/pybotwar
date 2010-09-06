import sqlite3
import os
import hashlib
import conf


dbversion = 2
dbversion_reset = dbversion


def fullpath():
    try:
        from PyQt4 import QtCore
        QtCore.QCoreApplication.setOrganizationName('pybotwar.googlecode.com')
        QtCore.QCoreApplication.setOrganizationDomain('pybotwar.googlecode.com')
        QtCore.QCoreApplication.setApplicationName('pybotwar')
        settings = QtCore.QSettings()
        settings.sync()

        d = settings.value('pybotwar/robotdir', '').toString()
        if d and d not in conf.robot_dirs:
            conf.robot_dirs.insert(0, str(d))

    except ImportError:
        d = ''

    if '~' in conf.dbfile:
        fname = os.path.expanduser(conf.dbfile)
    else:
        fdir = conf.robot_dirs[0]
        fname = os.path.join(fdir, conf.dbfile)

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

    try:
        conn = sqlite3.connect(fname)
    except sqlite3.OperationalError:
        print 'Cannot find dbfile. Working in :memory:'
        conn = sqlite3.connect(':memory:')
        dbversion = ':memory:'

    conn.row_factory = sqlite3.Row
    global c
    c = conn.cursor()

    if dbversion == ':memory:':
        dbcheck()


def dbclose(restart=False):
    global dbversion
    if restart or dbversion != ':memory:':
        conn.close()
    if restart:
        dbversion = dbversion_reset

def dbcheck():
    fname = fullpath()
    if not os.path.exists(fname):
        initialize()
        print 'stats database initialized'

    if not dbcheckver():
        print 'ERROR: Database version mismatch.'
        return False
    else:
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
        os.remove(fname)

def initialize():
    'Create empty database'

    schemadef = '''\

CREATE TABLE dbversion (
    n integer
);

CREATE TABLE stats (
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

    if dbversion != ':memory:':
        dbclose()



def fingerprint(name):
    fname = '%s.py' % name
    for d in conf.robot_dirs:
        pth = os.path.join(d, fname)
        if os.path.exists(pth):
            break

    m = hashlib.md5()
    for line in file(pth):
        m.update(line)

    return m.hexdigest()

def exists(name, fp):
    q = '''\
    SELECT *
    FROM stats
    WHERE program_name=:name AND
            fingerprint=:fp
    '''
    c.execute(q, locals())
    r = c.fetchall()
    return bool(r)

def update(name, win, opponents, kills, damage_caused):
    fp = fingerprint(name)
    win = int(win) # turn True/False in to 1/0
    if exists(name, fp):
        q = '''\
        UPDATE stats
        SET matches = matches + 1,
            wins = wins + :win,
            opponents = opponents + :opponents,
            kills = kills + :kills,
            damage_caused = damage_caused + :damage_caused
        WHERE
            program_name = :name AND
            fingerprint = :fp
        '''

    else:
        q = '''\
        INSERT INTO stats
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
                    1,
                    :win,
                    :opponents,
                    :kills,
                    :damage_caused)
        '''
    c.execute(q, locals())
    conn.commit()



def tournament_exists(tournament, name, fp):
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

def tournament_update(tournament, kind, name, win, opponents, kills, damage_caused):
    fp = fingerprint(kind)
    win = int(win) # turn True/False in to 1/0
    if tournament_exists(tournament, name, fp):
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

    else:
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
                    1,
                    :win,
                    :opponents,
                    :kills,
                    :damage_caused)
        '''
    c.execute(q, locals())
    conn.commit()

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
    dbopen()
    q = '''
    SELECT
        program_name,
        fingerprint,
        matches,
        wins,
        opponents,
        kills,
        damage_caused

    FROM stats
    ORDER BY
        wins DESC,
        kills DESC

    '''

    c.execute(q, locals())
    results = c.fetchall()

    print 'Top 10 List:'
    for n, line in enumerate(results[:10]):
        print n+1, '::', line[0], ':', line[3], 'wins', ':', line[5], 'defeated', ':', line[6], 'dmg caused'


if __name__ == '__main__':
    top10()
