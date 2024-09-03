# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

from collections import OrderedDict
from dataclasses import dataclass
import os
import re
import sys

# Have to define some paths to make this work (should be rearranged, ideally)
mydir = os.path.dirname(__file__)
for p in ['pyfranca', 'pyfranca/pyfranca']:
    if p not in sys.path:
        sys.path.append(os.path.join(mydir,p))

from ifex.model.ifex_ast_construction import add_constructors_to_ifex_ast_model, ifex_ast_as_yaml
import ifex.model.ifex_ast as ifex
import other.franca.pyfranca.pyfranca as pyfranca
import pyfranca.ast as franca


def array_type_name(francaitem):
    return translate_type_name(francaitem) + '[]'  # Unbounded arrays for now

def translate_type_name(francaitem):
    return translate_type(francaitem)

def concat_comments(list):
    return "\n".join(list)

# If enumerator values are not given, we must use auto-generated values.
# IFEX model requires all enumerators to be given values.
enum_count = -1
def reset_enumerator_counter(_ignored):
    print("***Resetting enum counter")
    global enum_count
    enum_count = -1

def translate_enumerator_value(franca_int_value):
    if franca_int_value is None:
        global enum_count
        enum_count = enum_count + 1
        return enum_count
    # otherwise, type *should* be of IntegerValue class type, which has a "value" member
    return franca_int_value.value

def translate_integer_constant(franca_int_value):
    return franca_int_value.value

# -----------------------------------------------------------------------------
# Translation Table
# -----------------------------------------------------------------------------
# The classes help in our table definition by defining a small DSL (Domain Specific Language)
# that aids us in expressing the translation table with things like "List Of" a
# certain type.  Some other ideas such as [SomeClass] to represent array (list) of SomeClass
# doesn't work because the table is a dict and arrays are not hashable.
# Similarly list(SomeClass) -> a type is not hashable.

@dataclass(frozen=True)
class ListOf:
    itemtype: type

# Map to Unsupported to make a node type unsupported
@dataclass(frozen=True)
class Unsupported:
    pass

# To insert the same value for all translations
@dataclass(frozen=True)
class Constant:
    value: int # Temporary, might be reassigned another type

# To wrap a function that will be called at this stage in the attribute mapping
@dataclass(frozen=True)
class Initialize:
    func: callable
    pass

# Translation definition
#
# - The data structure (table) describes the mapping from the types (classes) of the input AST to the output AST
# - Every type that is found in the input AST *should* have a mapping.  There is not yet perfect error
#   reporting if something is missing, but it might be improved.
# - For each class, the equivalent member variable that need to be mapped is listed.
# - Member variable mappings are optional because any variable with Equal Name on each object
#   will be copied automatically (with possible transformation, *if* the input data is listed as a
#   complex type).
# - Each attribute mapping can also optionally state the name of a transformation function (or lambda)
#   If no function is stated, the value will be mapped directly.  Mapping means to follow the transformation
#   rules of the type-mapping table *if* the value is an instance of an AST class, and in other
#   cases simly copy the value as it is (typically a string, integer, etc.)
# - In addition, it is possible to define global name-translations for attributes that are
#   equivalent but have different name in the two AST class families.
# - To *ignore* an attribute, map it to the None value.

franca_to_ifex_mapping = {

        # Attributes with identical name are normally automatically mapped.  If attributes have different names we can
        # avoid repeated mapping definitions by still defining them as equivalent in the global_attribute_map.
        # Attributes defined here ill be mapped in *all* classes.  Note: To ignore an attribute, map it to None!

        # Attribute name mapping for all
        'global_attribute_map':  {
            # Franca-name   :  IFEX-name
            'comments' : 'description', # FIXME allow transform also here, e.g. concat comments
            'extends' : None,  # TODO
            'flags' : None
            },

        # Here follows Type (class) mappings with optional local attribute mappings
        # (FROM-class on the left, TO-class on the right)
        'type_map': {
            (franca.Interface,         ifex.Interface) : [],
            (franca.Package,           ifex.Namespace) : [
                # TEMPORARY: Translates only the first interface
                ('interfaces', 'interface', lambda x: x[0]),
                ('typecollections', 'namespaces') ],
            (franca.Method,            ifex.Method) : [
                ('in_args', 'input'),
                ('out_args', 'output'),
                ('namespace', None) ],
            (franca.Argument,          ifex.Argument) : [
                ('type', 'datatype', translate_type_name), ],
            (franca.Enumeration,       ifex.Enumeration) : [
                (Initialize(reset_enumerator_counter), None),
                ('enumerators', 'options'),
                ('extends', Unsupported),

                # Note: Franca only knows integer-based Enumerations so we hard-code the enumeration datatype to
                # always be int32 in the IFEX representation
                (Constant('int32'), 'datatype')
                ],
            (franca.Enumerator,        ifex.Option) : [
                ('value', 'value', translate_enumerator_value)
                ],
            (franca.TypeCollection,    ifex.Namespace) : [
                ('structs', 'structs'),
                ('unions', None),  # TODO - implement theVariant type on IFEX side
                ('arrays', 'typedefs'),
                ('typedefs', 'typedefs')
                ],
            (franca.Struct,            ifex.Struct) : [
                ('fields', 'members')
                ],
            (franca.StructField,       ifex.Member) : [
                ('type', 'datatype', translate_type_name)
                ] ,
            (franca.Array,             ifex.Typedef) : [
                ('type', 'datatype', array_type_name)
                ],
            (franca.Attribute,         ifex.Property) : [],
            (franca.Import,            ifex.Include) : [],
            # TODO: More mapping to do, much is not yet defined here
            (franca.Package,           ifex.Enumeration) : [],
            (franca.Package,           ifex.Struct) : [],
            }
        }

