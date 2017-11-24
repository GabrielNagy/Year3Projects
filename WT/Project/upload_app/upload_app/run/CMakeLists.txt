cmake_minimum_required (VERSION 2.6)
project (TEMPLATE)
enable_testing()

#add_subdirectory (gmock-1.7.0)
add_subdirectory (src) 

add_custom_target(check COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure)
