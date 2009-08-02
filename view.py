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


from pygsear.Game import Game
from pygsear.Drawable import RotatedImage, Square, Rectangle, Stationary

from pygsear import conf
conf.MAX_FPS = 60

size = 30


def trans(pos):
    px, py =  pos
    sz = size / 2
    x, y = (px*sz)+400, (py*sz)+300
    return x, y

def scale(s):
    w, h = s
    sw, sh = (w*size), (h*size)
    return sw, sh

class Robot(RotatedImage):
    nrobots = 0
    def __init__(self, pos, ang):
        Robot.nrobots += 1
        filename = 'r{0:02d}.png'.format(Robot.nrobots)
        steps = 360
        RotatedImage.__init__(self, filename=filename, steps=steps)
        if size != 30:
            self.stretch(size=(size, size))
        self.setpos(pos)
        self.set_rotation(ang)

    def setpos(self, pos):
        x, y = trans(pos)
        self.set_position(x, y)

class Turret(RotatedImage):
    def __init__(self, pos, ang):
        filename = 'turret.png'
        steps = 360
        RotatedImage.__init__(self, filename=filename, steps=steps)
        self.setpos(pos)
        self.set_rotation(ang)

    def setpos(self, pos):
        x, y = trans(pos)
        self.set_position(x, y)


class Bullet(Square):
    def __init__(self, pos):
        Square.__init__(self, side=2)
        self.setpos(pos)

    def setpos(self, pos):
        x, y = trans(pos)
        self.set_position(x, y)


class Wall(Stationary):
    def __init__(self, pos, size):
        cx, cy = trans(pos)
        w, h = scale(size)
        x = cx-(w/2)
        y = cy-(h/2)

        sq = Rectangle(width=w, height=h, color=(120, 50, 50))
        Stationary.__init__(self, sprite=sq)
        self.set_position((x, y))
        self.draw()

class Arena(Game):
    pass
