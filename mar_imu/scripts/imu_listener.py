#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import math
import time

YELLOW  = '\033[93m\033[1m'
CYAN    = '\033[96m'
RED     = '\033[91m'
GREEN   = '\033[92m'
BOLD    = '\033[1m'
RESET   = '\033[0m'

def highlight(val, prev, threshold, fmt):
    if abs(val - prev) > threshold:
        return f"{YELLOW}{fmt.format(val)}{RESET}"
    return fmt.format(val)

class IMUListener(Node):
    def __init__(self):
        super().__init__('imu_listener')
        self.subscription = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)
        self.prev = {
            'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0,
            'avx': 0.0, 'avy': 0.0, 'avz': 0.0,
            'lax': 0.0, 'lay': 0.0, 'laz': 0.0,
        }
        self.ANGLE_TH = 0.5
        self.ACCEL_TH = 0.2
        self.get_logger().info('IMU Listener ready — watching for movement...')

    def imu_callback(self, msg):
        q = msg.orientation
        sinr = 2.0 * (q.w * q.x + q.y * q.z)
        cosr = 1.0 - 2.0 * (q.x * q.x + q.y * q.y)
        roll = math.degrees(math.atan2(sinr, cosr))

        sinp = 2.0 * (q.w * q.y - q.z * q.x)
        pitch = math.degrees(math.asin(max(-1.0, min(1.0, sinp))))

        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.degrees(math.atan2(siny, cosy))

        av = msg.angular_velocity
        la = msg.linear_acceleration
        p = self.prev

        changed = (
            abs(roll  - p['roll'])  > self.ANGLE_TH or
            abs(pitch - p['pitch']) > self.ANGLE_TH or
            abs(yaw   - p['yaw'])   > self.ANGLE_TH or
            abs(la.x  - p['lax'])   > self.ACCEL_TH or
            abs(la.y  - p['lay'])   > self.ACCEL_TH
        )

        if not changed:
            return

        if abs(pitch) > 5.0:
            state = f"{RED}ON RAMP / BUMP{RESET}"
        elif abs(la.x) > 1.0 or abs(la.y) > 1.0:
            state = f"{YELLOW}ACCELERATING{RESET}"
        elif abs(av.z) > 0.1:
            state = f"{CYAN}TURNING{RESET}"
        else:
            state = f"{GREEN}POSITION CHANGED{RESET}"

        ts = time.strftime("%H:%M:%S")
        print(f"\n--- {ts} — {state} ---")
        print(f"{CYAN}ORIENTATION{RESET}")
        print(f"  Roll  : {highlight(roll,  p['roll'],  self.ANGLE_TH, '{:+.2f} °')}")
        print(f"  Pitch : {highlight(pitch, p['pitch'], self.ANGLE_TH, '{:+.2f} °')}")
        print(f"  Yaw   : {highlight(yaw,   p['yaw'],   self.ANGLE_TH, '{:+.2f} °')}")

        print(f"{CYAN}ANGULAR VELOCITY  (rad/s){RESET}")
        print(f"  X : {highlight(av.x, p['avx'], 0.01, '{:+.4f}')}")
        print(f"  Y : {highlight(av.y, p['avy'], 0.01, '{:+.4f}')}")
        print(f"  Z : {highlight(av.z, p['avz'], 0.01, '{:+.4f}')}")

        print(f"{CYAN}LINEAR ACCELERATION  (m/s²){RESET}")
        print(f"  X : {highlight(la.x, p['lax'], self.ACCEL_TH, '{:+.4f}')}")
        print(f"  Y : {highlight(la.y, p['lay'], self.ACCEL_TH, '{:+.4f}')}")
        print(f"  Z : {highlight(la.z, p['laz'], self.ACCEL_TH, '{:+.4f}')}")

        self.prev = {
            'roll': roll, 'pitch': pitch, 'yaw': yaw,
            'avx': av.x, 'avy': av.y, 'avz': av.z,
            'lax': la.x, 'lay': la.y, 'laz': la.z,
        }

def main(args=None):
    rclpy.init(args=args)
    node = IMUListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
