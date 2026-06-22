import cv2
import numpy as np
from PIL import Image

import coord_math

# start video stream
cap = cv2.VideoCapture(1)

# configure camera parameters
cap.set(cv2.CAP_PROP_BRIGHTNESS, 64)
cap.set(cv2.CAP_PROP_CONTRAST, 0)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_EXPOSURE, 0)
cap.set(cv2.CAP_PROP_FOCUS, 100)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# setting bounds for desired color
lowerLimit, upperLimit = np.array([92,150,150]), np.array([123,255,255]) # blue
# lowerLimit, upperLimit = np.array([45,150,150]), np.array([75,255,255]) # green
# lowerLimit, upperLimit = np.array([10,150,150]), np.array([20,255,255]) # orange

# read in initial frame
_, init_frame = cap.read()
hsvImage = cv2.cvtColor(init_frame, cv2.COLOR_BGR2HSV)
width, height, channels = hsvImage.shape

# robot previous move info
robot_prev_x, robot_prev_y = 0,0

# update txt file with new move
def update_move_file(robot_targ_x, robot_targ_y):
	new_move_write = open("new_move.txt", "w") # open file for writing
	new_move_file.write(f"{robot_targ_x} {robot_targ_y} 0") # update file with target coordinates
	new_move_file.close()
	# record this as the last known move
	robot_prev_x, robot_prev_y = robot_targ_x, robot_targ_y

def check_move_finished():
	new_move_read = open("new_move.txt", "r") # open file for reading
	new_move_read.seek(-1,2) # read last character
	rfm = int(new_move_read.read())
	new_move_file.close()
	return (rfm == 1) # 1 means move finished, 0 means not yet finished

# run loop only if move finished
while (check_move_finished()):
	# read in a frame
	ret, frame = cap.read()

	# convert the frame from BGR to HSV
	hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# mask the frame using the bounds defined above
	mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)
	mask_ = Image.fromarray(mask)

	bbox = mask_.getbbox()
	if bbox is not None:

		# get coords of unmasked part of frame, and draw rectangle there
		pixel_x1, pixel_y1, pixel_x2, pixel_y2 = bbox
		cv2.rectangle(frame, (pixel_x1, pixel_y1), (pixel_x2, pixel_y2), (0,0,255), 5)

		# calculate center coords of bbox
		pixel_x = (pixel_x1 + pixel_x2) / 2
		pixel_y = (pixel_y1 + pixel_y2) / 2

		# convert from pixel coords to robot coords
		robot_targ_x, robot_targ_y = coord_math.get_robot_coords(pixel_x, pixel_y)
		# update file with new move if new robot coords are meaningfully different from previous move
		if (coord_math.coords_different(robot_targ_x, robot_targ_y, robot_prev_x, robot_prev_y)):
			update_move_file(robot_targ_x, robot_targ_y)

	# display the frame with bounding box
	cv2.imshow('frame', frame)

	# save the frame
	cv2.imwrite('frame.png', frame)
	
	# wait for key-press
	if cv2.waitKey(1) & 0xFF == 27:
		break

cap.release()
cv2.destroyAllWindows()
