#!/bin/bash
# HiTrinity — Jetson startup
source /opt/ros/humble/setup.bash
source ~/HiTrinity/jetson/install/setup.bash
export ROS_DOMAIN_ID=42

echo "Starting HiTrinity Jetson nodes..."
ros2 launch trinity_bringup jetson_bringup.launch.py "$@"
