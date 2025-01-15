This manual is useful primarily for implementation of new IFEX tools, but sometimes also for people who use the tools and then develop software based on the output that was generated to/from IFEX.   Before reading the developers' manual, make sure you have read the [IFEX Core IDL specification](ifex-specification.md) and [FAQ](./FAQ.md).

# Mapping documents

By "mapping" we mean to describe how we may interpret and ultimately translate IFEX to or from another interface description environment, or a particular output format (computing environment, protocol, programming language, etc.).  It can be such things as listing the "features" of IFEX and seeing how we may implement those features in the target environment (or the opposite direction, listing the features of the other environment and how IFEX can meet them).

General documents describe our general strategy for approaching mappings.

Individual documents describe particular target (or source) standards.

- [D-Bus](./static-mapping-dbus.md)
- [Protobuf/gRPC](./static-mapping-protobuf.md)

# Datatype mapping

This is a general overview of how to approach mapping of fundamental datatypes between IFEX and another technical environment.

Based on this general advice, specific plans are typically written for the translation/mapping between IFEX and a certain technology.  They might be linked under the [Mapping documents](#mapping-documents) chapter.

## Common types that are trivially mapped to/from IFEX fundamental types

### (Direction Other -> IFEX)

| Generic data type | Explanation | IFEX Fundamental type | How to represent in IFEX if not fundamental type |
| --- | --- | --- | --- |
| Integer |  | uint32, int32, and other sizes... |  |
| Floating point |  | float, double   |  |
| Boolean |  | boolean |  |
| Tuple | A pair, triple, or larger group of objects, possibly of different type. | -- | Assumed to be represented by an array of fixed size (if identical types), or a `Struct` (if mixed types), or array of `Variant`s (if unknown/dynamic mixed types are needed)** |
| Union/Variant |  A data type that allows a variable to hold values of different data types at different times.   |  variant |  |
| Bit field | Efficient encoding of on/off true/false switches, as a collection of bits handled as an integer | -- |  Assumed to be represented by a fixed size integer\*\*, or (better, more descriptive and more generic) by an array of booleans\*\* |
| Enum class |  Enumeration type that provids type safety and scoping of constants.  |  Enumeration  |  |
| Set |  A collection of unique elements, where each element occurs only once. A set is typically used to store a collection of items that are unordered and where the order does not matter.   |  set (new)\* | |
| Map/Dictionary/Key-Value |  A collection of key-value pairs, where each key is associated with a value.  | map (new)\* |  |

\* Sets and Maps could have been represented in IFEX using the other fundamental types, possibly with a "Layer" that adds on the special behavior of Sets and Maps.  (How Set/Map can be simulated in environments that don't support them natively is described in the next chapter).  Despite this, it was decided that sets and maps in interfaces are common enough that IFEX Core IDL should support them as fundamental types.

\*\* These solutions propose to represent datatypes using a _comparable_ fundamental type in the IFEX interface description.  In many cases this is enough and carries the required behavior over to the IFEX Core IDL types.  However, in some cases this might be more like an approximation of the original type behavior.  If there are any constraints or type behavior that would be lost be translating to the IFEX Core IDL _only_, then an additional layer file can be created to include those aspects.  If this seems hard to understand, it is probably clearer when looking at the other direction IFEX -> Other, in which case such additional layers will be part of the input files to control how the IFEX representation shall be translated to the Other environment.  In any case, when processed, this combination of IFEX Core IDL and possibly additional layer can ensures the behavior remains according to the original type.

For example: the generic interface description may contain several parameters that are of type array-of-boolean.  The usage might in some environments have a deployment model that specifies that (for one specific instance) it shall be represented as a bitfield, whereas other instances remain as array-of-boolean in the generated code.  Other code-generation environments may instead have a built in rule that bitfields shall be used as the _default_ translation.  In either case, these particular mapping rules are defined by the target environment, i.e. requirements on how the code-generator shall behave, including additional information that the deployment model may provide.  They are not in the core interface description, as represented by the IDL, but in additional layers, as well as the particular behavior of the code-generator (as described in its requirements or documentation).

### (Direction IFEX -> Other)

For primitive types, we won't repeat them here - in effect the table above can simply be referred to in reverse order.  From time to time a widening (using more bits) might be needed for ints and floats if the exact size is not available in the target environment.  We would expect widening mappings to be safe but when a mapping is reversed we should normally not use a narrowing mapping, unless it is known to be safe, for example through known value-range constraints.

Let's consider a few of the slightly more complex types instead:

Here we will see how we may represent things on a data protocol that does not fundamentally know about more complex type behaviors like Set and Map, and can fundamentally only transfer things like arrays and structs.

| IFEX built-in type | Explanation |  Explanation/mapping if other environment does *not* support it |
| --------------------- | -- | ---------------------------------- | ------------------------------------------------------------------|
| `set` |  A collection of unique elements, where each element occurs only once, and usually, the order does not matter | A set can simply be represented by a collection (array). That values shall be unique is either known and enforced on both sides of a server/client interface, and/or after data-transfer an actual Set type might be used in the rest of the program if the programming language supports it |
| `map` |  A collection of key-value pairs, where each key is associated with a value. | A map can be represented as a linear array of Variant (alternating keys and values), or better structured as an array of 2-tuples (pairs).  A tuple in turn is also either a 2-array, or a struct with two members (key and value).  One natural choice is to represent it as an array of such structs. Either key or value could be a Variant types if that type is variable or unknown. |
| `opaque` | An IFEX representation of a data type that is either not possible or not desired to describe in further detail | Can be equivalent to a void-pointer (low-level C), Variant<> type (where supported), or array-of-bytes.  When transferring Opaque across a data protocol, it might be `Variant` if supported, or simply be an array-of-bytes, where the server and client knows how to re-interpret the value on the other side |
| `variant` | A type that contain objects of _different_ types, a.k.a. union/Any/Variant. | This is a representation of a "union" or "variant" type in IFEX core IDL - in other words a type that contains one (any) choice out of a list of multiple types.  In programming environments that support Variant types it is not an unknown binary-blob, but the _actual_ type of the object is known underneath.  Just like opaque, there are several possible ways to creatively represent variant if the target environment does not have the type built in.  If the client and server side can be trusted to both convert the serialized representation back to the correct Variant type, then an anonymous "blob" (array of bytes) can of course be used for the data transfer.  If not, more creative solutions need to be created where we describe both the data, and the _actual_ type information explicitly (in a struct for example) and transfer that over the interface.|


## Additional types available in some programming environments

| Generic data type | Explanation | IFEX Fundamental type | How to represent in IFEX if not fundamental type |
| --- | --- | --- | --- |
| Function/Lambda  |  Some programming environments have functions as first class objects and can transfer them as arguments in interfaces. | -- |  The application of this would often be specific to a programming language environment, and it's unlikely that the interface description will be highly portable if this feature was represented in the interface description.  When needed it is possible to define an appropriate typedef for transferring code, for example as a string (interpreted language) or binary blob (compiled/bytecode), or as fallback "opaque".  Beyond this, the details are undefined in the core IDL scope and left open for a target environment to define. |
| Reference/Pointer  |  | -- |  This is not considered a _datatype_ in the IDL.  If we are truly speaking about a Type, that signifies a reference to something else, this could be modeled using a system-specific typedef, like using a string name/identifier to refer to an object, or any other appropriate encoding of that data.  That is the explaination why Reference/Pointer it is not seen as a _datatype_ in its own right.  To understand how _arguments are passed_ by pointer or reference (in C++ or other languages), see the separate section below. |
| Iterator  |  A data type that allows traversal of elements in a container, such as an array or linked list.   | -- |  Assumed to be represented by a primitive type such as integer (or struct if required)   |

## Opaque (special) type

If a system includes some data type that does not fit into any of the generalized types above, it can be modeled as the **opaque** type in the IFEX IDL.  This is a last resort and together with information that is probably provided by a deployment layer, a specific code generator would encode the type behavior that is necessary.

# Comments on pointers, references, etc.

The IFEX core interface description (IDL) focuses on describing reusable, generic, _behavior_ of interfaces.  It does not prescribe how to transfer an argument to a method, only the type of the argument, and its in/out expectation.  In a lot of cases, IFEX will be used in an over-the-network IPC or RPC scenario where the question of pointers/reference is moot.  However, when used to represent a programming interface it may be worthwhile to comment on this.  From the general IFEX description we can deduce that a pass-by-value behavior is generally assumed for "in" parameters.  However, it is still up to the target environment code generator to decide if language features like pointers and references make sense.  The exact translation might be controlled by deployment layer information.  For example, some target environments could make use of immutable (const) references in the generated code for "in" parameters, and pointers or references for "out" parameters.  In either of these cases there is still no need to mention a specific reference type in the IFEX interface description - it is all decided in the particular target environment mapping.  This is a long way of saying that the IFEX core IDL does not need to support the concept of pointers or references, but in particular cases code-generators might use certain layer types to control if such features are used.

# Layer Types and Schemas

- Each Layer Type shall be backed by a formal definition of the YAML format that shall be followed for that layer type
-  At the moment the core language (IFEX Core IDL) has its formal definition inside of a python source code file, but a JSON-schema\* version is generated and release in the GitHub releases sections.  A JSON schema allow tools like VSCode to verify the format (\*note that a **JSON** schema can also be used to check a **YAML** file for conformance)

## Conforming to schema:

  - Ultimately, the tool implementations that consume a file (a certain layer type for example) are responsible to check their input.  Layer types are often unique for a certain tool - therefore the implementation of that layer type is something that happens when the corresponding tool(s) are implemented.
  - Implementations should naturally aspire to use shared implementations of generic code such as schema-checkers etc.

## File definition with combined layers.

IFEX straddles a line carefully.  On the one hand, the concept requires
strongly that interface descriptions shall be pure and free from
target-environment specific details, so that they can have maximum reuse in a
new context.  On the other hand, for an individual developer, it may in some
cases be more convenient to keep all relevant information (for a certain target
environment) within a single file, rather than having to work in multiple layer
files at the same time.  Keeping the pure interface description free of
deployment details avoids the common scope-creep pitfall, that makes the core
IDL grows over time with deployment-specific details. That has happened to many
other attempts at interface-frameworks that start simple but over time add more
and more necessary deployment details that only fit their particular purpose.  

For this reason, IFEX tools are planned to support a number of features to
reach a good compromise between the IFEX separation-of-concerns concept and
"developer-friendliness".  For example:
 - The ability to merge multiple layers in order to get a "combined file" output for studying
 - The ability to input a "combined file" that covers multiple layers, as long as the separation is well understood at the same time.
 - Tool support to visualize which parts are part of core IDL and which parts are part of different layer types.
 - Tool support to separate a "combined" file into its pure layers again - specifically to get the core IDL version out for reuse in a new context.
 - Tools should to the greatest extent clarify how to specify the type of input file (such as, with specific command line parameters, or by requiring input files in a certain order, or through other means).  Despite that, the file format of the IFEX Core IDL, and a strong recommendation to any future Layer Types, is to include a `type:` field to indicate the layer type this file adheres to, and a `schema:` field that uniquely identifies the name of the corresponding JSON schema that can be used to test the file for conformance.

## Syntax shortcuts

- The YAML tree-based format has many advantages such as being well understood, familiar, easy to process with tools, etc.  The hierarchical nature of interface definitions also fits well.  At the same time, these hierarchies and the YAML format can lead to quite large files and some difficulty in the overview.  Some developers feel that the YAML format is inconvenient to write manually.
- The first remedy for this is IFEX tools ability to convert in the first place.  Any output format that is considered "more readable" is perfectly fine to use when this is desired, and conversion or visualization tools should support many ways to study/view the information for maximum usefulness.  When tools are solid, it is basically possible to use any chosen format for the manual editing, in order to feed the framework with information.

- However, for the standard YAML format, there are also some things we can do:
- An item is generally identified by its path through the tree, where the individual path components is made up of simply the names of each node.  The name (or possibly a future extension: "slug") is unique at each level of the hierarchy. (In certain cases it may be sufficient to have a unique name for each item type).
- The path to an item is possible to write more concisely, as long as the node type being used is allowed in the stated position of the tree.

Example:

```yaml
namespaces:
  - name: A
    namespaces:
    - name: B
      namespaces:
      - name C
        <content>
```

This can alternatively use the shortcut notation:
```yaml
namespaces:
  - name: A.B.C
  <content>
```
and

```yaml
namespaces:
  - name: A.B
    namespaces:
    - name C
      methods:
      - name myMethod
        input:
        - name: activityVariant
          type: string

```
can also use the shortcut:
```yaml
namespaces:
  methods:
  - name: A.B.C.MyMethod
    ...
```

However, this would not be possible:
```yaml
namespaces:
  input:
  - name: A.B.C.MyMethod.activityVariant
```
...because an "input" node is not valid underneath the parent node of type Namespace.  It must be located under a method node and tools are not expected to know that 'MyMethod' refers to a method node in this case.

These rules are stated for the IFEX Core IDL and apply generally to any layer
that follows the same hierarchical structure as the fundamental interface
definition written in IFEX Core IDL.  We might remind here, however, that a new
**Layer Type** is _theoretically_ free to define its own rules and formats -- see
next chapter.

## Layer Types

A Layer Type defines the rules for how Layer Instances (or more commonly simply "layers") of that type shall be written.  It is basically free to define its own rules for the YAML format.   To fit into the IFEX tool philosophy it shall however:

1) Use a YAML-based format
2) Be designed to add some new context or target-environment specific information
3) Never redefine or overlap the IFEX Core IDL scope

