cmake_minimum_required(VERSION 3.21)
project(issuecker)

set(CMAKE_CXX_STANDARD 20)


include_directories(/usr/local/include)
add_executable(issuecker main.cpp crow.h fly_redis.h fly_redis.cpp)

find_package(Boost REQUIRED COMPONENTS thread)
target_link_libraries(issuecker Boost::thread)
