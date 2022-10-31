# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass, field
from typing import List, Optional

# shortcut to reduce code duplication for default_factory
# parameter in field()
EmptyList = lambda: []

# Module contains Vehicle Service Catalog abstract syntax tree
# implemented using python dataclasses.
#

# The specification can be found here, but the rules will be generated from 
# this file.  This file is the formal definition of the language.
# https://github.com/COVESA/vehicle_service_catalog/blob/master/syntax.md

@dataclass
class Argument:
    """
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
    """
    name: str
    """ Specifies the name of the argument """

    datatype: str
    """
    Specifies the data type of the argument, The type can be either a native or defined type.
    If `datatype` refers to a defined type, this type can be a local, nested, or externally defined reference.
    If the type is an array (ending with `[]`), the arraysize key can optionally be provided to specify the number of elements in the array.
    If arraysize is not specified for an array type, the member array can contain an arbitrary number of elements.
    """

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
    Dataclass used to represent a VSC method error.

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

    Please see the methods sample code below for an example of how error(s) are defined
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
    """

    datatype: str
    """
    Specifies the data type of the returned error value, The type can be either a native or defined type.
    If datatype refers to a defined type, this type can be a local, nested, or externally defined reference.
    If the type is an array (ending with []), the arraysize key can optionally be provided to specify the number of elements in the array.
    If arraysize is not specified for an array type, the member array can contain an arbitrary number of elements.
    """

    name: Optional[str] = None
    """ Name is required only if multiple Errors are defined, to differentiate between them. """

    description: Optional[str] = str()
    """ Specifies a description of how the errors shall be used. """

    arraysize: Optional[str] = None
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
    """ Containts a list of errors the method can return. """

    input: Optional[List[Argument]] = field(default_factory=EmptyList)
    """ Containts a list of the method input arguments. """

    output: Optional[List[Argument]] = field(default_factory=EmptyList)
    """ Containts a list of the method output arguments. """


@dataclass
class Event:
    """
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
    Dataclass used to represent VSC Property.

    Each properties list object specifies a shared state object that can be read and set, and which is available to all subscribing entities.
    A properties sample list object is given below, together with a struct definition:

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
    The type can be either a native or defined type.
    If datatype refers to a defined type, this type can be a local, nested, or externally defined reference.
    If the type is an array (ending with []), the arraysize key can optionally be provided to specify the number of elements in the array.
    If arraysize is not specified for an array type, the member array can contain an arbitrary number of elements.
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
    """

    name: str
    """ Specifies the name of the struct member. """

    datatype: str
    """
    Specifies the data type of the struct member.
    The type can be either a native or defined type.
    If datatype refers to a defined type, this type can be a local, nested, or externally defined reference.
    If the type is an array (ending with []), the arraysize key can optionally be provided to specify the number of elements in the array.
    If arraysize is not specified for an array type, the member array can contain an arbitrary number of elements.
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
    Dataclass used to represent VSC Enumeration Option.

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

    value: int
    """ Specifies the value of the enum option. """

    description: Optional[str] = None
    """ Contains a description of the enum option. """


@dataclass
class Enumeration:
    """
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
    """
    name: str
    """ Defines the name of the enum. """

    datatype: str
    """
    Specifies the data type that should be used to host this enum.
    The type can be either a native or defined type, but must resolve to a native integer type.
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

    """
    name: str
    """ Specifies the name of the struct. """

    description: Optional[str] = str()
    """ Specifies the description of the struct. """

    # TODO: do we need type field in a struct?
    type: Optional[str] = None
    """ Specifies the type of the struct. """

    members: Optional[List[Member]] = field(default_factory=EmptyList)
    """ Contains a list of members of a given struct. """


@dataclass
class Typedef:
    """
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
    """
    name: str
    """ Specifies the name of the typedef. """

    datatype: str
    """ Specifies datatype name of the typedef. """

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

    """
    file: str
    """ Specifies the path to the file to include. """

    description: Optional[str] = str()
    """ Specifies description of the include directive. """


@dataclass
class Namespace:
    """
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
    """

    name: str
    """ Specifies the name of the namespace. """

    description: Optional[str] = str()
    """ Specifies description of the namespace. """

    major_version: Optional[int] = None
    """ Provides the major version of the namespace. """

    minor_version: Optional[int] = None
    """ Provides the minor version of the namespace. """

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

    namespaces: Optional[List['Namespace']] = field(default_factory=EmptyList)
    """ Contains a list of sub namespaces in a given namespace """


@dataclass
class AST(Namespace):
    """
    Dataclass used to represent root element in a VSC AST.

    Behaviour is inherited from Namespace class.
    """
    pass
