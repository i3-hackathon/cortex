import rpy2

#dictionary of route variable means and variances
route_var_params = {'turns': }

def chunk_hcl(route_data):

	#r changepoint module: detect changepoints

	#classify each segment as safe/unsafe (binary classify) -> more than N unsafes in a segment = unsafe

	#any neighboring segments with the same average are merged

	#any segments that are too short ...?


def preprocess_hcl(route_data):

	#durations = [3, 8, 4]
	#speed = [10, 20, 30]
	#traffic = [30, 30, 30]


	#directions - [0, 0, 1, 0, 0, ...] 1's are any sort of risky move: turn etc.


depart, departAirport, arrive, arriveAirport, arriveLeft, arriveRight,
leftLoop,leftUTurn,sharpLeftTurn, leftTurn, continue, slightRightTurn, rightTurn,sharpRightTurn,
rightUTurn, rightLoop, leftExit, rightExit, leftRamp, rightRamp, leftFork, middleFork, rightFork,
leftMerge, rightMerge, nameChange, trafficCircle, ferry ,leftRoundaboutExit1, leftRoundaboutExit2,
leftRoundaboutExit3, leftRoundaboutExit4, leftRoundaboutExit5, leftRoundaboutExit6,
leftRoundaboutExit7, leftRoundaboutExit8, leftRoundaboutExit9, leftRoundaboutExit10,
leftRoundaboutExit11, leftRoundaboutExit12, rightRoundaboutExit1, rightRoundaboutExit2,
rightRoundaboutExit3, rightRoundaboutExit4, rightRoundaboutExit5, rightRoundaboutExit6,
rightRoundaboutExit7, rightRoundaboutExit8, rightRoundaboutExit9, rightRoundaboutExit10,
rightRoundaboutExit11, rightRoundaboutExit12]

	#speed limit [30, 30, 10, 60, 60 ] : absolute change in speed limit
	speed_abs_diff = [abs(speed[i] - speed[i-1]) for i in range(1, len(speed))]
	speed_abs_diff_norm = normalize('speed', speed_abs_diff)
	speed_processed = vectorize(durations, speed_abs_diff_norm)	

	#traffic (diff between traffic_time and base_time [3, 0, 0, 0, 4, 6, 8, 10, 10]
	#get increase in driving time per minute of each interval
	traffic_per = [traffic[i] / durations[i] for i in range(len(durations))]
	traffic_per_norm = normalize('traffic', traffic_per)
	traffic_per_norm_processed = vectorize(durations, traffic_per_norm)

	#OTHER: weather - adds a multiplicative factor to everything 
	#curvature - high curvatures
	#slopes - high slopes
	#traffic signs

	return speed_processed, traffic_per_norm_processed, directions_processed



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

def get_direction(direction_input):



#get in lists of timestamps at which var changes occur, values within each interval
#return a time series vector
def vectorize(durations, vals):
	variable_vector = [0] * durations[0]
	#0 at start
	for i in range(len(vals)):
		#change at a timestamp
		variable_vector.extend([vals[i]])

		#no change in the interval
		variable_vector.extend([0] * durations[i+1])

	return variable_vector

#pass in a HERE data vector, normalize and return it
def normalize(var_name, var_vec):
	
	[var_mean, var_variance] = route_params[var_name]
	
	var_vec = [value - var_mean for value in var_vec]
	var_vec = [value/value_variance for value in var_vec]

	return var_vec

def compute_hcl(route_data):
	#get processed values
	speed, traffic, directions = preprocess(route_data)

	#aggregated weighted average into one ts
	aggregate_ts = [sum(a)/len(a) for a in zip(speed, traffic, directions)]

	#calculate the weighted averages of the series
	smoothed = exponential_smoothing(aggregate_ts)
	
	#for every 5 seconds, calculate PCL: weighted average of average values for each variable
	

