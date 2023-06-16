# IFEX / D-Bus mapping

# General

- IFEX Methods map to D-Bus methods.
- IFEX Events map to D-Bus signal concept
- IFEX Properties map to D-Bus properties.
    - The use of properties is described in part in D-Bus specification, and there are standard conventions for how to describe a getter/setter interface as well as a "change signal" and these ought to be followed.  An IFEX Layer Type is likely appropriate to control exactly how an IFEX interface gets translated, including which of the D-Bus property features shall be enabled.
- D-Bus methods have in and out parameters like IFEX, but neither return values or errors.
    - IFEX Return values would be translated to out-parameters as described in [Mapping method parameters](TBDLINK)
    - Error mapping is described below.
- D-Bus uses a dot-separated path to put features into an appropriate namespace.  Walking down the namespace hierarchy on an IFEX definition can create such a dot-separated path which can be used to define the services in the D-Bus description.  It may be appropriate for the generator implementation to have some configuration capabilities controlling this translation.
- D-Bus introspection format allows the naming of nodes, (where a <node> represents essentially the runtime object that provides the interface).  That rather has to do with system design and deployment of functionality (i.e. which Software Components exist in a system and which interfaces does each of them expose).  That part of system design is out of scope for the IFEX Core IDL (but might well be developed in some form in other IFEX related project).  A particular usage of IFEX will of course create their own necessary conventions around this. Initially, translations of IFEX interfaces will not name the node, and that is not required for the basic proxy/stub code generation.

# Primitive types

Most IFEX data types translate well to D-Bus.  We can follow the generic principles of [Mapping primitive types](TBDLINK).
In a few cases we need to follow a widening or minor-difference coercion approach (see linked chapter for details).

## D-Bus basic types

...as defined in [D-Bus Specification](https://dbus.freedesktop.org/doc/dbus-specification.html#basic-types)

|Name|Meaning|
|----|-------|
|BYTE             |Unsigned 8-bit integer|
|BOOLEAN          |Boolean value: 0 is false, 1 is true|
|INT16            |Signed (two's complement) 16-bit integer|
|UINT16           |Unsigned 16-bit integer|
|INT32            |Signed (two's complement) 32-bit integer|
|UINT32           |Unsigned 32-bit integer|
|INT64            |Signed (two's complement) 64-bit integer|
|UINT64           |Unsigned 64-bit integer|
|DOUBLE           |IEEE 754 double-precision floating point|
|UNIX_FD          |32-bit index into array of file descriptors|
|STRING           |UTF-8 string (must be valid UTF-8). Must be nul terminated and contain no other nul bytes.|

## D-Bus composite and non-obvious types

|Name|Meaning|
|----|-------|
|OBJECT_PATH      |Name of an object instance|
|SIGNATURE        |A type signature|
|VARIANT          |Variant type (the type of the value is part of the value itself)|
|DICT             |Key-value mapping|

### Type mappings (IFEX -> D-Bus)

Direction of IFEX Core IDL to D-Bus (represented by its introspection XML format):

- IFEX `uint8` maps to `BYTE` and also int8 maps to `BYTE` (coercion)
- IFEX `string`, `boolean`, int/uint of 16/32/64 bit varieties, as well as `double`, have exact equivalences in D-Bus.
- IFEX `float` must translate to `double` (widening)
- IFEX `map` translates to a D-Bus `DICT` (see Comments below)
- IFEX `set` can be transferred on (any) protocol as simply an array.  The enforcement of the set semantics happens only on the side of the server and/or client implementation.
- IFEX `variant` translates to D-Bus `VARIANT`
- IFEX `opaque` type translates to an array of `BYTE`

### Type mappings (D-Bus to IFEX)

Translating an existing D-Bus interface to IFEX Core IDL:

Follow the reverse of the above, with these additional comments:

As always, types that do not exist in the source (D-Bus) will naturally not appear in the translation (IFEX).  There could be some special situation where the use of additional metadata (a Layer), certain objects could be given more semantic meaning, for example "this array is actually is a set", but IFEX users will have to propose a solution if the need for this arises.

- `UNIX_FD` is simply a 32-bit (unsigned) integer with special meaning. It is a low-level mechanism which also only makes sense within a single local UNIX system.  Therefore, if an existing D-Bus interface is going to be translated to an IFEX description, it might be worthwhile to redesign the interface description to not use UNIX_FD (or in IFEX an equivalent integer).  A shared file between server/client/peers might in theory be an "optimized" low-level solution in a particular translation of an IFEX interface, but that comes into play in the opposite direction: IFEX to -> D-Bus mapping.  The type that is actually being transferred would be better described in the interface description using a higher-level type description, or at minimum as an array of bytes.  If someone has a D-Bus interface that transfers UNIX_FDs, and the interface is to be translated into IFEX core IDL - please at that time analyze how you think it would best be treated.  Ultimately, it could fall back to "just an integer" but that has limited use if the IFEX description is moved to a different environment.
- Neither OBJECT_PATH or SIGNATURE are supported (let us know if supporting them has any practical value)

### Comments

- The D-Bus specification requires the key in a dict to be a basic type only.  IFEX core IDL is unlikely to define this limitation, and it might be unsupported to translate IFEX maps that use non-primitive keys into D-Bus.  On the other hand, it ought to be possible to "misuse" D-Bus by transferring it as an array of key-value structs, which has no such limitation (and on the wire protocol, an array of structs is basically how a dict is transferred in all cases).  It would be required to generate comments in the D-Bus interface description to clarify this fact, and/or to create both sides of a server/client communication from the same generator to ensure that the map behavior can reappear in the code that uses it, after it has been transferred over as an "array".

- The D-Bus specification also describes some additional type codes but they are used only for the wire protocol, or seem generally not yet refined into a complete concept. (If something in D-Bus specification is missing and needs to be added to this document, please propose a change)

## Feature mapping

- IFEX `Method`s map to D-Bus `method`.
- IFEX `Properties` map to D-Bus properties.  See the specification for some some particular conventions to follow.
- IFEX `Event`s map to D-Bus `Signal` concept. The behavior matches IFEX description (like a method call but without a reply).
- The D-Bus specification describes a message of type Error but it is primarily seen as a reply message from a method call, in the case that the method is an error.  It is further constrained that the first argument must be a string.  

We ought to be able to convert IFEX `Errors` into a D-Bus error in the implementation but it seems to be not described in the XML format
(TODO: investigate further)

## Errors

D-Bus describes an Error message type that can be sent in different situations, but usually as a reply to a method call.
IFEX `Error`s concept also defines errors individually for each method.  There are few rules expressed in the D-Bus specification but this sentence seems most significant:

    "_An ERROR may have any arguments, but if the first argument is a STRING, it must be an error message. The error message may be logged or shown to the user in some way._"

This means that if the IFEX interface has a string as its first argument, we ought to establish whether it is an error message and shall be treated as such in the D-Bus representation of the interface (it could be a safe assumption to make, but alternatively some user interaction is appropriate, and/or to require this to be a parameter to the code generator).

TODO: Is there an XML representation of the error, or not?  (Cannot determine this from the D-Bus specification).

