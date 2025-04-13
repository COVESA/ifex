# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

# Have to define a search path to submodule to make this work (might be rearranged later)
import os
import sys
mydir = os.path.dirname(__file__)
for p in ['pyfranca', 'pyfranca/pyfranca']:
    if p not in sys.path:
        sys.path.append(os.path.join(mydir,p))

import models.ifex.ifex_ast as ifex
import input_filters.franca.pyfranca.pyfranca as pyfranca
import transformers.rule_translator as m2m
import pyfranca.ast as franca
import re

from models.ifex.ifex_ast_construction import add_constructors_to_ifex_ast_model, ifex_ast_as_yaml
from transformers.rule_translator import Preparation, Constant, Unsupported, Default

def translate_type_name(francaitem):
    return translate_type(francaitem)

def concat_comments(list):
    return "\n".join(list)

# If enumerator values are not given, we must use auto-generated values.
# IFEX model requires all enumerators to be given values.
enum_count = -1
def reset_enumerator_counter():
    #print("***Resetting enum counter")
    global enum_count
    enum_count = -1

def translate_enumerator_value(franca_int_value):
    if franca_int_value is None:
        global enum_count
        enum_count = enum_count + 1
        return enum_count
    return translate_simple_constant(franca_int_value)

# Integer value is represented by an instance of IntegerValue class type, which has a "value" member.
# Same principle for: BooleanValue, FloatValue, DoubleValue, and StringValue:  We expect
# that the .value field has the corresponding python type and that this is also what we expect
# in the corresponding field on the IFEX AST.
# FIXME: Confirm that constants in Binary, Hexadecimal, etc. will also translate correctly?
def translate_simple_constant(franca_int_value):
    return franca_int_value.value

mapname = "UNDEF"
def map_name(x):
    global mapname
    map_name = x
    return

keytype = "UNDEF"
def map_keytype(x):
    global keytype
    # Input attribute will be a franca.Reference to the actual type
    keytype = translate_type_name(x)

valuetype = "UNDEF"
def map_valuetype(x):
    global valuetype
    valuetype = translate_type_name(x)

def assemble_map_type():
    global valuetype, keytype
    return f"map<{keytype},{valuetype}>"


# Tip: This translation table format is described in more detail in rule_translator.py
franca_to_ifex_mapping = {

    Default :  {
        # Franca-name   :  IFEX-name
        'comments' : 'description', # FIXME allow transform also here, e.g. concat comments
        'extends' : None,  # TODO
        'flags' : None,
        'type' : ('datatype', translate_type_name),
        },

    (franca.Interface,         ifex.Interface) : [
        ('maps', 'typedefs'),
        ('manages', Unsupported),
        ],
    (franca.Package,           ifex.Namespace) : [
        # TEMPORARY: Translates only the first interface
        ('interfaces', 'interface', lambda x: x[0]),
        ('typecollections', 'namespaces'),
        ],
    (franca.Method,            ifex.Method) : [
        ('in_args', 'input'),
        ('out_args', 'output'),
        ('namespace', None) ],
    (franca.Argument,          ifex.Argument) : [
        ('type', 'datatype', translate_type_name), ],
    (franca.Enumeration,       ifex.Enumeration) : [
        Preparation(reset_enumerator_counter),
        ('enumerators', 'options'),
        ('extends', Unsupported),

        # Franca only describes integer-based Enumerations but IFEX can use any type.
        # In the translation we hard-code the enumeration datatype to be int32, which ought to
        # normally work.
        (Constant('int32'), 'datatype')
        ],
    (franca.Enumerator,        ifex.Option) : [
        ('value', 'value', translate_enumerator_value)
        ],
    (franca.TypeCollection,    ifex.Namespace) : [
        # FIXME - these translations are valid also for Interfaces -> move to global
        ('arrays', 'typedefs'),
        ('maps', 'typedefs'),
        ('enumerations', 'enumerations'),
        ('structs', 'structs'),
        ('unions', None),  # TODO - use the variant type on IFEX side, need to check its implementation first
        ],
    (franca.Struct,            ifex.Struct) : [
        ('fields', 'members')
        ],
    (franca.StructField,       ifex.Member) : [] ,
    (franca.Array,             ifex.Typedef) : [],
    (franca.Typedef,           ifex.Typedef) : [],
    (franca.Map,               ifex.Typedef) : [
        ('key_type', None, map_keytype),
        ('value_type', None, map_valuetype),
        (assemble_map_type, 'datatype')
        ],
    (franca.Attribute,         ifex.Property) : [],
    (franca.Import,            ifex.Include) : [],
}

