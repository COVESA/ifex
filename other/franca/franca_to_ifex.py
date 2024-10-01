# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project

# Have to define some paths to make this work (should be rearranged, ideally)
import sys
import os
mydir = os.path.dirname(__file__)
for p in ['pyfranca', 'pyfranca/pyfranca']:
    if p not in sys.path:
        sys.path.append(os.path.join(mydir,p))

from ifex.model.ifex_ast_construction import add_constructors_to_ifex_ast_model, ifex_ast_as_yaml
import ifex.model.ifex_ast as ifex
import pyfranca.ast as francatypes
import re
from other.franca.pyfranca.pyfranca import Processor


# --- Fundamental types ---

type_translation = {
    francatypes.Boolean : "boolean",
    francatypes.ByteBuffer : "uint8[]",
    francatypes.ComplexType : "opaque", # FIXME this is a struct reference,
    francatypes.Double : "double",
    francatypes.Float : "float",
    francatypes.Int8 : "int8",
    francatypes.Int16 : "int16",
    francatypes.Int32 : "int32",
    francatypes.Int64 : "int64",
    francatypes.String : "string",
    francatypes.UInt8 : "uint8",
    francatypes.UInt16 : "uint16",
    francatypes.UInt32 : "uint32",
    francatypes.UInt64 : "uint64",
}

def translate_type(t):
    if type(t) is francatypes.Enumeration:
        return t.name # FIXME use qualified name <InterfaceName>_<EnumerationName>, or change in the other place
    if type(t) is francatypes.Reference:
        return t.name
    if type(t) is francatypes.Array:
        # FIXME is size of array defined in FRANCA?
        converted_type = translate_type(t.type)
        converted_type = converted_type + '[]'
        return converted_type
    else:
        t2 = type_translation.get(type(t))
        return t2 if t2 is not None else t

def ifex_import_ref_from_fidl(fidl_file):
    return re.sub('.fidl$', '.ifex', fidl_file)


# HELPER FUNCTIONS

# flatmap: Call function for each item in input_array, and flatten the result
# into one array. The passed function is expected to return an array for each call.
def flatmap(function, input_array):
    return [y for x in input_array for y in function(x)]

# --- Partial tree conversion functions ---

# NOTE: The conventional python naming convention for methods is
# deliberately broken here by using Capitalized names.  This is to
# make the AST node type names stand out.  This helps understanding
# if you're familiar with the AST type names of Franca and IFEX.

def combined_name(parent, item):
    return parent + "_" + item

def Fields_to_Members(franca_fields):
    return [ifex.Member(f.name, translate_type(f.type)) for f in franca_fields]

def Structs_in_TypeCollection(franca_typecollection):
    return [ifex.Struct(name = combined_name(franca_typecollection.name, item.name),
                        members = Fields_to_Members(item.fields.values()))
            for item in franca_typecollection.structs.values() if item is not None]

def Structs_in_Interface(franca_interface):
    return [ifex.Struct(name = combined_name(franca_interface.name, item.name),
                        members = Fields_to_Members(item.fields.values()))
            for item in franca_interface.structs.values() if item is not None]

def Structs_in_Package(franca_package):
    return (flatmap(Structs_in_Interface, franca_package.interfaces.values()) +
            flatmap(Structs_in_TypeCollection, franca_package.typecollections.values()))


# Convert/dereference pyfranca enumerator values. They can be a reference to
# IntegerValue type or, None if not specified.
def Enumerator_Value(v):
    if isinstance(v, francatypes.IntegerValue):
        return v.value
    elif v is None:
        return None
    else:
        raise Exception(f"ERROR: BUG: Unexpected enumerator value type: {type(v)=}.")

def Enumerators_to_Options(enumerators, enumeration_name):
    # Franca allows (at least the parser we use...) enumeration with no specified
    # enumerators/options, but IFEX does currently not, and not sure that it should either.
    if len(enumerators) == 0:
        raise Exception(f"ERROR: Enumeration named '{enumeration_name}' must have at least one enumeration/option.")

    return [ifex.Option(name = item.name,
                        value = Enumerator_Value(item.value))
            for item in enumerators.values()]

def Enumerations_in_Interface(franca_interface):
    return [ifex.Enumeration(name = combined_name(franca_interface.name, item.name),
                             datatype = 'int32',
                             options = Enumerators_to_Options(item.enumerators, item.name))
            for item in franca_interface.enumerations.values()]

def Enumerations_in_Typecollection(franca_typecollection):
    return [ifex.Enumeration(name = combined_name(franca_typecollection.name, item.name),
                             datatype = 'int32',
                             options = Enumerators_to_Options(item.enumerators, item.name))
            for item in franca_typecollection.enumerations.values()]

def Enumerations_in_Package(franca_package):
    return (flatmap(Enumerations_in_Interface, franca_package.interfaces.values()) +
            flatmap(Enumerations_in_Typecollection, franca_package.typecollections.values()))

