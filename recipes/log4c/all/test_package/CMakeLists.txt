cmake_minimum_required(VERSION 3.0.0)

project(log4cTestPackage LANGUAGES C) 

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example1 application_1.c)
target_link_libraries(example1 ${CONAN_LIBS})
