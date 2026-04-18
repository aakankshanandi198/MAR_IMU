# MAR_IMU — Running the Simulation

## Prerequisites

Make sure you have the following installed:
- ROS 2 Jazzy
- Gazebo Harmonic (gz-sim 8.x)
- `ros-jazzy-ros-gz-sim`, `ros-jazzy-ros-gz-bridge`, `ros-jazzy-robot-state-publisher`
- `ros-jazzy-teleop-twist-keyboard`

```bash
sudo apt install ros-jazzy-ros-gz-sim ros-jazzy-ros-gz-bridge \
  ros-jazzy-robot-state-publisher ros-jazzy-joint-state-publisher \
  ros-jazzy-teleop-twist-keyboard
```

---

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

## Verify IMU Data

IMU data opens automatically in a new terminal when you run `run_sim.sh`.
To open it manually in a separate terminal:

```bash
source ~/MAR_IMU/install/setup.bash
ros2 topic echo /imu/data
```

### What to expect

| State | linear_acceleration.x | linear_acceleration.z | angular_velocity.z |
|-------|----------------------|----------------------|--------------------|
| Stationary | ~0.0 | ~9.8 | ~0.0 |
| Accelerating forward | positive spike | ~9.8 | ~0.0 |
| Turning left (`j`) | ~0.0 | ~9.8 | positive |
| Turning right (`l`) | ~0.0 | ~9.8 | negative |
| On ramp | ~0.0 | < 9.8 | ~0.0 |

---

## Verify Topics Are Active

```bash
# Check all active topics
ros2 topic list

# Check IMU publish rate (should be ~100 Hz)
ros2 topic hz /imu/data

# Check cmd_vel is reaching Gazebo
gz topic -e -t /cmd_vel

# Check robot exists in Gazebo
gz model -m mobile_robot -p
```

---

## Stop the Simulation

Press `Ctrl+C` in Terminal 1. The script will automatically kill Gazebo and all ROS nodes.

If anything is left over:
```bash
pkill -f gz
pkill -f ros2
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Robot doesn't appear | Gazebo wasn't ready — re-run `./run_sim.sh` |
| IMU topic not found | Wait a few more seconds after `READY` message, then check `ros2 topic list` |
| Robot not moving | Check `gz topic -e -t /cmd_vel` — if empty, cmd_vel bridge failed, re-run script |
| Gazebo crashes | VirtualBox 3D acceleration issue — re-run script, it cleans up automatically |
| `mar_imu` package not found | Run `source ~/MAR_IMU/install/setup.bash` or add it to `~/.bashrc` |