# Reminders of cases to be handled from previous implementation approach:
# Structs_in_TypeCollection(franca_typecollection):
# Structs_in_Interface(franca_interface):
# Structs_in_Package(franca_package):
# Enumerator_Value(v):
# Enumerators_to_Options(enumerators, enumeration_name):
# Enumerations_in_Interface(franca_interface):
# Enumerations_in_Typecollection(franca_typecollection):
# Enumerations_in_Package(franca_package):
# Arguments_to_Arguments(franca_arguments):
# Methods_to_Methods(franca_methods):
# Attributes_to_Properties(franca_attributes):
# Typedefs_from_TypeCollection(franca_typecollection):
# Typedefs_from_TypeCollections(franca_typecollections):
# Imports_to_Includes(franca_imports):
# translate_type(t):
# flatmap(function, input_array):
# combined_name(parent, item):
# getValue(intype, outtype):

# Concepts to be covered (from francatypes User Guide 0.12.0.1)
# 5 francatypes IDL Reference ......................................... 27
# 5.1 Data types 27
# 5.1.1 Primitivetypes ....................................................27
#    OK -> covered in type_translation
# 5.1.2 Integerwithoptionalrange ............................................29
#    TODO: -> Equivalent concept in IFEX - but not yet supported in translator
# 5.1.3 Arrays ..........................................................29
#    TODO: -> To be tested/evaluated
# 5.1.4 Enumerations .....................................................30
#    OK (Supported in translator)
# 5.1.5 Structures .......................................................31
#    TODO: -> To be tested/evaluated
# 5.1.6 Unions(akavariants)................................................32
#    TODO: -> Equivalent concept in IFEX (variant) - but not yet supported in translator
# 5.1.7 Maps(akadictionaries) ..............................................33
#    TODO: -> Equivalent concept in IFEX (map) - but not yet supported in translator
# 5.1.8 Typedefinitions(akaaliases) ..........................................33
#    OK (Supported in translator)
# 5.2 Constant definitions 33
# 5.1.4 Enumerations .....................................................30
#    OK (Supported in translator)
# 5.2.1 Primitiveconstants .................................................34
#    TODO: -> To be tested/evaluated
# 5.2.2 Complexconstants .................................................34
#    TODO: -> To be tested/evaluated
# 5.3 Expressions 35
# 5.3.1 Typesystem ......................................................35
# 5.3.2 Constantvalues....................................................36
# 5.3.3 Comparisonoperators ...............................................36
# 5.3.4 Arithmeticoperations ...............................................36
# 5.3.5 Booleanoperations .................................................36
#    Expressions NOT SUPPORTED - Not formally defined in current IFEX spec
#    version. Their use seem not very clear (it seems also to be an unfinished
#    area also in francatypes specification.
# 5.4 TypeCollection definition 36
#    OK Supported in translator
# 5.5 Interface definition 37
# 5.5.1 Basicinterfacedefinition .............................................37
#    OK Supported in translator
# 5.5.2 Attributes........................................................38
#    OK Supported in translator (IFEX:Property)
# 5.5.3 Methods.........................................................40
#    OK Supported in translator
# 5.5.4 Broadcasts .......................................................44
#    OK Supported in translator (IFEX:Event)
#    TODO: -> To be tested/evaluated
#    (In IFEX we would rather
# 5.5.5 Interfacesmanaginginterfaces .........................................45
#    WIP: Exact translation is being evaluated. Basically it would add a
#    namespace to the "inner" definitions
# 5.6 Contracts 45
#    Contracts/PSM enforcement is not part of IFEX specification or project.
#    This is a potential extension, or simply use the francatypes IDL development
#    environment if this feature is desired.
# 5.7 Comments 48
# 5.7.1 Unstructuredcomments ..............................................48
#    TODO: -> Equivalent concept in IFEX - but not yet supported in translator
# 5.7.2 Structuredcomments................................................48
#    TODO: -> Equivalent concept in IFEX - but not yet supported in translator

