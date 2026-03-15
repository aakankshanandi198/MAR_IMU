# MAR_IMU
A robot that thinks it knows where it is 
This project simulates a mobile robot equipped with IMU sensor and analyzes the readings
Defined with URDF and simulated with ROS2 ,GAZEBO .
##  OBJECTIVE
Observe:
-orientation
-angular velocity
-linear acceleration
## PROJECT STRUCTURE 
## 📁 Project Structure

```
MAR_IMU
│
├── robot_description
│   ├── urdf
│   │   └── mobile_robot.urdf
│   │
│   └── meshes
│       └── (3D models if added later)
│
├── simulation
│   ├── worlds
│   │   └── imu_world.world
│   │
│   └── launch
│       └── spawn_robot.launch.py
│
├── scripts
│   ├── imu_listener.py
│   └── robot_controller.py
│
├── docs
│   └── project_notes.md
│
├── README.md
└── .gitignore
```
## PLANNED WORKFLOW
1. Create the robot model using URDF  
2. Spawn the robot in Gazebo simulation  
3. Attach an IMU sensor plugin  
4. Publish IMU sensor data to ROS 2 topics  
5. Subscribe to and analyze the IMU data
   (LETS FINISH THIS BEFORE SEM TURNS VIOLENT)
