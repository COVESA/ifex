# (C) 2022 MBition GmbH
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
#
# VSC Tree management
#
#  A namespace tree populated by data types, includes, and methods
#
NATIVE_DATATYPES = [ 'int8', 'uint8', 'int16', 'uint16', 'int32',
                     'uint32', 'int64', 'uint64', 'float',
                     'double', 'boolean', 'string', 'binary' ]
_native_datatypes = {}

class Base:
    def __init__(self, name: str,
                 namespace: "NameSpace" = None):
        self._name = name
        self._namespace = namespace


    @property
    def name(self):
        return self._name


    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        self._namespace = namespace

    @property
    def root(self):
        tmp = self
        while True:
            if tmp.namespace == None:
                return tmp
            tmp = tmp.namespace

    def absolute_path_list(self):
        res = []
        tmp = self
        while tmp != None:
            res.insert(0, tmp)
            tmp = tmp.namespace

        return res


    def as_vsc_dict(self):
        return { "name": self._name} if self._name is not None else {}

#
# Nil Base class for all datatypes.
# Used for typechecking arguments.
#
class DatatypeBase(Base):
    def __init__(self, name: str, namespace: "NameSpace" = None):
        super().__init__(name, namespace)

    def find_unresolved_datatypes(self, path: list = []) -> list:
        raise Exception(f"Pure virtual DatatypeBase.find_unresolved_datatypes() called for self.name")

    def as_field_dict(self) ->dict:
        return {
            "datatype": self.namespace.find_datatype_by_name(self.name).datatype
        }


# Native datatypes
#
# Extends DatatypeBase with a support for native datatypes.
#
# Contains validation of datatype names and a
# as_dict() dictionary generator
#
class NativeDatatype(DatatypeBase):
    def __init__(self, name: str, namespace: "NameSpace" = None):
        if name not in NATIVE_DATATYPES:
            raise Exception(f"Unknown native type: {name}")

        super().__init__(name, namespace)

    # Native datatypes always resolves
    def find_unresolved_datatypes(self, path: list = []) -> list:
        return []

    def as_vsc_dict(self) -> dict:
        return { "datatype": self.name }




#
# A field consists of:
# 2. A datatype string
# 2. An optional field name
# 3. An optional default value
#
# A field is used by typedefs, struct members,
# and method in/out/error sections
#
# A field datatype string can be resolved to an actual
# DatatypeBase value via resolve_datatype().
#
class Field(DatatypeBase):
    def __init__(self,
                 datatype: str,
                 name: str = None,
                 default_value: any = None,
                 namespace: "NameSpace" = None):
        super().__init__(name, namespace)
        self._datatype = datatype
        self._default_value = default_value

    @property
    def name(self) -> str:
        return self._name

    @property
    def default_value(self) -> any:
        return self._default_value

    @property
    def datatype(self) -> str:
        return self._datatype

    # Check that our datatype can be resolved
    def find_unresolved_datatypes(self, path: list = []) -> list:
        if self.namespace.find_datatype_by_name(self.datatype) is None:
            return [ ( self.namespace.path_string(path + [self.name]), self.datatype) ]
        return []

    def as_vsc_dict(self) -> dict:
        return {
            "name": self.name,
            "datatype": self._datatype,
            **({ "default_value": self._default_value} if self._default_value is not None else {})
        }


# Typedef
#
# This is just a subclass of field
#
class Typedef(Field):
    def __init__(self, name: str, datatype: str, namespace: "NameSpace" = None):
        super().__init__(datatype=datatype, name=name, namespace=namespace)

