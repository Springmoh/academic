from setuptools import find_packages, setup

package_name = 'arm_simulation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            'share/' + package_name + '/reference',
            [
                'arm_simulation/reference/frame.jpg',
                'arm_simulation/reference/video.mp4',
            ],
        ),
    ],
    install_requires=['setuptools', 'fastapi', 'uvicorn[standard]', 'opencv-python', 'ultralytics'],
    zip_safe=True,
    maintainer='mohnc',
    maintainer_email='clementmoh1018@hotmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'target_pub = arm_simulation.target_pub:main',
            'simulation = arm_simulation.simulation:main',
            'ui_frontend = arm_simulation.ui_frontend:main',
            'image_processing = arm_simulation.image_processing:main',
        ],
    },
)
