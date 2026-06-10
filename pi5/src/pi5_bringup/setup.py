from setuptools import setup
from glob import glob
package_name = 'pi5_bringup'
setup(
    name=package_name, version='0.9.0', packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='legend', maintainer_email='ahlijin@163.com',
    description='Pi5 bringup', license='MIT',
)
