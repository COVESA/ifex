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

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |

#### Optional fields for Namespace:

|Field Name|Contents|
|-----|-----------|
| description | A single **str** |
| major_version | A single **int** |
| minor_version | A single **int** |
| version_label | A single **str** |
| events | A list of **Event**_s_ |
| methods | A list of **Method**_s_ |
| typedefs | A list of **Typedef**_s_ |
| includes | A list of **Include**_s_ |
| structs | A list of **Struct**_s_ |
| enumerations | A list of **Enumeration**_s_ |
| properties | A list of **Property**_s_ |
| namespaces | A list of **Namespace**_s_ |
| interface | A single **Interface** |


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

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |

#### Optional fields for Event:

|Field Name|Contents|
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

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |
| datatype | A single **str** |

#### Optional fields for Argument:

|Field Name|Contents|
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

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |

#### Optional fields for Method:

|Field Name|Contents|
|-----|-----------|
| description | A single **str** |
| errors | A list of **Error**_s_ |
| input | A list of **Argument**_s_ |
| output | A list of **Argument**_s_ |
| returns | A list of **Argument**_s_ |


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

Please see the methods sample code above for an example of how error parameter lists are used If no error element is
specified, no specific error code is returned. Results may still be returned as an out parameter`

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

|Field Name|Contents|
|-----|-----------|
| datatype | A single **str** |

#### Optional fields for Error:

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |
| description | A single **str** |
| arraysize | A single **str** |
| range | A single **str** |


----
## Typedef


Dataclass used to represent IFEX Typedef.

Each typedef is an alias to an existing fundamental type, defined type, or enumerator, giving it an additional name.
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

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |
| datatype | A single **str** |

#### Optional fields for Typedef:

|Field Name|Contents|
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

|Field Name|Contents|
|-----|-----------|
| file | A single **str** |

#### Optional fields for Include:

|Field Name|Contents|
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

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |

#### Optional fields for Struct:

|Field Name|Contents|
|-----|-----------|
| description | A single **str** |
| members | A list of **Member**_s_ |


----
## Member


Dataclass used to represent IFEX Struct Member.

Each members list object defines an additional member of the struct.
Each member can be of a fundamental or defined/complex datatype.

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

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |
| datatype | A single **str** |

#### Optional fields for Member:

|Field Name|Contents|
|-----|-----------|
| description | A single **str** |
| arraysize | A single **int** |


----
## Enumeration


Dataclass used to represent IFEX Enumeration.

Each enumerations list object specifies an enumerated list (enum) of options, where each option can have its own
integer value.  The new data type defined by the enum can be used by other datatypes, method & event parameters, and
properties.

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

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |
| datatype | A single **str** |
| options | A list of **Option**_s_ |

#### Optional fields for Enumeration:

|Field Name|Contents|
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

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |
| value | A single **Any** |

#### Optional fields for Option:

|Field Name|Contents|
|-----|-----------|
| description | A single **str** |


----
## Property


Dataclass used to represent IFEX Property.

Each properties list object specifies a shared state object that can be
read and set, and which is available to all subscribing entities.  A
properties sample list object is given below, together with a struct
definition:

```yaml
properties:
  - name: dome_light_status
    description: The dome light status
    datatype: dome_light_status_t

```

#### Mandatory fields for Property:

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |
| datatype | A single **str** |

#### Optional fields for Property:

|Field Name|Contents|
|-----|-----------|
| description | A single **str** |
| arraysize | A single **int** |


----
## Interface


Dataclass used to represent IFEX Interface

An Interface is a container of other items in a similar way as a Namespace, but it does not introduce a new
namespace level. Its purpose is to explicitly define what shall be considered part of the exposed as a "public
API" in the output.

Note that as with all IFEX concepts, the way it is translated into target code could be slightly varying, and
controlled by the target mapping and deployment information, but all mappings shall _strive_ to stay close to the
IFEX expected behavior.  Thus, the Interface section would omit for example internal helper-methods and type
definitions that are only used internally, while those definitions might still need to be in the parent Namespace
for the code generation to work.

An Interface can contain all the same child node types as Namespace can, except for additional (nested) Interfaces.
As mentioned, it does NOT introduce an additional namespace level regarding the visibility/reacahbility of the
items.  Its contents is not hidden from other Namespace or Interface definitions within the same Namespace.  To put
it another way, from visibility/reachability point of view all the content inside an interface container is part of
the "parent" Namespace that the Interface object is placed in.  Of course, if additional nested namespaces are
placed _below_ the Interface node, those Namespaces introduce new namespace levels, as usual.

Only one Interface can be defined per Namespace, and it cannot include other Interfaces

An Interface example is given below.

```yaml
namespaces:
  - name: seats
    major_version: 1
    minor_version: 3
    description: Seat interface and datatypes.
    interface:
      typedefs:
        - ...
      methods:
        - ...
      properties:
        - ...
```

#### Mandatory fields for Interface:

|Field Name|Contents|
|-----|-----------|
| name | A single **str** |

#### Optional fields for Interface:

|Field Name|Contents|
|-----|-----------|
| description | A single **str** |
| major_version | A single **int** |
| minor_version | A single **int** |
| version_label | A single **str** |
| events | A list of **Event**_s_ |
| methods | A list of **Method**_s_ |
| typedefs | A list of **Typedef**_s_ |
| includes | A list of **Include**_s_ |
| structs | A list of **Struct**_s_ |
| enumerations | A list of **Enumeration**_s_ |
| properties | A list of **Property**_s_ |
| namespaces | A list of **Namespace**_s_ |


