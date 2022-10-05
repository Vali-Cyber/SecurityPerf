#!/bin/bash

if [ -f Dockerfile ] && [ -f CMakeLists.txt ] && [ -d fanotify ]; then
    if [[ "$(docker images -q security_tool_builder 2> /dev/null)" == "" ]]; then
        docker build . -t security_tool_builder
    fi

    if [ -d $(pwd)/build ]; then
         docker run --rm -v "$(pwd)":/app security_tool_builder /bin/bash -c "cd build && make"
    else
         docker run --rm -v "$(pwd)":/app security_tool_builder /bin/bash -c "mkdir build && cd build && cmake ../ && make"
    fi
else
    echo "This script must be run from the securityperf/security_programs/examples directory"
    exit 1
fi
