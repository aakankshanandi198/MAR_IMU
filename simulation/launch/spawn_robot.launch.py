"""
spawn_robot.launch.py
=====================
Launches Gazebo Harmonic (ros_gz_sim) with imu_world.world
and bridges IMU plus cmd_vel topics between Gazebo and ROS 2.

ROS 2 Jazzy + Gazebo Harmonic compatible.

Build & run:
  cd ~/MAR_IMU
  colcon build --symlink-install
  source install/setup.bash
    ros2 launch mar_imu spawn_robot.launch.py imu_rate_hz:=20.0 use_rviz:=true
"""

import os
import tempfile

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
    ExecuteProcess,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ------------------------------------------------------------------ #
    #  Package paths                                                       #
    # ------------------------------------------------------------------ #
    pkg_share  = get_package_share_directory("mar_imu")
    urdf_path  = os.path.join(pkg_share, "robot_description", "urdf", "mobile_robot.urdf")
    world_path = os.path.join(pkg_share, "simulation", "worlds", "imu_world.world")
    rviz_path = os.path.join(pkg_share, "rviz", "mar_imu.rviz")

    # ------------------------------------------------------------------ #
    #  Launch arguments                                                    #
    # ------------------------------------------------------------------ #
    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="true",
        description="Use Gazebo simulation clock",
    )
    declare_imu_rate_hz = DeclareLaunchArgument(
        "imu_rate_hz",
        default_value="20.0",
        description="IMU publish rate in Hz (set in Gazebo sensor update_rate)",
    )
    declare_use_rviz = DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        description="Start RViz2 with a basic IMU/robot visualization config",
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    imu_rate_hz = LaunchConfiguration("imu_rate_hz")
    use_rviz = LaunchConfiguration("use_rviz")

    # ------------------------------------------------------------------ #
    #  Read URDF                                                           #
    # ------------------------------------------------------------------ #
    with open(urdf_path, "r") as f:
        robot_description_content = f.read()

    robot_description = {"robot_description": robot_description_content}

    def launch_setup(context, *args, **kwargs):
        # Build a temporary world file with the requested IMU rate.
        # This keeps the world file in the package clean while allowing launch-time tuning.
        imu_rate_value = imu_rate_hz.perform(context)
        with open(world_path, "r") as world_file:
            world_template = world_file.read()
        world_content = world_template.replace("__IMU_RATE_HZ__", imu_rate_value)

        temp_world_path = os.path.join(
            tempfile.gettempdir(),
            f"mar_imu_world_{imu_rate_value.replace('.', '_')}.world",
        )
        with open(temp_world_path, "w") as generated_world:
            generated_world.write(world_content)

        # ------------------------------------------------------------------ #
        #  Gazebo Harmonic                                                    #
        # ------------------------------------------------------------------ #
        gazebo = ExecuteProcess(
            cmd=["gz", "sim", "-r", temp_world_path],
            output="screen",
        )

        # ------------------------------------------------------------------ #
        #  robot_state_publisher                                             #
        # ------------------------------------------------------------------ #
        robot_state_publisher = Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[
                robot_description,
                {"use_sim_time": use_sim_time},
            ],
        )

        # ------------------------------------------------------------------ #
        #  ROS<->Gazebo bridges                                              #
        # ------------------------------------------------------------------ #
        imu_bridge = Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            name="imu_bridge",
            output="screen",
            arguments=[
                "/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU"
            ],
        )

        cmd_vel_bridge = Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            name="cmd_vel_bridge",
            output="screen",
            arguments=[
                "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist"
            ],
        )

        rviz = Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_path],
            parameters=[{"use_sim_time": use_sim_time}],
            condition=IfCondition(use_rviz),
        )

        return [
            gazebo,
            robot_state_publisher,
            imu_bridge,
            cmd_vel_bridge,
            rviz,
        ]

    # ------------------------------------------------------------------ #
    #  LaunchDescription                                                   #
    # ------------------------------------------------------------------ #
    return LaunchDescription([
        declare_use_sim_time,
        declare_imu_rate_hz,
        declare_use_rviz,
        OpaqueFunction(function=launch_setup),
    ])