#  Part Two
#
# 5.8 Fully qualified names, packages, and multiple files 48
# 5.8.1 Fullyqualifiednames ................................................48
# 5.8.2 Packagedeclarations ................................................48
# 5.8.3 Importsandnamespaceresolution .......................................50
# 6 francatypes Deployment Models .................................... 51
#    -> Equivalent concept in IFEX - but not yet supported in translator
#    Every deployment model is bespoke, and therefore developing translations
#    for them, must also be on a case-by-case basis.
#    Out of scope here.

# TODO: In the following table it is possible to list additional functions that are required but
# cannot be covered by the one-to-one object mapping above.  A typical example is to recursively
# loop over a major container, *and* its children containers create a flat list of items.
# Non-obvious mappings can be handled by processing the AST several times.
# Example: if in the input AST has typedefs defined on the global scope, as well as inside of a
# namespace/interface, but in the output AST we want them all collected on a global scope, then the
# direct mapping between AST objects does not apply well since that only creates a result that is
# analogous to the structure of the input AST.
ast_translation = {

}

# --- Fundamental types ---

type_translation = {
    franca.Boolean : "boolean",
    franca.ByteBuffer : "uint8[]",
    franca.ComplexType : "opaque", # FIXME this is a struct reference,
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
}

# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------

def is_builtin(x):
    return x.__class__.__module__ == 'builtins'

# is_composite_object: This is really supposed to check if the instance is one of the AST classes or possibly it could
# check if it is a class defined in the mapping table.  For now, however, this simple checks for NOT "builtin" works.
def is_composite_object(mapping_table, x):
    # Alternative: Check mapping_table
    return not is_builtin(x)

# FIXME: Unused, but could be used for error checking
def has_mapping(mapping_table, x):
    return mapping_table['type_map'].get(x.__class__) is not None

def translate_type(t):
    if type(t) is franca.Enumeration:
        return t.name # FIXME use qualified name <InterfaceName>_<EnumerationName>, or change in the other place
    if type(t) is franca.Reference:
        return t.name
    if type(t) is franca.Array:
        # FIXME is size of array defined in FRANCA?
        converted_type = translate_type(t.type)
        converted_type = converted_type + '[]'
        return converted_type
    else:
        t2 = type_translation.get(type(t))
        return t2 if t2 is not None else t

# Rename fidl to ifex, for imports
def ifex_import_ref_from_fidl(fidl_file):
    return re.sub('.fidl$', '.ifex', fidl_file)

# flatmap: Call function for each item in input_array, and flatten the result
# into one array. The passed function is expected to return an array for each call.
def flatmap(function, input_array):
    return [y for x in input_array for y in function(x)]

def combined_name(parent, item):
    return parent + "_" + item

# This function helps when we have multiple mappings with the same target attribute.
# We don't want to overwrite and destroy the previous value with a new one.
def set_attr(attrs_dict, attr_key, attr_value):
    if attr_key in attrs_dict:
        value = attrs_dict[attr_key]

        # If it's a list, we can add to it instead of overwriting:
        if isinstance(value, list):
            value.append(attr_value)
            attrs_dict[attr_key] = value
            return
        else:
            log("""ERR: Attribute {attr_key} already has a scalar (non-list) value.  Check for multiple translations
                  mapping to this one.  We should not overwrite it, and since it is not a list type, we can't append.""")
            log("=>  New value is ignored!")
            return

    attrs_dict[attr_key] = attr_value

# TODO - add better logging
def log(x):
    print(x)

# ----------------------------------------------------------------------------
# --- MAIN conversion function ---
# ----------------------------------------------------------------------------