# Enumeration
#  Extends DatatypeBase with a list of enumerated fields
#
class Enumeration(DatatypeBase):
    class Option:
        def __init__(self, name:str, value:any=None):
            self._name = name
            self._value = value

        @property
        def name(self):
            return self._name

        @property
        def value(self):
            return self._value

        def as_dict(self):
            if self._value is not None:
                value_dict = { "value": self._value}
            else:
                value_dict = {}

            return {
                "name": self._name,
                **value_dict
            }

    def __init__(self, name: str, datatype: str = None, namespace: "NameSpace" = None):
        super().__init__(name, namespace)
        self._datatype = datatype
        self._options = {}


    def add_option(self, option: Option):
        self._options[option.name] = option
        return option

    @property
    def datatype(self) -> str:
        return self._datatype

    @property
    def option(self):
        return self._options

    # If we have a specified datatype, make sure that it resolves.
    def find_unresolved_datatypes(self, path: list = []) -> list:
        if self.datatype is not None and self.namespace.find_datatype_by_name(self.datatype) is None:
            return [ ( self.namespace.path_string(path + [self.name]), self.datatype) ]
        return []

    def as_vsc_dict(self):
        # FIXME: Validate that datatype, if present, resolves to a
        #        native type and not a struct, other enum, etc.  This
        #        means that any Typedef datatypes must be resolved all
        #        their way to their terminal type, which must be a
        #        native type.
        #
        return {
            "name": self.name,
            **({"datatype": self._datatype} if self._datatype is not None else {}),
            "options": [ option.as_dict() for _, option in self._options.items() ]
        }


# Struct
#  Extends DatatypeBase with a list of struct fields
#
class Struct(DatatypeBase):
    def __init__(self, name: str, namespace: "NameSpace" = None):
        super().__init__(name, namespace)
        self._members = {}

    def add_member(self, name: str, datatype: str):
        self._members[name] = Field(datatype=datatype, name=name, namespace=self.namespace)
        return self._members[name]

    @property
    def members(self):
        return self._members

    # If we have a specified datatype, make sure that it resolves.
    def find_unresolved_datatypes(self, path: list = []) -> list:
        res = []

        for (_, member) in self.members.items():
            res.extend(member.find_unresolved_datatypes(path + [self.name]))

        return res

    def as_vsc_dict(self):
        return {
            "name": self.name,
            "members": [ member.as_vsc_dict() for _, member in self._members.items() ]
        }

# Method
#  Extends Base with input and output arguments and an
#  optional error type.
#
class Method(Base):
    def __init__(self, name: str, error_datatype: str = None, namespace: "NameSpace" = None):
        super().__init__(name, namespace)
        self._in_arg = []
        self._out_arg = []
        self._error_datatype = error_datatype

    def add_in_argument(self, name: str, datatype: str):
        self._in_arg.append(Field(datatype=datatype, name=name, namespace=self.namespace))

    def add_out_argument(self, name: str, datatype: str):
        self._out_arg.append(Field(datatype=datatype, name=name, namespace=self.namespace))


    # If we have a specified datatype, make sure that it resolves.
    def find_unresolved_datatypes(self, path: list = []) -> list:
        res = []

        for arg in self._in_arg:
            res.extend(arg.find_unresolved_datatypes(path + [self.name, "[in-argument]"]))

        for arg in self._out_arg:
            res.extend(arg.find_unresolved_datatypes(path + [self.name, "[out-argument]"]))

        if self._error_datatype is not None and self.namespace.find_datatype_by_name(self._error_datatype) is None:
            res.extend([ ( self.namespace.path_string([self.name, "[error-type]"]),
                           self._error_datatype) ])

        return res

    def as_vsc_dict(self):
        return {
            **super().as_vsc_dict(),
            "in": [ in_arg.as_vsc_dict() for in_arg in self._in_arg ],
            "out": [ out_arg.as_vsc_dict() for out_arg in self._out_arg ],
            "error": { "datatype": self._error_datatype }
        }


