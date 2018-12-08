import random
import sys
from models import Controller, State, FuzzyLogicController
from road import Vehicle, Lane

if __name__ == '__main__':
    wait_fuzzy = []
    wait_fixed = []
    simulations = 5 if len(sys.argv) == 1 else int(sys.argv[1])
    for i in range(simulations * 2):
        # create a controller
        control = Controller() if i % 2 == 0 else FuzzyLogicController()
        # create North-to-South and West-to-East lanes
        north2south = Lane(control, S=15, D=7, name='North to South', init_state=State.green)
        west2east = Lane(control, S=15, D=7, name='West to East', init_state=State.red)

        lanes = {
            north2south.id: north2south,
            west2east.id: west2east
        }

        # print("Intersection created")

        step = 0
        while (north2south.car_out < 50) and (west2east.car_out < 50):
            if step > 400:
                sys.exit(0)
            # print('[STEP {}]'.format(step))
            # coin toss to generate a new car or not
            if random.uniform(0, 1) >= 0.5:  #
                # print('new vehicle in lane {}'.format(north2south.name))
                north2south.append(Vehicle())
            if random.uniform(0, 1) >= 0.8:  # fewer cars on lane west2east
                # print('new vehicle in lane {}'.format(west2east.name))
                west2east.append(Vehicle())

            control.step()
            north2south.step()
            west2east.step()

            # print("N2S")
            # print(north2south) #comment to avoid printing the lane
            # print("W2E")
            # print(west2east) #comment to avoid printing the lane

            step += 1
            # print('\n')

        total_wait_time = north2south.total_wait + west2east.total_wait
        if i % 2 == 0:
            wait_fixed.append(total_wait_time)
        else:
            wait_fuzzy.append(total_wait_time)
        print(" {} % of the way there".format(round(i / (simulations * 2) * 100, 2)))
    print("total average wait time for 50 simulations of fixed controller was {}".format(
        sum(wait_fixed) / len(wait_fixed)))
    print("total average wait time for 50 simulations of fuzzy controller was {}".format(
        sum(wait_fuzzy) / len(wait_fuzzy)))
