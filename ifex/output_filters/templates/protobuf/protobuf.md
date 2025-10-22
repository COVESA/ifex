# Protobuf Generator

(C) 2022 Robert Bosch GmbH

## Introduction

The Protobuf Generator converts VSC (IFEX format) services to a [Google Protocol Buffer](https://developers.google.com/protocol-buffers/) definition.

## Known Limitations

*The Protobuf Generator has been developed as proof-of-concept and does not currently have product quality!*

The general tooling framework provided by IFEX is currently not that advanced, partially depending on that IFEX as language not yet is that stable.
The open source tooling perform syntactic checks, but it does not perform semantic checks, e.g. verifying that a referenced datatype actually exists.

Known limitations of the current implementation:

* Intended to support the [VSC example service](https://github.com/COVESA/vehicle_service_catalog/blob/master/comfort-service.yml) only, it does not intend to support all possible use-cases of VSC.
* Does not support use of types from other namespaces.

## Conversion Concept

* IFEX typedefs are not represented in protobuf, instead the base type is used.
* IFEX Structs are represented in protobuf.
* IFEX methods are represented as rpc in protobuf.
* IFEX events are represented as messages in protobuf.
* IFEX properties are represented as a read rpc and a write rpc in Protobuf.
* IFEX Error Messages are currently not imported.

## Using the Protobuf Generator


### Preparations

No additional installations needed to run the generator, but to validate output a protobuf compiler is needed. 

```
apt install -y protobuf-compiler
```

### Generating Protobuf

The code below runs the prototype protobuf generator and verifies that the generated code is syntactically correct.

```
# go to ifex tools if not already there
cd ifex
# make sure that VSC has been cloned
git clone https://github.com/COVESA/vehicle_service_catalog/
# Run the generator
ifexgen vehicle_service_catalog/comfort-service.yml protobuf.tpl > comfort-service.proto
```

### Validating generated Protobuf files

Generated Protobuf files can be validated/compiled using `protoc`.

```
mkdir tmp
protoc --cpp_out=tmp comfort-service.proto
```

