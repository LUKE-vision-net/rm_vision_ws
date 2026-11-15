 cmake_minimum_required(VERSION 3.8)
project(vision_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 1. 找依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# 2. 指定 OpenCV 的文件夹路径（注意：只写到 opencv4 文件夹！）
set(OpenCV_DIR "/usr/lib/x86_64-linux-gnu/cmake/opencv4")
find_package(OpenCV REQUIRED)

# 3. 生成可执行文件（路径改成 src/）
add_executable(s2_pnp_node src/S2_PnP_Computer.cpp)

# 4. 链接依赖
ament_target_dependencies(s2_pnp_node rclcpp std_msgs)
target_link_libraries(s2_pnp_node ${OpenCV_LIBS})

# 5. 安装规则（名字统一！）
install(TARGETS
  s2_pnp_node
  DESTINATION lib/${PROJECT_NAME}
)

# 6. 结尾
ament_package()