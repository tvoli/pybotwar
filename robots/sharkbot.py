from robot import Robot

class TheRobot(Robot):
    def respond(self):
        self.torque(50)
        if self.sensors['TICK'] % 10 == 0:
            self.fire()
