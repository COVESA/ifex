# IFEX JSON-schema

This file explains why JSON-schema support was added to the project and how it relates to the development philosophy.

## Background

Since its beginning IFEX development has strived to follow the elusive "single source of truth" principle.  Translated into development it means that the language syntax shall as far as possible be defined in a single place, and in a machine-processable format so that **all** programs and documentation derive from this single definition, and are thereby always consistent with eachother.

It is anticipated that the IFEX specification will evolve before becoming stabilized.  It is crucial to minimize the number of inconsistencies and errors during that period.  

As of now, important sections of the IFEX Core IDL Specification are _generated_ from an internal model of the language (a "meta-model" of sorts).  Documentation is generated from the same model that is used to read and validate IFEX input and as a basis for output (e.g. when translating another input format to IFEX).

JSON-schema support is not a step away from this (see below for details).  JSON-schema is added for the moment _primarily_ for IDE support (see 4th item under **Iteration 3** heading).

#### Iteration 1:
- The IFEX Core IDL language was first defined in a custom data-structure inside of the parser implementation (python).  Early on, the common idea of a schema (likely JSON-schema specifically) was considered.

  - Option A: Define the allowed syntax for the IDL in a separate "specification file" (JSON-schema).  Write a program that reads the definition, which can then be used inside of a program.  Then read the input, and use a library to see if the input conforms.
  - Option B: Define a simple definition directly in python source code (still very readable), and use that directly inside the program.  It is already written in the programming language, and does not need to be "created" by a previous step.
  - Option C: Keep the schema file separate and implement some parts of implementation independently.  Many programs take this approach and try to keep the consistency manually.  This breaks the goal of a single place of definition as described in the background, so this option was discarded immediately.

Option B was chosen because a schema file felt like an unnecessary intermediate step.  Furthermore, JSON-schema is somewhat complex and the files are noisy and a lot less readable than any of the alternative ways.  To understand the allowed structure of the language, the python source file was arguably more readable than the JSON schema.

- The data-structure defining the "meta-"- model was then iterated over to build python classes at run-time. These classes define the nodes inside the internal representation (abstract syntax tree) built from parsing the input which is in YAML, specifically in the IFEX Core IDL format.

- In practice, the classes defining the types for the AST are dataclasses since they do not include any operations, just fields.  

- A python dict is also used as an intermediate representation in all cases because that is what the standard YAML parsing library outputs.

- The python dict directly represents what was in YAML.  We get to this stage for any valid YAML file, but it is not necessarily valid according to IFEX Core IDL.

- One reason to build up a "tree" of python (data-)classes/objects instead of simply keeping a python-dict as the representation, is that it enables the minimal syntax for traversing the object tree when writing python code inside Jinja templates:  `item.namespaces[0].childnode.feature` as opposed to `item['namespaces'][0]['childnode']['feature']`.  
  - Furthermore, even though python is a dynamic language, it is more likely (for IDEs, for example) to indicate _before_ runtime errors occur, if some `.fieldname` does not exist at that position in the tree hierarchy (the valid fields are expressly defined by the class definitions).

#### Iteration 2:

- Some developers were fond of the @dataclass definition in python, combined with finding the `dacite` library. Part of the logic that was encoded in the original meta-definition datastructures could instead be defined in the dataclasses by adding in the typing module, namely: the intended type of each field, is it a single item or a list, and is it optional or mandatory. 

- Dacite library then also replaced the custom code that translates between the python dict and the AST representation.  Dacite will fail and provide some error information if the dict does not correspond to the hierarchy of dataclass definitions.  However, there was less detailed error information than we could give in the previous custom code that expressly iterated over the dict and could give IFEX-specific hints about what was wrong.

#### Iteration 3: JSON Schema addition

- First we note that JSON-schema is better supported than (various) YAML-schema alternatives, and simultaneously JSON-YAML equivalence makes it possible to use JSON-schemas to validate YAML. That is why JSON-schema is selected.
- Second, the main validation strategy has not changed - the core program is still working according to Iteration 2.  In other words, the "single source of definition" of the language has _not_ at this point switched to be a JSON schema file and the official definition is still in `ifex_ast.py`.  
- Because of that, we flip things around, and to ensure a consistent definition with minimal errors the JSON-schema file is not provided but instead generated from the internal model!  Such a program is now provided in this directory: `ifex_to_json_schema.py`. 
- The primary driver to still create a JSON-schema was IDE support.  By providing a JSON-schema, editing IFEX files in for example Visual Studio Code, will get automatic syntax-checking without any other custom plugin.  Validating against a JSON schema is already built into existing VSCode plugins.
- A future reason is that we could if it feels useful use a JSON-schema validation library to augment the formal check of the input. We might possibly get better error messages than the current YAML->dict->dacite chain does.  In addition, it may be a pathway for alternative IFEX tool implementations (in another programming language) since JSON-schema is generally very well supported in all languages.

#### Iteration 4 (future?):
- It is possible that there will be additional rewrites, which should still continue to be derived from the one formal definition to ensure full compatibility.  It is not yet decided but:
  - This rewrite might modify dacite or replace it, to get more detailed validation.
  - It might switch to JSON-schema as the official definition of the language (but there are no such plans now -- JSON-schema is still less readable and more complex).
  - In either case, detailed validation of fields needs improvement - the tree structure is checked but individual strings are not parsed to see if they make sense
  - As noted above, IFEX tools may later on be implemented in other programming languages than python, and when that happens there might be some strategy to move the source-of-truth from `ifex_ast.py` to something else.  It could be JSON-schema file as the official definition.  Or alternatively the initial seed for such development gets generated out of `ifex_ast.py` in some way.

### Issues to fix

- Examples are still not verified.  Although they are written inside of the `ifex_ast.py` file to facilitate consistency with the actual code model, they are still just opaque strings, and not programatically checked against any model or schema.  This means that examples in the specification can still be wrong due to human error.

