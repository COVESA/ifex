# Protobuf parser/input processing

## Dependencies:
- Lark parser framework

## Files
- `protobuf.grammar` - Protobuf syntax definition in Lark format
- `protobuf_lark.py` - Input parser, creates Protobuf AST
- `protobuf_ast.py` - Dataclass definitions for a Protobuf AST
- `protobuf_ast_construction.py` - Define helper functions that build AST nodes
- `protobuf_to_ifex.py` - AST Model-to-model transformation Protobuf->IFEX
