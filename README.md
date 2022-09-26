# VSC-tools

This repository includes tools related to the "VSC" interface/service
description language.

Primarily, it allows reading a service description and generating various
types of output.  It uses the [Jinja2 templating language](https://jinja.palletsprojects.com) ([(alt. link)](https://jinja2docs.readthedocs.io/en/stable/))
for most output definitions.

## Getting started

### Prerequisites
* Python 3.10 installed
* If the installation (pip install) is executed behind a (corporate) proxy, the following environments variables must be set: `http_proxy` and `https_proxy` (including authentication e.g., `http://${proxy_username):$(proxy_password)@yourproxy.yourdomain`)
* If you do not run with administration rights, you may need to configure pip target path to write to your user home directory or consider [using the `pipenv` method](#setup-with-pipenv).

```bash
On Unix and Mac OS X the configuration file is: $HOME/.pip/pip.conf
If the file does not exist, create an empty file with that name.

Add or replace the following lines:
[global]
target=/somedir/where/your/account/can/write/to

On Windows, the configuration file is: %HOME%\pip\pip.ini
If the file does not exist, create an empty file with that name.

Add or replace the following lines:
[global]
target=C:\SomeDir\Where\Your\Account\Can\Write\To
```
### Project Setup

* If you use a custom pip installation directory, set the `PYTHONPATH` environment variable to the directory that you set in the `pip.ini` file.

### Setup with `virtualenv`

```bash
   python3 -m venv venv
   source venv/bin/activate
```

### Setup with `pipenv`
[pipenv](https://pypi.org/project/pipenv/) is a tool that manages a virtual environment and install the package and its dependencies, making the process much simpler and predictable, since the `Pipfile` states the dependencies, while `Pipfile.lock` freezes the exact version in use.

If [`pyenv` shell command](https://github.com/pyenv/pyenv) is not installed, use its [installer](https://github.com/pyenv/pyenv-installer) to get it:

```bash
   curl https://pyenv.run | bash  # download and install
   exec $SHELL                    # restart your shell using the new $PATH
```

Make sure Python version 3.10.6 is installed:
```bash
   pyenv install 3.10.6  # install the versions required by Pipfile
```

Install this project and its dependencies in the local `.venv` folder in this project, then use it (`pipenv shell`):
```bash
   export PIPENV_VENV_IN_PROJECT=1 # will create a local `.venv` in the project, otherwise uses global location
   pipenv install --dev # install the development dependencies as well
   pipenv shell         # starts a shell configured to use the virtual environment
```

### Setup using plain `pip install`

Run from the vss-tools project root directory

```bash
   pip install -r requirements.txt
```  

## Testing it out
Work in progress!  This is the usage pattern:

```bash
   vscgen <input-yaml-file (path)> <output-template-file (name only, not path)>
```

For the moment, try this:

```bash
   git clone https://github.com/COVESA/vehicle_service_catalog
   
   vscgen vehicle_service_catalog/comfort-service.yml simple_overview.tpl
```

This example exercises the parser to create the AST out of a YAML file
from the Vehicle Service Specification
and then prints out an overview using the template.

^^^ Edit the code if you want to try out other things.  This will soon be more
flexible of course.

Looking at the jinja2 template shows how to traverse it directly by
referencing each object's public member variables (see template
[simple_overview.tpl](vsc/templates/simple_overview.tpl)).

# Unit Tests

The project uses pytest to define unit tests.  In the tests directory is a
simple starting point.  More can be added.

To run tests, just run pytest in the root directory.

```bash
   pytest -v
```

# Writing a generator

## Simple Generator

A simple generator (with only one template) can be done like this:

* Import the vsc_generator.py and vsc_parser.py modules
* Get the Service description file (YAML), for example from command line argument
* Get the Abstract Syntax Tree representation by calling `vsc_parser.get_ast_from_file(service_desc_file)`
* Call `gen()` function in generator module, and pass the AST, and the name of a single template.
* If needed, add any of your own custom logic (see also advanced usage for more information)

Unless you need to add more logic, generating one input file with a single
template is basically already available if vsc_generator.py is called as a main
program:

```bash
   vscgen <service-description.yml> <jinja-template-name>
```

NOTE:  Due to how jinja loads templates (without adding a custom
loader, which has not been done), the first argument is the *path* to the
YAML file, but the second argument is only the name of the template (which
must be in [vsc/templates/ dir](templates).  Pointing to the full path of a
template file in a different location is not implemented in vsc_generator.py

## Advanced Generator

An advanced generator (with several templates) can be done like this:

* Import the vsc_generator.py and vsc_parser.py modules
* Get the needed Service description file(s) (YAML), for example from command line argument
* For each file, get the Abstract Syntax Tree representation by calling `vsc_parser.get_ast_from_file(service_desc_file)`
* Write templates according to (some, not all) node types.  You can call `gen(node)` or `gen(node, <Template>)` from within a template - see details below.
* Set the default_templates member variable in generator to configure which templates to use (see section below).
* Implement the `gen()` function, normally by delegating directly into `vsc_generator.gen()`, but you can put your own logic here if needed.
* Call the `gen()`  function with the topmost node.  Store result in appropriate file.
* Continue calling the `gen()` function with another node, and another template for another file (for example, generating .c and .h header files from the same input)
* ... implement any other required logic in the generator code, and/or with the advanced control options available in jinja2 templates.

* **NOTE!  Remember to inject any globals (e.g. functions) into the jinja environment if these are referred by the templates.**  See vsc_generator.py for example.
You can also pass data into templates through other variables (see jinja2 documentation).

### Setting up default templates

This setting is a dictionary mapping the AST node types to the default
template to use for that node type.  It can be overridden in a call to
gen() but for a particular code generation purpose it is better to set this
up.

```python
generator.default_templates = {
   'AST' : 'AST-mystuff-toplevel.txt',
   'Service' : 'Service-mystuff.c',
   'Type' :    'Type-mystuff-smart_type_mapper.c',
   'Method' :  'Method-mystuff.c'
}
```

**NOTE:** It is not required to specify a separate template for every type.
Very often, nodes can be generated directly from the parent template type.
For simple cases, a single top-level template might suffice for the whole 
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
and generate using the predetermined template for that node type.  (See 
`default_templates` variable).

2. Providing the node and a specific template.  The specified template is
   used regardless of the node type:

```python
def gen(node : AST, templatename : str)
```

example use:

```python
gen(node, 'My-alternative-method-template.tpl')
```

# Writing Templates

### Naming convention
Templates must be stored in the vsc/templates/ directory.

Templates should be named using this convention:

`<node-type>-<target-format>-<variant>.<suffix>`

* **node-type** must be the exact name of the corresponding class in the AST, e.g.
Service, Method, Type, etc. A template that consumes the top-level root node
would use the node type AST.
* **target-format** is a free form name for whatever it is you are generating
* **variant** is optional and just to indicate there might be multiple ways to generate the
same thing for the same target.  Basically, use your own judgement to name the
template with useful information here.
* **suffix** should try to mimic the normal suffix for the file format that is
being generated.  For example, if the templates aims to generate a HTML
document, name the template with .html.  If it is generating a programming
language, use an appropriate suffix for the file, etc.  If there is no obvious
type, we use ".tpl".

Examples:

```yaml
Datatypes-my_docs-simple.html
Datatypes-my_docs-advanced.html
Method-c++-without-comments.cpp
Method-c++-with-comments.cpp
Service-nodejs.js
Service-rust.rs
```

### Variable use in templates

* The standard functions in vsc_generator.py will pass in only a single node
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
generalized and introduced into the vsc_generator.py helper module, for
better reuse between custom generator implementations.

### Template example

This template expects that the "item" passed in is a Service object.
It calls the gen() function from within the template to delegate work
to a separate template for Methods.

**Service-mygen.c**

```python
// General file header information
// ...

// Service name: {{ item.name }}

{% for i in s.namespaces %}
// namespace: {{ i.name }}
// {{ i.description }}
{% for x in i.methods %}
  {{ gen(x) }}     <- delegate work to a separate template for Methods
{% endfor %}
{% endfor %}
```

The gen() function in the vsc_generator implementation will determine the node
type of `x` at runtime, yielding `Service`.  It will will then look into the
`default_templates` variable to see which is the template file to use for a
Service node, and generate the node using that template.

The global `default_templates` variable is defined by vsc_generator to point
to some templates used for test/demonstration. A custom generator
implementation would modify this variable, or simply overwrite the value after
including the vsc_generator as a module (or later on, this might be passed in
at run-time in a different way).

# Existing Tools/Templates

Template | Description | Status | Documentation |
| ------------------ | ----------- | -------------------- |-------------------- |
[dtdl.tpl](vsc/templates/dtdl.tpl) | Generates a DTDL description of the service | Functional | [documentation](vsc/templates/dtdl.md) |
[protobuf.tpl](vsc/templates/protobuf.tpl) | Generates a Protobuf description of the service | Functional | [documentation](vsc/templates/protobuf.md) |
[sds-bamm-aspect-model.tpl](vsc/templates/sds-bamm-aspect-model.tpl) (using [sds-bamm-macros.tpl](vsc/templates/sds-bamm-macros.tpl))| Generates a BAMM Aspect Meta Model of the service | Functional | [documentation](vsc/templates/sds-bamm-aspect-model.md) |
[test.tpl](vsc/templates/test.tpl) | Dummy Example | Not Functional | - |
[AST-simple_doc.tpl](vsc/templates/AST-simple_doc.tpl) | Very simple HTML generator, relying on [Service-simple_doc.html](vsc/templates/Service-simple_doc.html)| Not Functional | - |
[simple_overview.tpl](vsc/templates/simple_overview.tpl) | Generates a textual overview of a service | Functional | - |
[Argument-simple_doc.html](vsc/templates/Argument-simple_doc.html) | Default template for arguments| Not Functional | - |
[Service-simple_doc.html](vsc/templates/Service-simple_doc.html) | Default template for services| Not Functional | [- |

# Future plans, new proposals and enhancements

Please refer to [GitHub tickets](https://github.com/COVESA/vsc-tools/issues)
(Feel free to make a proposal or ask a question)

# Known bugs

Please refer to [GitHub tickets](https://github.com/COVESA/vsc-tools/issues)
with the label "bug"
