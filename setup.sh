# building
source /opt/ros/jazzy/setup.bash
source install/setup.bash
colcon build

# launching the AUV world
export GZ_SIM_RESOURCE_PATH="$(pwd)/models:${GZ_SIM_RESOURCE_PATH}"
gz sim worlds/forest_world.world

# launching the AUV
ros2 launch bluerov2_description upload_bluerov2_launch.py sliders:=true