### Example: End-to-end data integrity check

Here we exemplify this freedom with a theoretical Layer Type that is able to specify that certain method parameters must be transferred using a data integrity check (but others not).  In other words, the expectation from this Layer Type and its associated code-generator tool is that it should add the calculation of a CRC checksum on the sending side, and check it on the receiving side, but only for those method parameters that specify this.

This is also an example of a fundamental principle in the IFEX approach - many systems take a more primitive approach and model the dataCRC as an explicit method parameter.  This means adding/removing this changes the interface definition and gives a tighter coupling.  Here we show the advantage of separating the purely functional description of the interface - in this framework the method needs a parameter that is called activityvariant.  The need for integrity check on this parameter (because it may be particularly critical that the wrong activity is not started?) is not related to the function itself, but rather a characteristic that may be decided at a later stage in design.  The modification of the _generated code_ for this exchange would be the responsibility of the code generator, rather than the original interface designer who can focus on the functionality only.  In another system, perhaps the communication is protected by a transport-level data integrity checker, and this is considered OK.  So in that case, the use of this dataCRCcheck defined on the parameter is not necessary.  This clear separation of the _functional_ interface definition from its deployment details makes all interface descriptions more reusable in different contexts.

We also simplify the work by delegating to a code-generator all things that can be automatically generated from simple meta-data configuration.  It is of course always possible for a designer to fall back on modelling such parameters explicitly as part of the interface description itself, with the knowledge that it may reduce the flexibility somewhat.

