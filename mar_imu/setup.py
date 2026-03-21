from setuptools import find_packages, setup

package_name = 'mar_imu'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
   data_files=[
    ('share/ament_index/resource_index/packages', ['resource/mar_imu']),
    ('share/mar_imu', ['package.xml']),
    ('share/mar_imu/robot_description/urdf', ['robot_description/urdf/mobile_robot.urdf']),
    ('share/mar_imu/simulation/worlds', ['simulation/worlds/imu_world.world']),
    ('share/mar_imu/simulation/launch', ['simulation/launch/spawn_robot.launch.py']),
],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vboxuser',
    maintainer_email='alanmathew2311@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
