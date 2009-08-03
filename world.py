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


import random

import Box2D as box2d
pi = box2d.b2_pi

import view



class Robot(object):
    nrobots = 0
    def __init__(self, w, name, pos, ang):
        Robot.nrobots += 1
        self.n = Robot.nrobots

        self.alive = True
        self.health = 10
        self.name = name

        self._pingtype = 'w'
        self._pingangle = 0
        self._pingdist = 0

        self._cannonheat = 0

        bodyDef = box2d.b2BodyDef()
        bodyDef.position = pos
        bodyDef.angle = ang

        bodyDef.linearDamping = 1.5
        bodyDef.angularDamping = 3.0
        bodyDef.userData = {}

        body = w.CreateBody(bodyDef)

        shapeDef = box2d.b2PolygonDef()
        shapeDef.SetAsBox(1, 1)
        shapeDef.density = 1
        shapeDef.friction = 0.3
        shapeDef.restitution = 0.4
        shapeDef.filter.groupIndex = -self.n
        body.CreateShape(shapeDef)
        body.SetMassFromShapes()

        body.userData['actor'] = self
        body.userData['kind'] = 'robot'

        self.body = body

        turretDef = box2d.b2BodyDef()
        turretDef.position = pos
        turretDef.angle = ang

        turretDef.linearDamping = 0
        turretDef.angularDamping = 0
        turret = w.CreateBody(bodyDef)

        shapeDef = box2d.b2PolygonDef()
        shapeDef.SetAsBox(.1, .1)
        shapeDef.density = 1
        shapeDef.friction = 0
        shapeDef.restitution = 0
        shapeDef.filter.groupIndex = -self.n
        turret.CreateShape(shapeDef)
        turret.SetMassFromShapes()
        self.turret = turret

        jointDef = box2d.b2RevoluteJointDef()
        jointDef.Initialize(body, turret, pos)
        jointDef.maxMotorTorque = 10.0
        jointDef.motorSpeed = 0.0
        jointDef.enableMotor = True
        self.turretjoint = w.CreateJoint(jointDef).getAsType()
        self._turretangletarget = 0

        v = view.Robot(pos, ang)
        self.v = v

        t = view.Turret(pos, ang)
        self.t = t

    def set_turretangle(self, angle):
        'Angle comes in degrees. Convert to radians and set.'
        radians = (pi / 180.) * angle
        self._turretangletarget = radians

    def get_turretangle(self):
        'return turret angle in degrees.'
        degrees = int(round((180 / pi) * self.turretjoint.GetJointAngle()))
        return degrees

    def turretcontrol(self):
        joint = self.turretjoint
        angleError = joint.GetJointAngle() - self._turretangletarget
        gain = 0.5
        joint.SetMotorSpeed(-gain * angleError)


class Bullet(object):
    def __init__(self, w, robot):
        r = robot.turret
        pos = r.position
        vel = r.linearVelocity
        ang = r.angle

        blocalvel = box2d.b2Vec2(30, 0)
        bwvel = r.GetWorldVector(blocalvel)
        bvel = bwvel + vel
        #print bvel, bvel.Length()

        bodyDef = box2d.b2BodyDef()
        blocalpos = box2d.b2Vec2(.1, 0)
        bwpos = r.GetWorldVector(blocalpos)
        bpos = bwpos + pos
        bodyDef.position = bpos
        bodyDef.angle = ang
        bodyDef.isBullet = True
        bodyDef.linearDamping = 0
        bodyDef.userData = {}

        body = w.CreateBody(bodyDef)
        #print body
        #print 'IB', body.isBullet
        body.linearVelocity = bvel

        shapeDef = box2d.b2PolygonDef()
        shapeDef.SetAsBox(.1, .1)
        shapeDef.density = .2
        shapeDef.restitution = 0
        shapeDef.friction = 0
        shapeDef.filter.groupIndex = -robot.n
        body.CreateShape(shapeDef)
        body.SetMassFromShapes()

        body.userData['actor'] = self
        body.userData['kind'] = 'bullet'
        body.userData['shooter'] = robot

        self.body = body

        v = view.Bullet(pos)
        self.v = v


