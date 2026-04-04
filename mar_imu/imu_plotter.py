#!/usr/bin/env python3

from collections import deque

import matplotlib.pyplot as plt
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu


class ImuPlotter(Node):
    def __init__(self):
        super().__init__("imu_plotter")

        self.declare_parameter("window_sec", 20.0)
        self.declare_parameter("max_points", 400)

        self.window_sec = float(self.get_parameter("window_sec").value)
        self.max_points = int(self.get_parameter("max_points").value)

        self.time_data = deque(maxlen=self.max_points)
        self.gx_data = deque(maxlen=self.max_points)
        self.gy_data = deque(maxlen=self.max_points)
        self.gz_data = deque(maxlen=self.max_points)
        self.ax_data = deque(maxlen=self.max_points)
        self.ay_data = deque(maxlen=self.max_points)
        self.az_data = deque(maxlen=self.max_points)

        self.start_time = self.get_clock().now()

        self.create_subscription(Imu, "/imu/data", self.imu_callback, 10)
        self.create_timer(0.1, self.update_plot)

        plt.ion()
        self.fig, (self.ax_gyro, self.ax_accel) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

        self.gx_line, = self.ax_gyro.plot([], [], label="wx")
        self.gy_line, = self.ax_gyro.plot([], [], label="wy")
        self.gz_line, = self.ax_gyro.plot([], [], label="wz")
        self.ax_gyro.set_ylabel("rad/s")
        self.ax_gyro.set_title("IMU Angular Velocity")
        self.ax_gyro.legend(loc="upper right")
        self.ax_gyro.grid(True)

        self.ax_line, = self.ax_accel.plot([], [], label="ax")
        self.ay_line, = self.ax_accel.plot([], [], label="ay")
        self.az_line, = self.ax_accel.plot([], [], label="az")
        self.ax_accel.set_ylabel("m/s^2")
        self.ax_accel.set_xlabel("time (s)")
        self.ax_accel.set_title("IMU Linear Acceleration")
        self.ax_accel.legend(loc="upper right")
        self.ax_accel.grid(True)

        self.get_logger().info("imu_plotter subscribed to /imu/data")

    def imu_callback(self, msg: Imu) -> None:
        t = (self.get_clock().now() - self.start_time).nanoseconds * 1e-9
        self.time_data.append(t)

        self.gx_data.append(msg.angular_velocity.x)
        self.gy_data.append(msg.angular_velocity.y)
        self.gz_data.append(msg.angular_velocity.z)

        self.ax_data.append(msg.linear_acceleration.x)
        self.ay_data.append(msg.linear_acceleration.y)
        self.az_data.append(msg.linear_acceleration.z)

    def update_plot(self) -> None:
        if not self.time_data:
            return

        t = list(self.time_data)

        self.gx_line.set_data(t, list(self.gx_data))
        self.gy_line.set_data(t, list(self.gy_data))
        self.gz_line.set_data(t, list(self.gz_data))

        self.ax_line.set_data(t, list(self.ax_data))
        self.ay_line.set_data(t, list(self.ay_data))
        self.az_line.set_data(t, list(self.az_data))

        t_max = t[-1]
        t_min = max(0.0, t_max - self.window_sec)

        self.ax_gyro.set_xlim(t_min, t_max + 1e-6)
        self.ax_accel.set_xlim(t_min, t_max + 1e-6)

        self.ax_gyro.relim()
        self.ax_gyro.autoscale_view(scalex=False, scaley=True)
        self.ax_accel.relim()
        self.ax_accel.autoscale_view(scalex=False, scaley=True)

        self.fig.tight_layout()
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()


def main(args=None):
    rclpy.init(args=args)
    node = ImuPlotter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        plt.close("all")


if __name__ == "__main__":
    main()
