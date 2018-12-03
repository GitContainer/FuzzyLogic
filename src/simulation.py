import random
import sys
from models import Controller, State
from road import Vehicle, Lane

class FuzzyLogicController(Controller):
    def __init__(self):
        super().__init__()
        # map light_state -> lane_id to keep track of which lane is green or not
        self.mapState = {}
        # car_in, car_out metrics used to compute Arrival and Queue 
        self.metrics = {
            State.green: {
                'in':0,
                'out':0
            },
            State.amber: { # this is treated as a buffer
                'in':0,
                'out':0
            },
            State.red: {
                'in': 0,
                'out':0
            }
        }
        #buffer for the state switch
        self.buffer = 0 

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
        #self.metrics[State.red]['in'] = queue

    def switch_red(self):
        """
        Update metrics when the red light is switching green by 
        converting waiting vehicles in current red lane to arrival
        """
        arrival = self.get_queue()
        self.metrics[State.green]['in'] = arrival
        self.metrics[State.green]['out'] = 0 #metrics[red][out]
        self.metrics[State.red]['in'] = self.buffer + self.metrics[State.amber]['in']
        #reset the buffers
        self.buffer = 0
        self.metrics[State.amber]['in'] = 0

    def add_traffic_light(self, tlight, lane_id):
        super().add_traffic_light(tlight, lane_id)
        # keep track of which lane is in which state
        self.mapState[tlight.state] = lane_id

    def step(self):
        super().step()
        # if there has been a switch, reset metrics properly
        greenLane = self.mapState[State.green]
        redLane = self.mapState[State.red]
        if greenLane is not None and self.lights[greenLane].state != State.green:
            # green light turned amber
            print('[FLC] green -> amber')
            self.switch_green()
        elif self.lights[redLane].state != State.red:
            # red light turned green
            # (no need to handle amber light turning red)
            print('[FLC] red -> green')
            self.switch_red()
        self.refresh()

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
        print('[FLC] arrival: {} queue: {}'.format(self.get_arrival(), self.get_queue()))
        # compute the extend period based on arrival and queue metrics



if __name__ == '__main__':
    # create a controller
    #control = Controller()
    control = FuzzyLogicController()
    # create North-to-South and West-to-East lanes
    north2south = Lane(control,S=10, D=5, name='North to South', init_state=State.green)
    west2east = Lane(control, S=10, D=5, name='West to East', init_state=State.red)

    lanes = {
        north2south.id: north2south,
        west2east.id: west2east
    }

    print("Intersection created")

    step = 0
    while (north2south.car_out < 50) and (west2east.car_out < 50):
        if step > 200:
            sys.exit(0)
        print('[STEP {}]'.format(step))
        # coin toss to generate a new car or not
        if random.uniform(0, 1) >= 0.5: 
            print('new vehicle in lane {}'.format(north2south.name))
            north2south.append(Vehicle())
        if random.uniform(0,1) >= 0.5:
            print('new vehicle in lane {}'.format(west2east.name))
            west2east.append(Vehicle())

        control.step()
        north2south.step()
        west2east.step()

        print("N2S")
        print(north2south)
        print("W2E")
        print(west2east)
        
        step+=1
        print('\n')
    
    print("N2S total wait: {}".format(north2south.total_wait))
    print("W2S total wait: {}".format(west2east.total_wait))

    



