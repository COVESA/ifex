# BAMM Aspect Model Generator

(C) 2022 Robert Bosch GmbH

## Introduction

The BAMM Aspect Model Generator converts VSC (IFEX format) services to a valid BAMM Aspect Model according to the [BAMM Aspect Meta Model](https://github.com/OpenManufacturingPlatform/sds-bamm-aspect-meta-model), 
keeping as much as possible of the information from the IFEX definition.  It consists of a template ([sds-bamm-aspect-model](sds-bamm-aspect-model.tpl) and [sds-bamm-macros](sds-bamm-macros.tpl)) 
using the template framework of the IFEX project to parse and transform services.

## BAMM Aspect Meta Model
The BAMM Aspect Meta Model (BAMM) allows the creation of models to describe the semantics of digital twins by defining
their domain specific aspects. In this context, digital twins are the digital representation of a physical or virtual
object that bundles and combines several aspects. The BAMM Aspect Meta Model (BAMM) provides a set of predefined objects
(as depicted below) that allow a domain expert to define aspect models and complement a digital twin with a semantic
foundation. In case you were wondering what the B in BAMM refers to: BAMM is recursively defined and thus the B refers
to BAMM itself.

## Known Limitations

*The Generator has been developed as proof-of-concept and does not currently have product quality!*

Known limitations of the implementation:
* Handling of whitespaces between the model elements are not optimal
* No support for namespaces of arbitrary depth. Currently, everything expected to be within the same namespace.
* No support for including other files or referencing types in other namespaces
* No support for deployment files defined in IFEX.

In general all data in the example service can be converted.

## Using the BAMM Aspect Model Generator

### Generating a Seat Aspect Model 

The tool can be used like below:

```
# go to ifex tools if not already there
cd ifex
# make sure that VSC has been cloned
git clone https://github.com/COVESA/vehicle_service_catalog/
ifexgen vehicle_service_catalog/comfort-service.yml sds-bamm-aspect-model.tpl > comfort/2.0.1/seat.ttl
```

### Mapping of the different concepts
* [IFEX Structs](https://github.com/COVESA/vehicle_service_catalog#namespace-list-object-structs) is represented as [Entity](https://openmanufacturingplatform.github.io/sds-documentation/bamm-specification/snapshot/entities.html).
* [IFEX Typedefs](https://github.com/COVESA/vehicle_service_catalog#namespace-list-object-typedefs) is represented as [Characteristic](https://openmanufacturingplatform.github.io/sds-documentation/bamm-specification/snapshot/characteristics.html).
* [IFEX Enumerations](https://github.com/COVESA/vehicle_service_catalog#namespace-list-object-enumerations) is represented as [Characteristic](https://openmanufacturingplatform.github.io/sds-documentation/bamm-specification/snapshot/characteristics.html).
* [IFEX Methods](https://github.com/COVESA/vehicle_service_catalog#namespace-list-object-methods) is represented as [Operation](https://openmanufacturingplatform.github.io/sds-documentation/bamm-specification/v1.0.0/meta-model-elements.html).
* [IFEX Events](https://github.com/COVESA/vehicle_service_catalog#namespace-list-object-events) is represented as [Event](https://openmanufacturingplatform.github.io/sds-documentation/bamm-specification/v1.0.0/meta-model-elements.html).

### Validating the generated Aspect Model

To validate the generated Aspect Model the open source [Java SDK]() can be used.
The SDK can be downloaded from the official project page [here](https://github.com/OpenManufacturingPlatform/sds-sdk/releases).
Install and use the SDK: 
- Install Java
- Download the latest SDK release (bamm-cli-x.x.x-x.jar)
- Create the following directory structure 'comfort/2.0.1' and copy seat.ttl into the directory '2.0.1' 
- Run in the project root folder `java -jar bamm-cli-x.x.x-x.jar -i comfort/2.0.1/seat.ttl -v`

Example of successful validation:

``` bat 
java -jar bamm-cli-1.1.0-M3.jar -i comfort/2.1.0/seat.ttl -v
Validation report: Input model is valid
```

Besides the CLI, the Aspect Model Editor application can be used to visualize and validate the generated Aspect Model. The editor
is freely available for Windows, Linux and MAC and can be downloaded [here](https://www.bosch-connected-industry.com/de/de/downloads/aspect-model-editor/index.html).
The editor is offered currently as freeware and will be open source this year within the OMP.

### Further usage of an Aspect Model

Based on the Aspect Model and the SDK the following additional topics can be generated:
* JSON-Schema, running `java -jar bamm-cli-x.x.x-x.jar -i comfort/2.0.1/seat.ttl -schema`
* HTML Documentation, running `java -jar bamm-cli-x.x.x-x.jar -i comfort/2.0.1/seat.ttl -html`
* OpenAPI Spec, running `java -jar bamm-cli-x.x.x-x.jar -i comfort/2.0.1/seat.ttl -oapi-yaml -base-url 'http://<base-url>'`
