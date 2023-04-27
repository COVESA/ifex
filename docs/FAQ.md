# What is a Layer Type?

There can be multiple layer types, that define different meta-data about the interface and the target/deployment environment.  
A Layer Type is thus the definition of the allowed syntax for a certain type of layer.  The Layer Type is defined in a formal language (JSON/YAML schema or python class file) and it acts as a specification and schema to check the validity of layer instances.

Pure interface descriptions (written in IFEX core IDL) are kept separate from details that are target/deployment specific.  The IFEX Core IDL language is built to be maximally generic and reusable in different contexts
In contrast to that, other layer types are very often specific to a certain deployment scenario, and they might therefore be documented together with specific tooling for a specific purpose.  

For example, a code generator implementation may define a specific Layer Type for target/deployment information. It specifies the type of information that the code generator needs in addition to the interface description that was provided in IFEX Core IDL.  It means that when using this code generator, an IFEX interface file plus an instance of the layer type is required as input for the code generator to be able to do its job.

# What is a Layer?

Most of the time when we say layer we mean a layer instance, although when speaking less carefully it might refer to layer type, as evidenced by the context.

A layer can be a "overlayed" IFEX core IDL file that redefines or augments certain aspects of the base definition of the interfaces.  This type of layer that complements the original definition is written using the same syntax as the original definition (the IFEX core IDL syntax).

A layer is an _instance_ of a Layer Type.  In other words it is written to follow the required format (as defined by the type) and it includes the actual defined values that the layer type specification requires.

For further explanation of the layer concept in general, please refer to the IFEX Core Specification.


# Is there any kind of ranking property for different IFEX files so that there will be a absolute order?

In general, no.  The simple approach is that each individual IFEX tool shall document its behavior.  A simple and common behavior is that when multiple files are applied, they are done so in the order they are given on the command line to the tool, which means that "last file wins" if a particular property is redefined in a later file.

That behavior is the most likely scenario and more complex setups are unlikely to be much better in most cases.  However, if it becomes needed in some case, then it is definitely possible for tools to implement other behavior and even define what type of additional input-configuration is required to modify the behavior.

Tools are also encouraged to provide flags as part of command-line parameters, that can enable/disable information about the processing, or control the processing.  For example, there could be an optional warning printed when some item is re-defined by a later processed interface-file or layer, or there could be an option to disallow redefinition of items (report an Error).

