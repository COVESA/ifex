# IFEX CORE SPECIFICATION

(C) 2022, 2023 - MBition GmbH  
(C) 2022 - COVESA  
(C) 2021 - Magnus Feuer  

This document contains an introduction to the the Interface Exchange (IFEX)
framework and specification of the core Interface Description Language/Model
(also known as ifex-idl and ifex-core).  IFEX is the name for the _technology_
(language, tools, etc.) behind the Vehicle Service Catalog (VSC) project.

License: Creative Commons Attribution 4.0 International
License (CC-BY-4.0), described [here](https://creativecommons.org/licenses/by/4.0/)

<!-- Heading and TOC -->
- [FEATURES](#features)  
    - [Features that are not included _in the core IDL_, but worth describing](#features-that-are-not-included-in-the-core-idl-but-worth-describing)  
    - [Feature concept details](#feature-concept-details)  
        - [Namespace](#namespace)  
    - [Interface](#interface)  
        - [Method](#method)  
        - [Error](#error)  
        - [Event](#event)  
        - [Property](#property)  
        - [Return values](#return-values)  
            - [Return/status communication in asynchronous vs. synchronous method calls](#returnstatus-communication-in-asynchronous-vs-synchronous-method-calls)  
    - [Target Environment](#target-environment)  
        - [Service (not a core feature)](#service-not-a-core-feature)  
        - [Signals (not a core feature)](#signals-not-a-core-feature)  
- [NAMESPACE VERSIONING](#namespace-versioning)  
- [INTERFACE VERSIONING](#interface-versioning)  
- [TYPES PLACEHOLDER](#types-placeholder)  
- [LAYERS CONCEPT](#layers-concept)  
    - [Deployment file object list extensions](#deployment-file-object-list-extensions)  
- [DEPLOYMENT LAYER](#deployment-layer)  
- [IFEX FILE SYNTAX, SEMANTICS AND STRUCTURE](#ifex-file-syntax-semantics-and-structure)  
    - [NODE TYPES](#node-types)  
    - [Namespace](#namespace)  
            - [Mandatory fields for Namespace](#mandatory-fields-for-namespace)  
            - [Optional fields for Namespace](#optional-fields-for-namespace)  
    - [Event](#event)  
            - [Mandatory fields for Event](#mandatory-fields-for-event)  
            - [Optional fields for Event](#optional-fields-for-event)  
    - [Argument](#argument)  
            - [Mandatory fields for Argument](#mandatory-fields-for-argument)  
            - [Optional fields for Argument](#optional-fields-for-argument)  
    - [Method](#method)  
            - [Mandatory fields for Method](#mandatory-fields-for-method)  
            - [Optional fields for Method](#optional-fields-for-method)  
    - [Error](#error)  
            - [Mandatory fields for Error](#mandatory-fields-for-error)  
            - [Optional fields for Error](#optional-fields-for-error)  
    - [Typedef](#typedef)  
            - [Mandatory fields for Typedef](#mandatory-fields-for-typedef)  
            - [Optional fields for Typedef](#optional-fields-for-typedef)  
    - [Include](#include)  
            - [Mandatory fields for Include](#mandatory-fields-for-include)  
            - [Optional fields for Include](#optional-fields-for-include)  
    - [Struct](#struct)  
            - [Mandatory fields for Struct](#mandatory-fields-for-struct)  
            - [Optional fields for Struct](#optional-fields-for-struct)  
    - [Member](#member)  
            - [Mandatory fields for Member](#mandatory-fields-for-member)  
            - [Optional fields for Member](#optional-fields-for-member)  
    - [Enumeration](#enumeration)  
            - [Mandatory fields for Enumeration](#mandatory-fields-for-enumeration)  
            - [Optional fields for Enumeration](#optional-fields-for-enumeration)  
    - [Option](#option)  
            - [Mandatory fields for Option](#mandatory-fields-for-option)  
            - [Optional fields for Option](#optional-fields-for-option)  
    - [Property](#property)  
            - [Mandatory fields for Property](#mandatory-fields-for-property)  
            - [Optional fields for Property](#optional-fields-for-property)  

<!-- Features and introduction -->
<!-- Features and introduction -->
--------------------
# FEATURES
The format supports the following features

* **Namespaces**  
  Logical grouping of methods, events, properties, and defined data types that can be nested.

* **Methods**  
  A call, executed by a single server instance, that optionally returns a value.
  Execution is guaranteed to TCP level with server failure being reported.

* **Rich type system**
  Named data types that can be enumerations, structs or typedefs, and collections (arrays) of types, and each of those types can be nested.  Type aliases are supported, and constraints such as a limited value-range (work in progress).

* **Events**  
  A fire-and-forget call/message, sent to or invoked on zero or more subscribing instances. The Event has no return a value and does not guarantee delivery (details are target dependent).

* **Data Properties**  
  An observable shared state object that can be read and set, and which is available to all subscribing entities. 

* **Layered architecture and Deployment files**  
  IFEX Core IDL is the fundamental format describing interfaces.  The IFEX concept adds on a layered architecture that adds deployment-specific data to an interface definition, and other composable features.

## Features that are not included _in the core IDL_, but worth describing:

* **Service**

This current version of the IFEX Core IDL has removed the "service:" keyword but the concept of a service should still be defined in terms of the interfaces the service provides.  (See detailed definition chapter).

* **Signal**

IFEX Core IDL does not include the name Signal but supports both **Events** and **Properties** to cover the idea of a signal.  See next chapter for a more detailed analysis.

----

## Feature concept details

### Namespace

- A Namespace is a way to separate definitions inside named groups.
- Namespaces are used to ensure that local names will not clash with identically named items in other namespace.
- Namespaces affect visibility, in other words what objects can be *seen* or *reached* from within a part of a program.
- Namespaces can contain other Namespaces, creating a hierarchy.
- How visibility/reachability is handled _might_ be specific to the target language or environment, but IFEX expects the following behavior to be the normal one unless there are very good reasons for exceptions:
  - Items within different (non-parent) namespaces are isolated from each other unless otherwise specified, and these frequently used hierarchy rules apply:  Everything within a child namespace can see and reach items in any of its parent namespaces.  For non-parent relationship, it is required to either specify an item using a fully-qualified "path" through the namespace hierarchy, or to make a statement of reference or inclusion of another namespaces into the current namespace.

## Interface

- Generally, Interface is a broad term.  We are here concerned with functional software interfaces.
- The IFEX core IDL strives to usable in all areas of a computing system.  The interface definition therefore does not define details around communication hardware, implementation language, data-communication protocols, bit-encoding and in-memory layouts etc.  Such information is however added through supplementary information in the mappings and tools that consume the interface description.  In this environment the content of an Interface are things like 
- A IFEX **Interface** is _primarily_ defined by a collection of **Methods**, but may also expose functionality through **Event**s and data **Properties**.  The interface might also include variables, constants, method-arguments, types, observable data-items and events that are required only inside the interface.
- An Interface name is not itself a Namespace but its contents must be defined within a Namespace.
- All Methods defined or referred to by an Interface are required to be within the same Namespace, i.e. it is not possible to build an Interface by referring to Methods that have been defined in different Namespaces.

### Method

- A method is a function with a (mandatory) name, plus a set of (optional) **input parameters**, **output parameters**, **return parameters** and **error conditions**.
- Like most other objects, a Method is always defined in the context of a Namespace, but this is often as a result of being within the context of an Interface.

### Error

- An IFEX Error definition is an error condition that can appear while (attempting to) execute a given Method.
- An error is defined by referencing one or more **Type**s that define the data that shall be communicated when an error occurs.  Enumeration types are common, but it could be any defined type.
- NOTE!  There can be _more than one_ error, each with its own datatype, defined for a method.
- It is not specified by IFEX how errors are propagated to the caller of a function - that translation is target language/environment specific.  It may be done using a return or output parameter in one programming language and using **Exception**-handling in another.  Communication protocols may implement their own error-condition side-channels, or other methods.

### Event

- An Event is a time-sensitive communication with _fire-and-forget_ behavior, sent between parts in the distributed system.
- A IFEX Event can carry multiple pieces of data with it, each of which can use an arbitrary data type.
- A IFEX Event definition looks similar to a Method but with some differences in definition and behavior:
  - An Event has a name, and optionally a set of parameters that are distributed with the event, each having a name and a datatype.  This mimics a Method signature.
  - An Event can however **not** have a Return type, nor any out-parameters.
  - An Event may have **Error**s defined but it is likely to be rarely used.  Since the exected semantics are "fire and forget", the usage of Error is likely to be limited to very fundamental errors, such as the network protocol returning an error because the connection was closed, etc.
- _Fire-and-forget_ expected behavior means that on the IFEX semantics level it is _not expected_ to be a guaranteed delivery.  It is decided by the target environment mapping whether an Event can be guaranteed to be received or if it is non-reliable.  In either case, there is **no reply** defined for an Event.  A Method call shall be used where reliability is required, in which case a return value would indicate that the request was received and completed.
- A IFEX **Event** is a separate and expressly defined object in the interface description.  It is therefore not (in our particular definition) to be mixed up with any other "happenings" in a system that are not defined inside a IFEX/interface definition.  It shall not be confused with messages that are _automatically_ sent by some target environment because of the defined behavior of its objects.  For example, in some systems, subscribing to changes of an observable data Property, may trigger something that some might call "update events", but that is a consequence of the behavior of the observable Property, and is not to be confused by expressly defined **Event** objects in the interface. It shall not be required to define any IFEX Events for such messages that are created automatically by the particular data protocol or target environment mapping.

- A IFEX Event is also not a persistent data item, and thus has no concept of active-low, edge-trigger, rising/falling edge, etc. (other than what its name and documentation indicates\*\*).  The Event is simply transferred by the sender when the sender thinks it is appropriate, and the documentation would explain the associated meaning.

- \*\* Design tip:  If there is a desire to model On/Off events, and avoid the verbosity of duplicating everything into two different Event objects -> simply give the event a single name and transfer a boolean as argument: FooState(bool) where the true/false value indicates the on/off state.  Another option, as always, is to define an observable boolean data Property and use the target environment's Pub/Sub capability to get updates on its state.  (Depending on the details of the target environment, the latter might give reliability guarantees that Events do not have).

- An Event can be sent from client to server or from server to client(\*).
(\*) TODO: Shall the direction of an event be defined somehow?

- \*\* If an event is to be transferred as a "broadcast" in a particular environment whereas other Events would be addressed uniquely to a particular client, then define this difference as extra information in a deployment model / target mapping.  It is not specified in the interface description.

### Property

- A **Property** is an observable data item.  It belongs in an **Interface**, has a canonical name in addition to possible **aliases** (i.e. alternative names), and a data type.
- A Property is defined as a single item but the data type could be an arbitrary data type, including composite data types.
- The singular nature of a property suggests that it is generally expected behavior that its value shall updated and communicated as an atomic operation, (it is either fully updated or not at all).
- The available features for update and communication are target-environment specific, but the most common expectation is that a Property can be updated and _observed_, meaning that a client can call a method to get or set the current value of the property (with appropriate access control rules) and often also _subscribe_ to be notified of when the value of a property was changed for any reason.
- In some other language definitions this type of item is called an **Attribute** or **Field**.
- A property can also be seen as analogous (and bi-directionally translatable, if datatypes allow it) to a sensor Signal in the Vehicle Signal Specification (VSS).

**Side proposal**: Consider renaming Property to Attribute to match Franca IDL, and because properties have another use in OpenAPI and AsyncAPI, and it seems other HTTP-related communication as well.

### Return values

- A Return Value specifies what is returned from a Method execution.  Although "out parameters" could serve a similar purpose, the Return Value has been given special status.
- Please be aware that while return-value is often traditionally used for indicating success/error, the abstract Errors concept is more powerful and should often be preferred.
- Only one single return value type is supported, but it can of course use any data type including composite types.
- The term Status may be used in other technologies and the meaning of return value shall be seen as equivalent of status.

#### Return/status communication in asynchronous vs. synchronous method calls

- In computing systems there are two main paradigms regarding invocation of a procedure/function: Blocking/synchronous vs. Non-blocking/asynchronous.

  - In a blocking/synchronous environment, the client invokes an operation (a.k.a. calls a function) and will halt until the operation is completed, a.k.a. "the function returns". Upon return, a return-value (result) may be communicated back to the client, and the client then continues its normal execution flow.

  - In an asynchronous setup, a client can trigger the start of an operation and then continue doing other work while the method executes in parallel.  In this case, the executing function will report back when the operation is finished, but it could also give continuous reports as to the progress of the function ("streaming updates").

- In the IFEX core IDL, methods can only be defined _without_ defining their (synchronous/asynchronous) invocation strategy.  It is more flexible to define this separately in a deployment-model/target-mapping because it leads to interface descriptions that can be reused in a wider set of circumstances.  The desire for sync vs. async may change in different circumstances, and the availability of sync/async might also be constrained by the target environment capability.

- In all cases, an IFEX Method may define a Return Value type.  The return value can be defined for the interface, without knowing the manner that the function will be invoked (e.g. the chosen communication protocol). IFEX-IDL-language has the unique feature of using the Return Value type to serve two different purposes in sync vs async situations:

- Although some details are often target-dependent, the following defines the _expected_ behavior of the return type in a system built from a IFEX interface:
  1. In the case of a blocking/synchronous call, the Return Value type is the value communicated once after the operation completes.
  2. In the case of a non-blocking/asynchronous call, the same defined Return Value type is also used with the difference that it _may_ be returned _multiple times_.  Using that behavior is optional and target-dependent, but if it is used then a target environment may choose to provide a regular stream of status updates while the method executes.  In each such update, a value is transferred that matches the defined Return Value type\*\*.

  - It follows that only valid values of the Return Value type may be returned. 

  - \*\* Design note:  This is already in itself a very powerful mechanism and should suffice in a majority of cases, but if any additional status/streaming-data functionality is required, that may of course be done by defining a data Property in the interface, whose value is used to indicate the status of the system for the executing method.  This would enable to listen (subscribe) to update to the Property, or fetch it on-demand, depending on what features the target mapping provides for Properties.  Note that there is no _formal_ way to describe the relationship between Property and Method in this design approach - it would rely on documenting the relationship in descriptions.

  - \*\*\*Design note 2: While the interface can now be defined without deciding up front about synchronous/asynchronous operation, if an async operation _may_ be expected it is still a good idea to design the return value with this in mind.  It is likely to include something to indicate that processing is under way.  For example the streaming returns during an operation might be: Started, Processing..., Processing..., Processing..., Done!"`  (Note that this, like most details, can be extended by overlays.)

- While a return value can also indicate that the operation did NOT complete successfully, the more capable **Errors** concept should not be overlooked.

- After an operation has been completed and its equivalent of "DONE" has been communicated, the function is expected to seize any further communication of the return/status type.

## Target Environment

- Target Environment is a catch-all term to indicate the context and environment of those artifacts that are generated from source IDL.
- For each type of output result from a generator or conversion tool, there will be environment-specific details to consider, and in the documentation we often refer to all of those as simply the "target environment".
- The term thus signifies any and all things that are unique about that environment.

For example:
1. The chosen programming language in the case of code-generation tools.
2. Any other details pertaining to other levels of software technology that is being targeted.  (For example if HTTP is an applicable protocol to use then details of transport layer security (TLS) would apply, whereas for other protocols it might not).

N.B. In the text, "target-environment dependent", may sometimes be shortened to simply target-dependent.

### Service (not a core feature)

This current version of the IFEX Core IDL has removed the "service:" keyword
but the concept of a service should still be defined in terms of the interfaces
the service provides.  In the future a new concept may be appropriate to add
but at the moment it is expected that a "service" may be defined externally
from the IFEX Core IDL file(s), but that the definition points to one or
several IDL files that define the interface that the service provides.

It is still worthwhile to prepare our understanding of what a service is:

- A service is a software functionality or set of functionalities that can be activated by a client. A key characteristic of a service in support of SOA is that it has low coupling to other services and strives to provide a useful function also if used independently from other services.
- In IFEX philosophy, a **Service** provides one or more **Interface**s and it is expected that a service is defined in the form of one or several interfaces described by the IFEX Core IDL.
- Most likely, a service definition will only make sense together with deployment information such as the chosen target environment and technology (a specific RPC protocol, a REST-style web-service, etc.)

### Signals (not a core feature)

The word Signal is interpreted by some as the transfer of a _value_ associated 
with a name/id for what that value represents.  This value transfer ought to
be semantically equivalent to single-argument Event, and is therefore supported
that way within IFEX.  Another interpretation is that the word Signal represents
the underlying data item itself, so that value-transfers are defined more as a
consequence of for example "subscribing to changes of a Signal".  In this second
interpretation the Signal is represented by a Property in IFEX.  The Vehicle
Signal Specification (VSS) typically uses the the second interpretation, and
VSS Signals can then be represented by Properties in IFEX.  (Refer to further
documentation on IFEX/VSS relationship).

**TODO**: Includes and references needs some further analysis and documentation.

--------------------

# NAMESPACE VERSIONING

IFEX namespaces can optionally have a major and minor version, specified by
`major_version` and `minor_version` keys, complemented by an additional
free format string named version-label.

Namespace version management can be used to understand the impact of changes
on various namespace levels and how this may affect compabitility.
For general API-compatibility evaluation, the version on the **Interface**
node might be used more often, however.

Versioning shall follow the Semantic Versioning principle.  More details
are described under Interface Versioning.

Namespace versioning can be used build-time to ensure that the correct
version of all needed namespace implementations are deployed, while
also detecting if multiple, non-compatible versions of a namespace is
required.

# INTERFACE VERSIONING

An Interface is essentially a specialization of the Namespace concept.
Interfaces may be verisoned in the same manner as described for Namespaces.

There might be rules implemented in validation tools that ensure interface
versions match the versioning of namespaces.  (E.g. Don't claim an interface is
compatible if its parent namespace have changed in an incompatible way).

Versioning shall follow the Semantic Versioning principle:

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

An optional field for patch version exists but some choose to not use it
when focusing on the actual interface definition and behavior concerning
backward-compatibility, modifying the minor version if any part of the actual
interface changed.  However, patch version is there if desired, and if it
is used it is recommended to be used for minor documentation-related changes.
Some setups choose to not bother with patch version since the fact that an
interface file has been modified might also be identified in other ways, such
as using a git commit hash.  Note also the additional field `version-label`
that is a free-form field in which implementations can place their own type of
identifying information.


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
| version_label | A single **str** |
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
