<!-- Features and introduction -->
--------------------
# FEATURES
The format supports the following features

* **Namespaces**  
  Logical grouping of methods, events, properties, and defined data types that can be nested.

* **Methods**  
  A call, executed by a single server instance, that optionally returns a value.
  Execution is guaranteed to TCP level with server failure being reported.

* **Events**  
  A fire-and-forget call, executed by zero or more subscribing instances, that does not return a value.
  Execution is best effort to UDP level with server failures not being reported.

* **Defined data types**  
  Named data types that can be enumerations, (nested) structs or typedefs.

* **Properties**  
  A shared state object that can be read and set, and which is
  available to all subscribing entities. Compared with a signal (see
  below), a property can be viewed as a level trigger while a signal
  is an edge trigger.

* **Deployment files**  
  Adds deployment-specific data to a IFEX file.

## Features that are not included, or under discussion:

The following features are worth commenting on here:

* **Signals**  
  The word Signal is interpreted by some as the transfer of a _value_ associated 
  with a name/id for what that value represents.  This value transfer ought to
  be semantically equivalent to single-argument Event, and is therefore supported
  that way within IFEX.  Another interpretation is that the word Signal represents
  the underlying data item itself, so that value-transfers are defined as a
  consequence of for example "subscribing to changes of a Signal".  In this second
  interpretation the Signal is represented by a Property in IFEX.  The Vehicle
  Signal Specification (VSS) typically uses the the second interpretation, and
  VSS Signals can then be represented by Properties in IFEX.  (Refer to further
  documentation on IFEX/VSS relationship).
 
--------------------

# NAMESPACE VERSIONING

IFEX namespaces can optionally have a major and minor version, specified by
`major_version` and `minor_version` keys, complemented by an additional
free format string named version-label.

Namespace version management lets a client implementation have
expectations that a server implementation will support a specific
variant of data types, method call, or property.

Bumped minor numbers identifies backward-compatible additions to the
previous version.  This means that if a client requires version 1.3 of
a server namespace and its methods, it knows that it can safely
interface a server implementation of version 1.4 of that same
namespace.

Bumped major versions identifies non-compatible changes to the
previous version, such as a changed method signature. This means that
a client requiring version 1.3 of a server knows that it cannot invoke
a version 2.0 server implementation of that interface since that
implementation is not backward compatible.

Namespace versioning can be used build-time to ensure that the correct
version of all needed namespace implementations are deployed, while
also detecting if multiple, non-compatible versions of a namespace is
required.

# INTERFACE VERSIONING

An Interface is essentially a specialization of the Namespace concept.
Interfaces may be verisoned in the same manner as described for Namespaces.
There may be rules implemented in validation tools that ensure interface
versions match the versioning of namespaces.  (E.g. Don't claim an interface is
compatible if its parent namespace have changed in an incompatible way).

**This section needs clarification**


<!-- Types, constraints/ranges, type resolution in namespaces. -->
----

# TYPES PLACEHOLDER

----

<!-- Layers concept, IFEX File Syntax, semantics and structure -->
-----------------------

# LAYERS CONCEPT

The IFEX approach implements a layered approach to the definition of interfaces,
and potentially other aspects of a system.  The core interface file (Interface
Description Language, or Interface Description Model) shall contain only a
_generic_ interface description that can be as widely applicable as possible.

As such, it avoids including specific information that only applies in certain
interface contexts, such as anything specific to the chosen transport protocol,
the programming language, and so on.

Each new **Layer Type** defines what new metadata it provides to the overall
model.  A Layer Type Specification may be written as a human-readable document,
but is often provided as a "YAML schema" type of file, that can be used to
programatically validate layer input against formal rules.

Layers do not always need to add new _types_ of information.  It is possible to
'overlay' files that are of the same core interface (IDL) schema as an original
file, for the purpose of adding details that were not defined, removing nodes,
or even redefining/changing the definition of some things defined in the
original file.

In other words, tools are expected to process multiple IDL files and to merge
their contents according to predefined rules.  Conflicting information could,
for example be handled by writing a warning, or to let the last provided layer
file to take precedence over previous definitions.  (Refer to detailed
documentation for each tool).

Example:

**File: `comfort-service.yml`**  
```YAML
name: comfort
  typedefs:
    - name: movement_t
      datatype: int16
      min: -1000
      max: 1000
      description: The movement of a seat component
```

**File: `redefine-movement-type.yml`**  
```YAML
name: comfort
  typedefs:
    - name: movement_t
      datatype: int8 # Replaces int16 of the original type
```

The combined YAML structure to be processed will look like this:

```YAML
name: comfort
  typedefs:
    - name: movement_t
      datatype: int8 # Replaced datatype
      min: -1000
      max: 1000
      description: The movement of a seat component
```

## Deployment file object list extensions

If a deployment file's object list element (e.g. `events`) is also
defined in the IFEX file, the IFEX's list will traversed recursively and
extended by the deployment file's corresponding list.

**FIXME** Possibly add description on how various edge cases are resolved.

Example:

**File: `comfort-service.yml`**  
```YAML
name: comfort
events:
  - name: seat_moving
    description:  The event of a seat starting or stopping movement
    in:
      - name: status
        datatype: uint8
      - name: row
        datatype: uint8

```

**File: `add_seat_moving_in_parameter.yml`**  
```YAML
name: comfort
events:
- name: seat_moving: 
    in:
      - name: extended_status_text
        datatype: string
```

The combined YAML structure to be processed will look like this:

```YAML
name: comfort
events:
  - name: seat_moving
    description:  The event of a seat starting or stopping movement
    in:
      - name: status
        datatype: uint8
      - name: row
        datatype: uint8
      - name: extended_status_text
        datatype: string
```



There is not a fixed list of layer types - some may be standardized and
defined, and therefore documented, but the design is there to allow many
extensions that have not yet been invented or agreed upon.


# DEPLOYMENT LAYER

Deployment layer, a.k.a. Deployment Model files, is a specialization of the
general layers concept.  This terminology is used to indicate a type of layer
that in adds additional metadata that is directly related to the interface 
described in the IDL.  It is information needed to process, or interpret, IFEX
interface files in a particular target environment.

An example of deployment file data is a DBUS interface specification to be used
for a namespace, or a SOME/IP method ID to be used for a method call.  

By separating the extension data into their own deployment files the
core IFEX specification can be kept independent of deployment details
such as network protocols and topology.

An example of a IFEX file sample and a deployment file extension to
that sample is given below:


**File: `comfort-service.yml`**  
```YAML
name: comfort
namespaces:
  - name: seats
    description: Seat interface and datatypes.

    structs: ...
    methods: ...
   ...
```

**File: `comfort-dbus-deployment.yml`**  

```YAML
name: comfort
namespaces: 
  - name: seats
    dbus_interface: com.genivi.cabin.seat.v1
```

The combined YAML structure to be processed will look like this:

```YAML
name: comfort
namespaces: 
  - name: seats
    description: Seat interface and datatypes.
    dbus_interface: com.genivi.cabin.seat.v1

    structs: ...
    methods: ...
```

The semantic difference between a regular IFEX file included by an
`includes` list object and a deployment file is that the deployment
file can follow a different specification/schema and add keys that
are not allowed in the plain IDL layer.  In the example above, the
`dbus_interface` key-value pair can only be added in a deployment file since
`dbus_interface` is not a part of the regular IFEX IDL file syntax.

----------

# IFEX FILE SYNTAX, SEMANTICS AND STRUCTURE

A Vehicle Service Catalog is stored in one or more YAML files.  The
root of each YAML file is assumed to be a `namespace` object and needs
to contain at least a `name` key, and, optionally, a `description`. In
addition to this other namespaces, `includes`, `datatypes`, `methods`,
`events`, and `properties` can be specified.

A complete IFEX file example is given below:

**NOTE: This example might be outdated**

```YAML
---
name: comfort
major_version: 2
minor_version: 1
description: A collection of interfaces pertaining to cabin comfort.

# Include generic error enumeration to reside directly
# under comfort namespace
includes:
  - file: vsc-error.yml
    description: Include standard VSC error codes used by this namespace

namespaces:
  - name: seats
    description: Seat interface and datatypes.

    typedefs:
      - name: movement_t
        datatype: uint16
  
    structs:
      - name: position_t
        description: The position of the entire seat
        members:
          - name: base
            datatype: movement_t
            description: The position of the base 0 front, 1000 back
    
          - name: recline
            datatype: movement_t
            description: The position of the backrest 0 upright, 1000 flat
    
    enumerations:
      - name: seat_component_t
        datatype: uint8
        options:
          - name: base
            value: 0
          - name: recline
            value: 1
    
    methods:
      - name: move
        description: Set the desired seat position
        in: 
          - name: seat
            description: The desired seat position
            datatype: movement.seat_t
    
    
    events:
      - name: seat_moving
        description: The event of a seat beginning movement
        in:
          - name: status
            description: The movement status, moving (1), not moving (0)
            datatype: uint8
    
    properties:
      - name: seat_moving
        description: Specifies if a seat is moving or not
        type: sensor
        datatype: uint8
```


