cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(morton-nd REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE morton-nd::MortonND)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
if(morton-nd_VERSION VERSION_LESS "4.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "MORTONND_LESS_4_0_0")
endif()
