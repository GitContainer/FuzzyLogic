"""
Contains the base classes for the simulation.
"""
from enum import IntEnum 
from abc import ABCMeta, abstractmethod

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
    def __init__(self, green_t=11, amber_t=4, red_t=15, init_state=State.green):
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
        n = (((self.state-1)+1) % 3 ) + 1
        return State(n)

    def step(self):
        """
        At each call, the current clock time counter is decreased until it reaches 0, at 
        which point the light switches to its next state (and counter is reset). 
        """
        self.clocks[self.state]-= 1
        print('({}) clock: {}'.format(self.state,  self.clocks[self.state]))
        if self.clocks[self.state] == 0:
            #reset 
            self.clocks[self.state] = self.__clock_reset[self.state]
            # next state 
            self.state = self.__next_state()
            print('switch to: {}'.format(self.state))

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
    
    def add_traffic_light(self, tlight: TrafficLight):
        """
        Register the given traffic light to this controller.  
        """
        # ensure that the added light does not have the same colour
        if len(self.lights) > 0:
            hasGreen = False
            for l in self.lights:
                hasGreen = l.state = State.green
            if hasGreen:
                tlight.state = tlight.__next_state()
        self.lights.append(tlight)

    def step(self):
        """
        This function has to be called at each timestep to simulate time. 
        """
        for light in self.lights:
            light.step()

    def update(self, id, position):
        """
        A call to this function notifies the controller of a vehicle detected 
        by the sensor.  
        """
        print("car detected on lane {}, position {}".format(id, position))
        


             



