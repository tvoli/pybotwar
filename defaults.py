# Settings
use_qt_settings = True


# Robot subprocess
subproc_python = '/usr/bin/python'
subproc_main = 'control.py'

init_timeout = 1.0
tick_timeout = 0.015


# Robot selection
base_dir = 'robots' # user robot files generally stored here
more_robot_dirs = ['examples']  # In order, in case of dup name
                                # bare names are relative to base_dir
                                # absolute paths also acceptable
r1 = 'robot01'
r2 = 'robot02'
r3 = 'robot03'
r4 = 'robot04'
r5 = 'robot05'
r6 = 'robot06'
r7 = 'robot07'
r9 = 'robot09'
robots = [r2, r3, r4, r5, r6, r7, r9]

logdir = 'logs' # relative to robot_dirs[0]

template = 'template.py'

lineups = 'lineups' # relative to robot_dirs[0]


# Game
maxtime = 600 # Seconds before calling the match a draw

maxhealth = 100
direct_hit_damage = 10

explosion_radii = [1, 2, 3] # meters
explosion_damage = [3, 4, 5] # Cumulative. If hit by ring 0, will also get 1 and 2

collision_damage_start = 25 # Minimum impulse value for damage to occur
collision_damage_factor = 0.15 # Collision damage = (cdf * (impulse - cds))**2 + 1

remove_dead_robots = True

graphical_display = True


# Physics
pybox2d_version = '2.3b0'

## robot
maxforce = 5
maxtorque = 15

robot_density = 1

robot_linearDamping = 1.5
robot_angularDamping = 3.0

robot_friction = 0.3
robot_restitution = 0.4

## cannon
cannon_reload_ticks = 15 # ticks (60 = 1 second)
cannon_maxheat = 100
cannon_heating_per_shot = 20
cannon_cooling_per_tick = 0.1
overheat_fire_reload_penalty = 0 # ticks
unloaded_fire_reload_penalty = 0 # ticks

## turret
turret_density = 3 # kg/m^3
turret_maxMotorTorque = 10.0
turret_maxMotorSpeed = 1 # radian / second


## bullet
bulletspeed = 40

bullet_density = .2


# Statistics
dbfile = 'stats.db' # relative to robot_dirs[0]


# Other
help_url = 'http://code.google.com/p/pybotwar/wiki/Programming'
