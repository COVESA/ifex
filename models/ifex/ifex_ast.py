# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass, field
from typing import List, Optional, Any


# shortcut to reduce code duplication for default_factory
# parameter in field()
def EmptyList():
    return []


# Module contains Vehicle Service Catalog abstract syntax tree
# implemented using python dataclasses.
#
# The specification can be found here, but the rules will be generated from
# this file.  This file is the formal definition of the language.
# https://github.com/COVESA/vehicle_service_catalog/blob/master/syntax.md


@dataclass
class Argument:
    """
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
    """

    name: str
    """ Specifies the name of the argument """

    datatype: str
    """
    Specifies the data type of the argument, The type can be either a fundamental or defined type.  If `datatype` refers
    to a defined type, this type can be a local, nested, or externally defined reference.  If the type is an array
    (ending with `[]`), the arraysize key can optionally be provided to specify the number of elements in the array.  If
    arraysize is not specified for an array type, the member array can contain an arbitrary number of elements.  """

    description: Optional[str] = str()
    """ Contains a description of the argument. """

    arraysize: Optional[int] = None
    """
    Specifies the number of elements in the argument array.
    This key is only allowed if the datatype element specifies an array (ending with []).
    """

    range: Optional[str] = None


@dataclass
class Error:
    """
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
    """

    datatype: str
    """
    Specifies the data type of the returned error value, The type can be either a fundamental or defined type.  If
    datatype refers to a defined type, this type can be a local, nested, or externally defined reference.  If the type
    is an array (ending with []), the arraysize key can optionally be provided to specify the number of elements in the
    array.  If arraysize is not specified for an array type, the member array can contain an arbitrary number of
    elements.  """

    name: Optional[str] = None
    """ Name is required only if multiple Errors are defined, to differentiate between them. """

    description: Optional[str] = str()
    """ Specifies a description of how the errors shall be used. """

    arraysize: Optional[int] = None
    """
    Specifies the number of elements in the input parameter array.
    This key is only allowed if the datatype element specifies an array (ending with []).
    """

    range: Optional[str] = None
    """
    Specifies the legal range for the value.
    https://github.com/COVESA/vehicle_service_catalog/blob/master/syntax.md#value-range-specification
    """


@dataclass
class Method:
    """
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
    """

    name: str
    """ Specifies the name of the method. """

    description: Optional[str] = None
    """ Specifies a description of the method. """

    errors: Optional[List[Error]] = field(default_factory=EmptyList)
    """ Contains a list of errors the method can return. """

    input: Optional[List[Argument]] = field(default_factory=EmptyList)
    """ Contains a list of the method input arguments. """

    output: Optional[List[Argument]] = field(default_factory=EmptyList)
    """ Contains a list of the method output arguments. """

    # FIXME return argument should be possible to have anonymous (no given name)
    returns: Optional[List[Argument]] = field(default_factory=EmptyList)
    """ Contains a list of the method return arguments. """


@dataclass
class Event:
    """
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
    """

    name: str
    """ Specifies the name of the event. """

    description: Optional[str] = str()
    """ Specifies a description of the event. """

    input: Optional[List[Argument]] = field(default_factory=EmptyList)
    """
    Each `input` list object defines an input parameter to the event
    Please see the events sample code above for an example of how in parameter lists are use.
    """


@dataclass
class Property:
    """
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
    """

    name: str
    """ Specifies the name of the property. """

    datatype: str
    """
    Specifies the data type of the property,
    The type can be either a fundamental or defined type.
    - If datatype refers to a defined type, this type can be a local, nested, or externally defined reference.
    - If the type is an array (ending with []), the arraysize key can optionally be provided to specify the number of
      elements in the array.
    - If arraysize is not specified for an array type, the member array can contain an arbitrary number of elements.
    """

    description: Optional[str] = str()
    """ Specifies a description of the property. """

    arraysize: Optional[int] = None
    """
    Specifies the number of elements in the input parameter array.
    This key is only allowed if the datatype element specifies an array (ending with []).
    """


@dataclass
class Member:
    """
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
    """

    name: str
    """ Specifies the name of the struct member. """

    datatype: str
    """
    Specifies the data type of the struct member.
    The type can be either a fundamental or defined type.
    - If datatype refers to a defined type, this type can be a local, nested, or externally defined reference.
    - If the type is an array (ending with []), the arraysize key can optionally be provided to specify the number of
      elements in the array.
    - If arraysize is not specified for an array type, the member array can contain an arbitrary number of elements.
    """

    description: Optional[str] = str()
    """ Contains a description of the struct member. """

    arraysize: Optional[int] = None
    """
    Specifies the number of elements in the struct member array.
    This key is only allowed if the datatype element specifies an array (ending with []).
    """


