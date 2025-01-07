# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project

"""
Light-weight support functions for creating the Protobuf tree from program code,
likely to be used in Protobuf-to/from-IFEX model conversions.
"""

# See ifex_ast_construction.py for a more in-depth description of what this
# is and why.  It follows the exact same pattern.

from dataclasses import is_dataclass
from models.ifex.type_checking_constructor_mixin import add_constructor
import other.protobuf.protobuf_ast as protobuf_ast

def add_constructors_to_protobuf_ast_model() -> None:
    """ Mix-in the type-checking constructor support into each of the protobuf_ast classes: """
    for c in [cls for cls in protobuf_ast.__dict__.values() if
              isinstance(cls, type) and
              is_dataclass(cls)]:
        add_constructor(c)

