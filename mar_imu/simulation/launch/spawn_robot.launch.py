"""
spawn_robot.launch.py
=====================
Launches Gazebo Harmonic (ros_gz_sim) with imu_world.world
and spawns mobile_robot.urdf.

ROS 2 Jazzy + Gazebo Harmonic compatible.

Build & run:
  cd ~/MAR_IMU
  colcon build --symlink-install
  source install/setup.bash
  ros2 launch mar_imu spawn_robot.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ------------------------------------------------------------------ #
    #  Package paths                                                       #
    # ------------------------------------------------------------------ #
    pkg_share  = get_package_share_directory("mar_imu")
    urdf_path  = os.path.join(pkg_share, "robot_description", "urdf", "mobile_robot.urdf")
    world_path = os.path.join(pkg_share, "simulation", "worlds", "imu_world.world")

    # ------------------------------------------------------------------ #
    #  Launch arguments                                                    #
    # ------------------------------------------------------------------ #
    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="true",
        description="Use Gazebo simulation clock",
    )
    declare_x   = DeclareLaunchArgument("x",   default_value="0.0")
    declare_y   = DeclareLaunchArgument("y",   default_value="0.0")
    declare_z   = DeclareLaunchArgument("z",   default_value="0.1")
    declare_yaw = DeclareLaunchArgument("yaw", default_value="0.0")

    use_sim_time = LaunchConfiguration("use_sim_time")
    x   = LaunchConfiguration("x")
    y   = LaunchConfiguration("y")
    z   = LaunchConfiguration("z")
    yaw = LaunchConfiguration("yaw")

    # ------------------------------------------------------------------ #
    #  Read URDF                                                           #
    # ------------------------------------------------------------------ #
    with open(urdf_path, "r") as f:
        robot_description_content = f.read()

    robot_description = {"robot_description": robot_description_content}

    # ------------------------------------------------------------------ #
    #  Gazebo Harmonic  (ros_gz_sim — Jazzy)                              #
    # ------------------------------------------------------------------ #
    gz_launch_path = os.path.join(
        get_package_share_directory("ros_gz_sim"),
        "launch",
        "gz_sim.launch.py",
    )
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_launch_path),
        launch_arguments={"gz_args": f"-r {world_path}"}.items(),
    )

    # ------------------------------------------------------------------ #
    #  robot_state_publisher                                               #
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
    #  joint_state_publisher                                               #
    # ------------------------------------------------------------------ #
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
    )

    # ------------------------------------------------------------------ #
    #  Spawn entity via ros_gz_sim (Jazzy compatible)                     #
    #  Delayed by 5 s to give Gazebo time to start                        #
    # ------------------------------------------------------------------ #
    spawn_entity = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                name="spawn_mobile_robot",
                output="screen",
                arguments=[
                    "-topic", "robot_description",
                    "-name",  "mobile_robot",
                    "-x", x,
                    "-y", y,
                    "-z", z,
                    "-Y", yaw,
                ],
            )
        ],
    )

    # ------------------------------------------------------------------ #
    #  IMU bridge — maps Gazebo IMU topic -> ROS 2 /imu/data              #
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

    # ------------------------------------------------------------------ #
    #  LaunchDescription                                                   #
    # ------------------------------------------------------------------ #
    return LaunchDescription([
        declare_use_sim_time,
        declare_x,
        declare_y,
        declare_z,
        declare_yaw,

        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        spawn_entity,
        imu_bridge,
    ])