@dataclass
class Option:
    """
    Dataclass used to represent IFEX Enumeration Option.

    Each options list object adds an option to the enumerator.

    Please see the enumerations sample code above for an example of how options list objects are used.

    ```yaml
    options:
      - name: base
        value: 0
        description: description of the option value
    ```
    """

    name: str
    """ Specifies the name of the enum option. """

    value: Any
    """ Specifies the value of the enum option. """

    description: Optional[str] = None
    """ Contains a description of the enum option. """


@dataclass
class Enumeration:
    """
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
    """

    name: str
    """ Defines the name of the enum. """

    datatype: str
    """
    Specifies the data type that should be used to host this enum.
    The type can be either a fundamental or defined type, but must resolve to a primitive type.
    If datatype refers to a defined type, this type can be a local, nested, or externally defined reference.
    """

    options: List[Option]
    """
    Each options list object adds an option to the enumerator.
    Please see the enumerations sample code above for an example of how options list objects are used
    """

    description: Optional[str] = None
    """ Specifies a description of the enum. """


@dataclass
class Struct:
    """
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

    """

    name: str
    """ Specifies the name of the struct. """

    description: Optional[str] = str()
    """ Specifies the description of the struct. """

    members: Optional[List[Member]] = field(default_factory=EmptyList)
    """ Contains a list of members of a given struct. """


@dataclass
class Typedef:
    """
    Dataclass used to represent IFEX Typedef.

    A Typedef is an alias to an existing fundamental type or defined type, including structs, enumerators, etc.  It can also be used to name and define a variant type.  The new data type name can be used in the definition of other datatypes, method- and event-parameters, and properties.

    A typedefs list object example is given below:

    ```yaml
    typedefs:
      - name: movement_t
        datatype: int16
        min: -1000
        max: 1000
        description: The movement of a seat component
    ```

    **Variant types**

    The fields `datatype` and `datatypes` are mutually exclusive - only one of them may have a value.  The field `datatypes` is used to specify multiple types associated with this type name.  Doing this makes it a `variant` type.  It is also possible to define a variant type using the `variant<a,b,c>`-style syntax in any location requiring a datatype, but the ability to specify it as a list can be more useful if the number of types is large.  Handling this as a list can also allow Layers to extend a variant type more conveniently.

    ```yaml
    typedefs:
      - name: StringOrStruct
        datatypes:
          - string
          - MyStruct
          - OtherStruct
        description: The Thing, represented in one of 3 ways.
    ```

    **NOTE!** The fields `datatype` and `datatypes` are defined as optional in the language model, but one of them must be defined.

    """

    name: str
    """ Specifies the name of the typedef. """

    datatype: Optional[str] = str()
    """ Specifies datatype name of the typedef. """

    datatypes: Optional[List[str]] = field(default_factory=EmptyList)
    """ If specified, then the type is a variant type.  At least two datatypes should be listed.  The single datatype: field must *not* be used at the same time. """

    description: Optional[str] = str()
    """ Specifies the description of the typedef. """

    arraysize: Optional[int] = None
    """
    Specifies the number of elements in the array.
    This key is only allowed if the datatype element specifies an array (ending with `[]`).
    """

    # TODO: can min/max be not only integers?
    min: Optional[int] = None
    """ Specifies the minimum value that the defined type can be set to."""

    max: Optional[int] = None
    """ Specifies the maximum value that the defined type can be set to."""


@dataclass
class Include:
    """
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

    """

    file: str
    """ Specifies the path to the file to include. """

    description: Optional[str] = str()
    """ Specifies description of the include directive. """


@dataclass
class Interface:
    """
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
    """

    name: str
    """ Specifies the name of the interface. """

    description: Optional[str] = str()
    """ Specifies description of the interface. """

    major_version: Optional[int] = None
    """ Provides the major version of the interface. """

    minor_version: Optional[int] = None
    """ Provides the minor version of the interface. """

    version_label: Optional[str] = str()
    """ A free-form string that contains any additional information about the content/version """

    events: Optional[List[Event]] = field(default_factory=EmptyList)
    """ Contains a list of the events in a given interface """

    methods: Optional[List[Method]] = field(default_factory=EmptyList)
    """ Contains a list of the methods in a given interface """

    typedefs: Optional[List[Typedef]] = field(default_factory=EmptyList)
    """ Contains a list of the typedefs in a given interface """

    includes: Optional[List[Include]] = field(default_factory=EmptyList)
    """ Contains a list of the includes in a given interface """

    structs: Optional[List[Struct]] = field(default_factory=EmptyList)
    """ Contains a list of the structs in a given interface """

    enumerations: Optional[List[Enumeration]] = field(default_factory=EmptyList)
    """ Contains a list of the enumerations in a given interface """

    properties: Optional[List[Property]] = field(default_factory=EmptyList)
    """ Contains a list of the properties in a given interface """

    namespaces: Optional[List["Namespace"]] = field(default_factory=EmptyList)
    """ Contains a list of the properties in a given interface """


