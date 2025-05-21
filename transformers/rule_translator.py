# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

"""
## rule_translator.py

rule_translator implements a generic model-to-model translation function used to copy-and-transform values from one
hierarchical AST representation to another.  It is driven by an input data structure that describes the translation
rules to follow, and implemented by a generic function that can be used for many types of transformation.

## Translation definition

- The data structure (table) describes the mapping from the types (classes) of the input AST to the output AST
- Every type that is found in the input AST *should* have a mapping.  There is not yet perfect error
  reporting if something is missing, but it might be improved.
- For each class, the equivalent member variable that need to be mapped is listed.
- Member variable mappings are optional because any variable with Equal Name on each object
  will be copied automatically (with possible transformation, *if* the input data is listed as a
  complex type).
- Each attribute mapping can also optionally state the name of a transformation function (or lambda)
  If no function is stated, the value will be mapped directly.  Mapping means to follow the transformation
  rules of the type-mapping table *if* the value is an instance of an AST class, and in other
  cases simly copy the value as it is (typically a string, integer, etc.)
- In addition, it is possible to define global name-translations for attributes that are
  equivalent but have different name in the two AST class families.
- To *ignore* an attribute, map it to the None value.

See example table in rule_translator.py source for more information, or any of the implemented programs.

"""

from collections import OrderedDict
from dataclasses import dataclass
import os
import re
import sys


# -----------------------------------------------------------------------------
# Translation Table Helper-objects
# -----------------------------------------------------------------------------
#
# These classes help the table definition by defining something akin to a small DSL (Domain Specific Language) that aids
# us in expressing the translation table with things like "List Of" a certain type, or "Constant" when a given value is
# always supposed to be used, etc. Some ideas of representing the rules using python builtin primitives do not work.
# For example, using '[SomeClass]' to represent and array (list) of SomeClass is a valid statement in general, but
# does not work in our current translation table format because it is a key in a dict. Plain arrays are not a hashable
# value and therefore can't be used as a key. Similarly list(SomeClass) -> a type is not hashable.

# (Use frozen dataclasses to make them hashable. The attributes are given values at construction time only.)

# Map to Unsupported to make a node type unsupported
@dataclass(frozen=True)
class Unsupported:
    pass

# To insert the same value for all translations
@dataclass(frozen=True)
class Constant:
    const_value: int # Temporary, might be reassigned another type

# To wrap a function that will be called at this stage in the attribute mapping
@dataclass(frozen=True)
class Preparation:
    func: callable
    pass

# This class wraps the store_delegated_object function as a closure, binding the two input parameters node_type and
# attr_name when created.  Next when the Delegate operation is found, it will store the delegated object for later
# use.  Finally, during processing, the getattr_value function always checks first if there is a delegated object
# and the stored object to be processed under the predefined stated node type and attribute name.
class Delegate:
    def __init__(self, node_type, attr_name):
        _log("DEBUG", f"Instantiate Delegate: {node_type=}, {attr_name=}")
        self.delegate_to_this_node_type = node_type
        self.delegate_to_this_attr = attr_name
        # Closure captures the node_type and attr_name
        self.func = lambda input_obj, input_attr : \
            store_delegated_object(input_obj, input_attr, self.delegate_to_this_node_type, self.delegate_to_this_attr)

# -----------------------------------------------------------------------------
# Translation Table - Example, not used. The table be provided instead by the program
# that uses this module)
# -----------------------------------------------------------------------------

