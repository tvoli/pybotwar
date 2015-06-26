from robot import Robot

class TheRobot(Robot):
    def initialize(self):
        self.act_next = 0

    def respond(self):
        kind, angle, dist = self.sensors['PING']
        if self.sensors['TICK'] > self.act_next:
            self.torque(50)
            self.turret(40)
            self.force(40)
        else:
            self.turret(0)
            self.torque(0)
            self.force(0)

        if kind == 'r':
            self.log('Wait')
            self.act_next = self.sensor['TICK'] + 10000

        self.log(kind)
        if self.sensors['TICK'] % 10 == 0:
            self.fire()
        self.ping()

