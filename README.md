# Interface Exchange framework (IFEX)

<img src="docs/images/IFEX-Logo-updated-turquoise%201.svg" alt="IFEX Logo Turquoise SVG" width="300" height="118">

This repository includes:

1. Specifications and documentation
2. Programs and tools

...for the the *Interface Exchange framework (IFEX)*.

IFEX is a general interface description and transformation technology which
started in the Vehicle Service Catalog (VSC) project.  The technology (IFEX) is
now developed under a separate name to better describe its purpose and that it
is widely and generally applicable.  (This repository was previously named
_vsc-tools_)

Please refer to the [documentation](https://covesa.github.io/ifex) for more information.

## IFEX software tools

Some of the programs implement the tools for reading/writing/translating
interface descriptions and code-generation.  Other programs generate the IFEX
interface model/language-specification and other documentation.

The implementations are primarily written in python and using some preferred
technologies, such as the [Jinja2 templating language](https://jinja.palletsprojects.com) 
([(alt.  link)](https://jinja2docs.readthedocs.io/en/stable/)).

## Getting started

### Prerequisites
* Python >=3.10 installed (exact version might vary - the best
  definition of what works is likely the [automated workflow
files](https://github.com/COVESA/ifex/tree/master/.github/workflows)
or [tox.ini](./tox.ini))
* Dependencies installed according to instructions below

### Container use

As an alternative to installation instructions below, all the installations can also be hidden in a container.  Refer to the [README in the packaging/docker/ directory](./packaging/docker/README.md) for running the tools using containers instead.

## Installing and use python version(s) with `pyenv`

NOTE: Pyenv is not quite the same as other virtual environment
handlers.  Its most important function is to download, compile, and
install a particular python version from source code.  If your
system python version is one that is not supported by this project
and you are not able to install the right python version using
another method, then this can be used *if* you are not able to
install the right python version using another method.  It can also
be used in combination with virtual-environment handlers, to get
access to different python versions.

If [`pyenv` shell command](https://github.com/pyenv/pyenv) is not installed, use its [installer](https://github.com/pyenv/pyenv-installer) to get it:

```bash
   curl https://pyenv.run | bash  # download and install (YOU are responsible to check the script content)
   exec $SHELL                    # restart your shell using the new $PATH
```

### Setup a python virtual environment (recommended)

Once you have an appropriate version of python, a virtual environment is
recommended to avoid any particulars in the main system installation.

Go to project directory and then:
```sh
python -m venv venv
source venv/bin/activate
```

NEXT: Go to **Installing packages**

### Setup without virtual environment (not recommended)

Go directly to Installing packages

### Setup with `pipenv`
[pipenv](https://pypi.org/project/pipenv/) is a tool that manages a virtual environment and install the package and its dependencies, making the process much simpler and predictable, since the `Pipfile` states the dependencies, while `Pipfile.lock` freezes the exact version in use.

Install this project and its dependencies in the local `.venv` folder in this project, then use it (`pipenv shell`):
```bash
   export PIPENV_VENV_IN_PROJECT=1 # will create a local `.venv` in the project, otherwise uses global location
   pipenv install --dev # install the development dependencies as well
```

NEXT: Go to **Installing packages**

You can then run:
```
   pipenv shell         # starts a shell configured to use the virtual environment
```

### Activate a chosen python version using pyenv

Activate a version in the current environment
```sh
pyenv local 3.10.6
```

IMPORTANT: Follow the pyenv instructions to make sure that pyenv environment
setup is added to `.bashrc` so that the binaries can be found every time a
shell is started.  Something like:

```sh
eval ($pyenv init)
```
should be run before anything else.

NEXT: Go to **Installing packages**

### Setup and run tests using tox

Tox is another way to set up the working environment.  It is primarily used to test the program using multiple python versions.

1. Install tox
2. Install pyenv (most likely needed, use it if additional python versions are required)
3. (optional) edit the provided tox.ini file
4. Run tox  -- this will execute pytest for all stated python versions

Here we provide a script that will check which versions are requested by `tox.ini`, and install all of those versions first, using pyenv:

```bash
   pip install "tox>=4"
   scripts/pyenv_install_for_tox.sh
   tox
```
Note:  In this case, tox takes care of calling `pip` and `setup.py` to install the required packages.

## Installing packages

(for any or none, virtual-environment -- but not needed if using tox)

Regardless of which type of virtual environment (if any) you use, it is required to install the IFEX package into your python environment, and to install needed dependencies with pip.

0. **If you use a virtual environment, remember to first activate it!**  
For example:
```
source venv/bin/activate
```

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Install the IFEX provided modules into your virtual environment
The following installs the package in develop mode (using setup.py)
```
pip install -e .
```

## Trying it out

Installing the IFEX tools using `setup.py` creates some convenient
executable shims, e.g. `ifexgen`, `ifexgen_dbus`, `ifexconv_protobuf`, ...

If those commands are not in your environment, try setting up python virtual environment and make sure pip install -e (setup.py) runs correctly.  After that, they should be in the `$PATH` variable and possible to run.

To run a generic code generator and specify an output template:

```
usage: ifexgen [-h] -d templates-dir-name ifex-input-file
```
To get some test IFEX files, clone the VSC repo:

```bash
   git clone https://github.com/COVESA/vehicle_service_catalog

   # Using a template
   ifexgen vehicle_service_catalog/comfort-service.yml -d dtdl 

   # D-Bus:
   ifexgen_dbus vehicle_service_catalog/comfort-service.yml
```

To test some <other>-to-IFEX conversion, for example **gRPC/protobuf**:

```bash
   git clone https://github.com/COVESA/uservices
   ifexconv_protobuf uservices/src/main/proto/vehicle/propulsion/engine/v1/engine_service.proto >engine_service.ifex
```

To try the D-Bus XML generator:
```
usage: ifexgen_dbus input_ifex.yaml
```

# Unit Tests

The project uses pytest to define unit tests. A starting point is in the tests
directory and more can be added.

To run tests, just run pytest in the root directory, (optionally specify the tests directory).

```bash
   pytest -v tests
```

# Contribution

Propose changes using the GitHub Issues or Pull Request.

# Development

Make sure you have read the [Specification](https://covesa.github.io/ifex/developers-manual)
Then please refer to the [developer documentation](https://covesa.github.io/ifex/developers-manual)

# Future plans, new proposals and enhancements

Please refer to [GitHub tickets](https://github.com/COVESA/ifex/issues)
(Feel free to make a proposal or ask a question)

# Known bugs

Please refer to [GitHub tickets](https://github.com/COVESA/ifex/issues)
with the label "bug"

# Troubleshooting

Various tips to consider:

* If the installation (pip install) is executed behind a (corporate) proxy, the following environments variables must be set: `http_proxy` and `https_proxy` (including authentication e.g., `http://${proxy_username):$(proxy_password)@yourproxy.yourdomain`)
* If you use a custom pip installation directory, set the `PYTHONPATH` environment variable to the directory that you set in the `pip.ini` file.
* If you do not run with administration rights, you may need to configure pip target path to write to your user home directory or consider using one of the `virtual environment` methods.
