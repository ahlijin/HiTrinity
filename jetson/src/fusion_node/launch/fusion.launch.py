from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_dir = get_package_share_directory('fusion_node')
    config_file = os.path.join(pkg_dir, 'config', 'fusion_params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('config', default_value=config_file),

        Node(
            package='fusion_node',
            executable='mode_manager',
            name='mode_manager',
            parameters=[LaunchConfiguration('config')],
            output='screen'
        ),
        Node(
            package='fusion_node',
            executable='fusion_node',
            name='fusion_node',
            parameters=[LaunchConfiguration('config')],
            output='screen'
        ),
    ])
