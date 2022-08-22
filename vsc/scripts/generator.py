from vsc.model.vsc_generator import gen
from vsc.model.vsc_parser import get_ast_from_file
import argparse

def vsc_generator_run():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('input', metavar='input', type=str,
                        help='input.yaml-file (path)')
    parser.add_argument('template', metavar='template', type=str,                        
                        help='output-template-file (name only, not path)')

    args = parser.parse_args()
    
    ast = get_ast_from_file(args.input)
    
    templatename = args.template
    
    print(gen(ast, templatename))


if __name__ == "__main__":
    vsc_generator_run()