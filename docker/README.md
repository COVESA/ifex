## docker directory

This defines some docker images to produce a controlled environment to execute
the tools, including an installation of the specified python version and all
dependent packages.

The initial build may take some time if it installs a particular python version
by compiling it from source code.  After that, of course there is no particular
delay to run the tools using the container (or to rebuild image, **if** changes
are added after the python installation step).

Usage:
```
cd docker
make build_ubuntu
make run_ubuntu
```

The above will map the current directory to /work.

See `Makefile` and `Dockerfile.*` for other options (e.g. alpine based)
