# IFEX Arrays

IFEX Array defines an abstract datatype for sequences of items of the same
type (a Variant type can be used to wrap multiple types).  It can have
a fixed or variable size and in programming languages it translates to an
array, vector, list, or other sequence.

IFEX's design prioritizes a balance between core functionality and
extensibility. Direct support for features is convenient, but it often
leads Interface Definition Language (IDL) initiatives to become too
specialized when including every convenient feature for a specific usage
environment.

IFEX adopts a layered approach, and defers less common information to
"Layers, but for convenience the core IDL still directly supports
frequently used features.

IFEX shall support, in all places where a datatype is specified, the following abilities:

1.  **Array of a datatype without size:**
    Example:

    Built-in types:
    ```yaml
    datatype: int32[]
    ```
    ...and any self-defined type:
    ```yaml
    datatype: MyData_t[]
    ```

2.  **Array with inline fixed size:**
    ```yaml
    datatype: int32[100]
    datatype: MyData[8]
    ```

3.  **Array size as a separate entry:**
    ```yaml
    datatype: int32[]
    arraysize: 100
    ```
    ```yaml
    datatype: MyData[]
    arraysize: 8
    ```

### Why are there two ways of specifying a fixed or maximum array size, and one way of not specifying it?


The layers concept deals with two major types – modifying layers (same type
of metadata – changed values) and augmenting layers (new types of
metadata). 

All interface definitions have some sort of hierarchy (package/namespace,
interface, interface parts, etc.). By using YAML representation,
the hierarchy of the IFEX model becomes explicit. This fits very well with the
concepts of modifying and augmenting layers.

In this example we show a _modifying layer_ because `arraysize` is
a core-IDL feature, and thus we are not adding new types of information
- adding this field is formally a redefinition of the core IDL content:

The initial file might be involved in defining interfaces on an abstract level:

Here, the designer only cares to indicate that it is a sequence of strings,
of some size.

```yaml
methods:
  - name: process_list
    input:
    - name: the_list
      datatype: string[]
```

Later on, for a specific case (for example if the target language
_requires_ a fixed size), the definition of the array size could be added
in a separate file that is “overlayed” (a modifying layer) instead of
modifying the original.

Such layering is optional, but can be useful to show for example the
sequence of refinement of the interface. Another scenario is if the
original is a "standard", then the original can be unmodified and 
layering makes it more explicit what has been changed from the standard.

The modifying layer could choose to overwrite the type:
```yaml
      ...
      datatype: string[8]
```

or this layer could simply _add_ the `arraysize` field to the existing definition
```yaml
  - name: process_list
    input:
    - name: the_list
      arraysize: 8
```

Choosing the separate `arraysize` field instead of the [<size>] syntax
is optional but it fits well into the YAML hierarchy and layering concept
to add a field instead of changing it.

