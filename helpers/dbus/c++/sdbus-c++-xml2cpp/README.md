# sdbus-c++-xml2cpp

This is a code generator from the
[sdbus-cpp](https://github.com/Kistler-Group/sdbus-cpp) project.

**sdbus-cpp** is a C++ binding for D-Bus, which is layered on top of sdbus, a
D-Bus implementation by the systemd project.

**sdbus-c++-xml2cpp** translates a D-Bus interface description in D-Bus
introspection format (XML) into C++ proxy and adapter/stub code.

For **IFEX** this means we do not need to generate C++ code to interface with a
D-Bus library like sdbus - instead the D-Bus XML introspection format is
generated from IFEX to describe the interface, and a code generator like this
one can then be used to get C++ code.

This directory contains only a container description to compile and "package"
the `sdbus-c++-xml2cpp` tool into something that can be run with docker.
Alternatively, the `build.sh` script can be reused in another setup.  It
encodes the few commands to compile the `sdbus-cpp` project, specifically with
the code generator included.  The script does not install the dependencies
needed to compile sdbus-cpp since that requires distro-specific commands
anyway => Look at the Dockerfile for what is needed.
