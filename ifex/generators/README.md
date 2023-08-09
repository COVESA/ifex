# generators directory

This directory is intended to host output (generation) implementations for
different code programming languages and description formats.

It is only required to implement new generators for 'advanced' cases that need
to some intermediate to advanced logic in python code.  Some simple cases might
be possible to generate using the generic `ifexgen` binary, combined with
output (jinja) templates.

Sometimes simple logic is already emedded in jinja-templates, like this for
example: `{% for x in list %} ... {% endfor %}`, and also simple if-conditionals.

It is however recommended to use separate python modules for advanced cases.
For all cases that require a particular set of input files (for example
additional input layers), it is at minimum needed to make a new python file to
act as an entry-point (executable) for that type of output.  The same python
file, or related modules, can provide useful helper functions that the
jinja-templates can call.

## See also

Simpler formats can be created directly with the generic generator (`ifexgen`)
and jinja-templates only -- the templates can be found in their associated
sub-directory below `templates/`.
