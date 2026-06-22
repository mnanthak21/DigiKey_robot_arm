# margin of coordinates before a change is detected (mm)
coord_tolerance = 10

# convert pixel coordinates to robot control coordinates
def get_robot_coords(x, y):
	robot_y = 0.636 * x - 428.24
	robot_x = -0.6222 * y + 532.55
	return robot_x, robot_y

# returns whether or not the coordinates have changed a meaningful amount
def coords_different(targ_x, targ_y, prev_x, prev_y):
	x_is_diff = (targ_x < (prev_x - coord_tolerance)) and (targ_x > (prev_x + coord_tolerance))
	y_is_diff = (targ_y < (prev_y - coord_tolerance)) and (targ_y > (prev_y + coord_tolerance))
	return x_is_diff or y_is_diff
