"""
spawn_robot.launch.py
=====================
ALL-IN-ONE launch file.
Starts Gazebo, spawns robot, starts all bridges.

ROS 2 Jazzy + Gazebo Harmonic (gz-sim 8.x)

Build & run:
  cd ~/MAR_IMU
  colcon build --symlink-install
  source install/setup.bash
  ros2 launch mar_imu spawn_robot.launch.py

Then in a second terminal run teleop:
  ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel

Monitor IMU:
  ros2 topic echo /imu/data
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

    # ------------------------------------------------------------------ #
    #  Read URDF for robot_state_publisher                                 #
    # ------------------------------------------------------------------ #
    with open(urdf_path, "r") as f:
        robot_description_content = f.read()

    robot_description = {"robot_description": robot_description_content}

    # ------------------------------------------------------------------ #
    #  Gazebo Harmonic                                                     #
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
    #  Needed for TF tree and RViz — not used for spawning                #
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
    #  Spawn via -file (most reliable on this machine)                    #
    #  Delayed 10s to give Gazebo time to fully load on VirtualBox        #
    # ------------------------------------------------------------------ #
    spawn_entity = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                name="spawn_mobile_robot",
                output="screen",
                arguments=[
                    "-file", urdf_path,
                    "-name", "mobile_robot",
                    "-x", LaunchConfiguration("x"),
                    "-y", LaunchConfiguration("y"),
                    "-z", LaunchConfiguration("z"),
                    "-Y", LaunchConfiguration("yaw"),
                ],
            )
        ],
    )

    # ------------------------------------------------------------------ #
    #  Bridges — delayed to 12s so robot is fully spawned first           #
    # ------------------------------------------------------------------ #

    # IMU: Gazebo -> ROS 2
    imu_bridge = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="imu_bridge",
                output="screen",
                arguments=[
                    "/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU"
                ],
                parameters=[{"use_sim_time": use_sim_time}],
            )
        ],
    )

    # cmd_vel: ROS 2 -> Gazebo
    cmd_vel_bridge = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="cmd_vel_bridge",
                output="screen",
                arguments=[
                    "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist"
                ],
                parameters=[{"use_sim_time": use_sim_time}],
            )
        ],
    )

    # odom: Gazebo -> ROS 2
    odom_bridge = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="odom_bridge",
                output="screen",
                arguments=[
                    "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry"
                ],
                parameters=[{"use_sim_time": use_sim_time}],
            )
        ],
    )

    # ------------------------------------------------------------------ #
    #  Static TF: base_link -> imu_link                                   #
    # ------------------------------------------------------------------ #
    imu_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="imu_static_tf",
        arguments=["0", "0", "0.05", "0", "0", "0", "base_link", "imu_link"],
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

        # Start immediately
        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        imu_tf,

        # After 10s: spawn robot (gives Gazebo time to load on VirtualBox)
        spawn_entity,

        # After 12s: start bridges (after robot is spawned)
        imu_bridge,
        cmd_vel_bridge,
        odom_bridge,
    ])
