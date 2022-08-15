#!/usr/bin/env python3
# (C) 2022 MBition GmbH
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

import sys
from vsclib import vsc

def test_vsc():
    root_ns = vsc.create_root_namespace()
    a_ns = root_ns.add_namespace("a")
    a_a_ns = a_ns.add_namespace("a")
    a_b_ns = a_ns.add_namespace("b")
    a_b_a_ns = a_b_ns.add_namespace("a")

    # Add an int8 typedef at a.b.a
    my_typedef_dt = a_b_a_ns.add_typedef("my_typedef", "int8")

    # Mathing dictionary
    my_typedef_dict = {
        "name": "my_typedef",
        "datatype": "int8"
    }


    # Locate datatype we just added via root search from root
    if root_ns.find_datatype_by_name(".a.b.a.my_typedef") != my_typedef_dt:
        print("Fail typedef root search test 1")
        sys.exit(1)

    print("Pass typedef root search test 1")

    # Locate datatype we just added via root search from different child
    if a_a_ns.find_datatype_by_name(".a.b.a.my_typedef") != my_typedef_dt:
        print("Fail typedef root search test 2")
        sys.exit(2)

    print("Pass typedef root search test 2")

    if a_a_ns.find_datatype_by_name(".a.b.a.my_typedef").as_vsc_dict() != my_typedef_dict:
        print(f"Wanted: {my_typedef_dict}")
        print(f"Got:    {a_a_ns.find_datatype_by_name('.a.b.a.my_typedef').as_vsc_dict()}")
        print("\nFail typedef dictionary integrity test")
        sys.exit(3)

    print("Pass typedef dictionary integrity test")

    # Add an int16 typedef at a
    my_int16_dt = a_b_a_ns.add_typedef("my_int16", "int16")

    # Check that we can resolve an inherited datatype from a a.b.a (which is a child of a)
    if a_b_a_ns.find_datatype_by_name("my_int16") != my_int16_dt:
        print("Fail inherited typedef search test")
        sys.exit(4)

    print("Pass inherited typedef search test")
    # Passed all path tests

    # Setup a struct
    my_struct = a_ns.add_struct("my_struct")
    my_struct.add_member("f1", "int8")
    my_struct.add_member("f2", ".a.b.a.my_typedef") # Abs path
    my_struct.add_member("f3", "b.a.my_int16")
    my_struct_dict = {
        "name": "my_struct",
        "members": [
            { "name": "f1", "datatype": "int8" },
            { "name": "f2", "datatype": ".a.b.a.my_typedef" },
            { "name": "f3", "datatype": "b.a.my_int16" }
        ]
    }


    if my_struct.as_vsc_dict() != my_struct_dict:
        print(f"Wanted: {my_struct_dict}")
        print(f"Got:    {my_struct.as_vsc_dict()}")
        print("\nFail struct dictionary integrity test")
        sys.exit(7)

    # Passed all struct tests
    print("Pass struct dictionary integrity test")



    # Setup an enum
    my_enum = a_ns.add_enumeration("my_enum", "uint8")
    my_enum.add_option(vsc.Enumeration.Option("option1", 10))
    my_enum.add_option(vsc.Enumeration.Option("option2", 20))
    my_enum.add_option(vsc.Enumeration.Option("option3", 30))

    my_enum_dict = {
        "name": "my_enum",
        "datatype": "uint8",
        "options": [
            { "name": "option1", "value": 10 },
            { "name": "option2", "value": 20 },
            { "name": "option3", "value": 30 }
        ]
    }

    if my_enum.as_vsc_dict() != my_enum_dict:
        print("Fail 8")
        print(f"Wanted: {my_enum_dict}")
        print(f"Got:    {my_enum.as_vsc_dict()}")
        print("\nFail enumeration dictionary integrity test")
        sys.exit(8)


    print("Pass enumeration dictionary integrity test")

    # Setup a method
    my_method = a_ns.add_method("my_method", "uint32")
    my_method.add_in_argument("in_arg1","string")
    my_method.add_in_argument("in_arg2", "my_enum")
    my_method.add_in_argument("in_arg3", "my_struct")
    my_method.add_in_argument("in_arg4", ".a.b.a.my_typedef")

    my_method.add_out_argument("out_arg1","string")
    my_method.add_out_argument("out_arg2", "my_enum")
    my_method.add_out_argument("out_arg3", ".a.my_struct")
    my_method.add_out_argument("out_arg4", ".a.b.a.my_typedef")



    my_method_dict = {
        "name": "my_method",
        "in": [
            { "name": "in_arg1", "datatype": "string" },
            { "name": "in_arg2", "datatype": "my_enum" },
            { "name": "in_arg3", "datatype": "my_struct" }, # Inherited from "a"
            { "name": "in_arg4", "datatype": ".a.b.a.my_typedef" },
        ],
        "out": [
            { "name": "out_arg1", "datatype": "string" },
            { "name": "out_arg2", "datatype": "my_enum" },
            { "name": "out_arg3", "datatype": ".a.my_struct" }, # Abs path back to self's ns
            { "name": "out_arg4", "datatype": ".a.b.a.my_typedef" },
        ],
        "error": {
            "datatype": "uint32"
        }
    }

    if my_method.as_vsc_dict() != my_method_dict:
        print(f"Wanted: {my_method_dict}")
        print(f"Got:    {my_method.as_vsc_dict()}")
        print("\nFail method dictionary integrity test")
        sys.exit(9)


    # Passed all method tests
    print("Pass method dictionary integrity test")

    my_root_dict = {
        "namespaces": [
            { "name": "a",
              "namespaces": [
                  { "name": "a" },
                  { "name": "b",
                    "namespaces": [
                        { "name": "a",
                          "typedefs": [
                              { "name": "my_typedef", "datatype": "int8" },
                              { "name": "my_int16", "datatype": "int16" }
                          ]
                        }
                    ]
                  }
              ],
              "structs": [
                  { "name": "my_struct",
                    "members": [
                        { "name": "f1", "datatype": "int8" },
                        { "name": "f2", "datatype": ".a.b.a.my_typedef" }, # Abs path
                        { "name": "f3", "datatype": "b.a.my_int16" } # Relative path
                    ]
                  }
              ],
              "enumerations": [
                  { "name": "my_enum",
                    "datatype": "uint8",
                    "options": [
                        { "name": "option1", "value": 10 },
                        { "name": "option2", "value": 20 },
                        { "name": "option3", "value": 30 }
                    ],
                  }
              ],
              "methods": [
                  { "name": "my_method",
                    "in": [
                        { "name": "in_arg1", "datatype": "string" },
                        { "name": "in_arg2", "datatype": "my_enum" },
                        { "name": "in_arg3", "datatype": "my_struct" },
                        { "name": "in_arg4", "datatype": ".a.b.a.my_typedef" } # Abs Path
                    ],
                    "out": [
                        { "name": "out_arg1", "datatype": "string" },
                        { "name": "out_arg2", "datatype": "my_enum" },
                        { "name": "out_arg3", "datatype": ".a.my_struct" },
                        { "name": "out_arg4", "datatype": ".a.b.a.my_typedef" } # Abs path
                    ],
                    "error": {
                        "datatype": "uint32"
                    }
                  }
              ]
            }
        ]
    }

    if root_ns.as_vsc_dict() != my_root_dict:
        print(f"Wanted: {my_root_dict}")
        print(f"Got:    {root_ns.as_vsc_dict()}")
        print("\nFailed root namespace dictionary integrity test")
        sys.exit(10)

    print("Passed root namespace dictionary integrity test")

    res = root_ns.find_unresolved_datatypes()
    if len(res) > 0:
        print(f"Unresolved data types:\n")
        for (path, dt) in res:
            print(f"Location: {path}   Type: {dt}")

        print(f"Failed datatype resolve test\n")
        sys.exit(11)

    print(f"Passed datatype resolve test\n")
    print("\nAll tests pass")
    sys.exit(0)
if __name__ == "__main__":
    test_vsc()
