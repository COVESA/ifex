# SPDX-FileCopyrightText: Copyright (c) 2025 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

from models.common.ast_utils import find_all_by_type
from models.common.type_checking_constructor_mixin import add_constructors_to_ast_model
from models.ifex.ifex_parser import get_ast_from_yaml_file
from transformers.rule_translator import Constant, Unsupported, _log, Default
import inflection
import models.ifex.ifex_ast as ifex
import models.protobuf.protobuf_ast as protobuf
import output_filters.protobuf.grpc_generator as grpc_generator
import transformers.rule_translator as m2m

# -------------------------------------------------------------------
# Type-mapping table for primitive types: IFEX -> Protobuf/gRPC
# -------------------------------------------------------------------
type_translation = {
        "double" : "double",
        "float" : "float",
        "int32" : "int32",
        "int64" : "int64",
        "uint32" : "uint32",
        "uint64" : "uint64",
        "int32" : "sint32",
        "int64" : "sint64",
        "uint32" : "fixed32",
        "uint64" : "fixed64",
        "int32" : "sfixed32",
        "int64" : "sfixed64",
        "boolean" : "bool",
        "string" : "string",
        "uint8[]" : "bytes",
        }

# -------------------------------------------------------------------
# Common Helper functions
# -------------------------------------------------------------------
# Convert name to the target language style preference
def target_style(s):
    return inflection.camelize(s)


# -------------------------------------------------------------------
# Other helper functions
# -------------------------------------------------------------------
# UNUSED/WIP
def map_name(x):
    global mapname
    map_name = x
    return

keytype = "UNDEF"
def map_keytype(x):
    global keytype
    keytype = translate_type_name(x)

valuetype = "UNDEF"
def map_valuetype(x):
    global valuetype
    valuetype = translate_type_name(x)

def assemble_map_type(input_obj, output_obj):
    global valuetype, keytype
    return f"map<{keytype},{valuetype}>"

def concat_comments(list):
    return "\n".join(list)

def get_description(input_obj, output_attributes_so_far):
    return "Default text: This is " + output_attributes_so_far.get('name')

# -------------------------------------------------------------------
# Helper functions for table- translation
# -------------------------------------------------------------------

def translate_type_name(t):
    # FIXME - should handle arrays for repeated fields
    # Enumeration types might need qualified option names
    t2 = type_translation.get(t)
    return t2 if t2 is not None else t

def construct_response_name(s):
    return target_style(s+'Response')

def construct_request_name(s):
    return target_style(s+'Request')

def if_to_services(interface):
    res = m2m.transform(mapping_table, interface)
    # Protobuf model expects a *list* of services. We expect _one_ interface node to be specified (per namespace) in a
    # single generation instance - that is what defines the interface to generate.  But if processing an input model
    # combined from many input files, that may need to change.
    return [res]  # For now return as list, with one service only

def only_map_fields(x):
    return [protobuf.Field(x[0].name, x[0].datatype)]

def no_map_fields(x):
    return [protobuf.Field(x[0].name, x[0].datatype)]

# Define RPCs - it is easy since in gRPC they always have only one input (request) message, and only one return message
# The actual content of those messages are defined separately
def define_rpcs(methods):
    rpcs = None
    if methods is None:
        return None
    else:
        rpcs = []
        for m in methods:
            if m is not None: # FIXME check this
                rpcs.append(protobuf.RPC(name = target_style(m.name),
                                         input = construct_request_name(m.name),
                                         returns = construct_response_name(m.name)))
    return rpcs

# -------------------------------------------------------------------
# Main Translation Table
# -------------------------------------------------------------------
#
# Conversion strategy:
#
# There is not an obvious 1-1 translation of the structure itself --  for example some objects at one level of the input
# tree need to appear at a different tree-level in the output.
#
# The framework provides convenience functions to collect items of certain type, store in temporary variables.
# Let's do the main parts using a table-based translation, and then make additional translation passes, on
# details. We can use 'merge-tree' function to combine result, or insert them directly.
#
# Note: Typedefs are not supported in grpc/protobuf
# (except the workaround to encapsulate the type inside a named message)
# We should handle them by replacing with the target type instead.

