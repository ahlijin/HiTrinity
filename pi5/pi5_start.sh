#!/bin/bash
# HiTrinity — Pi5 startup
source /opt/ros/humble/setup.bash
source ~/HiTrinity/pi5/install/setup.bash
export ROS_DOMAIN_ID=42

echo "Starting HiTrinity Pi5 nodes..."
ros2 launch pi5_bringup pi5_bringup.launch.py "$@"
