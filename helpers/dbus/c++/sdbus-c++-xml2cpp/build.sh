#!/bin/sh -xe

if [ ! -d sdbus-cpp ] ; then
   git clone --depth=1 https://github.com/Kistler-Group/sdbus-cpp
fi
cd sdbus-cpp
rm -rf build
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DSDBUSCPP_BUILD_CODEGEN=ON
cmake --build  .
tools/sdbus-c++-xml2cpp -h
