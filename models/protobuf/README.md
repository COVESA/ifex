# Protobuf parser/input processing

## Dependencies:
- Lark parser framework

## Files
- `protobuf.grammar` - Protobuf syntax definition in Lark format
- `protobuf_lark.py` - Input parser, creates Protobuf AST
- `protobuf_ast.py` - Dataclass definitions for a Protobuf AST
- `protobuf_ast_construction.py` - Define helper functions that build AST nodes

## How to run

Go to input_filters/protobuf directory to find the converter.

For simple conversions or tests, the protobuf_to_ifex.py has a main method and
can be run as a script directly. It will print out the result as IFEX Core IDL
in YAML text:

```
python protobuf_to_ifex.py <input.proto>
```
 
For developing on top of this module, for example in a direct translation to other format without the IFEX text format as an intermediiate:  Import and use the function `proto_ast_from_input(protofile)` followed by `protobuf_to_ifex(proto_ast)` on that result.  The latter returns an IFEX AST that can be further processed.
