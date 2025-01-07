# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project

from models.ifex.ifex_ast_construction import add_constructors_to_ifex_ast_model, ifex_ast_as_yaml
from other.protobuf.protobuf_lark import create_proto_ast
import models.ifex.ifex_ast as ifex
import other.protobuf.protobuf_ast as pb
import os
import sys

# NOTE: The following node types / features are not processed at
# the moment:
#   - Reserved and Range
#   - OneOf
#   - MapField
#   - Import
#   - "stream" modifier for types
#   - options

# --- Fundamental types ---
type_translation = {
   "bool"     : "boolean",
   "bytes"    : "uint8[]",
   "double"   : "double",
   "fixed32"  : "uint32",
   "fixed64"  : "uint64",
   "float"    : "float",
   "int32"    : "int32",
   "int64"    : "int64",
   "sfixed32" : "int32",
   "sfixed64" : "int64",
   "sint32"   : "int32",
   "sint64"   : "int64",
   "string"   : "string",
   "uint32"   : "uint32",
   "uint64"   : "uint64"
}

def translate_type(t):
    t2 = type_translation.get(t)
    return t2 if t2 is not None else t

# --- Partial tree conversion functions ---

# NOTE: The conventional python naming convention for methods is
# deliberately broken here by using Capitalized names.  This is to
# make the AST node type names stand out.  This helps understanding
# if you're familiar with the AST type names of Protobuf and IFEX.

# Protobuf Messages are defined as IFEX Struct data types.  This conversion is
# applied for both outer and inner (nested) message types.
def Fields_to_Members(proto_fields):
    return [ifex.Member(f.name, translate_type(f.datatype)) for f in proto_fields]

def Messages_to_Members(proto_messages):
    if proto_messages == None:
        return []
    else:
        # Nested messages are treated as members of the parent message (struct):
        return [ifex.Member(m.name+"_", m.name) for m in proto_messages]

def Messages_to_Structs(proto_messages):
    if proto_messages == None:
        return []
    else:
        retval = [ifex.Struct(name = m.name,
                              members = Fields_to_Members(m.fields) + Messages_to_Members(m.messages))
                  for m in proto_messages if m is not None]

        # Recurse for potential nested Message-in-Message definitions:
        for m in proto_messages:
            retval += Messages_to_Structs(m.messages)
        return retval

def Fields_to_Options(proto_fields):
    return [ifex.Option(name = f.name,
                        value = int(f.value)) for f in proto_fields]

def Enums_to_Enumerations(proto_enums):
    return [ifex.Enumeration(name = e.name,
                             datatype = 'int32',
                             options = Fields_to_Options(e.fields)) for e in proto_enums]

def Enumerations_in_Messages(proto_messages):
    enums = [] # Flat list of enums - all we can find inside messages
    for m in proto_messages:
        enums += [ifex.Enumeration(name = m.name+"_"+e.name,
                                   datatype = 'int32',
                                   options = Fields_to_Options(e.fields)) for e in m.enums]
    return enums


def RPCs_to_Methods(proto_rpcs):
    return [ifex.Method(name = r.name,
                        input = [ifex.Argument(name = "in", 
                                               datatype = translate_type(r.input))],
                        returns = [ifex.Argument("_", r.returns)]) for r in proto_rpcs]

def Service_to_Interface(proto_service):
    return ifex.Interface(name = proto_service.name,
                          methods = RPCs_to_Methods(proto_service.rpcs))


# --- MAIN conversion function ---

def proto_to_ifex(node):
    ns = ifex.Namespace(name = node.package or '_',
                        structs = Messages_to_Structs(node.messages),
                        enumerations = Enums_to_Enumerations(node.enums) + Enumerations_in_Messages(node.messages))

    # For now, only one service per conversion is supported
    if len(node.services) > 1:
        print("UNSUPPORTED: multiple services -> multiple interfaces")
    if len(node.services) == 1:
        ns.interface = Service_to_Interface(node.services[0])

    return ifex.AST(namespaces = [ns])


def proto_ast_from_input(protofile):
    # Parse protobuf input and create Protobuf AST
    thisdir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return create_proto_ast(grammar_file = os.path.join(thisdir, 'protobuf.grammar'),
                                 proto_file = protofile)

# --- Script entry point ---

if __name__ == '__main__':

    # Add the type-checking constructor mixin
    add_constructors_to_ifex_ast_model()

    # Parse protobuf input and create Protobuf AST
    proto_ast = proto_ast_from_input(sys.argv[1])

    # Add the type-checking constructor mixin
    add_constructors_to_ifex_ast_model()

    # Convert Protobuf AST  to IFEX AST
    ifex_ast = proto_to_ifex(proto_ast)

    # Output as YAML
    print(ifex_ast_as_yaml(ifex_ast))
