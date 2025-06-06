# protobuf/gRPC test files

This directory holds several test files from the original Google protobuf and
gRPC projects. We use them primarily to check that the protobuf parser can read
them all, or to see if output from conversions has changed as a consequence of
code changes (i.e. regression tests).

## Supported protobuf syntax is proto3

1-2 files were modified to remove a yet unsupported complex string escape sequence.
This might be fixed later, if a real-world usage requires it.

While there are a few files here marked as syntax = "proto2", we did not include all proto2
related files that would fail parsing because of a few (deprecated?) features that are not implemented
by the grammar/parser.

==> There is NO current plan to officially support anything else than "proto3" syntax.
(but contributions welcome if there is a way to support proto2 without unnecessary complications)

## LICENSE

The copyright and license information for the example and unit-test files are
specified in each file header but generally governed by the project they stem
from.  The corresponding license texts can be found in the LICENSES directory:

Directory:
* protobuf/ - uses MIT license -> see LICENSES/MIT
* grpc/ - uses multiple licenses but the protofiles have only headers with Apache license -> see LICENSES/Apache-2.0

Example files found outside of these two directories are written by or for the IFEX
project and licensed the same as the project as a whole (unless explicitly marked otherwise).

