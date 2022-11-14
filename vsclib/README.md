# VSC Generator library

This repo contains a Vehicle Service Catalog library
enabling the developer to build up VSC model with namespaces,
includes, typedefs, structs, enumerations, methods, events, and properties.

Once the structure has been created all datatypes references throughout
the model can be validated to make sure that they refer to real types.

The model is used to generate a python dictionary that can be written out
as a VSC YAML file.


TO TEST:
pip3 install .
python3 vsc_test.py

TODO: Implement properties.
TODO: Read and resolve include files.

