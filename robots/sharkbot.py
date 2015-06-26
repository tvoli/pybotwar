from robot import Robot

class TheRobot(Robot):
    def respond(self):
        self.torque(50)
        self.log(sensors['TICK'])
        if self.sensors['TICK'] % 10 == 0:
            self.fire()

