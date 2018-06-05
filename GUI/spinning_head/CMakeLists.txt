cmake_minimum_required(VERSION 2.8)

project(spinning_head)
add_executable(spinning_head obj_loader.c)
find_package(OpenGL REQUIRED)
find_package(GLUT REQUIRED)
configure_file(obj/cap.obj obj/cap.obj COPYONLY)
include_directories( . ${OPENGL_INCLUDE_DIRS}  ${GLUT_INCLUDE_DIRS} )

target_link_libraries(spinning_head m ${OPENGL_LIBRARIES} ${GLUT_LIBRARY} )
