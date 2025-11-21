# Layer Types

This directory stores well-defined Layer Types.  The layer concept of IFEX is extensible for nearly any future interface-related information. This means it must be possible to define proprietary layer types in downstream projects.  This directory is however a place for Layer types that the "upstream" IFEX project provides and have adopted from the IFEX development community, so that they may be considered as an agreed-upon standard.

Tools are expected to build upon these layer types rather than similar ones, if they need the kind of information these layer types provide.  As always, propose changes as needed.

Unless there is a separate linked specification document, the README.md in each directory acts as the specification.

Layer types should be usually stable, but are versioned just in case.

## Basic introduction

This is a primer for those that have not read the official project documentation, and other related blog posts, presentations, etc:

### What is a Layer?

A layer is a separate file that is processed as an addition to an original interface definition file.

A layer is either an modifying layer, or an augmenting layer.

An overlay, a.k.a. modifying layer, redefines (adds, changes or removes) information _within the same information set_ as the file it is modifying.  An augmenting layer adds new _types_ of information to the interface model.  In the hierarchical model we usually deal with, as represented by YAML, new types of information would simply be new keys in a key-value structure.  In some projects, it may be called as "new metadata fields".

For an overlay / modifying layer, the base file and the layer are written with the same Layer Type.  The most common use is to have a base file written in the IFEX Core IDL syntax, and to layer on top of this a file that is _also_ written in IFEX Core IDL.  This second file might be used to modify the original interface definition.  

For example, it might be desirable to keep the original unchanged because it is predefined as an interface standard. If circumstances require some special modification, an overlay would be appropriate to show these changes separately.  Overlays on the core interface definition would do things like removing unused methods, adding a parameter to certain methods, extending an Enum definition, changing a data type, and so on.

#### Specific examples of overlay scenarios

 1) A standard interface defines multiple methods, but a particular implementation does not use all of them.  It is then required to remove them from the final result, so that they are not part of a code-generation result.

 2) Usually, deployment-information often requires a new Layer Type (next section) because it adds new type of information, but there is an example of a deployment-time decision that may use an overlay written also using the Core IDL:.  You may want to add a parameter to a selection of methods from the predefined interface (using pattern-matching on method names for example).  The added parameter could be a security-token, or a data-integrity checksum, or a log-trace ID.  The point here is that such parameters are not really part of the business logic, and can therefore be kept away from the core interface description, and layered on top when it is time to deploy the interface in a particular context.  The extra parameters would show up in the generated code, but would not be complicating the understanding of the pure function of the interface, and its business logic.

#### Augmenting Layer Examples

An augmenting Layer Type, defines a _new class of information_ that is added to what is possible to express in IFEX Core IDL.  It defines new "metadata" fields that can be added to the interface model tree.

This ability is the core feature of IFEX that guarantees separation of concerns.  The pure interface description (core IDL) is defined separately from any deployment or technology-specific details (other layers).  This enables IFEX to be extensible to just about any needs, without feature-creep in the core IDL.

Some augmenting layers are specified in the directories of this, but here are additional examples:
- Timing requirements on data
- Specifying synchronous or asynchronous operation of method calls.  (This is by design not specified in the pure functional interface description, as this does not change the meaning of the operation)
- Configuration of code generation for a target language:  E.g. C++14 or 20?  2021 or 2024 edition of Rust?**
- Deployment details needed for a certain communication protocol (Any configuration that is possible to do on this technology. Endpoints and IP addresses, transport protocol (TCP or UDP) IP addresses, "service IDs", etc.)
- Access control rules applied to operations

** Although we should here note the purpose of a layer is primarily to apply different configuration to different parts of the interface description.  It might be more likely that all of the generated code must be of the same generation, and therefore this fits better as an input parameter or flag to the code generator, than in a layer.

### What is Layer Type?

A Layer, is always an instance of a Layer Type.  This means that all layer files must adhere to the syntax and information rule set up by the Layer Type.

### How are Layer Types defined?

As indicated, all Layers shall be possible to validate against their Layer Type, in the same way as an IFEX file parser will ensure that the input adheres to the features and structure of the IFEX Core Model / Core IDL.

Just like IFEX Core IDL, other layers are written in YAML.  Most layers are there to add metadata to the interface structure defined using IFEX Core IDL, and therefore the layer tree structure will mimic the tree structure of the core IDL.  This is how the layer specifies which objects it intends to modify.  However, it is possible to define layers that have a different tree-structure than the core if that is the best way to encode the information.

### Layer Type Requirements

 0) Like IFEX Core IDL files, the text format of Layers is YAML*
 1) The Layer Type shall provide usage documentation
 2) The Layer Type shall provide a JSON-schema, which can be used to verify input layers against its format rules.

### Other notes

Layers are used to add information to an interface description, because this information is required to achieve a certain result.  Therefore Layers, and Layer Types are strongly related to the implementation of the tools that process the information (for example a code-generator for a specific output technology).  That is to say that Layer Types are primarily expected to be defined by those stakeholders that want to implement a particular technology.  Some Layer Types may have wider use, but many others would be consumed only by a specific tool that they are designed for.

### Definitions in this directory

The IFEX Core IDL is already defined by the AST definition under models/ifex.  This directory is for specifying all _other_ Layer Types, that add _different_ metadata.