First we look at the normally recommended way to create layer types, which is that they should mimic the structure of the core IDL when adding new metadata to an object, like this:

```yaml
namespaces:
  methods:
  - name: A.B.C.MyMethod
    input:
    - name: activityVariant
      dataCRCcheck: true
```

**dataCRCcheck** field is the only new piece of information, that is not part of IFEX Core IDL.  Note here that all _other_ parts are mirroring the original core-IDL hierarchy that we would see in the IFEX Core IDL definition of this method and its input.

The above strategy is the recommended structure to keep things consistent, but to exemplify that layers are _in principle_ free to define their own YAML-syntax and rules, the following would also be possible:

```yaml
AllDataCRCcheckDefinitions:
  - A.B.C.MyMethod.activityVariant: true
  - A.B.C.MyMethod.anotherParam: false
  ...
```

So, in a situation where the designer\*\* of this Layer Type anticipates that there will be many very similar lines and feels that the above is a more efficient way to write the information, THEN such a layer type definition *is* allowed.  This format is not allowed by the core IDL language, but it may be allowed by this Layer Type!  It should here be noted that the ability to build visualization tools that can add/remove layers or separate the input from different layers _might_ be affected if the hierarchical nature is not matched between Core IDL and other layers.  With that said, layer types are there to support efficient developer use (primary), and efficient tool implementation (secondary), so considering how things are best expressed is part of the task of defining a new Layer Type.

\*\*If the Layer Type has general applicability, it is of course recommended to discuss with the IFEX Community to get inspiration and feedback about what the most appropriate format is for any given Layer Type, _and_ to strive to create a common catalog of "official" Layer Types as well.


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
main program.  You specify the directory name (relative to `<project-dir>/output_filters/templates`)
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
* Write templates according to (some, not all) node types.  You can call `gen(node)` or `gen(node, <Template>)` from within a template - see details below.  Templates must be under a specific sub-directory of `<project-dir>/output_filters/templates` and must be named with the naming convention such that the node type is mentioned first (see template chapter).
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

Templates can be stored in the sub-directories of the output_filters/templates/ directory.

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

______________________________________________________________________

