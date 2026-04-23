# MAR_IMU
A robot that thinks it knows where it is 
This project simulates a mobile robot equipped with IMU sensor and analyzes the readings.
Defined with URDF and simulated with ROS2 + Gazebo Harmonic.

## OBJECTIVE
Observe:
- Orientation
- Angular velocity
- Linear acceleration

## 📁 Project Structure

```
MAR_IMU/
├── mar_imu/                        # Main ROS 2 package
│   ├── __init__.py
│   ├── imu_plotter.py              # IMU data plotting node
│   ├── scripts/
│   │   └── imu_listener.py         # IMU topic listener node
│   ├── robot_description/
│   │   └── urdf/
│   │       └── mobile_robot.urdf   # Robot URDF model
│   ├── simulation/
│   │   ├── launch/
│   │   │   └── spawn_robot.launch.py  # Launch file to spawn robot in Gazebo
│   │   └── worlds/
│   │       └── imu_world.world     # Gazebo simulation world
│   ├── test/
│   │   ├── test_copyright.py
│   │   ├── test_flake8.py
│   │   └── test_pep257.py
│   ├── resource/
│   │   └── mar_imu
│   ├── docs/
│   ├── package.xml
│   ├── setup.cfg
│   └── setup.py
├── robot_description/              # Top-level robot description
│   └── urdf/
│       └── mobile_robot.urdf
├── simulation/                     # Top-level simulation files
│   ├── launch/
│   │   └── spawn_robot.launch.py
│   └── worlds/
│       └── imu_world.world
├── rviz/
│   └── mar_imu.rviz                # RViz configuration
├── resource/
│   └── mar_imu
├── build/                          # Colcon build output (generated)
├── install/                        # Colcon install space (generated)
├── log/                            # Colcon build logs (generated)
├── package.xml
├── setup.py
├── setup.cfg
├── run_sim.sh                      # Script to launch the simulation
├── how-to-run.md
└── README.md
```

## PLANNED WORKFLOW
1. Create the robot model using URDF
2. Spawn the robot in Gazebo simulation
3. Attach an IMU sensor (Gazebo Harmonic native)
4. Publish IMU sensor data to ROS 2 topics via ros_gz_bridge
5. Subscribe to and analyze the IMU data
   (LETS FINISH THIS BEFORE SEM TURNS VIOLENT)

## STACK
- ROS 2 Jazzy
- Gazebo Harmonic
- ros_gz_sim / ros_gz_bridge

## Build

```bash
cd ~/MAR_IMU
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

> Add these two lines to your `~/.bashrc` so you never have to source manually:
> ```bash
> echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
> echo "source ~/MAR_IMU/install/setup.bash" >> ~/.bashrc
> source ~/.bashrc
> ```

---

## Run the Simulation

### Terminal 1 — Start everything
```bash
cd ~/MAR_IMU
./run_sim.sh
```

This single script will:
1. Kill any leftover processes from previous runs
2. Start Gazebo with `imu_world.world`
3. Wait until Gazebo is fully ready (no blind timers)
4. Spawn `mobile_robot` at position (0, 0, 0.1)
5. Start `robot_state_publisher`
6. Start all ROS-Gazebo bridges (IMU, cmd_vel, odometry)
7. Automatically open a new terminal showing live IMU data

> Wait for the message **`Simulation is READY!`** before proceeding.

---

### Terminal 2 — Drive the robot
```bash
source ~/MAR_IMU/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r cmd_vel:=/cmd_vel
```

#### Teleop keys
| Key | Action |
|-----|--------|
| `i` | Forward |
| `,` | Backward |
| `j` | Rotate left |
| `l` | Rotate right |
| `u` | Forward + left arc |
| `o` | Forward + right arc |
| `k` | Stop |
| `q` / `z` | Increase / decrease speed |

---
## VERIFY IMU RATE
```bash
ros2 topic hz /imu/data
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
