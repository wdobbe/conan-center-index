cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(hictk REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE hictk::libhictk)
target_compile_features(${CMAKE_PROJECT_NAME} PRIVATE cxx_std_17)