def Arguments_to_Arguments(franca_arguments):
    return [ifex.Argument(name = name, datatype = translate_type(item.type))
            for name, item in franca_arguments.items()]

def Methods_to_Methods(franca_methods):
    return [ifex.Method(name = name,
                        input = Arguments_to_Arguments(item.in_args),
                        output = Arguments_to_Arguments(item.out_args),
                        # NOTE: Franca does not have return values, only out-parameters.
                        # We could consider a heuristic here that converts a single output value to a return value.
                        # There should be reasonable defaults, and user configuration for this.
                        returns = [])
            for name, item in franca_methods.items()]

def Attributes_to_Properties(franca_attributes):
    return [ifex.Property(name = name,
                          datatype = translate_type(item.type),
                          description = "TODO")
            for name, item in franca_attributes.items()]

def Typedefs_from_TypeCollection(franca_typecollection):
    return [ifex.Typedef(name = name,
                         datatype = translate_type(item.name),
                         description = "TODO")
            for name, item in franca_typecollection.structs.items()]

def Typedefs_from_TypeCollections(franca_typecollections):
    return flatmap(Typedefs_from_TypeCollection, franca_typecollections.values())

def Imports_to_Includes(franca_imports):
    return [ifex.Include(file = ifex_import_ref_from_fidl(item.file)
                       # namespace = foo -- FIXME Need import *into* a Namespace?
                       # Franca: namespace
                       # Franca: package_reference
                       # Franca: namespace_reference
                       ) for item in franca_imports]

# --- MAIN conversion function ---

def franca_to_ifex(package):
    ns = ifex.Namespace(name = package.name or '_',
                        structs = Structs_in_Package(package),
                        typedefs = Typedefs_from_TypeCollections(package.typecollections),  # References(todo),
                        enumerations = Enumerations_in_Package(package))

    if len(package.interfaces) > 1:
        print("Warning!  Partly unsupported: Multiple Franca interfaces in package and this is only partly supported (WIP)")


    # Here follows some logic to define namespaces appropriately.  Franca has a
    # concept of one interface "managing" another interface.  It appears to me
    # to be primarily a way to introduce another level of namespacing since
    # "package" is the only other one Franca supports.  At least, it seems to
    # be used that way - i.e. the A "manages" B, C, and D, is just a way to
    # group together B, C, and D, and set a version for them.  IFEX supports
    # versioning on namespaces.  The closest translation is to translate this
    # managing interface into another namespace, but we also need to handle the
    # fact that this namespace can contain multiple interfaces.

    inner_interfaces = []

    # No managing interface -> use the current parent namespace
    managing_interface_namespace = ns.name

    # If there is a managing interface, collect its children interfaces
    # Otherwise just collect all interfaces.
    for iname, i in package.interfaces.items():
        # ... but if there is a managing interface, put that as the top level
        if i.manages == []:
            print(f"UNEXPECTED")
        if i.manages is not None:
            managing_interface_namespace = iname
            # FIXME: We are only expecting one - do error checking/reporting
        else:
            # Collect the remaining ones
            inner_interfaces.append(i)

    # FIXME: We are not converting the version of the managing interface/namespace yet

    # Finally, do the work with the collection of the "real" interfaces
    for i in inner_interfaces:
        #namespace = ifex.Namespace(name = managing_interface_namespace + '.' + i.name)
        namespace = ifex.Namespace(name = i.name)
        ns.namespaces.append(namespace)

        # If we're adding the interface name as a namespace, then the interface itself
        # gets an anonymous name (_) . (Different strategies might be selected later -> TBD)
        namespace.interface = ifex.Interface(name = '_',
                                             methods = Methods_to_Methods(i.methods),
                                             properties = Attributes_to_Properties(i.attributes))

    return ifex.AST(namespaces = [ns],
                    includes = Imports_to_Includes(package.imports))


def franca_ast_from_input(fidl_file):
    # Parse protobuf input and create Protobuf AST
    thisdir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    processor = Processor()

    x =  processor.import_file(fidl_file)
    # This returns the top level package
    return processor.import_file(fidl_file)

# --- Script entry point ---

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(__file__)} <filename>")
        sys.exit(1)

    # Add the type-checking constructor mixin
    add_constructors_to_ifex_ast_model()

    try:
        # Parse franca input and create Franca AST (top node is the Package definition)
        franca_ast = franca_ast_from_input(sys.argv[1])

        # Convert Protobuf AST  to IFEX AST
        ifex_ast = franca_to_ifex(franca_ast)

        # Output as YAML
        print(ifex_ast_as_yaml(ifex_ast))

    except FileNotFoundError:
        print("ERROR: File not found")
    except Exception as e:
        raise(e)
        print("ERROR: An unexpected error occurred: {}".format(e))

