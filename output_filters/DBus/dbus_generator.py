# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
# (C) 2023 Novaspring AB
# Custom generator for D-Bus XML format
# ----------------------------------------------------------------------------

from models.ifex.ifex_generator import jinja_env, gen
from models.ifex.ifex_parser import get_ast_from_yaml_file
from models.DBus import dbus_types
import lxml.etree as etree
import sys

# Collect up namespaces in hierarchy
namespace_path = ""


def add_namespace(ns):
    global namespace_path
    if namespace_path != "":
        namespace_path += "."
    namespace_path += ns.name
    # Must return empty string since it's called from generation template!
    # Otherwise, the return value "None" will be printed to output
    return ""


# Construct the interface name from the Namespace hierarchy
def get_interface_name(if_name):
    global namespace_path
    return f"{namespace_path}.{if_name}"


# Errors need to be given a name if they don't have one
counter = 0


def gen_error_name(err):
    global counter
    if err.name is None:
        counter += 1
        return "error" + str(counter)
    else:
        return err.name


def main_generate(yaml_file):
    template_dir = "D-Bus"
    ast = get_ast_from_yaml_file(yaml_file)
    # re-initialize jinja environment with the given template dir
    jinja_env.__init__(template_dir)
    jinja_env.set_template_env(
        gen=gen,
        gen_dbus_type=dbus_types.gen_dbus_type,
        add_namespace=add_namespace,
        get_interface_name=get_interface_name,
        gen_error_name=gen_error_name,
    )
    dbus_types.collect_types(ast.namespaces)
    raw_xml=gen(ast)

    # OMG this is complicated to get a decent XML output!
    # You MUST ask to remove any spaces in input, otherwise the parser believes
    # they are significant (like in HTML) and will not reindent the XML.
    parser = etree.XMLParser(remove_blank_text=True)
    print(etree.tostring(etree.fromstring(raw_xml, parser), pretty_print=True).decode("utf-8"))

# ----------------------------------------------------------------
# MAIN = Standalone test Code only, not normal use.
if __name__ == "__main__":
    main_generate(sys.argv[1])
