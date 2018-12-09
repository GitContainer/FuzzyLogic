import random
import sys
from models import Controller, State, FuzzyLogicController
from road import Vehicle, Lane
from getopt import gnu_getopt, GetoptError




def usage():
    s = "usage: simulation.py [OPTIONS] \n"
    s+= "By default, simulation.py launches 1 simulation for each type of controller. \n"
    s+= "The following options may be provided:\n"
    s+= "-l\n\t enables logs\n"
    s+= "-h\n\t print this help\n"
    s+= "-n INT\n\t define the number of simulation\n"
    s+= "-s 'fixed' or 'fuzzy' \n\t launch the simulation with only fixed-time or fuzzy controller\n"
    print(s)

if __name__ == '__main__':
    wait_fuzzy = []
    wait_fixed = []
    simulations = 1
    mono = False
    controller_fuzzy = False
    log = False
    wait = []

    options = 'hln:s:'
    try:
        opt_arg, args =  gnu_getopt(sys.argv[1:], options)
        for opt, arg in opt_arg:
            if opt == '-l':
                log = True
            elif opt == '-n':
                simulations = int(arg)
            elif opt == '-h':
                usage()
            elif opt == '-s':
                if arg == 'fixed':
                    mono = True
                    simulations /= 2
                elif arg == 'fuzzy':
                    controller_fuzzy = True
                    mono = True
                    simulations /= 2
                else:
                    raise GetoptError()
    except GetoptError:
        usage()
        sys.exit(-1)


    #simulations = 5 if len(sys.argv) == 1 else int(sys.argv[1])
    for i in range(int(simulations * 2)):
        # create a controller
        if mono:
            control = FuzzyLogicController(log=log) if controller_fuzzy else Controller(log=log)
        else:
            control = Controller(log=log) if i % 2 == 0 else FuzzyLogicController(log=log)
        
        # create North-to-South and West-to-East lanes
        north2south = Lane(control, S=15, D=7, name='North to South', init_state=State.green)
        west2east = Lane(control, S=15, D=7, name='West to East', init_state=State.red)

        lanes = {
            north2south.id: north2south,
            west2east.id: west2east
        }

        if log:
            print("Intersection created")

        step = 0
        while (north2south.car_out < 50) and (west2east.car_out < 50):
            if step > 400:
                sys.exit(0)
            if log:
                print('[STEP {}]'.format(step))
            # coin toss to generate a new car or not
            if random.uniform(0, 1) >= 0.5:  #
                if log:
                    print('new vehicle in lane {}'.format(north2south.name))
                north2south.append(Vehicle())
            if random.uniform(0, 1) >= 0.8:  # fewer cars on lane west2east
                if log:
                    print('new vehicle in lane {}'.format(west2east.name))
                west2east.append(Vehicle())

            control.step()
            north2south.step()
            west2east.step()

            if log:
                print("N2S")
                print(north2south) #comment to avoid printing the lane
                print("W2E")
                print(west2east) #comment to avoid printing the lane
                print('\n')

            step += 1

        total_wait_time = north2south.total_wait + west2east.total_wait
        if not mono:
            if i % 2 == 0:
                wait_fixed.append(total_wait_time)
            else:
                wait_fuzzy.append(total_wait_time)
        else:
            wait.append(total_wait_time)
        print(" {} % of the way there".format(round(i / (simulations * 2) * 100, 2)))
    
    print(" 100 % of the way there")
    if not mono:
        print("total average wait time for {} simulations of fixed controller was {}".format(simulations,
            sum(wait_fixed) / len(wait_fixed)))
        print("total average wait time for {} simulations of fuzzy controller was {}".format(simulations,
            sum(wait_fuzzy) / len(wait_fuzzy)))
    else:
         print("total average wait time for {} simulations of controller was {}".format(simulations,
            sum(wait) / len(wait)))

