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

