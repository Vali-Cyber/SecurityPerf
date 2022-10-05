cmake_minimum_required(VERSION 3.11)


set(CMAKE_LIBRARY_OUTPUT_DIRECTORY
    /app/build/bin
    CACHE PATH "Output directory for shared libraries.")

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY
    /app/build/bin
    CACHE PATH "Output directory for executables and SO's.")

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
message(STATUS "Compiler Settings = ${COMPILER_SETTINGS}")
set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${COMPILER_SETTINGS} -O3 -Wall -Wextra -Werror \
    -Wformat-security -Wsign-conversion -fstack-protector -fPIC -ggdb")

set(CMAKE_EXE_LINKER_FLAGS_RELEASE ",-z,relro,-z,now -D_FORTIFY_SOURCE=2 -ggdb")

add_executable(fanotify
    fanotify/fanotify.cpp)
