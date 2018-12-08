import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class traficLightFuzzyController():
    def __init__(self):
        # first we need to design the membership functions

        # The arrival membership function
        # assign the bounds of the membership function
        arrivals = ctrl.Antecedent(np.arange(0, 16, 1), 'arrivals')

        # assign the bounds of every fuzzy member
        arrivals["AN"] = fuzz.trimf(arrivals.universe, [0, 0, 2])
        arrivals["F"] = fuzz.trimf(arrivals.universe, [1,4 , 7])
        arrivals["MY"] = fuzz.trimf(arrivals.universe, [5, 9, 13])
        arrivals["TMY"] = fuzz.trimf(arrivals.universe, [10, 15, 15])

        # the queue membership function
        # assign the bounds of the queue membership function
        queue = ctrl.Antecedent(np.arange(0, 16, 1), 'queue')

        # assign the the bounds of each fuzzy member
        queue["VS"] = fuzz.trimf(queue.universe, [0, 0, 2])
        queue["S"] = fuzz.trimf(queue.universe, [1, 4, 7])
        queue["M"] = fuzz.trimf(queue.universe, [5, 9, 13])
        queue["L"] = fuzz.trimf(queue.universe, [10, 15, 15])

        # the extension membership function
        # assign the bounds of the extension membership function
        extension = ctrl.Consequent(np.arange(0, 7, 1), 'extension')

        # assign the bounds of each fuzzy member
        extension["Z"] = fuzz.trimf(extension.universe, [0, 0, 2])
        extension["SO"] = fuzz.trimf(extension.universe, [0, 2, 4])
        extension["ML"] = fuzz.trimf(extension.universe, [2, 4, 6])
        extension["LO"] = fuzz.trimf(extension.universe, [4, 6, 6])
        self.extension =  extension

        # implement all the rules available
        rule1 = ctrl.Rule(arrivals["AN"] & queue["VS"], extension["Z"])
        rule2 = ctrl.Rule(arrivals["AN"] & queue["S"], extension["Z"])
        rule3 = ctrl.Rule(arrivals["AN"] & queue["M"], extension["Z"])
        rule4 = ctrl.Rule(arrivals["AN"] & queue["L"], extension["Z"])
        rule5 = ctrl.Rule(arrivals["F"] & queue["VS"], extension["SO"])
        rule6 = ctrl.Rule(arrivals["F"] & queue["S"], extension["SO"])
        rule7 = ctrl.Rule(arrivals["F"] & queue["M"], extension["Z"])
        rule8 = ctrl.Rule(arrivals["F"] & queue["L"], extension["Z"])
        rule9 = ctrl.Rule(arrivals["MY"] & queue["VS"], extension["ML"])
        rule10 = ctrl.Rule(arrivals["MY"] & queue["S"], extension["ML"])
        rule11 = ctrl.Rule(arrivals["MY"] & queue["M"], extension["SO"])
        rule12 = ctrl.Rule(arrivals["MY"] & queue["L"], extension["Z"])
        rule13 = ctrl.Rule(arrivals["TMY"] & queue["VS"], extension["LO"])
        rule14 = ctrl.Rule(arrivals["TMY"] & queue["S"], extension["ML"])
        rule15 = ctrl.Rule(arrivals["TMY"] & queue["M"], extension["ML"])
        rule16 = ctrl.Rule(arrivals["TMY"] & queue["L"], extension["SO"])

        # implement the control system that does the fuzzification, composition inference and defuzzification for us
        traffic_lights_ctrl = ctrl.ControlSystem(rules=
                                                 [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
                                                  rule11,
                                                  rule12, rule13, rule14, rule15,
                                                  rule16])
        if graphs:
            extension.view()
            arrivals.view()
            queue.view()
            traffic_lights_ctrl.view()

        self.traffic_lights_simulation = ctrl.ControlSystemSimulation(traffic_lights_ctrl)

    def get_extension(self, cars_in_queue, cars_arriving_at_green_light):
        self.traffic_lights_simulation.inputs({"arrivals":cars_arriving_at_green_light,"queue":cars_in_queue})
        self.traffic_lights_simulation.compute()
        if graphs:
            self.extension.view(sim=self.traffic_lights_simulation)
        return self.traffic_lights_simulation.output["extension"]


#fuzzy_controller = traficLightFuzzyController()
#for i in range(0,7):
#    for j in range(0,7):
#        print("for queue equal to {0} cars and {1} cars arriving at the traffic light".format(i,j))
#        print("the controller will extend green with {0} seconds".format(fuzzy_controller.get_extension(i,j)))
graphs = False
# fuzzycontroller= traficLightFuzzyController()
# fuzzycontroller.get_extension(6,12)