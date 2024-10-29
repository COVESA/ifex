# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

"""
This module adds a type-checking constructor to dataclass definitions if they have type hints using the python typing module.
"""

from dataclasses import dataclass, fields
from typing import get_type_hints, List, Optional, Any
from ifex.model.ifex_ast_introspect import is_list, actual_type, inner_type, is_optional, field_is_optional, is_any

def is_correct_type(value, _type):
    if type(value) is list and is_list(_type):
        # In standard python code values placed _inside_ a list could be of any
        # type (and different types!)   We want to check that the specification
        # is fulfilled, so we check that all values in list have the right type:
        expected_type = inner_type(_type)
        return all(type(v) == expected_type for v in value)
    # For optional types, it's OK to set them to None
    elif is_optional(_type):
        #print(f"OPTIONAL-> allowing None")
        return value == None or type(value) == actual_type(_type)
    # If type is "Any", then any type is accepted
    elif is_any(_type):
        return True
    else:
        return type(value) == actual_type(_type)


def add_constructor(cls):
    """
    Adds a type-checking constructor (__init__) to a named dataclass, based on its member fields, and their type specifications.
    """
    # Get the names and types of the member variables (fields) in the dataclass
    arg_names = [f.name for f in fields(cls)]
    arg_types = get_type_hints(cls)  # (dict mapping name->type)

    # Store original init function. It will be called from within the new constructor and
    # because of closure magic, the correct one will be called.
    orig_init = cls.__init__

    # Define the constructor function
    def type_checking_constructor(self, *args, **kwargs):

        # Initialize object using the original __init__ first - this calls the default_factory stuff, for example
        orig_init(self, *args, **kwargs)

        # First check that enough args are given
        if len([f for f in fields(cls) if not field_is_optional(f)]) > (len(args) + len(kwargs)):
           raise TypeError(f'Object construction error:  Not all mandatory arguments were given, through positional or keyword arguments')

        # Now check arguments against their expected type:

        # 1. Check positional arguments with the name/value zip. It works because 
        #    positional args are required to be in the same order as the fields.
        #    The zip function will create pairs, only for as many args that are
        #    given in *args and then stop.  Therefore, this checks each of the
        #    positional args against the corresponding field.  Any fields that
        #    remain are either optional (a default value in the dataclass will
        #    remain), or given as keyword arguments. 
        # 2. Next, check keyword arguments using the **kwargs (name/value pairs)
        # 3. Since the check is identical for both, it is combined into one loop.

        for name, value in list(zip(arg_names, args)) + list(kwargs.items()):
            if not is_correct_type(value, arg_types[name]):
                try:
                    nameinfo = f"Additional Info:  The object was named: {self.name}"
                except:
                    nameinfo = ""
                raise TypeError(f'Object construction error for class {type(self)}: According to specification, value named \'{name}\' must be of type: {arg_types[name]}, but was instead: {type(value)!r}. {nameinfo}')

            # Assign field value
            setattr(self, name, value)



    # Add the constructor to the metaclass
    cls.__init__ = type_checking_constructor

    return cls


# ---- TEST CODE ----
if __name__ == '__main__':

    @add_constructor
    @dataclass
    class Special:
        s: Optional[str] = 'special'
        i: Optional[int] = 42

    @add_constructor
    @dataclass
    class Person:
        name: str
        height: float
        hobbies: List[str]
        age: Optional[int] = 99
        special: Optional[Special] = None

    @dataclass
    class Test:
        name: str
        height: float
        hobbies: List[str]
        age: Optional[int] = 99
        special: Optional[Special] = None

    # Example of a correct object
    p = Person('Alice', 1.75, ['reading', 'swimming'], age=25)
    print("If no error then this passed: ", p.name, p.age, p.height, p.hobbies, p.special)

    # Example of a correct object, with an inner complex type
    p = Person('Bob', 1.75, ['reading', 'swimming'], 30, Special('foo',1000))
    print("If no error then this passed: ", p.name, p.age, p.height, p.hobbies, p.special)

    # Example of a correct object, skipping optional values
    p = Person('Celine', 1.75, ['reading', 'swimming'])
    print("If no error then this passed: ", p.name, p.age, p.height, p.hobbies, p.special)

    # Example of a correct object, with default values
    p = Person('Darwin', 1.75, ['reading', 'swimming'], 45, Special('bar'))
    print("If no error then this passed: ", p.name, p.age, p.height, p.hobbies, p.special)

    # Example of a correct object, using keyword arguments
    p = Person('Eric', 1.75, special = Special(), age = 55, hobbies = ['reading', 'swimming'])
    print("If no error then this passed: ", p.name, p.age, p.height, p.hobbies, p.special)

    # This example raises TypeError because we not all mandatory fields are specified
    try:
        p = Person('Fiona', hobbies = ['boxing'])
    except TypeError as e:
        print("---------------------------------------------------------------")
        print(f"=> Passed test because we caught an /expected/ type exception:")
        print("    " + str(e))
        print("---------------------------------------------------------------")

    # This example raises TypeError because age '35' is given as string instead of int:
    try:
        p = Person('George', 1.80, ['hiking', 'biking'], '35')
    except TypeError as e:
        print("---------------------------------------------------------------")
        print(f"=> Passed test because we caught an /expected/ type exception:")
        print("    " + str(e))
        print("---------------------------------------------------------------")

    # This example raises TypeError because we hobbies has a non-string element
    try:
        p = Person('Hilda', 1.85, ['running', 'basketball', 42], 45)
    except TypeError as e:
        print("---------------------------------------------------------------")
        print(f"=> Passed test because we caught an /expected/ type exception:")
        print("    " + str(e))
        print("---------------------------------------------------------------")

