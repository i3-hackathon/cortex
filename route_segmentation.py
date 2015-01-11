def precompute_hcl(route_data):

	#preprocess hcl inputs
	processed_route_data = preprocess_hcl(route_data)

	#compute base hcl graph
	compute_hcl(processed_route_data)

	#chunk the graph
	chunk_hcl()

	#return safe times and unsafe times
	return

def check_trigger_app_on():
	
	type_of_event = None

	#conditions that can trigger the app to turn on

	#if we should trigger, return a trigger event; otherwise return -1.
	#on the server side keep a dictionary mapping event types with how often to check back in
	return type_of_event


def keep_trigger_app_on(trigger_event):

	next_event = trigger_event
	
	#conditions that can trigger the app to stay on are less severe than conditions that can trigger an app to turn on
	#this prevents the app from turning on and off constantly. the trigger period ends when we are confident
	#that the danger is over

	return next_event