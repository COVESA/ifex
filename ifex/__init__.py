"""
Interface Exchange Framework (IFEX) - Python Library

IFEX is a general interface description and transformation technology to
integrate/unify/translate different IDLs, and provide tools and methods to
facilitate system integration using popular IPC/RPC protocols.
"""

try:
    from importlib.metadata import version
    __version__ = version("ifex")
except ImportError:
    from importlib_metadata import version
    __version__ = version("ifex")
