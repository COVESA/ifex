## container/docker directory

This defines some container images that provide a controlled environment to
execute the tools, including an installation of a specific python version and
all dependent packages for the IFEX tools.  We want to provide a choice of a
minimal size (Alpine Linux), or more featured version, and also to create some
diversity in testing environment.  Therefore, two different distros are provided.

The very first build can take some time if it installs a particular python
version by compiling it from source code\*.  After that the image is normally
reused, as usual of course.

**VARIANTS**

-  Ubuntu: (latest) This one manages python using uv.
-  Alpine Linux: This one uses a preinstalled python container image - see DETAILS.


### Usage:
```
cd docker
make build_ubuntu
make run_ubuntu
```
or
```
make build_alpine
make run_alpine
```

When the container is run, it will map the current directory to /work.

Once inside an interactive shell in the container, you can run tools like `ifexgen` directly.

**BUGS**
See `Makefile` and `Dockerfile.*` for other options (e.g. alpine based)
