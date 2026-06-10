#!/bin/bash
# HiTrinity — Pi3 startup (unchanged from HiWonder_JetAuto)
source /opt/ros/humble/setup.bash
source ~/HiTrinity/pi3/install/setup.bash
export ROS_DOMAIN_ID=42

echo "Starting Pi3 nodes..."
ros2 launch bringup pi3_bringup.launch.py "$@"
