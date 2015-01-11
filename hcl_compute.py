import rpy2

#dictionary of max's per var
route_params = {'directions': 5, 'traffic': 2, 'speed': 45}
directions_scores = {''}
parse_interval = 30 #30 seconds
def chunk_hcl(route_data):

	#r changepoint module: detect changepoints

	#classify each segment as safe/unsafe (binary classify) -> more than N unsafes in a segment = unsafe

	#any neighboring segments with the same average are merged

	#any segments that are too short ...?

#parse a list of dicts
def parse_dicts(input):
	
	directions = []
	traffic_time = []
	speed_limit = []
	durations = []

	for leg in input:
		action = leg['action']
		directions.append(convert_action_to_score(action))

		traffic = float(leg['traffic_time'])/float(leg['base_time'])
		traffic_time.append(traffic)

		#get average speeds per link - for now
		speed = sum(leg['speed_limit'])/len(leg['speed_limit'])
		speed_limit.append(speed)

		#durations - length per leg
		durations.append(max(1, leg['traffic_time']/parse_interval))

	return directions, traffic_time, speed_limit, durations

def convert_action_to_score(action):

	action = action.lower()

	if(action.find("sharp") >= 0 or action.find("exit") >=0 or action.find("ramp") >= 0): 
		return 5
	if(action.find("merge") >= 0 or action.find("fork") >= 0 or action.find("loop") >= 0):
		return 4
	if(action.find("loop") >= 0 or action.find("turn") >= 0):
		return 3
	
	return 0


#route_data is a list of dicts
def preprocess_hcl(input):

	directions, traffic, speed, durations = parse_dicts(input)

	#directions - scoring, rule based (assume first is forward)
	directions_processed = vectorize_speedOrDirections(durations, directions[1:])

	#speed limit [30, 30, 10, 60, 60 ] : absolute change in speed limit
	speed_abs_diff = [abs(speed[i] - speed[i-1]) for i in range(1, len(speed))]
	speed_processed = vectorize_speedOrDirections(durations, speed_abs_diff)	

	#traffic (diff between traffic_time and base_time [3, 0, 0, 0, 4, 6, 8, 10, 10]
	#get increase in driving time per minute of each interval
	traffic_processed = vectorize_traffic(durations, traffic)

	#OTHER: weather - adds a multiplicative factor to everything 
	#curvature - high curvatures
	#slopes - high slopes
	#traffic signs

	return directions_processed, speed_processed, traffic_processed

#smooth the HCL
def exponential_smoothing(input):
	
	#EXPONENTIAL SMOOTHING
	#discount factor alpha
	alpha_one = 0.5
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
		print(i+j, i-j)
		smoothed.append(sum(input[i+j] * factors[j+span] for j in range(-1 * span, span+1)))

	return smoothed

#get in lists of timestamps at which var changes occur, values within each interval
#return a time series vector
def vectorize_speedOrDirections(durations, vals):
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
def vectorize_traffic(durations, vals):

	variable_vector = []
	#0 at start
	for i in range(len(vals)):
		#change at a timestamp
		variable_vector.extend([vals[i]] * durations[i])

	return variable_vector

#pass in a HERE data vector, normalize and return it
def normalize(var_name, var_vec):
	
	var_max = route_params[var_name]

	#get min to 0
	var_vec = [x - min(var_vec) for x in var_vec]
	#use max of (param, observed_param_max) in the scaling normalization
	var_vec = [100 * x / max(var_max, max(var_vec)) for x in var_vec]

	return var_vec

def compute_hcl(input):

	#get processed values
	directions, speed, traffic = preprocess_hcl(input)

	#stupid normalization
	directions = normalize('directions', directions)
	speed = normalize('speed', speed)
	traffic = normalize('traffic', traffic)

	#aggregated weighted average into one ts
	aggregate_ts = [sum(a)/len(a) for a in zip(speed, traffic, directions)]

	#calculate the weighted averages of the series
	smoothed = exponential_smoothing(aggregate_ts)

	#for every 5 seconds, calculate PCL: weighted average of average values for each variable


