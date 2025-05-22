from models.common.ast_utils import ast_as_yaml, find_all_by_type
from models.common.type_checking_constructor_mixin import add_constructors_to_ast_model
from models.protobuf.protobuf_lark import get_ast_from_proto_file
from transformers.rule_translator import Preparation, Constant, Unsupported, _log, Default
import models.ifex.ifex_ast as ifex
import models.protobuf.protobuf_ast as protobuf
import os
import re
import sys
import transformers.rule_translator as m2m

# -------------------------------------------------------------------
# Fundamental type-mapping table Protobuf/gRPC -> IFEX
# -------------------------------------------------------------------
type_translation = {
                  "double" : "double",
                  "float" : "float",
                  "int32" : "int32",
                  "int64" : "int64",
                  "uint32" : "uint32",
                  "uint64" : "uint64",
                  "sint32" : "int32",
                  "sint64" : "int64",
                  "fixed32" : "uint32",
                  "fixed64" : "uint64",
                  "sfixed32" : "int32",
                  "sfixed64" : "int64",
                  "bool" : "boolean",
                  "string" : "string",
                  "bytes" : "uint8[]",
                  }

# TODO? set, map, variant, opaque

# -------------------------------------------------------------------
# Helper functions for Protobuf->IFEX table translation
# -------------------------------------------------------------------

# Persistent global variable
package_name = ""

def translate_type_name(t):
    # FIXME - might need to handle arrays for repeated fields
    # Enumeration types might need qualified option names
    t2 = type_translation.get(t)
    return t2 if t2 is not None else t

def handle_options(option):
    #print(f"Ignored Option : {option} ")
    pass

def rpc_parameter_message_to_params(msgtype):
    # FIXME, this can be done better by expanding the message to individual args
    return [ifex.Argument(name = '_', datatype = translate_type_name(msgtype))]

def store_package_name(p):
    global package_name
    package_name = p

def get_package_name():
    global package_name
    return package_name

def pick_first(array):
    if len(array) > 1:
        print(f"WARNING: only one object of this type is supported: {type(array[0])}")
    return array[0]

mapname = "UNDEF"
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

# -------------------------------------------------------------------
# The main translation table
# -------------------------------------------------------------------

def get_description(input_obj, output_attributes_so_far):
    return "Default text: This is " + output_attributes_so_far.get('name')

# In case package is undefined, the Namespace will get a default name because a name is required
def set_default_package_name(obj):
    if obj is None:
        return "_"
    else:
        return obj

mapping_table = {

   # (Proto node type, IFEX node type)
   # [ ... attribute mappings ...]

    Default : [
        ('datatype', 'datatype', translate_type_name),
        ('name', 'name'),
        #(Constant("This is description"), 'description'),
        (get_description, 'description'),
       ],

    (protobuf.Proto, ifex.Namespace): [
        #('imports', 'includes'),
        ('package', 'name', set_default_package_name),
        ('messages', 'structs'),
        ('services', 'interface', pick_first),
        ('options', None, handle_options),
        # We could map 'enums' to 'enumerations' here - they belong in the
        # Namespace, but it is not included here since we collect up *all*
        # enums later in the code.
       ],
    (protobuf.Service, ifex.Interface): [
        ('rpcs', 'methods'),
        ('options', None, handle_options),
        ],

    (protobuf.RPC, ifex.Method): [
        ('input', 'input', rpc_parameter_message_to_params),
        ('returns', 'returns', rpc_parameter_message_to_params),
        ('options', None, handle_options),
        ],

    # TODO, go through any missing types
    
    (protobuf.Enumeration, ifex.Enumeration): [
        ('fields', 'options'),
        ('options', None, handle_options),
        ('reservations', Unsupported),
        (Constant("int32"), 'datatype')
        ],

    (protobuf.EnumField, ifex.Option): [
        ('options', None, handle_options),
        ('value', 'value')
        ],

    (protobuf.Message, ifex.Struct): [
        ('fields', 'members'),
        ('options', None, handle_options),
        # message-embedded enums are handled separately since they don't fit into the Struct concept
        ('messages', Unsupported),
        ('oneofs', Unsupported),
        ('reservations', Unsupported)
        ],

    (protobuf.Field, ifex.Member): [
        ('repeated', Unsupported),
        ('optional', Unsupported),
        ('options', None, handle_options),
        ],

    (protobuf.Import, ifex.Include): [
        ('path', 'file'),
    ],

    (protobuf.Option, ifex.Include): [
        ('name', None, handle_options),
    ],

    # TODO, go through any missing types
}

# ----------------------------------------------------------------------------
# Old functions that may need conversion to new approach
# ----------------------------------------------------------------------------
def Messages_to_Members(proto_messages):
    if proto_messages == None:
        return []
    else:
        # Nested messages are treated as members of the parent message (struct):
        # Prefix name and add them to the members of the parent message struct
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


# -------------------------------------------------------------------
# MAIN conversion function
# -------------------------------------------------------------------

# Convert Protobuf AST to IFEX AST
def proto_to_ifex(proto):

    if len(proto.services) > 1:
        print("UNSUPPORTED: multiple services -> multiple interfaces")

    # Note that table mapping creates a ifex.Namespace node as root
    top_namespace = m2m.transform(mapping_table, proto)

    # Collect enumerations separately, because they don't match
    # the table-based setup. Then convert them to IFEX enums.

    proto_enums = find_all_by_type(proto, protobuf.Enumeration)

    # NOTE: If enumerations are defined inside a message
    # (protobuf IDL is a silly language that enables using a
    # "message" as a namespace)
    # ... then we could prepend the message name to the
    # enumeration name to make it unique in case that this
    # namespace scope matters. For now, we'll keep it simple and
    # assume enumeration names are unique.  Fix this later if it
    # is necessary.

    enum_list = [m2m.transform(mapping_table, e) for e in proto_enums]

    # FIXME Where to place? For now, let's assume they belong to the top level protobuf package, which has become the toplevel IFEX namespace
    top_namespace.enumerations = enum_list
    return top_namespace


# --- Script entry point ---

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(__file__)} <filename>")
        sys.exit(1)

    # Add the type-checking constructor mixin
    add_constructors_to_ast_model(ifex)

    try:
        # Parse protobuf input and create Protobuf AST
        proto_ast = get_ast_from_proto_file(sys.argv[1])

        # Conversion table will output a Namespace - create the AST around it
        # FIXME: Do the imports
        ifex_ast = ifex.AST(namespaces = [proto_to_ifex(proto_ast)])

        # Output as YAML
        print(ast_as_yaml(ifex_ast))

    except FileNotFoundError:
        _log("ERROR", "File not found")

    except Exception as e:
        _log("ERROR", f"An unexpected error occurred: {e}")
        raise(e)
