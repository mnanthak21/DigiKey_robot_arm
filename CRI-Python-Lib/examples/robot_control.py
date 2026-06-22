import logging
import asyncio
from time import sleep
from cri_lib import CRIController

# Arm orientations along A, B, and C axes
A, B, C = (-179, 0, 179)

# bounds at z = 20mm
min_x, max_z = (100, 400)
min_y, max_y = (-300, 300)
max_z = 150

# TODO - determine bin configuration
bin_x = 200
bin_y_scalar = 100
bin_drop_z = 50

# midpoint - the position of the arm right before placing 
mid_x, mid_y, mid_z = (200, 0, 100)

# sidepoint - the position of the arm after every successful place
        # we move to the side so the camera can capture a photo without obstruction
side_x, side_y, side_z = (150, -250, 100)

sharpie_height = 50

diag_len = 5

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# CRIController is the main interface for controlling the iRC
controller = CRIController()

def init_robot():
    # Connect to default iRC IP
    if not controller.connect("192.168.3.11"):
        logger.error("Unable to connect to iRC! Ensure the simulator is running.")
        quit()

    # Acquire active control.
    controller.set_active_control(True)
    logger.info("Acquired active control.")

    # Enable motors to reference
    logger.info("Enabling motors...")
    controller.enable()
    sleep(2)

    # Reference motors
    controller.get_referencing_info()
    ref_state = controller.reference_all_joints()

    if not ref_state:
        logger.info("Error with referencing, exiting...")
        controller.disable()
        controller.close()
        quit()
    sleep(2)

    # Re-enable motors to run
    controller.enable()
    controller.get_referencing_info()

    # Wait until kinematics are ready
    logger.info("Waiting for kinematics to be ready...")
    controller.wait_for_kinematics_ready(10)
    controller.set_override(100.0)

def exit_robot():
    # Disable motors and disconnect
    logger.info("Disabling motors and disconnecting...")
    controller.disable()
    controller.close()

    logger.info("Script execution completed successfully.")

# opens the jaws by driving digital outputs
def open_end_effector():
    controller.set_dout(31, False)
    controller.set_dout(30, True)
    sleep(.75)

# closes the jaws by driving digital outputs
def close_end_effector():
    controller.set_dout(30, False)
    controller.set_dout(31, True)
    sleep(.75)

# helper function to move the arm to midpoint
def move_midpoint():
    controller.move_cartesian(mid_x, mid_y, mid_z, A,B,C,0,0,0,100,'#base',True)

# helper function to move the arm to sidepoint
def move_sidepoint():
    controller.move_cartesian(side_x, side_y, side_z, A,B,C,0,0,0,100,'#base',True)

# moves to specified coordinates
def move_to(cart_x, cart_y, cart_z, speed):
    controller.move_cartesian(cart_x, cart_y, cart_z, A,B,C,0,0,0,speed,'#base',True)

# moves to specified coordinates, picks up object, and moves to midpoint
def pick(cart_x, cart_y, cart_z):
    open_end_effector()
    controller.move_cartesian(cart_x, cart_y, side_z, A,B,C,0,0,0,100,'#base',True)
    controller.move_cartesian(cart_x, cart_y, cart_z, A,B,C,0,0,0,100,'#base',True)
    # controller.move_joints_relative(0,0,0,0,0,0,0,0,0,100,True) # rotate end-effector to match object orientation
    close_end_effector()
    move_midpoint()

def place_at(x, y):
    controller.move_cartesian(x, y, 150, A,B,C,0,0,0,100,'#base',True)
    open_end_effector()

# moves to specified bin, drops object, and moves to sidepoint
def place(bin):
    controller.move_cartesian(bin_x, 200 - bin_y_scalar * bin, bin_drop_z, A,B,C,0,0,0,100,'#base',True)
    open_end_effector()
    controller.move_cartesian(side_x, side_y, side_z, A,B,C,0,0,0,100,'#base',True)

# draws an "X" at specified coordinates
def draw(x, y):
    move_to(x + diag_len, y - diag_len, sharpie_height, 100)
    move_to(x - diag_len, y + diag_len, sharpie_height, 30)
    move_to(x - diag_len, y + diag_len, sharpie_height + 10, 30)
    move_to(x - diag_len, y - diag_len, sharpie_height, 30)
    move_to(x + diag_len, y + diag_len, sharpie_height, 30)
    move_to(250, 0, sharpie_height + 100, 100)

# storage for last valid move read from file
new_move_coord_x, new_move_coord_y = 0,0
moving = False

def set_moving(bool_moving):
	global moving
	moving = bool_moving

def get_moving():
	global moving
	return moving

# reads the file and determines if there is a new move waiting
def poll_move():
	move_file = open("/home/mohnish_nanthakumar/cv/new_move.txt", 'r') # open file for reading
	
	# store move information
	new_move_str = move_file.read()
	new_move_arr = new_move_str.split(" ")
	move_file.close()
	# if the arm has not started executing on the move in the file, prepare for a move
	if (int(new_move_arr[2]) == 0) and not get_moving():
		global new_move_coord_x, new_move_coord_y
		set_moving(True)
		new_move_coord_x = float(new_move_arr[0])
		new_move_coord_y = float(new_move_arr[1])
		return True

	return False

# set the move-completed flag in the file
def update_move_file():
	move_file = open("/home/mohnish_nanthakumar/cv/new_move.txt", 'wb')
	move_file.seek(-2,2)
	move_file.write("1")
	move_file.close()

########### script to run ###########
init_robot()

while (True):

	# if there is a new move available, execute on it and update the file
	if poll_move():
		logger.info(f"LOGGGGGGGEEEERRRRRRRRRR!!!!!!!!!!!!! {new_move_coord_x} {new_move_coord_y}")
		pick(new_move_coord_x, new_move_coord_y, 10)
		set_moving(False)
		# update_move_file()

# exit gracefully
exit_robot()
