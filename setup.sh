# building
source /opt/ros/jazzy/setup.bash
source install/setup.bash
colcon build

# launching the AUV in gazebo
ros2 launch bluerov2_description world_launch.py
ros2 launch bluerov2_description upload_bluerov2_launch.py sliders:=true