# TODO set, map, variant?
# Support for variant type could be implemented in the primitive
# protobuf/gRPC world, maybe this way:  (Use the answer that defines optional
# fields in the message)
# https://stackoverflow.com/questions/6519533/how-to-implement-variant-in-protobuf

mapping_table = {

        Default : [
            ('datatype', 'datatype', translate_type_name),
            ('name', 'name'),
            ],

        (ifex.Namespace, protobuf.Proto): [
            #('imports', 'includes'),
            ('name', 'package'),
            ('structs', 'messages'),
            ('typedefs', 'messages'),
            ('interface', 'services', if_to_services),
            # Nested Namespaces - how?
            #('namespaces', 'services'),
        ],

        (ifex.Interface, protobuf.Service): [
            ('methods', 'rpcs', define_rpcs),
            ],

        # Method arguments are equivalent to fields in the message that defined as Request/Response of an RPC
        (ifex.Argument, protobuf.Field): [ ],

        # Method arguments are equivalent to fields in the message that defined as Request/Response of an RPC
        (ifex.Method, protobuf.RPC): [ ],

        (ifex.Enumeration, protobuf.Enumeration): [
            ('fields', 'options'),
            ('reservations', Unsupported),
            (Constant("int32"), 'datatype')
            ],

        (ifex.Option, protobuf.EnumField): [
            ('value', 'value')
            ],

        (ifex.Struct, protobuf.Message): [
            ('members', 'fields'),
            # TODO Handle variant types
            # 'datatypes' --> handle_variant_type()
            ],

        (ifex.Member, protobuf.Field): [
            ],

        (ifex.Include, protobuf.Import): [
            ('path', 'file'),
        ],

        # TODO, go through any missing types
}


# -------------------------------------------------------------------
# MAIN conversion function
# -------------------------------------------------------------------

# Convert Protobuf AST to IFEX AST
def ifex_to_proto(namespace):

    # Main translation done here, with mapping table
    proto = m2m.transform(mapping_table, namespace)

    # Still TODO: Typedef support
    # Note: Typedefs are not supported in grpc/protobuf
    # (except with the workaround to encapsulate the type in a message of course)
    # ... but in the conversion to protobuf, the typedefs could be replaced by their original type

    # Add now the Request and Response messages for each RPC.
    # (previous translation has only defined the RPC def which refers to Request/Response messages,
    # that we will now define)

    methods = find_all_by_type(namespace, ifex.Method)
    if proto.messages == None:
        proto.messages = []
    for m in methods:
        if m is not None:
            # Input args become Request message.  We can use the mapping_table to convert fields.
            fields = [m2m.transform(mapping_table, arg) for arg in m.input]
            proto.messages.append(protobuf.Message(name = construct_request_name(m.name), fields = fields))

            # Output and return args become Response message
            fields = [m2m.transform(mapping_table, arg) for arg in m.output] + \
                     [m2m.transform(mapping_table, arg) for arg in m.returns]
            proto.messages.append(protobuf.Message(name = construct_response_name(m.name), fields = fields))

    return proto

# --- Script entry point = Test/Dev Code ---

if __name__ == '__main__':
    import sys
    import os

    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(__file__)} <filename>")
        sys.exit(1)

    # Add the type-checking constructor mixin
    add_constructors_to_ast_model(protobuf)

    try:
        # Parse protobuf input and create Protobuf AST
        ifex_ast = get_ast_from_yaml_file(sys.argv[1])

        proto = ifex_to_proto(ifex_ast.namespaces[0])

        # Get template directory which is templates/ relative to this file location
        template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")

        # Print out the protobuf result
        #print(proto)

        print(grpc_generator.proto_to_text(proto))

    except FileNotFoundError:
        _log("ERROR", "File not found")

    except Exception as e:
        _log("ERROR", f"An unexpected error occurred: {e}")
        raise(e)
