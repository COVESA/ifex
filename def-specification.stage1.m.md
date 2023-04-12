<!-- Features and introduction -->
!INCLUDE "static-general-description.md"

<!-- Types, constraints/ranges, type resolution in namespaces. -->
!INCLUDE "static-types.md"

<!-- Layers concept, IFEX File Syntax, semantics and structure -->
!INCLUDE "static-files-and-layers.md"

----

## NODE TYPES

The chapters that follow this one specify the node types for the core interface language/model.  They are generated from a "source of truth" which is the actual python source code of `ifex_ast.py`.  This means that while the examples are free-text and may need manual updating, the list of fields and optionality should always match the behavior of the tool(s).  => Always trust the tables over the examples, and report any discrepancies.

<!-- Syntax specification (generated from source) -->
!INCLUDE "generated-syntax.md"

<!-- End of document -->
!INCLUDE "static-footer.md"
