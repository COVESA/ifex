----
## Namespace


Dataclass used to represent VSC Namespace.

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


Dataclass used to represent VSC Event.

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


Dataclass used to represent VSC method Argument.

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


Dataclass used to represent VSC Method.

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

    error:
      datatype: .stdvsc.error_t
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
| error | A list of **Error**_s_ |
| input | A list of **Argument**_s_ |
| output | A list of **Argument**_s_ |


----
## Error


Dataclass used to represent VSC method error.

The optional error element defines an error value to return.
The error element is returned in addition to any out elements specified for the method call.
Please see the methods sample code above for an example of how error parameter lists are used
If no error element is specified, no specific error code is returned. Results may still be returned as an out parameter`
Note error specifies return values for the method call itself.
Transport-layer issues arising from interrupted communication, services going down, etc,
are handled on a language-binding level where each langauage library
implements their own way of detecting, reporting, and recovering from network-related errors.

```yaml
methods:
  - name: current_position
    description: Get the current position of a seat

    error:
      datatype: .stdvsc.error_t
      range: $ in_set("ok", "in_progress", "permission_denied")
```

#### Mandatory fields for Error:

|Field Name|Required contents|
|-----|-----------|
| datatype | A single **str** |

#### Optional fields for Error:

|Field Name|Required contents|
|-----|-----------|
| description | A single **str** |
| arraysize | A single **str** |
| range | A single **str** |


----
## Typedef


Dataclass used to represent VSC Typedef.

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


Dataclass used to represent VSC Include.

Each includes list object specifies a VSC YAML file to be included into the namespace hosting the includes list.
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


Dataclass used to represent VSC Struct.

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


Dataclass used to represent VSC Enumeration Member.

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


Dataclass used to represent VSC Enumeration.

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


Dataclass used to represent VSC Enumeration Option.

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


Dataclass used to represent VSC Property.

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


