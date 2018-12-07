"""
Contains the base classes for the simulation.
"""
import numpy as np
from enum import IntEnum
from abc import ABCMeta, abstractmethod
from trafficLightFuzzyController import traficLightFuzzyController as TLFC


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
        n = (((self.state - 1) + 1) % 3) + 1
        return State(n)

    def step(self):
        """
        At each call, the current clock time counter is decreased until it reaches 0, at 
        which point the light switches to its next state (and counter is reset). 
        """
        self.clocks[self.state] -= 1
        # print('({}) clock: {}'.format(self.state,  self.clocks[self.state]))
        if self.clocks[self.state] == 0:
            # reset
            self.clocks[self.state] = self.__clock_reset[self.state]
            # next state 
            self.state = self.__next_state()
            # print('switch to: {}'.format(self.state))


class Controller(object):
    """
    Base Class for controllers. 
    A controller monitors the state of each traffic light in the system 
    and enforces a cycle of green-amber-red states. 
    Based on inputs from sensors, the controller can extend the duration of the green state
    of a specific traffic light. 
    """

    def __init__(self):
        # map of (lane_id -> light) in the system
        self.lights = {}

    def add_traffic_light(self, tlight: TrafficLight, lane_id):
        """
        Register the given traffic light to this controller.  
        """
        # ensure that the added light does not have the same colour
        if len(self.lights) > 0:
            hasGreen = False
            for i, l in self.lights.items():
                hasGreen = l.state == State.green or hasGreen
            if hasGreen and tlight.state == State.green:
                tlight.state = State.red
        self.lights[lane_id] = tlight

    def step(self):
        """
        This function has to be called at each timestep to simulate time. 
        """
        for lane_id, light in self.lights.items():
            light.step()

    def update(self, id, position):
        """
        A call to this function notifies the controller of a vehicle detected 
        by the sensor.  
        """
        # print("car detected on lane {}, position {}".format(id, position))


class FuzzyLogicController(Controller):
    def __init__(self):
        super().__init__()
        # map light_state -> lane_id to keep track of which lane is green or not
        self.mapState = {}
        # car_in, car_out metrics used to compute Arrival and Queue 
        self.metrics = {
            State.green: {
                'in': 0,
                'out': 0
            },
            State.amber: {  # this is treated as a buffer
                'in': 0,
                'out': 0
            },
            State.red: {
                'in': 0,
                'out': 0
            }
        }
        # buffer for the state switch
        self.buffer = 0
        # control variable to avoid lane starvation 
        self.extended_to_max = False

    def get_arrival(self):
        """
        Returns the Arrival value.
        """
        return self.metrics[State.green]['in'] - self.metrics[State.green]['out']

    def get_queue(self):
        """
        Returns the Queue value.
        """
        return self.metrics[State.red]['in']

    def refresh(self):
        """
        Refresh the mapState.
        """
        for colour in [State.green, State.amber, State.red]:
            self.mapState[colour] = None
        for lane_id, light in self.lights.items():
            self.mapState[light.state] = lane_id

    def switch_green(self):
        """
        Update metrics when the green light is switching to amber by 
        converting remaining vehicles in current green lane to queue
        """
        queue = self.get_arrival()
        self.buffer = queue
        # self.metrics[State.red]['in'] = queue

    def switch_red(self):
        """
        Update metrics when the red light is switching green by 
        converting waiting vehicles in current red lane to arrival
        """
        arrival = self.get_queue()
        self.metrics[State.green]['in'] = arrival
        self.metrics[State.green]['out'] = 0  # metrics[red][out]
        self.metrics[State.red]['in'] = self.buffer + self.metrics[State.amber]['in']
        # reset the buffers
        self.buffer = 0
        self.metrics[State.amber]['in'] = 0

    def add_traffic_light(self, tlight, lane_id):
        super().add_traffic_light(tlight, lane_id)
        # keep track of which lane is in which state
        self.mapState[tlight.state] = lane_id

    def update(self, lane_id, position):
        """
        1) Determine which lane is green (Arrival) and which lane is not (Queue)
        2) extend its duration with the right amount, depending on the Arrival 
            and the Queue variables
        """
        super().update(lane_id, position)

        state = self.lights[lane_id].state
        # update metrics 
        if position == 0:
            assert state == State.green, "car crossing while amber/red light"
            self.metrics[state]['out'] += 1
        else:
            self.metrics[state]['in'] += 1
        # print('[FLC] arrival: {} queue: {}'.format(self.get_arrival(), self.get_queue()))
        # compute the extend period based on arrival and queue metrics

    def extend(self):
        """
        Extend the time of the green light (and the red light) according to the value retured by the Fuzzy Control System.
        """
        # id of the lane with green and red light on
        greenL = self.mapState[State.green]
        redL = self.mapState[State.red]
        assert greenL is not None, 'no green light'
        fuzzy = TLFC()

        if not self.extended_to_max:
            extension = np.rint(fuzzy.get_extension(self.get_queue(), self.get_arrival()))
            green_clock = self.lights[greenL].clocks[State.green]
            green_clock = min(20, green_clock + extension)
            self.extended_to_max = True if green_clock == 20 else False

            red_clock = self.lights[redL].clocks[State.red]
            red_clock = min(20, red_clock + extension)

            # print('[FLC] clock set at {}'.format(green_clock) )
            self.lights[redL].clocks[State.red] = red_clock
            self.lights[greenL].clocks[State.green] = green_clock

    def step(self):
        super().step()
        # if there has been a switch, reset metrics properly
        greenLane = self.mapState[State.green]
        redLane = self.mapState[State.red]
        if greenLane is not None:
            self.extend()
            if self.lights[greenLane].state != State.green:
                # green light turned amber
                # print('[FLC] green -> amber')
                self.switch_green()
        elif self.lights[redLane].state != State.red:
            # red light turned green
            # (no need to handle amber light turning red)
            # print('[FLC] red -> green')
            self.switch_red()
        self.refresh()
