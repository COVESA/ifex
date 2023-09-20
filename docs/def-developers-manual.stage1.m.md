This manual is useful primarily for implementation of new IFEX tools, but sometimes also for people who use the tools and then develop software based on the output that was generated to/from IFEX.   Before reading the developers' manual, make sure you have read the [IFEX Core IDL specification](ifex-specification.md) and [FAQ](./FAQ.md).

# Mapping documents

By "mapping" we mean to describe how we may interpret and ultimately translate IFEX to or from another interface description environment, or a particular output format (computing environment, protocol, programming language, etc.).  It can be such things as listing the "features" of IFEX and seeing how we may implement those features in the target environment (or the opposite direction, listing the features of the other environment and how IFEX can meet them).

General documents describe our general strategy for approaching mappings.

Individual documents describe particular target (or source) standards.

- [D-Bus](./static-mapping-dbus.md)

!INCLUDE "static-ifex-type-mapping-howto.md"

!INCLUDE "static-developer-generators.md"

______________________________________________________________________

!INCLUDE "static-footer.md"
