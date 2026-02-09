# Interface Exchange framework (IFEX)

<img src="docs/public/ifex-logo.svg" alt="IFEX Logo Turquoise SVG" width="300" height="118">

This repository includes:

1. Specifications and documentation
2. Programs and tools

...for the the *Interface Exchange framework (IFEX)*.

IFEX is a general interface description and transformation technology to
integrate/unify/translate different IDLs, and provide tools and methods to
facilitate system integration using popular IPC/RPC protocols, and a variety of
deployment technologies.

In addition, IFEX defines a Interface Model (and its associated YAML syntax =
IDL), which can be *optionally* used as a one-and-all source format for
interface definitions.  The flexible core model together with the strong
*Composable Layers* design makes it a strong candidate for being the most
capable interface description approach available. However, using the
translation tools does not in itself require accepting the IFEX "IDL" as the
unifying format.

## License and Contributions

- The code is provided under the license listed in the file LICENSE, unless otherwise stated in each section or file.

- Contributions to the project are accepted under the terms of the license applicable to each file, pursuant to the standard Developer Certificate of Origin (DCO) used in Linux Kernel development and elsewhere (see DCO.txt or <https://developercertificate.org>).  Contributors are expected to familiarize themselves with the DCO, and to add Signed-Off-By: lines to their commits to reiterate that the contribution is made according to the statements in the DCO.

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
│   ├── README.md => when viewing docs directory in GitHub, the README is render
ed
├── helpers
│   ├── Integrations to associated ecosystems and tools
│   ├── How-tos or scripts to run code-generation on output results
│   ├── Example:  sd-bus-c++ generator tools
├── ifex
│   ├── input_filters
│   │   ├── Separate dirs for each supported input IDL
│   │   ├── Implementation of common code for parsing/reading each format
│   │   ├──    ... but not including the AST definitions (see models/)
│   │   ├──    ... therefore, dirs are not guaranteed to include any code
│   │   │      ... if it is self contained under the respective transformation implementation
│   │   ├──    ... however, some common code for a language may find its place here
│   ├── output_filters
│   │   ├── Separate dirs for each supported interface description model
│   │   ├── Implementation of converters from ANY (AST) to text IDL
│   │   ├──    ... in other words "print out this AST" type of function
│   │   ├── JSON-schema generation
│   │   ├── Jinja templates exist here
│   ├── layer_types
│   │   ├── Framework for Layers, and separate dirs for each Layer Type definition
│   ├── models
│   │   ├── Separate dirs for each supported interface description model
│   │   ├── The internal models (a.k.a. AST definition) for IFEX and other languages
│   ├── transformers
│   │   ├── Separate dirs for each supported interface description model
│   │   ├── Generic rule-based "transformation engine" implementation, that maybe used by multiple tools
│   │   ├── Implementation of specific transformers, if not covered by input/output filters
│   └── entrypoints -
│       ├── Short script wrappers defining entry-points for python tools
│       └──    ... defines the executable commands created when installing the package
├── distribution
│   ├── Helper files for packaging or deploying the project in various ways
│   ├── docker - Docker deployment, for testing and/or end-user use
├── pyproject.toml. - Python dependencies and project setup
├── scripts
│   ├── Helper scripts primarily used for development, not end-user scripts
└── tests
    ├── Unit test definitions, and input data
```

## Getting started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- Python >=3.10 (uv will manage this automatically)

### Installation with uv

Install uv if you haven't already, using [one of the proposed installation methods](https://docs.astral.sh/uv/getting-started/installation/), e.g.:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup and install

Go to the project directory and install the project with dependencies:

```bash
# Install the project in development mode
uv sync

# Activate the virtual environment
source .venv/bin/activate
```

Alternatively, run commands directly with uv:

```bash
# Run commands without activating the environment
uv run ifexgen --help
```

If you want to use the entrypoints as convenient commands in your environment, install them as `uv tool`.

> Note: This requires `~/.local/bin` to be in your `$PATH`!

```bash
uv tool install .
ifexgen --help
```

### Container use

As an alternative to installation instructions below, all the installations can also be hidden in a container.  Refer to the [README in the distribution/docker/ directory](./distribution/docker/README.md) for running the tools using containers instead.

## Trying it out

Installing the IFEX tools using `uv tool install .` creates some convenient
executable shims, e.g. `ifexgen`, `ifexgen_dbus`, `ifexconv_protobuf`, ...

If those commands are not in your environment, try setting up python virtual environment and make sure `uv tool install .` runs correctly.  After that, they should be in the `$PATH` variable and possible to run.

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

# Building PyPI Package

To build the IFEX package for distribution:

```bash
uv build
```

This creates both source distribution (`.tar.gz`) and wheel (`.whl`) files in the `dist/` directory.

# Unit Tests

The project uses pytest to define unit tests. A starting point is in the tests
directory and more can be added.

To run tests:

```bash
uv run pytest -v tests
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

- If the installation (uv sync) is executed behind a (corporate) proxy, the following environments variables must be set: `http_proxy` and `https_proxy` (including authentication e.g., `http://${proxy_username):$(proxy_password)@yourproxy.yourdomain`)