The following chapters specifies all YAML objects and their keys
supported by IFEX.  The "Lark grammar" specification refers to the Lark
grammar that can be found [here](https://github.com/lark-parser/lark).
The terminals used in the grammar (`LETTER`, `DIGIT`, etc) are
imported from
[common.lark](https://github.com/lark-parser/lark/blob/master/lark/grammars/common.lark)

----

## NODE TYPES

The chapters that follow this one specify the node types for the core interface language/model.  They are generated from a "source of truth" which is the actual python source code of `ifex_ast.py`.  This means that while the examples are free-text and may need manual updating, the list of fields and optionality should always match the behavior of the tool(s).  => Always trust the tables over the examples, and report any discrepancies.

<!-- Syntax specification (generated from source) -->
----
## Namespace


Dataclass used to represent IFEX Namespace.

A namespace is a logical grouping of other objects, allowing for separation of datatypes, methods,
events, and properties into their own spaces that do not interfere with identically named objects
in other namespaces. Namespaces can be nested inside other namespaces to an arbitrary depth, building
up a scalable namespace tree. Namespaces can be reused either locally in a single file via YAML anchors,
or across YAML files using the includes object. The root of a YAML file is assumed to be a namespaces object,
and can contain the keys listed below.

A namespace example is given below.

```yaml
namespaces:
  - name: seats
    major_version: 1
    minor_version: 3
    description: Seat interface and datatypes.
```

#### Mandatory fields for Namespace:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |

#### Optional fields for Namespace:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |
| major_version | A single **int** |
| minor_version | A single **int** |
| events | A list of **Event**_s_ |
| methods | A list of **Method**_s_ |
| typedefs | A list of **Typedef**_s_ |
| includes | A list of **Include**_s_ |
| structs | A list of **Struct**_s_ |
| enumerations | A list of **Enumeration**_s_ |
| properties | A list of **Property**_s_ |
| namespaces | A list of **Namespace**_s_ |


----
## Event


Dataclass used to represent IFEX Event.

Each events list object specifies a fire-and-forget call, executed by zero or more subscribing instances, 
that does not return a value. Execution is best effort to UDP level with server failures not being reported.

A events sample list object is given below:

```yaml
events:
  - name: seat_moving
    description: Signal that the seat has started or stopped moving

    in:
      - name: status
        description: The movement status, moving (1), not moving (0)
        datatype: boolean

      - name: row
        description: The row of the seat
        datatype: uint8
```    

#### Mandatory fields for Event:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |

#### Optional fields for Event:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |
| input | A list of **Argument**_s_ |


----
## Argument


Dataclass used to represent IFEX method Argument.

```yaml
methods:
  - name: current_position
    input:
      - name: row
        description: The desired seat to row query
        datatype: uint8
        range: $ < 10 and $ > 2

```

#### Mandatory fields for Argument:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |
| datatype | A single **str** |

#### Optional fields for Argument:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |
| arraysize | A single **int** |
| range | A single **str** |


----
## Method


   Dataclass used to represent IFEX Event.

   Each methods list object specifies a method call, executed by a single server instance,
   that optionally returns a value. Execution is guaranteed to TCP level with server failure being reported.

   A methods sample list object is given below:

   ```yaml
   methods:
     - name: current_position
       description: Get the current position of a seat

       input:
         - name: row
           description: The desired seat to row query
           datatype: uint8
           range: $ < 10 and $ > 2

         - name: index
           description: The desired seat index to query
           datatype: uint8
           range: $ in_interval(1,4)

       output:
         - name: seat
           description: The state of the requested seat
           datatype: seat_t

       errors:
         - datatype: .stdvsc.error_t
           range: $ in_set("ok", "in_progress", "permission_denied")    
   ```
   
#### Mandatory fields for Method:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |

#### Optional fields for Method:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |
| errors | A list of **Error**_s_ |
| input | A list of **Argument**_s_ |
| output | A list of **Argument**_s_ |


----
## Error


Dataclass used to represent a IFEX method error.

The optional error element defines an error value to return.  Note that the
concept allows for _multiple_ Errors.  This is easy to misunderstand: It is
not only multiple different error values as you are used to from most programming
environments.  Multiple value choices can be handled by a single Enumeration error type.
The concept also allows multiple independent return _parameters_, each having
their own data type (and name).

The purpose of this is to be able to separate different error categories
and to define them independently using layers.  For example, a method is likely
to have a collection of business-logic errors defined in its interface
description and represented by one enum type.  At a later time
transport-protocol specific errors can be added when the interface is
deployed over a certain protocol, and that error parameter has a different
name and a different type (enumeration or otherwise).

Error elements are returned in addition to any out elements specified for the method call.

Please see the methods sample code above for an example of how error parameter lists are used
If no error element is specified, no specific error code is returned. Results may still be returned as an out parameter`

```yaml
methods:
  - name: current_position
    description: Get the current position of a seat

    errors:
      - name: "progress"
        datatype: .stdvsc.error_t
        range: $ in_set("ok", "in_progress", "permission_denied")        
      - <possibly additional error definition>

```

#### Mandatory fields for Error:

|Field Name|Required contents|
|-----|-----------|
| datatype | A single **str** |

#### Optional fields for Error:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |
| description | A single **str** |
| arraysize | A single **str** |
| range | A single **str** |


----
## Typedef


Dataclass used to represent IFEX Typedef.

Each typedefs list object aliases an existing primitive type, defined type, or enumerator, giving it an additional name.
The new data type can be used by other datatypes, method & event parameters, and properties.

A typedefs list object example is given below:    

```yaml
typedefs:
  - name: movement_t
    datatype: int16
    min: -1000 
    max: 1000
    description: The movement of a seat component    
```

#### Mandatory fields for Typedef:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |
| datatype | A single **str** |

#### Optional fields for Typedef:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |
| arraysize | A single **int** |
| min | A single **int** |
| max | A single **int** |


----
## Include


Dataclass used to represent IFEX Include.

Each includes list object specifies a IFEX YAML file to be included into the namespace hosting the includes list.
The included file's structs, typedefs, enumerators, methods, events, 
and properties lists will be appended to the corresponding lists in the hosting namespace.

A includes sample list object is given below:    

```yaml
namespaces:
  - name: top_level_namespace
    includes
    - file: vsc-error.yml;
      description: Global error used by methods in this file
```


#### Mandatory fields for Include:

|Field Name|Required contents|
|-----|-----------|
| file | A single **str** |

#### Optional fields for Include:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |


----
## Struct


Dataclass used to represent IFEX Struct.

Each structs list object specifies an aggregated data type.
The new data type can be used by other datatypes, method & event parameters, and properties.

A structs list object example is shown below:

```yaml    
structs:
  - name: position_t
      description: The complete position of a seat
      members:
      - name: base
          datatype: movement_t
          description: The position of the base 0 front, 1000 back

      - name: recline
          datatype: movement_t
          description: The position of the backrest 0 upright, 1000 flat
```


#### Mandatory fields for Struct:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |

#### Optional fields for Struct:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |
| type | A single **str** |
| members | A list of **Member**_s_ |


----
## Member


   Dataclass used to represent IFEX Enumeration Member.

   Each members list object defines an additional member of the struct.
   Each member can be of a native or defined datatype.

   Please see the struct sample code above for an example of how members list objects are used.

   ```yaml
   structs:
     - name: position_t
       description: The complete position of a seat
       members:
         - name: base
           datatype: movement_t
           description: The position of the base 0 front, 1000 back
   ```
   
#### Mandatory fields for Member:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |
| datatype | A single **str** |

#### Optional fields for Member:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |
| arraysize | A single **int** |


----
## Enumeration


Dataclass used to represent IFEX Enumeration.

Each enumerations list object specifies an enumerated list (enum) of options, where each option can have its own integer value.
The new data type defined by the enum can be used by other datatypes, method & event parameters, and properties.

A enumerations example list object is given below:

```yaml    
enumerations:
  - name: seat_component_t
    datatype: uint8 
    options:
      - name: base
        value: 0

      - name: cushion
        value: 1
```    

#### Mandatory fields for Enumeration:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |
| datatype | A single **str** |
| options | A list of **Option**_s_ |

#### Optional fields for Enumeration:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |


----
## Option


Dataclass used to represent IFEX Enumeration Option.

Each options list object adds an option to the enumerator.

Please see the enumerations sample code above for an example of how options list objects are used.

```yaml
options:
  - name: base
    value: 0
    description: description of the option value
```

#### Mandatory fields for Option:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |
| value | A single **int** |

#### Optional fields for Option:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |


----
## Property


   Dataclass used to represent IFEX Property.

   Each properties list object specifies a shared state object that can be read and set, and which is available to all subscribing entities.
   A properties sample list object is given below, together with a struct definition:

   ```yaml
   properties:
     - name: dome_light_status
       description: The dome light status
       datatype: dome_light_status_t

   ```
   
#### Mandatory fields for Property:

|Field Name|Required contents|
|-----|-----------|
| name | A single **str** |
| datatype | A single **str** |

#### Optional fields for Property:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |
| arraysize | A single **int** |



<!-- End of document -->
