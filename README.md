# Interface Exchange framework (IFEX)

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
* Python >=3.10 installed (exact version might vary - the best definition of what works is likely the [automated workflow files](https://github.com/COVESA/ifex/tree/master/.github/workflows)
* Dependencies installed according to instructions below

### Project Setup

* If you use a custom pip installation directory, set the `PYTHONPATH` environment variable to the directory that you set in the `pip.ini` file.

### Setup with `virtualenv`

```sh
python3 -m venv venv
source venv/bin/activate
```

### Setup with `pipenv`
[pipenv](https://pypi.org/project/pipenv/) is a tool that manages a virtual environment and install the package and its dependencies, making the process much simpler and predictable, since the `Pipfile` states the dependencies, while `Pipfile.lock` freezes the exact version in use.

### (alternative) setup with `pyenv`

If [`pyenv` shell command](https://github.com/pyenv/pyenv) is not installed, use its [installer](https://github.com/pyenv/pyenv-installer) to get it:

```bash
   curl https://pyenv.run | bash  # download and install
   exec $SHELL                    # restart your shell using the new $PATH
```

NOTE: In the following instructions, you might have to adjust the exact python version.  See prerequisites.

Make sure Python version 3.10.6 is installed:
```bash
   pyenv install 3.10.6  # install the versions required by Pipfile
```

Activate a virtual environment
```sh
pyenv local 3.10.6
```

## Installing packages

_(regardless of which venv tool you use)_

Install the IFEX provided modules into your virtual environment)
```
python setup.py develop

```
Install dependencies:
```
pip install pyyaml jinja2 pytest anytree
```
(Alternatively, we are providing a requirements.txt file but it might be
deprecated later in favor of pipenv):

```
pip install -r requirements.txt
```

## Setup  with pipenv (alternative)

**DEPRECATED / currently not working**
(We would welcome if you investigate it, and provide an updated instructions)

[pipenv](https://pypi.org/project/pipenv/) is a tool that manages a virtual environment and install the package and its dependencies, making the process much simpler and predictable, since the `Pipfile` states the dependencies, while `Pipfile.lock` freezes the exact version in use.

Install this project and its dependencies in the local `.venv` folder in this project, then use it (`pipenv shell`):
```bash
   export PIPENV_VENV_IN_PROJECT=1 # will create a local `.venv` in the project, otherwise uses global location
   pipenv install --dev # install the development dependencies as well
   pipenv shell         # starts a shell configured to use the virtual environment
```

### Setup without virtual environment (not recommended)

To install to your system environment:
```
pip install -r requirements.txt
python setup.py develop
```

## Trying it out

Installing the IFEX tools using `setup.py` also creates some convenient
executable shims, e.g. `ifexgen`:

To run this generic code generator and specify an output template:

```
usage: ifexgen [-h] -d templates-dir-name ifex-input-file [root-template]
```

Example:
```bash
   ifexgen comfort-service.yml -d d-bus
```

For the moment, try this:

```bash
   git clone https://github.com/COVESA/vehicle_service_catalog

   ifexgen vehicle_service_catalog/comfort-service.yml -d simple 
```

The comfort-service example above exercises the parser to create the AST out
of a YAML file from the Vehicle Service Catalog definition, and then prints
out an overview using the template.

# Unit Tests

The project uses pytest to define unit tests. In the tests directory is a
simple starting point. More can be added.

To run tests, just run pytest in the root directory.

```bash
   pytest -v
```

# Development

Please refer to the [developer documentation](https://covesa.github.io/ifex/developers-manual)

# Existing Tools/Templates

Try the directory names of dtdl, protobuf, sds-bamm, simple etc.  (see [templates dir](https://github.com/COVESA/ifex/tree/master/ifex/templates) for more)

- dtdl: Generates a DTDL description of the service: [documentation](ifex/templates/dtdl/dtdl.md)
- sds-bamm:  Generates a BAMM Aspect Meta Model of the service: [documentation](ifex/templates/sds-bamm-aspect-model.md)
- simple: Just outputs some simple overview (incomplete) in HTML format.  For simple testing.
- protobuf: Generate protobuf(gRPC) description language, including the "rpc" feature.
- d-bus: Linux D-Bus introspection XML format (pending)

# Future plans, new proposals and enhancements

Please refer to [GitHub tickets](https://github.com/COVESA/ifex/issues)
(Feel free to make a proposal or ask a question)

# Known bugs

Please refer to [GitHub tickets](https://github.com/COVESA/ifex/issues)
with the label "bug"

# Troubleshooting

Various tips to consider:

* If the installation (pip install) is executed behind a (corporate) proxy, the following environments variables must be set: `http_proxy` and `https_proxy` (including authentication e.g., `http://${proxy_username):$(proxy_password)@yourproxy.yourdomain`)
* If you do not run with administration rights, you may need to configure pip target path to write to your user home directory or consider using one of the `virtual environment` methods.