@dataclass
class Namespace:
    """
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
    """

    name: str
    """ Specifies the name of the namespace. """

    description: Optional[str] = str()
    """ Specifies description of the namespace. """

    major_version: Optional[int] = None
    """ Provides the major version of the namespace. """

    minor_version: Optional[int] = None
    """ Provides the minor version of the namespace. """

    version_label: Optional[str] = str()
    """ A free-form string that contains any additional information about the content/version """

    events: Optional[List[Event]] = field(default_factory=EmptyList)
    """ Contains a list of the events in a given namespace """

    methods: Optional[List[Method]] = field(default_factory=EmptyList)
    """ Contains a list of the methods in a given namespace """

    typedefs: Optional[List[Typedef]] = field(default_factory=EmptyList)
    """ Contains a list of the typedefs in a given namespace """

    includes: Optional[List[Include]] = field(default_factory=EmptyList)
    """ Contains a list of the includes in a given namespace """

    structs: Optional[List[Struct]] = field(default_factory=EmptyList)
    """ Contains a list of the structs in a given namespace """

    enumerations: Optional[List[Enumeration]] = field(default_factory=EmptyList)
    """ Contains a list of the enumerations in a given namespace """

    properties: Optional[List[Property]] = field(default_factory=EmptyList)
    """ Contains a list of the properties in a given namespace """

    namespaces: Optional[List["Namespace"]] = field(default_factory=EmptyList)
    """ Contains a list of sub namespaces in a given namespace """

    interface: Optional[Interface] = None
    """ Optional Interface node.  (!) Can only be used once per Namespace, and its children cannot contain another
    Interface. """


@dataclass
class AST():
    """
    Dataclass used to represent root element in a IFEX AST.
    """
    name: Optional[str] = str()              # Represents name of file.  Usually better to name the Namespaces and Interfaces
    description: Optional[str] = str()
    major_version: Optional[int] = None      # Version of file.  Usually better to version Interfaces, and Namespaces!
    minor_version: Optional[int] = None      # ------ " ------
    includes: Optional[List[Include]] = field(default_factory=EmptyList)
    namespaces: Optional[List[Namespace]] = field(default_factory=EmptyList)

    # The following two arguments are strictly not necessary for IFEX Core IDL
    # files, however to prepare for differentiating between multiple Layer
    # Types, these fields are added here, with the intention that all future
    # Layer Types shall also include them.  For this AST model, which defines
    # the IFEX Core IDL, the value shall always be written as indicated here.
    # Other Layer types may define their own name for the filetype.
    filetype: Optional[str] = "IFEX Core IDL"

    # The schema field may optionally be a filename (typically to communicate
    # the schema name to a human) or a URI (typically to communicate to tools
    # where to fetch the schema).  **If** a more strict definition is required
    # (for example if a particular tool MUST be able to download the schema to
    # function correctly), then it is up to that tool to inform the tool user
    # that the value must be a complete URI.
    schema: Optional[str] = str()


class FundamentalTypes:
    # Fundamental types are the same as for VSS (Vehicle Signal Specification)
    # This table copied from VSS documentation:
    ptypes = [
            # name, description, min value, max value
            ["uint8", "unsigned 8-bit integer", 0, 255],
            ["int8", "signed 8-bit integer", -128, 127],
            ["uint16", "unsigned 16-bit integer", 0, 65535],
            ["int16", "signed 16-bit integer", -32768, 32767],
            ["uint32", "unsigned 32-bit integer", 0, 4294967295],
            ["int32", "signed 32-bit integer", -2147483648, 2147483647],
            ["uint64", "unsigned 64-bit integer", 0, "2^64 - 1"],
            ["int64", "signed 64-bit integer", "-2^63", "2^63 - 1"],
            ["boolean", "boolean value", False, True],
            ["float", "floating point number", "-3.4e -38", "3.4e 38"],
            ["double", "double precision floating point number", "-1.7e -300", "1.7e 300"],
            ["string", "character string", "N/A","N/A"]
            ]

    ctypes = [
            # name, description, min value, max value
            ["set", "A set (unique values), each of the same type. Format: set<ItemType>", "N/A", "N/A"],
            ["map", "A key-value mapping type.  Format: map<keytype,valuetype>", "N/A", "N/A"],
            ["variant", "A variant (union) type that can carry any of a predefined set of types, akin to Union in C.  Format: variant<type1,type2,type3...>", "N/A", "N/A"],
            ["opaque", "Indicates a complex type which is not explicitly defined in this context.", "N/A","N/A"]
            ]