# Event
#  Extends Base with input and output arguments and an
#  optional error type.
#
class Event(Base):
    def __init__(self, name: str, namespace: "NameSpace" = None):
        super().__init__(name, namespace)
        self._in_arg = []
        self._out_arg = []
        self._error_datatype = error_datatype

    def add_in_argument(self, name: str, datatype: str):
        self._in_arg.append(Field(datatype=datatype, name=name, namespace=self.namespace))

    # If we have a specified datatype, make sure that it resolves.
    def find_unresolved_datatypes(self, path: list = []) -> list:
        res = []
        for (_, arg) in self.in_arg.items():
            res.extend(arg.find_unresolved_datatypes(path + [self.name]))

        return res

    def as_vsc_dict(self) -> dict:
        return {
            **super().as_vsc_dict(),
            "in": [ in_arg.as_vsc_dict() for in_arg in self._in_arg ],
        }


class NameSpace(Base):
    class IncludeFile:
        def __init__(self, filename: str, description: str = None):
            self._filename: filename
            self._description: description


        @property
        def filename(self) -> str:
            return self._filename

        @property
        def description(self) -> str:
            return self._description

        def as_dict(self) -> dict:
            return {
                "file": self.filename,
                **({ "description": self.description } if self.description is not None else {})
            }


    def __init__(self, name: str,
                 namespace: "NameSpace" = None,
                 namespace_separator: str = None,
                 search_inherited_namespaces: bool = True):


        super().__init__(name, namespace)
        if namespace is not None and (namespace_separator is not None or
                                      search_inherited_namespaces is not None):
            raise Exception(f"Namespace {name} has both parent namespace set together with at "
                            "least one of namespace separator and sarch inherited namespace flag.")

        if namespace is None:
            self._namespace_separator = namespace_separator
            self._search_inherited_namespaces = search_inherited_namespaces
        else:
            self._namespace_separator = namespace.namespace_separator
            self._search_inherited_namespaces = namespace.search_inherited_namespaces

        self._includes = []
        self._namespaces = {}

        self._typedefs = {}
        self._structs = {}
        self._enumerations = {}

        self._methods = {}
        self._events = {}
        self._properties = {}


    @property
    def namespace_separator(self) -> str:
        return self._namespace_separator

    @property
    def search_inherited_namespaces(self) -> bool:
        return self._search_inherited_namespaces

    def add_include(self, include: IncludeFile):
        self._includes[include.filename] = include

    def add_namespace(self, name: str) -> "NameSpace":
        #
        # Is 'name' not among our existing namesapces?
        # If so then create a new namespace and add it under self.
        #
        if name not in self._namespaces:
            namespace = NameSpace(name, self, None, None)

            self._namespaces[name] = namespace
            return namespace

        #
        # This is an existing namespace, just return it.
        #
        return self._namespaces[name]


    def add_method(self, name: str, error_datatype:str= None) -> Method:
        if name in self._methods:
            raise Exception("DUPLICATE METHOD: {name}")

        self._methods[name] = Method(name, error_datatype, self)
        return self._methods[name]


    def add_event(self, name: str) -> Event:
        if name in self._events:
            raise Exception("DUPLICATE EVENT: {name}")

        self._events[name] = Event(name, self)
        return self._events[name]

    def add_property(self, name: str, datatype: str) -> None: # Fixme
        if name in self._properties:
            raise Exception("DUPLICATE PROPERTY: {name}")

        self._properties[name] = None #FIXME ADD PROPERTY
        return self._properties[name]


    def add_typedef(self, name: str, datatype: str) -> Typedef:
        if name in self._typedefs:
            raise Exception("DUPLICATE TYPEDEF: {name}")

        self._typedefs[name] = Typedef(name, datatype, self)
        return self._typedefs[name]

    def add_struct(self, name: str) -> Struct:
        if name in self._structs:
            raise Exception("DUPLICATE STRUCT: {name}")

        self._structs[name] = Struct(name, self)
        return self._structs[name]

    def add_enumeration(self, name: str, datatype: str = None) -> Enumeration:
        if name in self._enumerations:
            raise Exception("DUPLICATE ENUMERATION: {name}")

        self._enumerations[name] = Enumeration(name, datatype, self)
        return self._enumerations[name]


    def as_vsc_dict(self):
        includes = [ include.as_vsc_dict() for include in self.includes ]
        namespaces = [ child.as_vsc_dict() for (_, child) in self.namespaces.items() ]

        typedefs = [ typedef.as_vsc_dict()  for (_, typedef) in self.typedefs.items() ]
        structs = [ struct.as_vsc_dict()  for (_, struct) in self.structs.items() ]
        enumerations = [ enum.as_vsc_dict()  for (_, enum) in self.enumerations.items() ]

        methods = [ method.as_vsc_dict() for (_, method) in self.methods.items() ]
        events = [ event.as_vsc_dict() for (_, event) in self.events.items() ]
        properties = [ prop.as_vsc_dict() for (_, prop) in self.properties.items() ]

        res = {
            **super().as_vsc_dict(),
            **({"includes": inlcudes} if len(includes) > 0 else {}),
            **({"namespaces": namespaces} if len(namespaces) > 0 else {}),

            **({"typedefs": typedefs} if len(typedefs) > 0 else {}),
            **({"structs":  structs} if len(structs) > 0 else {}),
            **({"enumerations": enumerations} if len(enumerations) > 0 else {}),

            **({"methods": methods} if len(methods) > 0 else {}),
            **({"events": events} if len(events) > 0 else {}),
            **({"properties": properties} if len(properties) > 0 else {})
        }
        return res


    @property
    def includes(self) -> list:
        return self._includes

    @property
    def namespaces(self) -> dict:
        return self._namespaces

    @property
    def structs(self) -> dict:
        return self._structs

    @property
    def typedefs(self) -> dict:
        return self._typedefs

    @property
    def enumerations(self) -> dict:
        return self._enumerations

    @property
    def methods(self) -> dict:
        return self._methods

    @property
    def events(self) -> dict:
        return self._events

    @property
    def properties(self) -> dict:
        return self._properties

    def path_string(self, path_list=[]):
        res = ''
        if isinstance(path_list, str):
            path_list = [path_list]

        for path_elem in path_list:
            if res == '':
                res = path_elem
                continue

            res = f"{res}{self.namespace_separator}{path_elem}"

        return res

    # Resolve an atomic type name to its datatype.
    # The datatype, which is atomic with no path element, is resolved
    # by looking up the datatypes defined in the local namespace.
    #
    # If self.search_inherited_namespaces is True then the parental
    # namespace structure will be traversed in search of the datatype
    # until the root namespace is found.
    #
    def find_local_datatype_by_name(self, datatype: str) -> Base:
        #
        # Is this a native datatype?
        #
        if datatype in _native_datatypes:
            return  _native_datatypes[datatype]

        # Is this a typedef?
        if datatype in self.typedefs:
            return self.typedefs[datatype]

        # Is this a struct?
        if datatype in self.structs:
            return self.structs[datatype]

        # Is this an enumerations?
        if datatype in self.enumerations:
            return self.enumerations[datatype]


        # Are we doing a local-only search and are not looking for inherited datatypes
        # that reside in our parental namespaces?
        if not self.search_inherited_namespaces:
            return None

        # We are to search inherited namespaces.
        # Do we have an owner?
        #
        if not self.namespace:
            return None

        # Recurse upward through namespace struture to find datatype.
        return self.namespace.find_local_datatype_by_name(datatype)


    # Find the namespace that hosts the datatype referred to
    # by a datatype path.
    #
    # The datatype argument is expected to be one of:
    #
    # 1. A local datatype.
    #    datatype is a datatype name with no path separator.
    #    Example "seat_position_t"
    #
    # 2. An absolute path to a datatype
    #    datatype is a separtor, followed by separator-split list
    #    of one or more namespaces, terminated by a datatype
    #    Example ".vehicle.cabin.seats.seat_position_t"
    #
    # 3. A relative path to a datatype
    #    datatype is a separator-split list of one or more
    #    namespaces, terminated by a datatype
    #    Example "cabin.seats.seat_position_t"
    #
    # ABSOLUTE PATH SEARCHES
    #
    # If datatype is ".vehicle.cabin.seats.seat_position_t" (note
    # the leading separtor), the namespace "seats" will be used to
    # resolve the datatype "seat_position_t". 
    #
    # vehicle <- Root of namespace tree
    #   cabin
    #     seats <- seat_position_t is defined by this namespace
    #
    #
    # RELATIVE PATH SEARCHES
    #
    # If datatype is "seats.seat_position_t" (no leading separator), then the
    # self will be used as a starting point to resolve "seat_position_t"
    #
    # vehicle
    #   cabin <- self
    #     seats <- seat_position_t is defined here.
    #
    #
    # If separator is "", treat datatype as a local datatype and do
    # no path processing. Only inheritance may be considered (see below).
    #
    # If search_inherited_namespaces is set, we will search the namespace namespace
    # struture to see if we have inherited the datatype from a parent.
    #
    def find_datatype_by_name(self, datatype: str) -> DatatypeBase:

        # If separator is not set, then we treat this as a
        # local datatype. Don't try to process any path
        # and just return a local (possibly inherited) resolution.
        #
        if self.namespace_separator == "":
            return self.find_local_datatype_by_name(datatype)

        #
        # Is this an absolute datatype path that starts with
        # a separator? If so move up to root namespace
        # and redo the search from there.
        #
        if datatype[0] == self.namespace_separator:
            # Try again from root, but now treat it as a relative path
            return self.root.find_datatype_by_name(datatype[1:])


        # We are doing a relative path resolve.
        # Split the datatype path into a list
        #
        dt_path_list = datatype.split(self.namespace_separator)

        # Use self as a starting namespace.
        ns = self

        # As long as we have path elements left (in addition to the
        # terminating datatype element), continue the traversal of
        # child namespaces.
        #
        while len(dt_path_list) > 1:

            # Can we find the next path component in among our namespaces?
            if not dt_path_list[0] in ns.namespaces:
                raise Exception(f"No: {dt_path_list[0]} in {ns.namespaces}")
                return None

            # Enter the namespace that matches the first element in the path list
            ns = ns.namespaces[dt_path_list[0]]

            # Trim off the first element of the path list
            dt_path_list = dt_path_list[1:]

        # We only have the final datatype element left in the path list.
        #
        # Use the current namespace to resolve the datatype
        #
        return ns.find_local_datatype_by_name(dt_path_list[0])

    #
    # Traverse all namespaces, methods, structs, enums, typedefs, events, and properties
    # and check that all referred datatypes can be resolved.
    # Return a list with a name of all datatypes that cannot be resolved.
    # Each list element is a string with the full path to the datatype that
    # could not be resolved.
    #
    def find_unresolved_datatypes(self, path: list = []) -> list:
        res = []
        for (_, ns) in self.namespaces.items():
            res.extend(ns.find_unresolved_datatypes(path + [self.name]))

        for (_, td) in self.typedefs.items():
            res.extend(td.find_unresolved_datatypes(path + [self.name]))

        for (_, st) in self.structs.items():
            res.extend(st.find_unresolved_datatypes(path + [self.name]))

        for (_, enum) in self.enumerations.items():
            res.extend(enum.find_unresolved_datatypes(path + [self.name]))

        for (_, meth) in self.methods.items():
            res.extend(meth.find_unresolved_datatypes(path + [self.name]))

        for (_, ev) in self.events.items():
            res.extend(ev.find_unresolved_datatypes(path + [self.name]))

        for (_, prop) in self.properties.items():
            res.extend(prop.find_unresolved_datatypes(path + [self.name]))

        return res


def create_root_namespace(separator=".", search_inherited_types = True):
    return NameSpace(None, None, separator, search_inherited_types)

#
# Load-time initialization of native types
#

for native_datatype in NATIVE_DATATYPES:
    _native_datatypes[native_datatype] = NativeDatatype(native_datatype)
