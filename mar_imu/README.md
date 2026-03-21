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
