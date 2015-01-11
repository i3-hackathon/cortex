import rpy2.interactive.packages
import rpy2.interactive as r
from rpy2 import robjects
import pylab
import matplotlib.pyplot as plt
import random


class ShiftAI:

    #dictionary of max's per var
    route_params = {'directions': 5, 'traffic': 1, 'speed': 45}

    def __init__(self, parse_interval=30):

        # HCL Vector
        self.hcl_vector = []

        # Dictionary of max values per variable
        self.route_params = {'directions': 5, 'traffic': 1, 'speed': 45}

        #### <DEMO> ####
        # Number of seconds per parse
        self.parse_interval = parse_interval
        self.speed_up_factor = 10
        self.delta_dev = []
        self._init_demo_delta_deviations()
        #### </DEMO> ####


    def _init_demo_delta_deviations(self, count=15):
        ''' Manually defined delta deviations for demo. '''

        for i in range(count):
            self.delta_dev.append({
                    'accel': 0.0,
                    'brakes': 0.0,
                    'lane': 0.0,
                    'rain': 0.0,
                    'rpm': 0.0,
                    'speed': 0.0,
                    'steer_change': 0.0})

        # Perturbations from observed data
        if count > 5:
            self.delta_dev[4]['brakes'] = 0.7
            self.delta_dev[5]['brakes'] = 0.7
            self.delta_dev[5]['steer_change'] = 0.8


    #input is list of dicts
    def compute_hcl(self, input):

        #compute base hcl graph
        hcl = self.precompute_hcl(input)

        #chunk the graph
        timestamps, unsafe, hcl_vector, parse_interval = self.chunk_hcl(hcl)

        self.hcl_vector = hcl_vector

        #return safe times and unsafe times
        return timestamps, unsafe, hcl_vector, parse_interval


    def chunk_hcl(self, hcl_vector):

        rpy2.interactive.packages.importr('changepoint')
        #r changepoint module: detect changepoints
        r_vector = rpy2.interactive.FloatVector(hcl_vector)
        rlib = rpy2.interactive.packages.packages

        as_vector = robjects.r("cpt.mean") # Unused, can I comment this out?
        #change point analysis. heuristic for max # of changepoints
        max_cpts = round(len(hcl_vector))/8
        results = rlib.changepoint.cpt_mean(r_vector,penalty="SIC",pen_value=0,method="BinSeg",Q=max_cpts,test_stat="Normal")
        changepoints = [int(x) for x in sorted(results.do_slot("cpts"))]

        #compute safety of each segment
        prev_cpt = 0
        #cpt_avgs = []

        #set threshold for "unsafe": mean value
        threshold = sum(hcl_vector)/len(hcl_vector)
        unsafe = [0] * len(changepoints)

        prev_cpt = 0
        #calculate # of unsafe points in each segment. classify each segment as safe/unsafe -> more than N unsafes in a segment = unsafe
        for i in range(len(changepoints)-1):
            for j in range(prev_cpt, changepoints[i]):
                if(hcl_vector[j] > threshold):
                    unsafe[i] += 1
            #this is janky heuristic
            if(unsafe[i] > min(2*round((changepoints[i+1] - changepoints[i])/3), 3)):
                unsafe[i] = 1
            else:
                unsafe[i] = 0
            prev_cpt = changepoints[i]

        #plot the thing
        #plt.plot(range(len(smoothed)), smoothed, '-o')
        #plt.show()

        plt.plot(range(len(hcl_vector)), hcl_vector, '-o')

        final_changepoints = []
        final_unsafe = [unsafe[0]]
        i = 1
        #any neighboring segments with the same average are merged
        prev_unsafe = changepoints[0]
        while i<len(changepoints):
            if(unsafe[i] != prev_unsafe):
                final_changepoints.append(changepoints[i-1])
                final_unsafe.append(unsafe[i])
            prev_unsafe = unsafe[i]
            i = i + 1

        for i in range(len(final_changepoints)):
            plt.axvline(x=final_changepoints[i], linewidth=2, color='k')

        pylab.savefig('static/hcl.png')
        plt.clf()

        #return expected timestamps, safe/unsafe per segment, full hcl vector (one point per parse_interval), parse_interval
        return [x * self.parse_interval for x in final_changepoints], final_unsafe, hcl_vector, self.parse_interval

    #parse a list of dicts
    def parse_dicts(self, input):
        
        directions = []
        traffic_time = []
        speed_limit = []
        durations = []

        for leg in input:
            action = leg['action']
            directions.append(self.convert_action_to_score(action))

            traffic = float(leg['traffic_time'])/float(leg['base_time'])
            traffic_time.append(traffic)

            #get average speeds per link - for now
            if len(leg['speed_limit']) == 0:
                try:
                    speed = speed_limit[-1]
                except:
                    speed = 50
            else:
                speed = sum(leg['speed_limit'])/len(leg['speed_limit'])
            speed_limit.append(speed)

            #durations - length per leg
            durations.append(max(1, leg['traffic_time']/self.parse_interval))
        
        return directions, traffic_time, speed_limit, durations

    def convert_action_to_score(self, action):

        action = action.lower()

        if(action.find("sharp") >= 0 or action.find("exit") >=0 or action.find("ramp") >= 0): 
            return 5
        if(action.find("merge") >= 0 or action.find("fork") >= 0 or action.find("loop") >= 0):
            return 4
        if(action.find("loop") >= 0 or action.find("turn") >= 0):
            return 3
        
        return 0


    #route_data is a list of dicts
    def preprocess_hcl(self, input):

        directions, traffic, speed, durations = self.parse_dicts(input)

        #directions - scoring, rule based (assume first is forward)
        directions_processed = self.vectorize_speedOrDirections(durations, directions[1:])

        #speed limit [30, 30, 10, 60, 60 ] : absolute change in speed limit
        speed_abs_diff = [abs(speed[i] - speed[i-1]) for i in range(1, len(speed))]
        speed_processed = self.vectorize_speedOrDirections(durations, speed_abs_diff)

        #traffic (diff between traffic_time and base_time [3, 0, 0, 0, 4, 6, 8, 10, 10]
        #get increase in driving time per minute of each interval
        traffic_processed = self.vectorize_traffic(durations, traffic)

        #OTHER: weather - adds a multiplicative factor to everything 
        #curvature - high curvatures
        #slopes - high slopes
        #traffic signs

        return directions_processed, speed_processed, traffic_processed

    #smooth the HCL
    def exponential_smoothing(self, input):
        
        #EXPONENTIAL SMOOTHING
        #discount factor alpha
        alpha = 0.5
        #sliding window span
        span = 5
        #exponential discounting function is discount = 0.5 ^ n where n is the steps away from center. max steps = span = 5
        factors = [alpha ** abs(n) for n in range(-1 * span, span + 1)]
        #normalize
        factors = [factor / sum(factors) for factor in factors]
        
        #add 0's at start and end
        dummy = [0]*span
        input = dummy + input + dummy

        smoothed = []
        for i in range(span, len(input)-span):
            smoothed.append(sum(input[i+j] * factors[j+span] for j in range(-1 * span, span+1)))

        return smoothed

    #get in lists of timestamps at which var changes occur, values within each interval
    #return a time series vector
    def vectorize_speedOrDirections(self, durations, vals):
        variable_vector = [0] * durations[0]
        #0 at start
        for i in range(len(vals)):
            #change at a timestamp

            variable_vector.extend([vals[i]])

            #no change in the interval
            if durations[i+1] >= 2:
                variable_vector.extend([0] * (durations[i+1]-1))

        return variable_vector

    #return a time series vector
    def vectorize_traffic(self, durations, vals):

        variable_vector = []
        #0 at start
        for i in range(len(vals)):
            #change at a timestamp
            variable_vector.extend([vals[i]] * durations[i])

        return variable_vector

    #pass in a HERE data vector, normalize and return it
    def normalize(self, var_name, var_vec):

        var_max = self.route_params[var_name]

        #get min to 0
        var_vec = [x - min(var_vec) for x in var_vec]
        #use max of (param, observed_param_max) in the scaling normalization
        var_vec = [100 * x / max(var_max, max(var_vec)) for x in var_vec]

        return var_vec

    def precompute_hcl(self, input):

        #get processed values
        directions, speed, traffic = self.preprocess_hcl(input)

        #stupid normalization
        directions = self.normalize('directions', directions)
        speed = self.normalize('speed', speed)
        traffic = self.normalize('traffic', traffic)

        #aggregated weighted average into one ts
        aggregate_ts = [sum(a)/len(a) for a in zip(speed, traffic, directions)]

        #calculate the weighted averages of the series
        smoothed = self.exponential_smoothing(aggregate_ts)

        return smoothed

    ############################################
    #REALTIME STUFF

    #IRL, compute based on history of rides
    #here, return a preset expectation
    def expectation_route(self):
        pass

    #just for training
    def get_training_input(self, test):

        sped_up_vector = []

        #every 10 seconds, get a data point for those 10 seconds
        for i in range(len(test)/self.speed_up_factor):
            
            start_point = i * self.speed_up_factor
            end_point = (i+1) * self.speed_up_factor

            accel = False
            lane_departure = False
            rpm = False
            speed = False
            steer_min = test[start_point]['steering_wheel_angle']
            steer_max = steer_min

            for j in range(start_point, end_point):
                accel = accel or test[j]['accelerometer_threshold']
                lane_departure = lane_departure or test[j]['lane_departure']
                rpm = rpm or test[j]['rpm_threshold']
                speed = speed or test[j]['speed_threshold']
                steer_min = min(steer_min, test[j]['steering_wheel_angle']) 
                steer_max = max(steer_min, test[j]['steering_wheel_angle']) 

            steer_change = steer_max - steer_min
            brakes = test[end_point]['brake_torque']
            rain = test[end_point]['rain_intensity']

            sped_up_vector.append({"accel": accel, "lane": lane_departure, "rpm": rpm, "speed": speed, "steer_change": steer_change, "brakes": brakes, "rain": rain})

        return sped_up_vector

    def get_delta(self, delta_input, i):

        #calculate expectations
        #here they are hardcoded
        #delta_out = []
        #get normalized delta: observed - expectations (off historical data). here, randomly generated w/ preset perturbations
         
        delta_curr = {'accel': random.normalvariate(0, 0.1) + self.delta_dev[i]['accel'],
        'brakes': random.normalvariate(0, 0.1) + self.delta_dev[i]['brakes'],
        'lane': random.normalvariate(0, 0.1) + self.delta_dev[i]['lane'],
        'rain': random.normalvariate(0, 0.1) + self.delta_dev[i]['rain'],
        'rpm': random.normalvariate(0, 0.1) + self.delta_dev[i]['rpm'],
        'speed': random.normalvariate(0, 0.1) + self.delta_dev[i]['speed'],
        'steer_change': random.normalvariate(0, 0.1) + self.delta_dev[i]['steer_change']}

        return delta_curr

    #at each slice of time, pass in a delta vector. then detect events for each event type
    def transform_delta_to_event(self, demoDataPoint, inputDelta, currTriggerState, states_remaining):

        #for each variable, transform delta into a score incorporating the baseline

        #alpha is the weight to delta. 1-alpha the weight to the hcl baseline. get the aggregate score.
        alpha = 0.75

        deltaSlice = self.get_delta(inputDelta, demoDataPoint)

        scores = {}

        if(states_remaining > 0):
            context = ['already_on']
        else:
            context = []

        trigger = False
        for key in deltaSlice.keys():
            score = alpha * deltaSlice[key] + (1-alpha) * (self.hcl_vector[int(round(demoDataPoint * 5 / self.parse_interval))])/max(self.hcl_vector) 
            scores[key] = score

            #from scores to events
            if(score > 0.5):
                trigger = True
                states_remaining = 1
                if(context == ['already_on']):
                    context = [key]
                else:
                    context.append(key)

        if(trigger == False and states_remaining > 0):
            states_remaining = states_remaining - 1
            return True, context, states_remaining
        else:
            return trigger, context, states_remaining
