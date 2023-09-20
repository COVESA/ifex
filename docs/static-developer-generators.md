# Generators

When the documentation speaks about generators, it is simply programs that output (non-IFEX) content:

- Other IDL formats
- Traditional "code generation", i.e. the output is some programming language
- Documentation

etc.

## Configurability - when to create a layer?

Let's identify two main ways that a tool can be configured:

- At invocation, for example using command-line flags/parameters
- Through IFEX "Layers" - which are input files in addition to the main IFEX core IDL file.

**Q: When should configurability be placed into layers, compared to command-line flags/parameters?**

A: Consider if the behavior is being changed "for all input", or in different ways for different objects mentioned in the main IFEX IDL file:

Layers are usually designed to refer to the individual items in the IFEX Core IDL description and add new metadata to their definitions.  Thus, layers are there to configure things _individually_ (by referring to each item, or through some pattern matching) for each item that is described in the interface.   For example, one `Property` might have get/set methods generated for it, whereas another `Property` _in the same interface_ should only have subscribe/unsubscribe methods generated for it.   One `Method` might be marked as "asynchronous" to generate appropriate code for asynchronous invocation, whereas another is going to be synchronous/blocking, and so on.

Just like different interface descriptions (IFEX Core IDL) are given as input, _different_ layer files might be given to the tool on each invocation.

In contrast, parameters that affect mostly the _whole_ generation step equally and are not modifying individual items of the input, should be given directly to the tool.  Most commonly, this is done by designing command line parameters that the tool accepts when it is run, but it is up to the designer to decide if an some other file (perhaps YAML) file is provided as input also to control such global configurations.

## Writing a generator

### Simple Generator

A simple generator (with only one template) can be done like this:

* Import the ifex_generator.py and ifex_parser.py modules
* Get the Interface description file in IFEX Core IDL format (YAML), for example from command line argument
* Get the Abstract Syntax Tree representation by calling `ifex_parser.get_ast_from_yaml_file(ifex_file)`
* Call `gen()` function in generator module, and pass the AST, and the name of a _single_ template.
* If needed, add any of your own custom logic (see also advanced usage for more information)

Unless you need to add more logic, generating one input file with one (or several)
templates is basically already available if ifex_generator.py is called as a
main program.  You specify the directory name (relative to `<project-dir>/ifex/templates`)
where the template(s) is stored.  Note that `setup.py` "installs" an executable entrypoint
`ifexgen` to call the program:

```bash
   ifexgen -d template-directory <service-description.yml>
```
### Advanced Generator

An advanced generator (with several templates) can be done like this:

* Import the ifex_generator.py and ifex_parser.py, and TemplateDir modules.
* Get the needed Service description file(s) (YAML), for example from command line argument
* For each file, get the Abstract Syntax Tree representation by calling `ifex_parser.get_ast_from_yaml_file(service_desc_file)`
* Write templates according to (some, not all) node types.  You can call `gen(node)` or `gen(node, <Template>)` from within a template - see details below.  Templates must be under a specific sub-directory of `<project-dir>/ifex/templates` and must be named with the naming convention such that the node type is mentioned first (see template chapter).
* Once the template directory is known, ee-initialize the TemplateDir object if needed.  This will populate the default templates data structure such that gen() knows which template to use.  It automatically uses the naming of the templates to know which template is for which node type.
* Implement the `gen()` function, normally by delegating directly into `ifex_generator.gen()`, but you can put your own logic here if needed.
* Set the jinja environment, passing in the gen() and any other symbols that must be callable from within Jinja templates.
* Call the `gen()`  function with the topmost node.  Store output in an appropriate file.
* Continue calling the `gen()` function with another node, and another template for another file (for example, generating .c and .h header files from the same input)
* ... implement any other required logic in the generator code, and/or with the advanced control options available in jinja2 templates.

* **NOTE!  Remember to inject any globals (e.g. functions) into the jinja environment if these are referred by the templates.**  See ifex_generator.py for example.
You can also pass data into templates through other variables (see jinja2 documentation).

## Setting up default templates

The generic generation always passes the top-level node (of type "AST") to the top-level template.
The template(s) can, if needed, call the gen() function on lower level nodes.

Unless a specific template is specified, the gen() function will use the predefined
table of templates and call the one that matches the node type that was passed.  The table
was initialized by the TemplateDir module, using the naming-convention mapping.

In other words, internally in the TemplateDir module, something like this will be set up, by matching the name of the template to the name of the node.

```python
default_templates = {
   'AST' : 'AST-mystuff-toplevel.txt',
   'Interface' : 'Interface-mystuff.c',
   'Type' :    'Type-mystuff-smart_type_mapper.c',
   'Method' :  'Method-mystuff.c'
}
```

All node templates must be inside a single directory (specified with the `-d` flag when calling `ifexgen`.   The naming convention is that the template file name must **start** with the node type name.  The rest of the file name does not matter\*.

e.g.
```
- AST.suffix
- Method-.something
- Interface-arbitrary_comments_can_be_written_here.html
```

\* If more than one template matches the node name (don't do that, unsupported) then the last found template will be used.

**NOTE:** It is not required to specify a separate template for every type as long as one of the upper level templates handle all necessary cases.  For simple cases, a single top-level AST template could even suffice for the whole generation and there are some such examples in the templates directory. (Also see further description under **Variable use in templates**).

## The gen() function

The `gen()` function has a short name to be convenient in templates.

You can call the `gen()` function from within a template to delegate the
required work for generating a certain node type to a separate template file.
(See Template example later).  Thus the templates can effectively "call" each
other, without the need for template-include or template-inheritance features
that jinja2 provides (but those features are of course also still possible to use).

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
The only strict requirement is that all templates to be used by automatic type-to-template mapping in the gen() function, must be within the same subdirectory and must be named according to the naming conventioned mentioned before.

Templates can be stored in the sub-directories of the ifex/templates/ directory.

The intended target format (output format) is normally clear from the naming of the subdirectory.  E.g. "protobuf", or "D-Bus" or "ARXML" or other output format.

Templates are only required to be named by using the node type name at the _start_ of the file name, but here is a more detailed _proposed_ naming convention:

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

If there is no obvious output type, we use normally ".tpl".

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
`item.namespaces[1].methods[0].description` - the description of the first
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
