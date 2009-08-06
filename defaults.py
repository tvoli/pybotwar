# Robot subprocess
subproc_python = '/usr/bin/python'
subproc_main = 'control.py'

init_timeout = 1.0
tick_timeout = 0.015


# Robot selection
robot_dirs = ['robots', 'robots/examples'] # In this order, in case of dup name
r1 = 'robot01'
r2 = 'robot02'
r3 = 'robot03'
r4 = 'robot04'
r5 = 'robot05'
r6 = 'robot06'
robots = [r1, r2, r3, r4, r5, r6]


# Game
maxhealth = 10
remove_dead_robots = True

graphical_display = True


# Physics
## robot
maxforce = 5
maxtorque = 15

robot_density = 1

robot_linearDamping = 1.5
robot_angularDamping = 3.0

robot_friction = 0.3
robot_restitution = 0.4

## cannon
cannon_maxheat = 100
cannon_heating_per_shot = 20
cannon_cooling_per_tick = 0.1

## turret
turret_maxMotorTorque = 10.0


## bullet
bulletspeed = 40

bullet_density = .2


# Statistics
dbfile = 'stats.db'
