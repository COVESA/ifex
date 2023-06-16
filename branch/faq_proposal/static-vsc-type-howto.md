# Type mapping examples

## Types that are trivially mapped to IFEX fundamental types

| Generic data type | Explanation | IFEX Fundamental type | How to represent in IFEX if not fundamental type |
| --- | --- | --- | --- |
| Integer |  | uint32, int32, and other sizes... |  |
| Floating point |  | float, double   |  |
| Boolean |  | boolean |  |
| Tuple | A pair, triple, or larger group of objects, possibly of different type. | -- | Assumed to be represented by an array of fixed size, or a struct (if mixed types), or array of Variants (where dynamic mixed types are needed)** |
| Union/Variant |  A data type that allows a variable to hold values of different data types at different times.   |  variant |  |
| Bit field | Efficient encoding of on/off true/false switches, as a collection of bits handled as an integer | -- |  Assumed to be represented by a fixed size integer\*\*, or (better, more descriptive and more generic) by an array of booleans\*\* |
| Enum class |  Enumeration type that provids type safety and scoping of constants.  |  Enumeration  |  |
| Set |  A collection of unique elements, where each element occurs only once. A set is typically used to store a collection of items that are unordered and where the order does not matter.   |  set (new) | Although a Set could be represented by a collection (array), with the 'unique values' constraint added in deployment information, a Set is such a common concept that it is worthwhile to include it in the IDL directly.  Some implementations may still use an array or similar in the target environment mapping. |
| Map/Dictionary/Key-Value |  A collection of key-value pairs, where each key is associated with a value.  | map (new) | A map can be represented as a linear array of Variant (alternating keys and values) or an array of 2-tuples (pairs), or array of struct with key and value members, and so on.  Despite that, using the same argument as for Set, a Map type is ubiquitous enough that it warrants its own fundamental type to easily express the intended behavior. |

** These solutions propose to represent datatype concepts using a comparable fundamental type in the IFEX interface description. For these situations it is expected to usually have an additional layer that specifies the constraints and type behavior for each part of the interface.  When processed, this combination of information ensures the behavior is according to the original type.  

For example: the generic interface description may contain several parameters that are of type array-of-boolean.  The usage might in some environments have a deployment model that specifies that (for one specific instance) it shall be represented as a bitfield, whereas other instances remain as array-of-boolean in the generated code.  Other code-generation environments may instead have a built in rule that bitfields shall be used as the _default_ translation.  In either case, these particular mapping rules are defined by the target environment, i.e. requirements on how the code-generator shall behave, including additional information that the deployment model may provide.  They are not in the core interface description, as represented by the IDL, but in additional layers, as well as the particular behavior of the code-generator (as described in its requirements or documentation).

## Additional types available in some programming environments

| Generic data type | Explanation | IFEX Fundamental type | How to represent in IFEX if not fundamental type |
| --- | --- | --- | --- |
| Function/Lambda  |  Some programming environments have functions as first class objects and can transfer them as arguments in interfaces. | -- |  The application of this would often be specific to a programming language environment, and it's unlikely that the interface description will be highly portable if this feature was represented in the interface description.  When needed it is possible to define an appropriate typedef for transferring code, for example as a string (interpreted language) or binary blob (compiled/bytecode), or as fallback "opaque".  Beyond this, the details are undefined in the core IDL scope and left open for a target environment to define. |
| Reference/Pointer  |  | -- |  This is not considered a _datatype_ in the IDL.  If we are truly speaking about a Type, that signifies a reference to something else, this could be modeled using a system-specific typedef, like using a string name/identifier to refer to an object, or any other appropriate encoding of that data.  That is the explaination why Reference/Pointer it is not seen as a _datatype_ in its own right.  To understand how _arguments are passed_ by pointer or reference (in C++ or other languages), see the separate section below. |
| Iterator  |  A data type that allows traversal of elements in a container, such as an array or linked list.   | -- |  Assumed to be represented by a primitive type such as integer (or struct if required)   |

## Additional simple examples

Any types that are normally implemented as a Struct or Class should be understood to be done using a Struct in IFEX as well.  Just to provide a simple example here, that can be extrapolated for most other specific types: 

| Generic data type | Explanation | IFEX Fundamental type | How to represent in IFEX if not fundamental type |
| --- | --- | --- | --- |
| Complex | A complex number, with real and imaginary part.  (This is an example that represents any simple structured type really) | -- | Assumed to be represented by a tuple or struct.  Typedef can still be used to give this a unique name. |

## Opaque (special) type

If a system includes some data type that really does not fit into any of the generalized types above, it can be modeled as the **opaque** type in the IFEX IDL.  This is only a last resort and together with information that is likely provided by a deployment layer a specific code generator would encode the type behavior that is necessary.

# Comments on pointers, references, etc.

The core interface description (IDL) does not prescribe how to transfer an argument to a method, only the type of the argument, and its in/out expectation.  In a lot of cases, IFEX will be used in an over-the-network / IPC / RPC scenario where the question is moot, or the concept of passing a reference simply does not work across the network.  However, if used to represent a programming interface, it may be worthwhile to comment on this.  We can deduce a pass-by-value behavior is assumed for "in" parameters.  However, it is still up to the target environment code generator to decide, possibly controlled by deployment layer information.  For example, some target environments could apply const-references in the generated code for "in" parameters, and pointers or references for "out" parameters.  In either of these cases there is still no need to mention a specific reference type in the pure interface description - it is all decided in the particular target environment mapping.


