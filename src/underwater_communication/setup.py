from setuptools import setup

package_name = 'underwater_communication'

setup(
    name=package_name,
    version='0.0.1',

    packages=[package_name],

    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
    ],

    install_requires=[
        'setuptools'
    ],

    zip_safe=True,

    maintainer='steve',
    maintainer_email='steve@example.com',

    description='ROS 2 underwater acoustic and laser communication simulator',

    license='Apache-2.0',

    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'acoustic = underwater_communication.acoustic:main',
            'laser = underwater_communication.laser:main',
        ],
    },
)