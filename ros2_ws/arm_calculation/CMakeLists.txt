cmake_minimum_required(VERSION 3.20)
project(arm_calculation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
# find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)

add_executable(angle_calc src/angle_calc.cpp)
add_executable(pid_calc src/pid_calc.cpp src/PID/PID.c)
target_include_directories(pid_calc PUBLIC src)
# ament_target_dependencies(angle_calc rclcpp geometry_msgs)
# ament_target_dependencies(pid_calc rclcpp geometry_msgs)
target_link_libraries(angle_calc PUBLIC rclcpp::rclcpp geometry_msgs::geometry_msgs)
target_link_libraries(pid_calc PUBLIC rclcpp::rclcpp geometry_msgs::geometry_msgs)

install(TARGETS
  angle_calc
  pid_calc
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