example = """
example_mapping = {

        # global_attribute_map: Attributes with identical name are normally automatically mapped.  If attributes have
        # different names we can avoid repeated mapping definitions by still defining them as equivalent in the
        # global_attribute_map.  Attributes defined here ill be mapped in *all* classes.  Note: To ignore an attribute,
        # map it to None!

        'global_attribute_map':  {
            # (Attribute in FROM-class on the left, attribute in TO-class on the right)
            'this' : 'that',
            'something_not_needed' : None
            },

        # type_map: Here follows Type (class) mappings with optional local attribute mappings
        'type_map': {
            (inmodule.ASTClass1, outmodule.MyASTClass) :
            # followed by array of attribute mapping

            # Here an array of tuples is used. (Format is subject to change)
            # (FROM-class on the left, TO-class on the right)
            # *optional* transformation function as third argument
            # Special case: Preparation(myfunc), which calls any function at that point in the list
            [
              ('thiss', 'thatt'),
              ('name', 'thename', capitalize_name_string),
              Preparation(pre_counter_init),
              ('zero_based_counter', 'one_based_counter', lambda x : x + 1),
              ('thing',  None)
             ]

            # Equally named types have no magic - it is still required to
            # define that they shall be transformed/copied over.
            (inmodule.AnotherType, outmodule.Anothertype), [
                # Use a Constant object to always set the same value in target attribute
                (Constant('int32'), 'datatype')
                ],
            # ListOf and other features are not yet implemented -> when the need arises
        }
}
"""

# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------

# TODO - add better logging
def _log_if(condition, level, string):
    if condition:
        _log(level, string)

def _log(entry_level, string):

    # Error is default if env-var is not specified
    output_level = os.getenv("IFEX_LOG_LEVEL", "ERROR") 

    order = ["DEBUG", "INFO", "WARN", "ERROR", "NONE"]
    if output_level in order and order.index(output_level) <= order.index(entry_level):
        print(f"{entry_level}: {string}")

def is_builtin(x):
    return x.__class__.__module__ == 'builtins'

# This function is used by the general translation to handle multiple mappings with the same target attribute.
# We don't want to overwrite and destroy the previous value with a new one, and if the target is a list
# then it is useful to be able to add to that list at multiple occasions -> append to it.
def set_attr(attrs_dict, attr_key, attr_value):
    if attr_key in attrs_dict:
        value = attrs_dict[attr_key]

        # If it's a list, we want to add to it instead of overwriting:
        if isinstance(value, list):
            # We don't have lists in lists, but it can happen that we get more than one list
            # Don't append empty (None) objects however
            if attr_value is not None:
                if isinstance(attr_value, list):
                    value = value + attr_value
                else:
                    value.append(attr_value)
                _log("DEBUG", f"Appending to list for {attr_key=}: amended list: {value}")
                attrs_dict[attr_key] = value
            return

        # If it's set to None by an earlier step -> just overwrite
        elif value is None:
            attrs_dict[attr_key] = attr_value
            return

        # If it's a non-list but already set to a value, this is an error.  Don't overwrite it.
        else:
            _log("ERROR", f"""Attribute {attr_key} already has a scalar (non-list) value.  Check for multiple translations
                  mapping to this one.  We should not overwrite it, and since it is not a list type, we can't append.""")
            _log("WARN", f"Target value {value} was ignored.")
            return

    # If it's a new assignment, go ahead
    attrs_dict[attr_key] = attr_value

# ----------------------------------------------------------------------------
# --- MAIN conversion function ---
# ----------------------------------------------------------------------------

# Here we use a helper function to allow one, two, or three values in the tuples
# of the mapping_table.
# With normal decomposition of a tuple, only the last can be optional, like this:
#     first, second, *maybe_more = (...tuple...)
# But the table also allows a single item like Preparation() so let's add some logic
# to avoid run-time error.
# This function always returns a full 4-value tuple, that can be processed in the
# main loop:
# Returns: (preparation_function, input_arg, output_arg, field_transform)

def eval_mapping(type_map_entry):
    if isinstance(type_map_entry, Preparation):
        # Return the function that is wrapped inside Preparation()
        return (type_map_entry.func, None, None, None)
    else:  # 3 or 4-value tuple is expected (field_transform is optional)
        input_arg, output_arg, *field_transform = type_map_entry
        # Unwrap array and use identity-function if no transformation required
        field_transform = field_transform[0] if field_transform else lambda _ : _

        # Returns: (preparation_function, input_arg, output_arg, field_transform)
        return (None, input_arg, output_arg, field_transform)


# Additional named helpers to make logic very visible.
# (We're at this time not concerned with performance hit of calling some extra functions)
def dataclass_has_field(_class, attr):
    return attr in _class.__dataclass_fields__

