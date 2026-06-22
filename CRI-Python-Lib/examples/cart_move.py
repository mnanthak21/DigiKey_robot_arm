import logging
from time import sleep

from cri_lib import CRIController

# 🔹 Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s",encoding='utf-8', filename='robot.log'
)
logger = logging.getLogger(__name__)

# CRIController is the main interface for controlling the iRC
controller = CRIController()

# Connect to default iRC IP
controller.connect("192.168.3.11")

controller.set_active_control(True)
controller.enable()
controller.wait_for_kinematics_ready(10)
controller.set_override(100.0)

sleep(1)

# logger.info("3 - REFERENCING")

logger.info("4 - ENABLING")
controller.reference_all_joints()
sleep(5)
controller.set_active_control(True)
controller.enable()
controller.wait_for_kinematics_ready(10)
controller.set_override(100.0)
logger.info("5 - MOVING")

# controller.move_joints_relative(0,0,-60,0,0,0,0,0,0,60,True)
# controller.move_joints_relative(0,0,-20,0,0,0,0,0,0,100,True)
controller.get_referencing_info()
controller.move_cartesian(300,0,20,0,0,180,0,0,0,100, '#base', False)
"""
# Open end-effector
controller.set_dout(30, True)
controller.set_dout(31, False)
logger.info("Opened end-effector")

sleep(3)
"""

# controller.move_cartesian(65, -300, 160, 0,0,0,0,0,0, 100, True, 300);


"""
# Close end-effector
controller.set_dout(31, True)
controller.set_dout(30, False)
logger.info("Closed end-effector")
"""



# Disable motors and disconnect
logger.info("6 - ENDING")
logger.info("Disabling motors and disconnecting...")
controller.disable()
controller.close()

logger.info("Script execution completed successfully.")
