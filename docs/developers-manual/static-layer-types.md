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

