# DTDL Generator

(C) 2022 Robert Bosch GmbH

## Introduction

The DTDL Generator converts VSC (IFEX format) services to correct DTDL according to the [DTDL specification](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md), keeping as much as possible of the information in the IFEX definition.
It consists of a [generator template](dtdl.tpl) that has been created using the template framework of the vsc-tools (now ifex) project.

## Known Limitations

*The DTDL Generator has been developed as proof-of-concept and does not currently have product quality!*

Known limitations of the implementation:

* Code contain quite a lot of code duplication - could possibly be avoided with addition of Jinja macros for code reuse
* Handling of commas between entities not optimal
* No support to put files under other prefix, `global:covesa` always used
* No support for namespaces of arbitrary depth. Currently everything expected to be within the same namespace
* No support for including other files or referencing types in other namespaces
* No support for including error messages defined in IFEX.


In general all data in the example service can be converted, but minor details are lost:

- Explicit min/max values (from IFEX typedefs)
- Implicit min/max values (from IFEX types like `uint8` as a bigger type like `integer` must be used in DTDL)


## Conversion concept
The intention is to generate correct DTDL according to the [DTDL specification](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md), keeping as much as possible of the information from the IFEX definition.
For now the focus is on concepts used in the [VSC example service](https://github.com/COVESA/vehicle_service_catalog/blob/master/comfort-service.yml).
The reason for this limitation is that the functionality of the tooling in the [COVESA vsc-tools repo](https://github.com/COVESA/ifex) (now IFEX) currently has significant limitations, concerning e.g. nested namespaces and inclusion of data from other files.
In this section mappings are described for all IFEX concepts used in the example file. 

### Namespace
Represented as [DTDL Interface](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#interface). Proposed default naming for [example service](https://github.com/COVESA/vehicle_service_catalog/blob/master/comfort-service.yml) is `"dtmi:global:covesa:comfort:seats"`, to be aligned with the homepage [http://covesa.global/](http://covesa.global/) of COVESA. In more advanced tooling the prefix (`global:covesa`) could be an input parameter.

It must be noted that for now VSC has not yet aligned on a specific tree/naming structure, e.g. whether there should exist a top level called `Vehicle` similar to [VSS](https://github.com/COVESA/vehicle_signal_specification).

### Primitive Types
General approach is to convert from [IFEX native datatype](https://covesa.github.io/ifex/developers-manual#datatype-mapping) to [DTDL datatype](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#primitive-schemas).

- `uint8`, `int8`, `uint16`, `int16`, `int32` -> `integer` (signed 4-byte)
- `uint32`, `uint64`, `int64` -> `long` (signed 8-byte). Some values of uint64 cannot be represented, but likely has no impact. Should possibly in long term give warning during conversion.
- `boolean` -> `boolean`
- `float` -> `float`
- `double` -> `double`
- `string` -> `string`

 A conversion tool could possibly add a DTDL comment giving a textual description of the base type, like `"Comment":"Original IFEX type: uint16"`.

### Struct

[IFEX Structs](https://covesa.github.io/ifex/ifex-specification#struct) can be represented as [DTDL Interface Object Schemas](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#interface-schemas).

### Typedef

No good DTDL representation exist for [IFEX Typedefs](https://covesa.github.io/ifex/ifex-specification#typedef) Suggested conversion is to use base-type, i.e. for the example below `integer`. A conversion tool could possibly add a DTDL comment giving a textual description of the base type, like `"Comment":"Original IFEX type: movement_t (int16, min: -1000, max:1000"`.

```
 typedefs:
      - name: movement_t
        datatype: int16
        min: -1000
        max: 1000
        description: |
          The movement of a seat component
```

### Enumerations
[Enumerations](https://covesa.github.io/ifex/ifex-specification#enumeration) should be straightforward to represent as [DTDL enum](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#enum).

### Methods
[Methods](https://covesa.github.io/ifex/ifex-specification#method) should be possible to represent as [DTDL Command](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#command)

If the IFEX method has more than 1 in-param or more than 1 out-param an inline struct needs to be used in DTDL representation. The struct must then have a name, a possible approach is to use `in` for the in-parameter and `out` for the out-parameter.
 
### Events
Assuming the [Events](https://covesa.github.io/ifex/ifex-specification#event) are sent by the vehicle, it could be represented as [DTDL Telemetry](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#telemetry). 

### Properties
[IFEX Properties](https://covesa.github.io/ifex/ifex-specification#property) is intended to be able to represent [VSS signals](https://github.com/COVESA/vehicle_signal_specification). They match [DTDL Property](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#property) quite well, but to a certain extent also [DTDL Telemetry](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#telemetry).

In the DTDL documentation examples for [Telemetry](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#telemetry-examples) and [Properties](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#property-examples) it seems that Telemetry is used for data similar to VSS sensors and Properties for items similar to VSS actuators and VSS attributes.
But in VSS an actuator can also act as a sensor, i.e. when you set it you set the "wanted" value, but when you read it you get the "actual" value rather than the "wanted" value.
An example is `Vehicle.Cabin.Seat.Row1.Pos1.Position`.

For now all IFEX properties are represented as DTDL Writeable Property.

### Handling of generic fields
- IFEX description can be represented as DTDL description property.
- IFEX does not have structured comments (only `#` comments that are ignored when creating internal model), not possible to convert to DTDL comment property.

## Using the DTDL Generator

### Generating DTDL

The tool can be used like below:

```
# go to ifex tools if not already there
cd ifex
# make sure that VSC has been cloned
git clone https://github.com/COVESA/vehicle_service_catalog/
ifexgen vehicle_service_catalog/comfort-service.yml dtdl.tpl > dtdl_generated.json
```

### Validating generated DTDL files

Validation of DTDL can be used by an [Azure example project](https://github.com/azure-samples/dtdl-validator/).

Steps required for compiling and running the tools on Windows 10 includes:

- Install Dotnet. When verifing the example DTDL file NET Core SDK 5.0 was used, others might work
- `git clone https://github.com/azure-samples/dtdl-validator/`
- Edit the `DTDLValidator.csproj` file to include the installed NET Core version, e.g. `<TargetFramework>netcoreapp5.0</TargetFramework>`
- Make sure environment variables `HTTP_PROXY`and `HTTPS_PROXY` are defined if needed
- Build it with `dotnet build DTDLValidator.csproj`

When running the DTDL file to analyze shall be put in a separate directory, as the tool analyzes all files found in current directory.

Example when errors are found in file:

``` bat 
MYUSER@MYCOMPUTER MINGW64 /c/myuser/dtdl-validator/DTDLValidator-Sample/DTDLValidator/tmp (master)
$ ../bin/Debug/netcoreapp5.0/DTDLValidator.exe
Simple DTDL Validator (dtdl parser library version 3.12.5.0)
Validating *.json files in folder 'C:\myuser\dtdl-validator\DTDLValidator-Sample\DTDLValidator\tmp'.
Recursive is set to True

Read 1 files from specified directory
Validated JSON for all files - now validating DTDL
*** Error parsing models. Missing:
  dtmi:com:example:SeatAdjusterVehicleApp;3
  dtmi:com:example:SwdcComfortSeat;3
  dtmi:com:example:VSSService;3
Could not resolve required references

```
Example of successful validation:

``` bat 
MYUSER@MYCOMPUTER MINGW64 /c/myuser/dtdl-validator/DTDLValidator-Sample/DTDLValidator/tmp (master)
$ ../bin/Debug/netcoreapp5.0/DTDLValidator.exe
Simple DTDL Validator (dtdl parser library version 3.12.5.0)
Validating *.json files in folder 'C:\myuser\dtdl-validator\DTDLValidator-Sample\DTDLValidator\tmp'.
Recursive is set to True

Read 1 files from specified directory
Validated JSON for all files - now validating DTDL

**********************************************
** Validated all files - Your DTDL is valid **
**********************************************
Found a total of 18 entities

```