class Wall(object):
    def __init__(self, w, pos, size):
        walldef = box2d.b2BodyDef()
        walldef.position = pos
        walldef.userData = {}
        wallbod = w.CreateBody(walldef)
        wallbod.userData['actor'] = None
        wallbod.userData['kind'] = 'wall'
        wallbod.iswall = True
        wallshp = box2d.b2PolygonDef()
        width, height = size
        wallshp.SetAsBox(width, height)
        wallbod.CreateShape(wallshp)

        v = view.Wall(pos, size)
        self.v = v


class World(object):
    def __init__(self):
        self.count = 1000
        self.force = 10

        self.robots = {}
        self.bullets = []
        self.sprites = {}
        self.to_destroy = []

        halfx = 30
        self.ahalfx = 26
        halfy = 25
        self.ahalfy = 20

        gravity = (0, 0)
        doSleep = True

        self.timeStep = 1.0 / 60.0
        self.velIterations = 10
        self.posIterations = 8


        aabb = box2d.b2AABB()
        aabb.lowerBound = (-halfx, -halfy)
        aabb.upperBound = (halfx, halfy)

        self.w = box2d.b2World(aabb, gravity, doSleep)
        self.w.GetGroundBody().SetUserData({'actor': None})

        self.v = view.Arena()
        self.makearena()


    def makearena(self):
        ahx = self.ahalfx
        ahy = self.ahalfy

        wl = Wall(self.w, (-ahx, 0), (1, ahy+1))
        wl = Wall(self.w, (ahx, 0), (1, ahy+1))
        wl = Wall(self.w, (0, ahy), (ahx+1, 1))
        wl = Wall(self.w, (0, -ahy), (ahx+1, 1))

        for block in range(5):
            #self.makeblock()
            pass

    def makeblock(self):
        x = random.randrange(-self.ahalfx, self.ahalfx+1)
        y = random.randrange(-self.ahalfy, self.ahalfy+1)
        w = random.randrange(1, 20)/10.0
        h = random.randrange(1, 20)/10.0
        wl = Wall(self.w, (x, y), (w, h))

    def posoccupied(self, pos):
        px, py = pos
        for name, robot in self.robots.items():
            b = robot.body
            rx, ry = b.position
            if (rx-2 < px < rx+2) and (ry-2 < py < ry+2):
                return True
            else:
                return False

    def makerobot(self, name, pos=None, ang=None):
        rhx = self.ahalfx-2
        rhy = self.ahalfy-2

        while pos is None or self.posoccupied(pos):
            rx = random.randrange(-rhx, rhx)
            ry = random.randrange(-rhy, rhy)
            pos = box2d.b2Vec2(rx, ry)

        if ang is None:
            ang = random.randrange(628) / float(100)

        robot = Robot(self.w, name, pos, ang)

        self.v.sprites.add(robot.v)
        self.v.sprites.add(robot.t, level=1)
        self.robots[name] = robot

        return robot

    def makebullet(self, rname):
        robot = self.robots[rname]
        if robot._cannonheat > 100:
            return None

        bullet = Bullet(self.w, robot)
        self.v.sprites.add(bullet.v)

        self.bullets.append(bullet)

        robot._cannonheat += 20

        return bullet

    def makeping(self, rname):
        robot = self.robots[rname]
        body = robot.turret

        segmentLength = 65.0

        blocalpos = box2d.b2Vec2(1.12, 0)

        segment = box2d.b2Segment()
        laserStart = (1.12, 0)
        laserDir = (segmentLength, 0.0)
        segment.p1 = body.GetWorldPoint(laserStart)
        segment.p2 = body.GetWorldVector(laserDir)
        segment.p2+=segment.p1

        lambda_, normal, shape = self.w.RaycastOne(segment, False, None)
        hitp = (1 - lambda_) * segment.p1 + lambda_ * segment.p2
        angle = robot.get_turretangle()
        dist = box2d.b2Distance(segment.p1, hitp)

        if shape is not None:
            hitbody = shape.GetBody()
            kind = hitbody.userData['kind']
            return kind, angle, dist
        else:
            # Not sure why shape returns None here. Seems to be when the
            #   robot is pressed right up against a wall, though.
            return 'w', angle, 0

    def step(self):
        #self.moveit()
        #print 'STEP', self.w.Step
        self.w.Step(self.timeStep, self.velIterations, self.posIterations)
        self.do_destroy()
        self.showit()


    def showit(self):
        for name, robot in self.robots.items():
            r = robot.body
            robot.turretcontrol()
            #vel = r.linearVelocity.Length()
            #pos = r.position.Length()
            pos2 = r.position
            ang = r.angle

            turret = robot.turretjoint
            tang = turret.GetJointAngle()

            #print '{name}: {pos:6.2f} {ang:5.1f} {vel:5.1f}'.format(
            #            name=name, vel=vel, pos=pos, ang=ang)

            robot.v.setpos(pos2)
            robot.v.set_rotation(-ang)

            robot.t.setpos(pos2)
            robot.t.set_rotation(-ang-tang)

            robot._cannonheat -= .1

        for bullet in self.bullets:
            b = bullet.body
            pos2 = b.position
            bullet.v.setpos(pos2)
            #print bullet.linearVelocity

        #print
        self.v.step()

    def do_destroy(self):
        while self.to_destroy:
            model = self.to_destroy.pop()
            body = model.body
            if hasattr(body, 'iswall') and body.iswall:
                continue
            #print 'destroy', id(body)
            if model in self.bullets:
                self.bullets.remove(model)
            #print 's0', self.v.sprites
            model.v.kill()

            if model.body.userData['kind'] == 'robot':
                model.t.kill()
                self.w.DestroyBody(model.turret)
                del self.robots[model.name]
            #print 's1', self.v.sprites
            #print 'destroying', id(body)
            self.w.DestroyBody(body)
            #print 'destroyed', id(body)




    def make_testrobots(self):
        self.makerobot('R1', (4, 0), pi)
        self.makerobot('R2', (-4, 0), 0)
        self.makerobot('R3', (0, 4), pi)
        self.makerobot('R4', (0, -4), 0)

        self.makerobot('R5', (4, 4), pi)
        self.makerobot('R6', (-4, 4), 0)
        self.makerobot('R7', (-4, -4), pi)
        self.makerobot('R8', (4, -4), 0)

        self.makerobot('R1')
        self.makerobot('R2')
        self.makerobot('R3')
        self.makerobot('R4')

        self.makerobot('R5')
        self.makerobot('R6')
        self.makerobot('R7')
        self.makerobot('R8')

    def testmoves(self):
        self.count -= 1
        if self.count < 0:
            self.force = -self.force
            self.count = 1000

        for name, robot in self.robots.items():
            r = robot.body
            pos = r.position
            vel = r.linearVelocity

            #print 'pos', pos
            #print dir(vel)

            localforce = box2d.b2Vec2(self.force, 0)
            worldforce = r.GetWorldVector(localforce)

            r.ApplyForce(worldforce, pos)

            #if r.angularVelocity < .5:
                #r.ApplyTorque(.5)
            #else:
                #print 'av', r.angle

            r.ApplyTorque(4)

            bullet = random.randrange(3)
            if bullet == 2:
                #print name, 'shoots'
                self.makebullet(name)