# --- Map fundamental/built-in types ---

type_translation = {
    franca.Boolean : "boolean",
    franca.ByteBuffer : "uint8[]",
    franca.Double : "double",
    franca.Float : "float",
    franca.Int8 : "int8",
    franca.Int16 : "int16",
    franca.Int16 : "int16",
    franca.Int32 : "int32",
    franca.Int64 : "int64",
    franca.String : "string",
    franca.UInt8 : "uint8",
    franca.UInt16 : "uint16",
    franca.UInt32 : "uint32",
    franca.UInt64 : "uint64",
    franca.ComplexType : "opaque", # FIXME this is actually a struct reference?
    franca.Map : "opaque", # FIXME maps shall be supported
}

# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------

def translate_type(t):

    # Special case: For references to complex types we want to refer to the original type name, since IFEX supports
    # named type definitions as well.  The type ought to be translated into a named typedef (or enum or struct, etc.) in
    # the IFEX representation also.  We don't need to de-reference it once more and end up with the inner definition of
    # the typedef, since IFEX supports named type definitions as well -> so don't recurse to figure out the inner type.
    if type(t) is franca.Reference and type(t.reference) in [franca.Array, franca.Struct, franca.Enumeration,
                                                             franca.Typedef, franca.Map]:
        return t.reference.name

    # Other references in a Franca AST are just some level of indirection -> Recurse on the actual type.
    # TODO: Check if this case still happens, considering previous lines?
    if type(t) is franca.Reference:
        return translate_type(t.reference)

    # This case can happen for arrays for plain-types that are defined directly, without a named typedef.
    # -> Translate the array's inner simple type, and add array to it.
    if type(t) is franca.Array:
        return translate_type(t.type) + '[]'

    # TODO This case is now probably redundant but let's come back to the comment about how to use qualified names
    if type(t) is franca.Enumeration:
        return t.name # FIXME use qualified name <InterfaceName>_<EnumerationName>, or change in the other place

    # Plain type -> use lookup table and if that fails return the original for now
    t2 = type_translation.get(type(t))
    return t2 if t2 is not None else t


# Rename fidl to ifex, for imports
def ifex_import_ref_from_fidl(fidl_file):
    return re.sub('.fidl$', '.ifex', fidl_file)


# Calling the pyfranca parser to build the Franca AST
def parse_franca(fidl_file):
    processor = pyfranca.Processor()
    return processor.import_file(fidl_file)  # This returns the top level package


# --- Script entry point ---

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(__file__)} <filename>")
        sys.exit(1)

    # Add the type-checking constructor mixin
    # FIXME Add this back later for strict checking
    #add_constructors_to_ifex_ast_model()

    try:
        # Parse franca input and create franca AST (top node is the Package definition)
        franca_package = parse_franca(sys.argv[1])

        # Convert Franca AST to IFEX AST
        ifex_ast = m2m.transform(franca_to_ifex_mapping, franca_package)
        final_ast = ifex.AST(namespaces = [ifex_ast])

        # Output as YAML
        print(ifex_ast_as_yaml(final_ast))

    except FileNotFoundError:
        log("ERROR: File not found")
    except Exception as e:
        raise(e)
        log("ERROR: An unexpected error occurred: {}".format(e))
