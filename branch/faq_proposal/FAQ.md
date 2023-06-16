# Definitions and Frequently Asked Questions

----
## What is an overlay?

An overlay is a special term in the layering approach.  Just be aware that we are sometimes are less careful and simply call these "layers" as well.

Overlay is used to mean a file that uses the _same syntax_ (same layer type) 'overlaying' an original file.   The second file redefines or extends on items that were already (partly) defined in another file, but it does not add completely new types of information.  To add new types of information, additional Layers of a new Layer Type would be used.

It is anticipated that overlays will mostly be written for the pure interface descriptions (the content of one IFEX core IDL file overlaps another IFEX core IDL file).  The overlay then extends or changes the existing interface description within the information scope of the IFEX core IDL syntax only.  In theory overlays could also be supported for any other Layer Types (not only for the core IDL), but tools are likely to omit this capability when it is not required.

Example 1)  
An interface describes methods with an error return type that encodes "business logic" error cases.  An overlay adds an additional error return type to the methods that is related to the chosen communication protocol, and thus kept separate from the business logic errors.  Although in this case it is a consequence of "deployment", it does not need a special layer type -- errors are defined within the IFEX core IDL, and thus use an overlay.

Example 2)  
An interface is adopted from an agreed-upon standard catalog, such as "Vehicle Service Catalog (VSC)".  An overlay makes a small modification by adding a few extra events.  By keeping the standard file and the proprietary addition in separate files, the addition. is more clearly separated and maintained, while it might be awaiting inclusion into the original standard.

----

## What is a Layer, a.k.a. Layer Instance?

Most of the time when we say layer we mean a layer instance, but when speaking less carefully it might refer to the layer type, depending on the context.

More generally, a layer (instance) is an instance of a Layer Type.  It is a file that follows the format of the layer type, as required by the associated Layer Specification, and it defines the actual values that are used in a specific situation.

----

## What is a Layer Type?

There can be multiple layers that define different meta-data about the interface and the target/deployment environment, each corresponding to a layer type.

The IFEX philosophy is that pure interface descriptions (written in IFEX core IDL) are kept separate from details that are target/deployment specific.  The IFEX Core IDL language is built to be maximally generic and reusable in different contexts.  In contrast to that, new layer types are very often written for a specific deployment scenario.  You may often find layer types and specifications defined and documented not in a central place, but near the implementation of a specific tool for a specific purpose.  

**Example**:  
A code generator implementation may define a specific Layer Type for target/deployment information. It specifies the type of information that the code generator needs, _in addition to_ the interface description_ that was provided in IFEX Core IDL.  It means that when using this code generator, at least two files are needed as input:  The IFEX core IDL interface description, plus an instance of the layer type that is also required as input for the code generator to be able to do its job.

The purpose and usage of each layer type should be described, and that is typically accompanied by a formal Layer Specification for its allowed format/syntax.

----

## What is a Layer Specification?

A Layer Specification is the definition of the allowed syntax for a certain Layer Type.  The Layer Specification is defined in a formal language (usually JSON-schema, YAML or python class file) and it acts as a specification or 'schema' to check the validity of layer instances.


For further explanation of the layer concept in general, please refer to the IFEX Core Specification.

----

## When files are combined, is there any kind of ranking property for different IFEX files so that there will be a absolute order?

No, not as part of the general IFEX specification.  The simple (and maybe only possible) approach is that each individual IFEX tool shall independently decide and document its behavior.

**Scenario 1**: A layer that adds new deployment details means the order does not matter - the final model combines the IFEX core IDL description and the additional data provided by the additional layer types.

**Scenario 2**: For overlays that redefine or affect a previous definitions, a simple and common behavior is that files are simply read in the order they are given on the command line to the tool, and if something is redefined in later files it overwrites what was in the earlier files.

That "last file wins" behavior appears naive but there is rarely any much better generalized solution.  In any case, **if** it becomes needed in some case, it is definitely possible for a certain tool to implement another behavior and explain it.  As explained in the first answer - each tool is free to define and document its behavior.  Some additional input-configuration could be used by the tool to modify the prioritization behavior.

Tools are also encouraged to have configuration flags that can control or enable/disable information about the processing.  For example, when some item is redefined by a later file, the tool might be configurable to:
  - Ignore it silently.
  - Print a warning.
  - Treat as an error.

