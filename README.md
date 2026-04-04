# MAR_IMU
A robot that thinks it knows where it is 
This project simulates a mobile robot equipped with IMU sensor and analyzes the readings.
Defined with URDF and simulated with ROS2 + Gazebo Harmonic.

## OBJECTIVE
Observe:
- Orientation
- Angular velocity
- Linear acceleration

## PROJECT STRUCTURE
```
MAR_IMU/
│
├── mar_imu/                        ← ROS 2 package
│   ├── package.xml
│   ├── setup.py
│   ├── setup.cfg
│   ├── resource/
│   ├── test/
│   │
│   ├── robot_description/
│   │   └── urdf/
│   │       └── mobile_robot.urdf
│   │
│   ├── simulation/
│   │   ├── worlds/
│   │   │   └── imu_world.world
│   │   └── launch/
│   │       └── spawn_robot.launch.py
│   │
│   ├── scripts/
│   │   ├── imu_listener.py
│   │   └── robot_controller.py
│   │
│   ├── docs/
│   │   └── project_notes.md
│   │
│   └── README.md
│
├── build/
├── install/
└── log/
```

## PLANNED WORKFLOW
1. ✅ Create the robot model using URDF
2. ✅ Spawn the robot in Gazebo simulation
3. ✅ Attach an IMU sensor (Gazebo Harmonic native)
4. ✅ Publish IMU sensor data to ROS 2 topics via ros_gz_bridge
5. ⬜ Subscribe to and analyze the IMU data
   (LETS FINISH THIS BEFORE SEM TURNS VIOLENT)

## STACK
- ROS 2 Jazzy
- Gazebo Harmonic
- ros_gz_sim / ros_gz_bridge

## BUILD
```bash
cd ~/ros2_ws
colcon build --packages-select mar_imu --symlink-install
source install/setup.bash
```

## RUN SIMULATION (IMU RATE CONFIGURABLE)
Default IMU rate is now 20 Hz and can be changed at launch time:

```bash
ros2 launch mar_imu spawn_robot.launch.py imu_rate_hz:=20.0 use_rviz:=true
```

For 10 Hz:

```bash
ros2 launch mar_imu spawn_robot.launch.py imu_rate_hz:=10.0 use_rviz:=true
```

## VERIFY IMU RATE
```bash
ros2 topic hz /imu/data
```

## TELEOP TESTING
Install keyboard teleop if needed:

```bash
sudo apt install ros-jazzy-teleop-twist-keyboard
```

Run teleop in a second terminal:

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel
```

While teleop is running, verify IMU publishing in a third terminal:

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 topic hz /imu/data
ros2 topic echo /imu/data --once
```

Verify robot motion command path:

```bash
ros2 topic info /cmd_vel
```

## PLOTTING IMU DATA
Use `rqt_plot`:

```bash
ros2 run rqt_plot rqt_plot /imu/data/angular_velocity/z /imu/data/linear_acceleration/x /imu/data/linear_acceleration/y /imu/data/linear_acceleration/z
```

To inspect orientation as quaternion:

```bash
ros2 topic echo /imu/data | grep orientation -A 4
```

Or run the Python live plotter node (angular velocity + linear acceleration):

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run mar_imu imu_plotter
```

## MOTION PIPELINE NOTE
The Gazebo diff-drive plugin is configured with:
- left wheel joint: `left_wheel_joint`
- right wheel joint: `right_wheel_joint`
- command topic: `/cmd_vel`

If teleop publishes to `/cmd_vel`, the robot should move and IMU values should change.

## RVIZ VISUALIZATION
RViz opens by default from launch (`use_rviz:=true`) and shows:
- Robot model from URDF
- TF frames
- IMU display on `/imu/data`
