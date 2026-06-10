cmake_minimum_required(VERSION 3.8)
project(trinity_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SystemMode.msg"
  "msg/Heartbeat.msg"
  "msg/VoiceCommand.msg"
  "msg/DetectionResult.msg"
  "msg/ObjectInfo.msg"
  "msg/FusionResult.msg"
  "msg/TtsAudio.msg"
  "msg/LlmResponse.msg"
  "srv/LlmRequest.srv"
  "srv/MapSync.srv"
  DEPENDENCIES std_msgs geometry_msgs
)

ament_package()