def translate_object(mapping_table, input_obj):

    # Builtin types (str, int, ...) are assumed to be just values to copy without any change
    if is_builtin(input_obj):
        return input_obj

    # Find a translation rule in the metadata
    # Using linear-search in mapping table until we find something matching input object:
    for (from_class, to_class), mappings in mapping_table['type_map'].items():

        # Does this transformation rule match input object?
        if from_class == input_obj.__class__:
            #log(f"INFO: Type mapping found: {from_class=} -> {to_class=}")

            # Comment: Here we might create an empty instance of the class and fill it with values using setattr(), but
            # that won't work since the redesign using dataclasses.  The AST classes now have a default constructor that
            # requires all mandatory fields to be specified when an instance is created.  Therefore we are forced to
            # follow this approach:  Gather all attributes in a dict and pass it into the constructor at the end using
            # python's dict to keyword-arguments capability.

            attrs = {}

            # To remember the args we have converted
            done_attrs = set()

            # First loop:  Perform the explicitly defined attribute conversions
            # for those that are specified in the translation table.

            for input_attr, output_attr, *transform in mappings:

                transform = transform[0] if transform else lambda x: x

                # A init/prep function was defined.  The "output_attr" is here misleadingly named.
                # It is (optionally) used to define a parameter to be passed to the function
                if isinstance(input_attr, Initialize):
                    input_attr.func(output_attr)
                    continue
                #log(f"INFO: Attribute mapping found: {input_attr=} -> {output_attr=} with {transform=}")
                if output_attr is None:
                    #log(f"INFO: Ignoring {input_attr=} for {type(input_obj)} because it was mapped to None")
                    continue

                if output_attr is Unsupported:
                    if value is not None:
                        log(f"ERR: Attribute {input_attr} has a value in {type(input_obj)}:{input_obj.name} but the feature ({input_attr}) is unsupported")
                        #print(f"^^^  {value=}")

                    # Regardless if there was a value or not: skip this Unsupported attribute
                    #log(f"INFO: Skipping {input_attr=} {output_attr=}")
                    continue

                if isinstance(input_attr, Constant):
                    value = input_attr.value
                else:
                    value = getattr(input_obj, input_attr)

                if isinstance(value, OrderedDict):
                    newval  = [translate_object(mapping_table, item) for name, item in value.items()]
                    set_attr(attrs, output_attr, newval)
                elif isinstance(value, list):  # (Unexpected)
                    newval = [translate_object(mapping_table, item) for item in value]
                    set_attr(attrs, output_attr, newval)
                else:
                    set_attr(attrs, output_attr, transform(value))

                # Mark this attribute as done
                done_attrs.add(input_attr)

            # Second loop: Any attributes that have the _same name_ in the input and output classes are assumed to be
            # the mappable to eachother.  They do not need to be listed in the translation table unless they need a
            # custom transformation.  Here we find all matching names here and map them (with recursive transformation,
            # as needed), but of course skip all attributes that have been handled already (done_attrs)

            global_attribute_map = mapping_table['global_attribute_map']
            for attr, value in vars(input_obj).items():

                # Skip already done items
                if attr in done_attrs:
                    continue

                # Translate attribute name according to global rules, if that is defined.
                if attr in global_attribute_map:
                    attr = global_attribute_map.get(attr)

                # Check if to_class has this attribute with the same name
                # => Things get a bit ugly here because of the use of dataclasses as explained above
                if to_class.__dataclass_fields__.__contains__(attr):
                    #log(f"INFO: Global or same-name auto-conversion for {attr=} from {from_class.__name__} to {to_class.__name__}\n")
                    if isinstance(value, OrderedDict):
                        # A dict of name/value pairs -> map it to a list in the output but iterate over the actual items, not the keys
                        value = [translate_object(mapping_table, item[1]) for item in value.items()]

                    elif isinstance(value, list):
                        # List value -> translate each contained object, and make a list of the results.
                        value = [translate_object(mapping_table, item) for item in value]

                    elif is_composite_object(mapping_table, value):
                        # Single, complex value -> recurse to translate the single type
                        value = translate_object(mapping_table, value)

                    else:
                        # Single, plain value -> just copy as it is
                        pass

                    # Store the value we determined for this attribute in the to_class object
                    set_attr(attrs, attr, value)

                # No match found in to_class
                elif attr is not None:
                    log(f"WARN: Attribute '{attr}' from Franca:{input_obj.__class__.__name__} was not used in IFEX:{to_class.__name__}")

            # Instantiate to_class object, and return
            #log(f"DEBUG: Creating and returning object of type {to_class} with {attrs=}")
            return to_class(**attrs)

    raise ValueError(f"No translation rule found for object {input_obj} of class {input_obj.__class__.__name__}")


def franca_ast_from_input(fidl_file):
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
        franca_ast = franca_ast_from_input(sys.argv[1])

        # Convert Protobuf AST  to IFEX AST
        ifex_ast = translate_object(franca_to_ifex_mapping, franca_ast)

        # Output as YAML
        print(ifex_ast_as_yaml(ifex_ast))

    except FileNotFoundError:
        log("ERROR: File not found")
    except Exception as e:
        raise(e)
        log("ERROR: An unexpected error occurred: {}".format(e))

