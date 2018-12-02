"""
Contains the base classes for the simulation.
"""
from enum import IntEnum 
from abc import ABCMeta, abstractmethod
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

class State(IntEnum):
    """
    Enum of possible traffic lights
    """
    green = 1
    amber = 2
    red = 3

class TrafficLight(object):
    """
    Simple model of a traffic light. 
    Attribute:
        lane_id (int): lane id of this traffic light
        green_t (int): green time
        amber_t (int): amber time
        red_t   (int): red time
        init_state (State): initial state of the traffic light
    """
    def __init__(self, lane_id, green_t=11, amber_t=4, red_t=15, init_state=State.green):
        self.green_t = green_t
        self.amber_t = amber_t
        self.red_t = red_t
        self.state = init_state
        self.__clock_reset = {
            State.green: green_t,
            State.amber: amber_t,
            State.red: red_t
        }
        self.clocks = {
            State.green: green_t,
            State.amber: amber_t,
            State.red: red_t
        }
    
    def __next_state(self) -> State:
        int n = (((self.state-1)+1) % 3 ) + 1
        return State(n)

    def __step(self):
        """
        At each call, the current clock time counter is decreased until it reaches 0, at 
        which point the light switches to its next state (and counter is reset). 
        """
        self.clocks[self.state]-= 1
        if self.clocks[self.state] == 0:
            #reset 
            self.clocks[self.state] = self.__clock_reset[self.state]
            # next state 
            self.state = self.__next_state()

class Sensor(object): 
    """
    Simple model of a sensor.
    """
    def __init__(self, lane_id, position=0, controller: Controller):
        self.lane_id = lane_id
        self.position = position
        self.controller = controller

    def notify_controller(self):
        """
        Notify the attached controller about the detection of a 
        vehicle at the position of the sensor. 
        """
        self.controller.update(self)

class Controller(object):
    """
    Base Class for controllers. 
    A controller monitors the state of each traffic light in the system 
    and enforces a cycle of green-amber-red states. 
    Based on inputs from sensors, the controller can extend the duration of the green state
    of a specific traffic light. 
    """

    def __init__(self):
        # list of lights in the system
        self.lights = []
    

    def step(self):
        """
        This function has to be called at each timestep to simulate time. 
        """
        for light in lights:
            light.__step()

    def update(sensor: Sensor):
        """
        A call to this function notifies the controller of a vehicle detected 
        by the sensor.  
        """
        pass

class Counter(object):
    count = 0
    def assign():
        count += 1
        return count

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
        self.id = Counter.assign()
        self.controller = controller
        self.D = D
        # initialize sensors
        self.sensors = {
            0: Sensor(self.id, 0, self.controller),
            D: Sensor(self.id, D, self.controller)
        }
        # traffic light
        self.light = TrafficLight(self.id, init_state=init_state)
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
            self.sensors[0].notify_controller()
        elif v.position == self.D:
            # in sensored area
            self.car_in += 1
            self.sensors[self.D].notify_controller()

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
        if self.light == State.green:
            # update metrics
            for v in self.v:
                self.__ride(v)
            # shift list 1 index to the left
            self.lane[0] = None 
            self.lane.rotate(-1)
            self.v.pop(0)

        # amber or red light
        else:
            for v in self.v:
                # first car has to stop
                if v.position == 1:
                    v.wait += 1
                # check position of the car in front    
                else:
                    if self.lane[v.position-1] is not None:
                        # no car ahead, this car can ride forward
                        self.__ride(v)
                    else:
                        # car ahead, this car has to wait
                        v.wait += 1
             



