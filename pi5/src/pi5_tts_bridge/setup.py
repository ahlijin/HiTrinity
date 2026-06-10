from setuptools import setup
package_name = 'pi5_tts_bridge'
setup(
    name=package_name, version='0.9.0', packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/tts_bridge.launch.py']),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='legend', maintainer_email='ahlijin@163.com',
    description='TTS bridge', license='MIT',
    entry_points={'console_scripts': [
        'tts_bridge = pi5_tts_bridge.tts_bridge:main',
    ]},
)
