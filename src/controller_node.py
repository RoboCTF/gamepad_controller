#!/usr/bin/env python
"""

Controller node
replacement for teleopjoy

evdev stick reading code adapted from:
https://stackoverflow.com/questions/44934309/how-to-access-the-joysticks-of-a-gamepad-using-python-evdev
author: Nick

"""
# evdev for controller input
import evdev
from evdev import ecodes, categorize

#ROS Specifics
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist

#LLC is expecting throttle in linear_x and steering in angular_z

# define the controller
dev = evdev.InputDevice(evdev.list_devices()[0])

# These are specific to the Logitech Controllers used.
CENTER_TOLERANCE = 5
STICK_MAX = 255

axis = {
    ecodes.ABS_X: 'ls_x', # 0 - 255   the middle is 127
    ecodes.ABS_Y: 'ls_y',
    ecodes.ABS_Z: 'rs_x',
    ecodes.ABS_RZ: 'rs_y'
}

center = {
    'ls_x': STICK_MAX/2,
    'ls_y': STICK_MAX/2,
    'rs_x': STICK_MAX/2,
    'rs_y': STICK_MAX/2
}

last = {
    'ls_x': STICK_MAX/2,
    'ls_y': STICK_MAX/2,
    'rs_x': STICK_MAX/2,
    'rs_y': STICK_MAX/2
}

def read_controller():
	
	# Define Publisher
	pub = rospy.Publisher("/cmd_vel",Twist,queue_size=1)
	
	throttle_value = 0
	steering_value = 0

	for event in dev.read_loop():
		
		# calibrate zero on Y button
		if event.type == ecodes.EV_KEY:
			if categorize(event).keycode[0] == "BTN_WEST":
				center['ls_x'] = last['ls_x']
				center['ls_y'] = last['ls_y']
				center['rs_x'] = last['rs_x']
				center['rs_y'] = last['rs_y']
				print( 'calibrated' )

		#read stick axis movement
		elif event.type == ecodes.EV_ABS:
			if axis[ event.code ] in [ 'ls_x', 'ls_y', 'rs_x', 'rs_y' ]:
				last[ axis[ event.code ] ] = event.value

				value = event.value - center[ axis[ event.code ] ]
				
				if abs( value ) <= CENTER_TOLERANCE:
					value = 0
					
				# normalize value
				value = -value / float(STICK_MAX/2)
				
				# correct range to [-1, 1]
				if value < -1:
					value = -1.0
				
				# set control values
				if axis[ event.code ] == 'rs_x':
					steering_value = value

				elif axis[ event.code ] == 'ls_y':
					throttle_value = value
					
				cmd_msg = Twist()
				cmd_msg.linear.x = throttle_value
				cmd_msg.angular.z = steering_value
				
				pub.publish(cmd_msg)
					
				print("%1.2f, %1.2f"%(throttle_value, steering_value))

# ROS Node section
class Controller():
	def __init__(self):
		"""
		pub = rospy.Publisher("/cmd_vel",Twist,queue_size=1)
		
		
		# Create the msg
		msg = Twist()
		msg.linear.x = ls_y
		msg.angular.z = rs_x
		"""

if __name__ == "__main__":
	print("Running the Controller")
	
	rospy.init_node("controller")
	try:
		read_controller()
	except rospy.ROSInterruptException:
		pass
	
	