class CL(box2d.b2ContactListener):
    def Add(self, point):
        s1 = point.shape1
        b1 = s1.GetBody()
        actor1 = b1.userData['actor']
        kind1 = b1.userData.get('kind', None)

        s2 = point.shape2
        b2 = s2.GetBody()
        actor2 = b2.userData['actor']
        kind2 = b2.userData.get('kind', None)

        if kind1=='bullet' and kind2=='robot':
            shooter = b1.userData['shooter']
            if shooter == actor2:
                #can't shoot yourself
                pass
            else:
                actor2.health -=1
                if actor2.health <= 0:
                    actor2.alive = False
                    if actor2 not in self.w.to_destroy:
                        self.w.to_destroy.append(actor2)
                else:
                    print 'Robot', actor2.name, 'down to', actor2.health

        if kind2=='bullet' and kind1=='robot':
            shooter = b2.userData['shooter']
            if shooter == actor1:
                #can't shoot yourself
                pass
            else:
                actor1.health -=1
                if actor1.health <= 0:
                    actor1.alive = False
                    if actor1 not in self.w.to_destroy:
                        self.w.to_destroy.append(actor1)
                else:
                    print 'Robot', actor1.name, 'down to', actor1.health

        if actor1 in self.w.bullets:
            if actor1 not in self.w.to_destroy:
                self.w.to_destroy.append(actor1)

        if actor2 in self.w.bullets:
            if actor2 not in self.w.to_destroy:
                self.w.to_destroy.append(actor2)



if __name__ == '__main__':
    w = World()
    cl = CL()
    w.w.SetContactListener(cl)
    cl.w = w
    while not w.v.quit:
        w.step()
