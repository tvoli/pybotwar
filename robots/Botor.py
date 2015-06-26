from robot import Robot

class TheRobot(Robot):
    def initialize(self):
        # Will be called once, immediately after robot is created
        # Must finish in less than 1 second
        pass



    def respond(self):
        tick = self.sensors['TICK']
        health = self.sensors['HEALTH']
        x, y = self.sensors['POS']
        turret_angle = self.sensors['TUR']
        kind, angle, distance = self.sensors['PING']
        robot_angle = self.sensors['GYRO']
        
        self.turret(100)
        self.fire()
        ## if tick < 120:
        ##    self.force(100)
        ##else:
        ##    self.force(0)
        # Will be called 60 times per second
        # Must finish in less than 0.015 seconds
        #
        # sensors are available as the self.sensors dictionary
        #
        # use robot.Robot class methods to control
        pass
