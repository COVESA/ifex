# Interface Exchange framework (IFEX)

<img src="docs/images/IFEX-Logo-updated-turquoise%201.svg" alt="IFEX Logo Turquoise SVG" width="300" height="118">

This repository includes:

1. Specifications and documentation
2. Programs and tools

...for the the *Interface Exchange framework (IFEX)*.

IFEX is a general interface description and transformation technology to
integrate/unify/translate different IDLs, and provide tools and methods to
facilitate system integration using popular IPC/RPC protocols, and a variety of
deployment technologies.

In addition, IFEX defines a Interface Model (and its associated YAML syntax =
IDL), which can be _optionally_ used as a one-and-all source format for
interface definitions.  The flexible core model together with the strong
_Composable Layers_ design makes it a strong candidate for being the most
capable interface description approach available. However, using the
translation tools does not in itself require accepting the IFEX "IDL" as the
unifying format.

## License and Contributions

- The code is provided under the license listed in the file LICENSE, unless otherwise stated in each section or file.

- Contributions to the project are accepted under the terms of the license applicable to each file, pursuant to the standard Developer Certificate of Origin (DCO) used in Linux Kernel development and elsewhere (see DCO.txt or https://developercertificate.org).  Contributors are expected to familiarize themselves with the DCO, and to add Signed-Off-By: lines to their commits to reiterate that the contribution is made according to the statements in the DCO.

- Contribution proposals can be made as Pull-Requests or Issues in the main project repository.

## Documentation

Please refer to the [documentation](https://covesa.github.io/ifex) for more information.  
For updates and deep-dive articles, see [the Wiki](https://github.com/COVESA/ifex/wiki) for this repository.

> [!TIP]
> Quickly prototype and validate your IFEX API definitions by using the [Playground](https://covesa.github.io/ifex-viewer/playground/).

## IFEX software tools

Some of the programs implement the tools for reading/writing/translating
interface descriptions and code-generation.  Other programs generate the IFEX
interface model/language-specification and other documentation.

The implementations are primarily written in python and using some preferred
technologies, such as the [Jinja2 template language](https://jinja.palletsprojects.com) 
([(alt.  link)](https://jinja2docs.readthedocs.io/en/stable/)).

## Project Structure

```
├── docs
│   ├── MD-formatted documents, templates for generation, and static content.
│   ├── README.md => when viewing docs directory in GitHub, the README is rendered
├── helpers
│   ├── Integrations to associated ecosystems and tools
│   ├── How-tos or scripts to run code-generation on output results
│   ├── Example:  sd-bus-c++ generator tools
├── input_filters
│   ├── Separate dirs for each supported input IDL
│   ├── Implementation of common code for parsing/reading each format
│   ├──    ... but not including the AST definitions (see models/)
│   ├──    ... therefore, dirs are not guaranteed to include any code
           ... if it is self contained under the respective transformation implementation
│   ├──    ... however, some common code for a language may find its place here
├── output_filters
│   ├── Separate dirs for each supported interface description model
│   ├── Implementation of converters from ANY (AST) to text IDL
│   ├──    ... in other words "print out this AST" type of function
│   ├── JSON-schema generation
│   ├── Jinja templates exist here
├── layer_types
│   ├── Framework for Layers, and separate dirs for each Layer Type definition
├── models
│   ├── Separate dirs for each supported interface description model
│   ├── The internal models (a.k.a. AST definition) for IFEX and other languages
├── packaging
│   ├── Helper files for packaging the project in various ways
│   ├── docker - Docker deployment, for testing and/or end-user use
│   └── entrypoints - 
│       ├── Short script wrappers defining entry-points for python tools
│       ├──    ... defines the executable commands created when installing the package
├── requirements.txt, pyproject.toml, tox.ini. - Python dependencies expressed in different ways
├── scripts
│   ├── Helper scripts primarily used for development, not end-user scripts
├── tests
│   ├── Unit test definitions, and input data
└── transformers
│   ├── Separate dirs for each supported interface description model
│   ├── Generic rule-based "transformation engine" implementation, that may be used by multiple tools
│   ├── Implementation of specific transformers, if not covered by input/output filters

```

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

NOTE: Pyenv can set up virtual environments but is often considered not the best
choice for that, and we don't use it that way.  Pyenv's most important function
is to download, compile, and install a particular python version from source
code.  If your system python version is one that is not supported by this
project and you are not able to install the right python version using another
method, then Pyenv can be used.  It can be used in combination with
virtual-environment handlers, to get access to different python versions.

If [`pyenv` shell command](https://github.com/pyenv/pyenv) is not installed, use its [installer](https://github.com/pyenv/pyenv-installer) to get it:

```bash
   curl https://pyenv.run | bash  # download and install (YOU are responsible to check the script content)
   exec $SHELL                    # restart your shell using the new $PATH
```

Activate a version in the current environment
```sh
pyenv local 3.10.6
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
