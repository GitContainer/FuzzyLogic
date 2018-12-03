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
            State.red: {
                'in': 0,
                'out':0
            }
        }


    def reset(self):
        """
        Reset the metrics used for arrival and queue count, and refresh the mapState.
        """
        for lane_id, light in self.lights.items():
            self.mapState[light.state] = lane_id

    def switch_green(self):
        """
        Update metrics when the green light is switching to amber by 
        converting remaining vehicles in current green lane to queue
        """
        queue = self.metrics[State.green]['in'] - self.metrics[State.green]['out']
        self.metrics[State.red]['in'] = queue

    def switch_red(self):
        """
        Update metrics when the red light is switching green by 
        converting waiting vehicles in current red lane to arrival
        """
        arrival = self.metrics[State.red]['in']
        self.metrics[State.green]['in'] = arrival
        self.metrics[State.green]['out'] = 0 #metrics[red][out]

    def add_traffic_light(self, tlight, lane_id):
        super().add_traffic_light(tlight, lane_id)
        # keep track of which lane is in which state
        self.mapState[tlight.state] = lane_id

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

    def step(self):
        super().step()
        # if there has been a switch, reset metrics properly
        greenLane = self.mapState[State.green]
        redLane = self.mapState[State.red]
        if self.lights[greenLane].state is not State.green:
            # green light turned amber
            self.switch_green()
        elif self.lights[redLane].state is not State.red:
            # red light turned green
            # (no need to handle amber light turning red)
            self.switch_red()
        print('[FLC] reset Queue and Arrival')
        self.reset()

    def update(self, lane_id, position):
        """
        1) Determine which lane is green (Arrival) and which lane is not (Queue)
        2) extend its duration with the right amount, depending on the Arrival 
            and the Queue variables
        """
        super().update(lane_id, position)
        # update metrics 
        if self.lights[lane_id].state == State.green:
            # update from current green light sensor
            if position > 0: # test if sensor D or sensor 0
                self.metrics[State.green]['in'] += 1
            else:
                self.metrics[State.green]['out'] += 1
        else:
            assert position > 0, "car crossing while amber/red light"
            self.metrics[State.red]['in'] += 1

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

    



