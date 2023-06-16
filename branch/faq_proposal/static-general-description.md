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

