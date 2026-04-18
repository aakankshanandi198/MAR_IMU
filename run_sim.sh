#!/bin/bash
# run_sim.sh
# Starts everything needed for the MAR_IMU simulation.
# Usage: ./run_sim.sh

source ~/MAR_IMU/install/setup.bash

# Kill any leftover processes from previous runs
echo "[1/6] Cleaning up old processes..."
pkill -f "gz sim" 2>/dev/null
pkill -f "ros2" 2>/dev/null
sleep 2

URDF=~/MAR_IMU/install/mar_imu/share/mar_imu/robot_description/urdf/mobile_robot.urdf
WORLD=~/MAR_IMU/install/mar_imu/share/mar_imu/simulation/worlds/imu_world.world

# Step 1: Start Gazebo in background
echo "[2/6] Starting Gazebo..."
gz sim "$WORLD" -r &
GZ_PID=$!

# Wait until Gazebo world service is available
echo "      Waiting for Gazebo to be ready..."
until gz service -l 2>/dev/null | grep -q "imu_world"; do
    sleep 1
done
echo "      Gazebo is ready!"

# Step 2: Spawn robot
echo "[3/6] Spawning robot..."
ros2 run ros_gz_sim create \
    -file "$URDF" \
    -name mobile_robot \
    -x 0.0 -y 0.0 -z 0.1
echo "      Robot spawned!"

# Step 3: Start robot_state_publisher in background
echo "[4/6] Starting robot_state_publisher..."
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p robot_description:="$(python3 -c "
with open('$URDF') as f: print(f.read())
")" &
RSP_PID=$!
sleep 2

# Step 4: Start bridges in background
echo "[5/6] Starting bridges..."
ros2 run ros_gz_bridge parameter_bridge \
    /imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU &
IMU_PID=$!

ros2 run ros_gz_bridge parameter_bridge \
    /cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist &
CMD_PID=$!

ros2 run ros_gz_bridge parameter_bridge \
    /odom@nav_msgs/msg/Odometry[gz.msgs.Odometry &
ODOM_PID=$!

sleep 2

echo ""
echo "========================================="
echo " Simulation is READY!"
echo "========================================="
echo ""
echo " In a new terminal run teleop:"
echo "   source ~/MAR_IMU/install/setup.bash"
echo "   ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel"
echo ""
echo " Monitor IMU:"
echo "   ros2 topic echo /imu/data"
echo ""
echo " Press Ctrl+C to stop everything."
echo "========================================="
# Step 5b: Open IMU data in a new terminal automatically
echo "[6/6] Opening IMU monitor..."
gnome-terminal -- bash -c "source ~/MAR_IMU/install/setup.bash && ros2 topic echo /imu/data; exec bash" &
# Step 6: Wait — keep script alive, kill all on Ctrl+C
trap "echo 'Shutting down...'; kill $GZ_PID $RSP_PID $IMU_PID $CMD_PID $ODOM_PID 2>/dev/null; pkill -f gz; pkill -f ros2; exit" SIGINT SIGTERM
wait
