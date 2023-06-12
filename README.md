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

Looking at other jinja2 templates shows how to traverse it directly by
referencing each object's public member variables (see template
[simple_overview.tpl](ifex/templates/simple_overview.tpl)).

## Writing a generator

### Simple Generator

A simple generator (with only one template) can be done like this:

* Import the ifex_generator.py and ifex_parser.py modules
* Get the Service description file (YAML), for example from command line argument
* Get the Abstract Syntax Tree representation by calling `ifex_parser.get_ast_from_yaml_file(service_desc_file)`
* Call `gen()` function in generator module, and pass the AST, and the name of a single template.
* If needed, add any of your own custom logic (see also advanced usage for more information)

Unless you need to add more logic, generating one input file with a single
template is basically already available if ifex_generator.py is called as a main
program:

```bash
   ifexgen <service-description.yml> <jinja-template-name>
```

NOTE:  Due to how jinja loads templates (without adding a custom
loader, which has not been done), the first argument is the *path* to the
YAML file, but the second argument is only the name of the template (which
must be in [ifex/templates/](ifex/templates) directory. Pointing to the full path of a
template file in a different location is not implemented in ifex_generator.py

### Advanced Generator

An advanced generator (with several templates) can be done like this:

* Import the ifex_generator.py and ifex_parser.py modules
* Get the needed Service description file(s) (YAML), for example from command line argument
* For each file, get the Abstract Syntax Tree representation by calling `ifex_parser.get_ast_from_yaml_file(service_desc_file)`
* Write templates according to (some, not all) node types.  You can call `gen(node)` or `gen(node, <Template>)` from within a template - see details below.
* Set the default_templates member variable in generator to configure which templates to use (see section below).
* Implement the `gen()` function, normally by delegating directly into `ifex_generator.gen()`, but you can put your own logic here if needed.
* Call the `gen()`  function with the topmost node.  Store result in appropriate file.
* Continue calling the `gen()` function with another node, and another template for another file (for example, generating .c and .h header files from the same input)
* ... implement any other required logic in the generator code, and/or with the advanced control options available in jinja2 templates.

* **NOTE!  Remember to inject any globals (e.g. functions) into the jinja environment if these are referred by the templates.**  See ifex_generator.py for example.
You can also pass data into templates through other variables (see jinja2 documentation).

## Setting up default templates

**THIS SECTION SHOULD MOVE TO DEVELOPMENT DOCUMENTATION**

The generic generation always passes the top-level node to the top-level template.
The template(s) can, if needed, call the gen() function on lower level nodes.

Unless a specific template is specified, the gen() function will use a predefined
table of templates and call the one that matches the node type that was passed.

For example:

```python
default_templates = {
   'AST' : 'AST-mystuff-toplevel.txt',
   'Interface' : 'Interface-mystuff.c',
   'Type' :    'Type-mystuff-smart_type_mapper.c',
   'Method' :  'Method-mystuff.c'
}
```

The table of default templates is now defined automatically through a naming convention.  All node templates must be inside a single directory (specified with the `-d` flag when calling `ifexgen`.   The templates also need to follow a naming convention.  The template file name must **start** with the node type name\*.

e.g.
```
- AST.suffix
- Method-.something
- Interface-arbitrary_comments_can_be_written_here.html
```

\* If more than one template matches the node name (don't do that, unsupported) then the last found template will be used.

**NOTE:** It is not required to specify a separate template for every type.
Very often, nodes can be generated directly from the parent template type.
For simple cases, a single top-level template might even suffice for the whole
generation.

## The gen() function

The `gen()` function has a short name to be convenient in templates.

You can call the `gen()` function from within a template to delegate the
required work for generating a certain node type to a separate template file.
(See Template example later).  Thus the templates can effectively "call" each
other, without the need for template-include or template-inheritance features
that jinja2 provides (but those features are of course still possible to use).

`gen()` can be called with (1) just the node (evaluating the passed parameter type at run-time)
or (2) by explicitly stating a template:

1. Providing the node reference only:

```python
def gen(node : AST)
```

example use:

```python
gen(node)
```

This variant will dynamically determine the node type (a subclass of AST)
and generate using the predetermined template for that node type.

2. Alternate use is to specify the node _and_ a specific template.  The
   specified template is then used regardless of the node type:

```python
def gen(node : AST, templatename : str)
```

example use:

```python
gen(node, 'My-alternative-method-template.tpl')
```

# Writing Templates

### Naming convention
The only strict requirements

Templates can be stored in the sub-directories of the ifex/templates/ directory, (but alternatively an absolute path can be given to the `ifexgen` tool).

The intended target format (output format) is normally clear from the naming of the subdirectory.  E.g. "protobuf", or "D-Bus" or "ARXML" or other output format.

Templates are only required to be named by using the node type name at the start of the file name.

Here is however a more detailed _proposed_ naming convention:

`<node-type>-<target-format>-<variant>.<suffix>`

* **node-type** must be the exact name of the corresponding class in the AST, e.g.
Service, Method, Type, etc. A template that consumes the top-level root node
would use the node type AST.
* **target-format** is a free form name for whatever it is you are generating
* **variant** is optional and just to indicate there might be multiple ways to generate the
same thing for the same target.  Basically, use your own judgement to name the
template with useful information here.
* **suffix** shall mimic the normal suffix for the file format that is
being generated.  For example, if the templates aims to generate a HTML
document, then name the template with `.html`.  If it is generating a
programming language, use an appropriate suffix for that language.

If there is no obvious type, we can use ".tpl".

### Variable use in templates

* The standard functions in ifex_generator.py will pass in only a single node
of AST type to the template generation framework.  (If you define your own
custom generator, it could choose to do something different).

The passed node and will have a particular node type (subclass to AST).  The
type depends on what type of template is being rendered (or more correctly,
what was specified when the generation function was called -- either a top
level function like render_ast_with_template_file() or a call to gen() with
the node in question as parameter.)

* When using the provided generator convenience functions, the node that is
"passed to the template" (roughly speaking) will always be named **item**

* The class member variables (referring to the children of a node) in
all AST nodes are public.  This means they can be referenced directly through
dot-notation inside code that is embedded in the jinja template.  For example,
if the passed `item` is a Service the template can get to the _list_ of
namespaces in the service by just referencing it: `item.namespaces`

This of course means that dot-notation could also be chained:
`item.namespaces[1].methods[0].description` - the description of th efirst
method name in the second namespace.

It is however more likely to use loop constructs to iterate over lists than to
address specific indexes like that:

```python
{% for i in item.namespaces %}
   this is each namespace name: {{ i.name }}
{% endfor %}
```

# Advanced features

jinja2 is a very capable templating language.  Generators can make use of any
features in python or jinja2 to create an advanced generator.  Any features
that might be applicable in more than one place would however be best
generalized and introduced into the ifex_generator.py helper module, for
better reuse between custom generator implementations.

### Template example

This template expects that the "item" passed in is a Service object.
It calls the gen() function from within the template, for each of the
method objects.  This delegates the work to to a separate template for Methods.

**Namespace-mygen.c**

```python
// General file header information
// ...

// Service interface name: {{ item.name }}

{% for i in s.namespaces %}
// namespace: {{ i.name }}
// {{ i.description }}
{% for x in i.methods %}
  {{ gen(x) }}     <- delegate work to a separate template for Methods
{% endfor %}
{% endfor %}
```

The gen() function in the ifex_generator implementation will determine the node
type of `x` at runtime, yielding `Namespace`.  It will will then look into the
`default_templates` variable to see which is the template file to use for a
Service node, and generate the node using that template.

The `default_templates` are defined when instantiating the JinjaTemplateEnv
class with a given template directory.  A search will happen to find the
matching templates in that directory.

A custom generator implementation might modify this variable to achieve
other effects, or instantiate more than one JinjaTemplateEnv.

# Existing Tools/Templates

Try the directory names of dtdl, protobuf, sds-bamm, simple etc.  (see [templates dir](https://github.com/COVESA/ifex/tree/master/ifex/templates) for more)

- dtdl: Generates a Protobuf description of the service: [documentation](ifex/templates/protobuf.md)
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

