# VSC-tools

This repository includes tools related to the "VSC" interface/service
description language.

Primarily, it allows reading a service description and generating various
types of output.  It uses the [Jinja2 templating language](https://jinja.palletsprojects.com) ([(alt. link)](https://jinja2docs.readthedocs.io/en/stable/))
for most output definitions.

# Work in progress...

Work in progress!  For the moment, try:

```
usage: vsc_generator.py <input-yaml-file (path)> <output-template-file (name only, not path)>
```
Try this:
```
python model/vsc_generator.py seats-service.yml simple_overview.tpl
```

This example exercises the parser to create the AST out of the YAML file
and then prints out an overview using the template.

^^^ Edit the code if you want to try out other things.  This will soon be more
flexible of course.

Looking at the jinja2 template shows how to traverse it directly by
referencing each object's public member variables (see template
[simple_overview.tpl](templates/simple_overview.tpl)).

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

```
python model/vsc_generator.py <service-description.yml> <jinja-template-name>
```

NOTE:  Due to how jinja loads templates (without adding a custom
loader, which has not been done), the first argument is the *path* to the
YAML file, but the second argument is only the name of the template (which
must be in [templates/ dir](templates).  Pointing to the full path of a
template file in a different location is not implemented in vsc_generator.py

## Advanced Generator

An advanced generator (with several templates) can be done like this:

* Import the vsc_generator.py and vsc_parser.py modules
* Get the needed Service description file(s) (YAML), for example from command line argument
* For each file, get the Abstract Syntax Tree representation by calling `vsc_parser.get_ast_from_file(service_desc_file)`
* Write templates according to (some, not all) node types.  You can call `gen(node, <Nodetype>)` from within a template - see details below.
* Set the default_templates member variable in generator to configure which templates to use (see section below).
* Implement the `gen()` function, normally by delegating directly into `generator.gen()`, but you can put your own logic here if needed.
* Call the `gen()`  function with the topmost node.  Store result in appropriate file.
* Continue calling the `gen()` function with another node, and another template. Possibly store result in another file (for example, generating .c and .h header files from the same input)
* ... implement any other required logic in the generator code, and/or with the advanced control options available in jinja2 templates.

* **NOTE!  Remember to inject any globals (e.g. functions) into the jinja environment if these are referred by the templates.**  See vsc_generator.py for example.
You can also pass data into templates through other variables (see jinja2 documentation).

### Setting up default templates

This setting is a dictionary mapping the AST node types to the default
template to use for that node type.  It can be overridden in a call to
gen() but for a particular code generation purpose it is better to set this
up.

```
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

The gen() function has a short name to be convenient in templates.

You can call the gen() function from within a template to delegate the
required work for generating a certain node type within a larger generation.
(See Template example).  Thus the templates can effectively "call" each other,
without the need for template-include or template-inheritance features from
jinja library (possible use for these in the future?)

gen() is an overloaded function that can be called in two ways. (Of course,
python does not directly support overloading, except through tricks like the
module named multipledispatch and decorators).  But with dynamic types and
evaluating the passed parameters in run-time it is possible to get this
effect. So just consider gen() to have two alternative function signatures as
follows:

1. Specifying the data type (node type) which can be any named subclass to the AST node type.  I.e. nodetype is the _class name_, not the node itself
This usage will use whatever default template was set up for that node type:
```
def gen(node : AST, nodetype)
example use:
 gen(node, Method)
 gen(anothernode, Type)

```
nodetype shall be the exact *class name*, i.e. any subclass of the AST class
(see vsc_parser.py)


2. Alternative usage which overrides the default template.  In this case, the node type is not required.
```
def gen(node : AST, templatename : str)
example use:
gen(node, 'My-alternative-method-template.tpl')
```

# Writing Templates

### Naming convention
Templates must be stored in the templates/ directory.

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
language, use an appropriate suffix for the file, etc.

Examples:

```
Datatypes-my_docs-simple.html
Datatypes-my_docs-advanced.html
Method-c++-without-comments.cpp
Method-c++-with-comments.cpp
Service-nodejs.js
Service-rust.rs
```

### Variable use in templates

* The standard functions in vsc_generator.py will pass in only a single node
of AST type to the template generation framework.  The node will be of a
particular type, depending on what type of template is being rendered
(or more correctly, what was specified when the generation function was called
 -- either a top level function like render_ast_with_template_file()
 or a call to gen() with the node in question as parameter.)

* When using the provided generator convenience functions, the node that is
"passed to the template" (roughly speaking) will always be named **item**

* Since the class members are public, they can be walked directly through
dot-notation in code that is embedded in the template.  For example, if the
passed item is a Service the template can get to the interfaces list by
just referencing it:  `item.interfaces`

Dot notation can be chained as needed:
`item.interfaces[1].methods[0].descripion` - the first method name in the
second interface.
...but of course it is more likely to use loop constructs to iterate over
lists than to address specific indexes like that:

```
{% for i in item.interfaces %}
   this is each interface name: {{ i.name }}
{% endfor %}
```

# Advanced features

jinja2 is a very capable templating language.  Advanced generators can of
course make use of any features in python or jinja2 to create an advanced
generator.  Any features that might be applicable in more than one place would
however be best generalized and introduced into the vsc_generator.py helper
modules, for better reuse.

### Template example

This templates expects that the "item" passed in is the Service object.
It calls the gen() function from within the template to delegate work
to a separate template for Methods.

**Service-mygen.c**
```
// General file header information
// ...

// Service name: {{ item.name }}

{% for i in s.interfaces %}
// Interface: {{ i.name }}
// {{ i.description }}
{% for x in i.methods %}
  {{ gen(Method, x) }}     <- delegate work to a separate template for Methods
{% endfor %}
{% endfor %}
```

# Future plans, new proposals and enhancements

Please refer to [GitHub tickets](https://github.com/GENIVI/vsc-tools/issues)
(Feel free to make a proposal or ask a question)

# Known bugs

Please refer to [GitHub tickets](https://github.com/GENIVI/vsc-tools/issues)
with the label "bug"

