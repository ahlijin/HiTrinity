from setuptools import setup
from glob import glob

package_name = 'gpu_scheduler'
setup(
    name=package_name, version='0.9.0', packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='legend', maintainer_email='ahlijin@163.com',
    description='GPU task scheduler', license='MIT',
    entry_points={'console_scripts': [
        'gpu_scheduler = gpu_scheduler.gpu_scheduler:main',
    ]},
)