# The following two functions are mutually recursive (transform -> transform_value_common -> transform)
# but you can think of it primarily as the main function, transform(), calling itself as it
# descends down the tree of nodes/values that neeed converting.
# This _common function is here only to avoid repeated code for the type-specific handling
def transform_value_common(mapping_table, value, field_transform):

    # OrderedDict is used at least by Franca AST -> return a list of transformed items
    if isinstance(value, OrderedDict):
        _log("DEBUG", f"Value is OrderedDict! {value=}")
        if len(value.items()) == 0:
            name = ""
            try:
                name = value.name
            except:
                pass
            _log("DEBUG", f"Empty OrderedDict for {value=} {name=} {field_transform=}")
            value = []
        else:
            value  = field_transform([transform(mapping_table, item) for name, item in value.items()])

    # A list in input yields a list in output, transforming each item
    # (not used by Franca parser, but others might)
    elif isinstance(value, list):
        if len(value) == 0:
            _log("DEBUG", f"Empty list: {value=}")
            value = None
        else:
            _log("DEBUG", f"Non-empty list: {value=}")
            value = field_transform([transform(mapping_table, item) for item in value])

    # Plain attribute -> use transformation function if it was defined
    else:
        value = field_transform(value)

    return value

delegated_refs = {}

def store_delegated_object(input_obj, input_attr, delegate_to_this_node_type, delegate_to_this_attr):
    global delegated_refs

    _log("DEBUG", f"\n\n==============   store_delegated_object: {delegate_to_this_attr=} {delegate_to_this_node_type=}:")

    # Store under a tuple of type and attr name
    delegated_refs[(delegate_to_this_node_type, delegate_to_this_attr)] = getattr(input_obj, input_attr)

def clear_delegated_ref(input_type, input_attr):
    global delegated_refs
    _log("DEBUG", f"Clearing delegated_ref: {(input_type, input_attr)=} ")
    delegated_refs.pop((input_type, input_attr), None)

def get_delegated_ref(input_type, input_attr):
    global delegated_refs
    _log("DEBUG", f"Looking for {(input_type,input_attr)} in {delegated_refs=}")
    return delegated_refs.get((input_type,input_attr))

def getattr_value(input_obj, input_attr):
    input_type = type(input_obj)

    dv = get_delegated_ref(input_type, input_attr)
    if dv is not None:
        clear_delegated_ref(input_type, input_attr)
        _log("DEBUG", f"Returning delegated value for {(input_type, input_attr)=}: {dv=}")
        return dv
    else:
        return getattr(input_obj, input_attr)

