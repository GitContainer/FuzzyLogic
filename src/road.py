from models import TrafficLight, Controller, State
from collections import deque

class Vehicle(object):
    """
    Simple model of a vehicle in a lane. 
    Each instance keeps a count of the time steps 
    spent riding or waiting in a queue.
    """
    def __init__(self, position=0):
        self.ride = 0
        self.wait = 0
        self.position = position

class Lane(object):
    """
    Simple model of a lane. 
    A lane can be populated by a list of vehicles within a predefined capacity 
    which is the size of the lane (in number of cells).
    Each lane has 1 traffic light and 2 sensors. The first one is located right before the intersection and 
    The second one is D cell(s) further away from it. 
    Constructor parameters:
        D   (int): distance between the sensors
        S   (int): size of the lane
        name    (String): name of the lane
        init_state  (State): initial state of the traffic light
        controller  (Controller): controller of the system
    """
    def __init__(self, controller: Controller,S=50, name='lane', D=15,init_state=State.green):
        self.lane = deque([None for i in range(S)], S)
        self.v = [] # contains the actual vehicles
        self.id = id(self)
        self.name = name
        self.controller = controller
        self.D = D
        # traffic light
        self.light = TrafficLight(init_state=init_state)
        # register the light to the controller
        self.controller.lights.append(self.light)
        ## metrics 
        # number of cars entering the sensed area
        self.car_in = 0
        # number of cars going out of the sensed area (passing the traffic light)
        self.car_out = 0
        # total waiting time
        self.total_wait = 0

    def append(self, v: Vehicle):
        """
        Add a new vehicle to the lane.
        When a new vehicle is added to the lane, it is appended right after the second sensor except if 
        there already are some vehicles after the second sensor, in which case the new vehicle is appended after the last vehicle.
        """
        if len(self.v) == 0:
            # no vehicles, insert in position D + 1
            v.position = self.D+1
            self.v.append(v)
            self.lane[v.position] = v
        else:
            # check position of last vehicle
            pos_last_v = self.v[-1].position
            if pos_last_v == len(self.lane)-1:
                # maximum capacity
                return 
            elif pos_last_v >= self.D+1: 
                v.position = pos_last_v
                self.lane[v.position] = v
                self.v.append(v) 
            else:
                v.position  = self.D+1 
                self.lane[ v.position] = v
                self.v.append(v)

    def __notify_controller(self, position):
        self.controller.update(self.id, position)

    def __ride(self, v: Vehicle):
        """
        move forward logic. Handle sensor detection
        """
        v.ride += 1
        v.position -= 1
        if v.position == 0:
            # out of sensored area
            self.car_out += 1 
            self.total_wait += v.wait 
            self.__notify_controller(0)
        elif v.position == self.D:
            # in sensored area
            self.car_in += 1
            self.__notify_controller(self.D)

    def step(self):
        """
        This function has to be called at each timestep to simulate time.
        At each time step, if the light is green, every vehicle in the lane rides 
        forward 1 cell.
        If the light is amber or red, a vehicle rides forward if there are no vehicles in front of it and 
        if the vehicle is not in position 0, otherwise it waits.
        When a vehicle reaches position 0, it is removed from the lane.
        """
        #green light, everyone moves forward
        if self.light.state == State.green:
            print("[{}]green light, everyone moves forward".format(self.name))
            # update metrics
            for v in self.v:
                self.__ride(v)
            # shift list 1 index to the left
            self.lane[0] = None 
            self.lane.rotate(-1)
            if len(self.v) > 0:
                self.v.pop(0) 
        # amber or red light
        else:
            print("[{}]amber or red light".format(self.name))
            for v in self.v:
                # first car has to stop
                if v.position == 1:
                    v.wait += 1
                # check position of the car in front    
                else:
                    if self.lane[v.position-1] is None:
                        # no car ahead, this car can ride forward
                        self.__ride(v)
                    else:
                        # car ahead, this car has to wait
                        v.wait += 1
    
    def __repr__(self):
        s= []
        for c in self.lane:
            if c is None:
                s.append('')
            else:
                s.append(('v', c.position, c.ride, c.wait ))
        return repr(s)