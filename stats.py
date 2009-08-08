import sqlite3
import os
import hashlib
import conf


def dbopen():
    global conn
    conn = sqlite3.connect(conf.dbfile)
    conn.row_factory = sqlite3.Row
    global c
    c = conn.cursor()

def dbclose():
    conn.close()

def dbcheck():
    if not os.path.exists(conf.dbfile):
        initialize()
        print 'stats database initialized'


def initialize():
    'Create empty database'

    schemadef = '''\

CREATE TABLE stats (
    program_name text,
    fingerprint text,
    matches integer,
    wins integer,
    opponents integer,
    kills integer
);

CREATE TABLE tournament_stats (
    tournament datetime,
    program_name text,
    fingerprint text,
    matches integer,
    wins integer,
    opponents integer,
    kills integer
);

    '''

    dbopen()
    conn.executescript(schemadef)
    conn.commit()
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

def update(name, win, opponents, kills):
    fp = fingerprint(name)
    win = int(win) # turn True/False in to 1/0
    if exists(name, fp):
        q = '''\
        UPDATE stats
        SET matches = matches + 1,
            wins = wins + :win,
            opponents = opponents + :opponents,
            kills = kills + :kills
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
                kills)
            VALUES
                (:name,
                    :fp,
                    1,
                    :win,
                    :opponents,
                    :kills)
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

def tournament_update(tournament, name, win, opponents, kills):
    fp = fingerprint(name)
    win = int(win) # turn True/False in to 1/0
    if tournament_exists(tournament, name, fp):
        q = '''\
        UPDATE tournament_stats
        SET matches = matches + 1,
            wins = wins + :win,
            opponents = opponents + :opponents,
            kills = kills + :kills
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
                kills)
            VALUES
                (:tournament,
                    :name,
                    :fp,
                    1,
                    :win,
                    :opponents,
                    :kills)
        '''
    c.execute(q, locals())
    conn.commit()
