# Simple round-trip to test both proto parser and output generator
from models.protobuf import protobuf_lark as protobuf_parser
from output_filters.protobuf import grpc_generator
import os

def proto_roundtrip(file):
    template_dir = os.path.join(os.path.dirname(grpc_generator.__file__), "templates")
    ast_root = protobuf_parser.get_ast_from_proto_file(file)
    generated = grpc_generator.ast_to_text(ast_root, template_dir)
    return generated

if __name__ == '__main__':
    test_gen()