def transform(mapping_table, input_obj):

    # Builtin types (str, int, ...) are assumed to be just values that shall be copied without any change
    if is_builtin(input_obj):
        return input_obj

    # Find a translation rule in the metadata
    for (from_class, to_class), mappings in mapping_table['type_map'].items():

        # Use linear-search in mapping table until we find something matching input object.
        # Since the translation table is reasonably short, it should be OK for now.
        if from_class != input_obj.__class__:
            continue

        # Continuing here with a matching mapping definition...
        _log("INFO", f"Type mapping found: {from_class=} -> {to_class=}")

        # Comment: Here we might create an empty instance of the class and fill it with values using setattr(), but
        # that won't work since the redesign using dataclasses.  The AST classes now have a default constructor that
        # requires all mandatory fields to be specified when an instance is created.  Therefore we are forced to
        # follow this approach:  Gather all attributes in a dict and pass it into the constructor at the end using
        # python's dict to keyword-arguments capability.

        attributes = {}

        # To remember the args we have converted
        done_attrs = set()

        # First loop: Perform explicitly defined attribute conversions listed in each entry

        for preparation_function, input_attr, output_attr, field_transform in [eval_mapping(m) for m in mappings]:
            _log("INFO", f"Attribute mapping found: {input_attr=} -> {output_attr=} with {field_transform=}")

            # TODO: It should be possible to let the preparation_function be a closure, with predefined parameters.
            # Also to be investigated:  Consider if it's better to go back to eval_mapping returning the
            # function-wrapper object (Preparation) and not just the function.

            # Call preparation function, if given.
            if preparation_function is not None:
                preparation_function()
                continue

            # In the case the rule is set to output_attr==None, then no output_attr is written.  But if field_transform
            # function is defined, the function is still called with the input_attr value.  Since output_attr was set to
            # None, there is no return value copied to any output_attr, but the function can manipulate and store the
            # input value for later use, for example another field_transform function called later.
            if output_attr is None:
                _log("DEBUG", f"{input_attr=} for {type(input_obj)} was mapped to None")
                field_transform(getattr_value(input_obj, input_attr))
                continue

            if output_attr is Unsupported:
                value = getattr_value(input_obj, input_attr)
                _log_if(bool(value) is not False, "ERROR", f"{type(input_obj)}:{input_obj.name} has an attribute for '{input_attr}' but that feature is unsupported. ({value=})")
                continue

            # If the input_attr is set to a function instead of an attribute name, then the result of calling the
            # function is copied to the output_attr.  Unlike the field_transform, this type of function gets no
            # input value.
            if callable(input_attr):
                set_attr(attributes, output_attr, input_attr()) # <- note that "input_attr" called as a function
                continue

            # If defined as a Constant object, copy the constant value to the output field
            if isinstance(input_attr, Constant):
                set_attr(attributes, output_attr, input_attr.const_value)
                continue

            # Delegate -> call the function that stores the value for later use
            if isinstance(output_attr, Delegate):
                output_attr.func(input_obj, input_attr)  # Wraps any function/closure, but probably: 
                continue

            # else: normal mapping input_attr to output_attr:
            # Get input value and copy it, after transforming as necessary
            set_attr(attributes, output_attr, transform_value_common(mapping_table, getattr_value(input_obj, input_attr),
                                                                     field_transform))

            # Mark this attribute as handled
            done_attrs.add(input_attr)


        # Second loop: Any attributes that have the _same name_ in the input and output classes are assumed to be
        # mappable to each other.  Thus, identical names do not need to be listed in the type-specific translation table
        # unless they need a custom transformation.  So here we can find all matching names and map them (with recursive
        # transformation, as needed), but we of course skip all attributes that have been handled already by a
        # type-specific rule (done_attrs).

        # In addition: global_attribute_map defines which attribute names shall be considered the same in all objects.

        global_attribute_map = mapping_table['global_attribute_map']

        # Checking all fields in input object, except fields that were handled and stored in done_attrs
        for attr, value in vars(input_obj).items():

            if attr in done_attrs:
                continue

            glob_transform = lambda _ : _  # Default is no-op

            # Translate attribute name according to global rules, if defined.
            # ... and extract the transform function if it's given
            if attr in global_attribute_map:
                attr = global_attribute_map.get(attr)
                if isinstance(attr, tuple):
                    # Tuple with transformation function
                    glob_transform = attr[1]
                    attr = attr[0]

            if dataclass_has_field(to_class, attr):
                _log("DEBUG", f"Performing global or same-name auto-conversion for {attr=} from {from_class.__name__} to {to_class.__name__}\n")
                set_attr(attributes, attr, transform_value_common(mapping_table, value, glob_transform))
                continue

            _log_if(attr is not None, "WARN", f"Attribute '{attr}' from Input AST:{input_obj.__class__.__name__} was not used in IFEX:{to_class.__name__}")


        # Both loops done. Attributes now filled with key/values. Instantiate "to_class" object and return it.
        _log("DEBUG", f"Creating and returning object of type {to_class} with {attributes=}")
        try:
            obj = to_class(**attributes)
            return obj
        except Exception as e:
            _log("ERROR", f"Could not create object of type {to_class} with {attributes=}.\n(Was mapped from type {from_class=}).  ")
            _log("ERROR", f"Exception is: {e}")


    no_rule = f"no translation rule found for object {input_obj} of class {input_obj.__class__.__name__}"
    _log("ERROR", no_rule)
    raise TypeError(no_rule)
