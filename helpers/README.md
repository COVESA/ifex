# Helpers

This directory contains tools that are developed outside of the IFEX project but are useful to process either the input or output files that are involved in the translation or code generation created by the IFEX tools.

The purpose is to make it easy to access useful companion tools for IFEX processing and in some cases they are required parts of processing pipelines.  It can be things like linters, formatters and compilers.

The inclusion of these tools into the IFEX git repository should be light-weight and could use different methods, such as:

- A git submodule referencing the git repository for the program
- A script that helps to download and install the program
- A document that explains how to manually find and install the program

Configuration files (typical for linters, formatters, etc.) might also be included near each tool.

