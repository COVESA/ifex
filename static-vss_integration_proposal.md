# IFEX and VSS interoperability

## Background

From the very beginning that the "VSC" project started discussing the interface description format that is now IFEX, there has been an obvious question on how that may relate to VSS.

Here we should answer specifically, how may we design systems using a combination of the technologies, or if that does not work, what would be the criteria for choosing one or the other.

One view that has been frequently proposed is the following:

- When modeling only data items, use VSS.  (The 'simplicity' of VSS is a strength rather than a limitation for data "signal" modeling and this needs only what the VSS model offers)
- Then, when and if more is required (method calls, events, complex datatypes and typedefs with constraints, etc.), pivot to using the IFEX description language.
- Some large software systems could use both languages, in different parts of a system where the needs are different.

With that view it seems obvious that analyzing and unifying the concepts is necessary to ensure that a system definition is coherent also when using both description formats.  In particular, it may be very useful to refer to the VSS standard catalog and other VSS-formatted standard data sets from the IFEX-described interfaces.

For that reason, here are proposals for how to model systems and how to create tools that can work with both standards.

#### Historical note:

_Some of the text was extended from "A proposal for how we can translate VSS signals to properties" by Magnus Feuer, originally stored at: https://github.com/COVESA/vehicle_service_catalog/blob/master/vss_integration_proposal.yml
(the file might be removed from the master branch at this point since this document supersedes it)._

### Fundamentals

For modeling IFEX and VSS together there are several common characteristics, as well as some differences, that are worth considering:

- The primitive/core data types of IFEX were defined to be identical to those of VSS, which is a good start for compatibility.
- VSS "signals" are functionally equivalent to the Property concept of IFEX:  The IFEX Property is used to model "observable data items".  This is something that is treated as an atomic data item, with a unique name/identifier, a well defined datatype, and supplementary information in the form of a description that explains what is actually encoded (including e.g. physical unit).
- IFEX Properties can however use any datatype, including typedefs and other complex datatypes.
- VSS recently introduced a basic structured datatype concept that needs to be considered in the described solution - in particular if it is compatible with type definitions in IFEX.

### Strategies

The similarity between these concepts is high enough that they can map to each other.  A **Property** definition in IFEX ought to be able to describe the exact same data object in the system as the VSS **Signal**.  This should be made clear by having the Property refer to a VSS-defined signal somehow.

The primary issues to review are:  
- A) Datatype compatibility
- B) Naming hierarchy: IFEX _Namespaces_ vs. VSS _branches_.

#### Types

- Primitive types are identical in IFEX and VSS.  Constraints (value range etc.) as well as the details of enumeration types need to compared, however.
- Complex types:  In IFEX, complex types can be defined including various constraints, range limits, etc and a Property can have any defined type.  VSS signals originally were only defined using primitive types but this includes enumerations and arrays, but now there are also structs in VSS and this needs to be reviewed for compatibility.

#### Namespace / branch mapping

Two different strategies are here proposed for branches and namespaces when describing a system with a combination of VSS and IFEX description formats:

1) The first is to treat the VSS tree made up of branches as identical to the nested namespace tree for IFEX interfaces.  This means that property, when it is defined as a reference to an existing VSS signal, its sequence of nested parent namespaces in IFEX must be identical to the names of each branch in the hierarchy that leads to the VSS signal name.  Since the VSS tree location is defined by Namespaces that are equal to branches, the IFEX property name needs only have the VSS signal name to be fully defined.

2) The second approach is to treat the independent namespace trees as completely independent.  In that case, IFEX definitions would need to refer to the VSS signals by their fully qualified name that includes branches and leaves.

*Example of strategy 1), copied from vss_integration_proposal.yml:*

```yaml
# From VSS :
#
# - Vehicle:
#   type: branch
#   description: High-level vehicle data.
#
# - Vehicle.VehicleIdentification:
#   type: branch
#   description: Attributes that identify a vehicle
#
# - Vehicle.VehicleIdentification.VIN:
#   datatype: string
#   type: attribute
#   description: 17-character Vehicle Identification Number (VIN) as defined by ISO 3779

namespaces:
  - name: Vehicle
    description: High-level vehicle data.

    namespaces:
      - name: VehicleIdentification
        description:  Attributes that identify a vehicle

        properties:
          - name: VIN  # The item's namespace+name equivalence entails that it is identical to the corresponding VSS signal
            description: 17-character Vehicle Identification Number (VIN) as defined by ISO 3779
            datatype: string

```

*Examples of strategy 2:*

2.1:

```yaml
# From VSS :
#
# - Vehicle:
#   type: branch
#   description: High-level vehicle data.
#
# - Vehicle.VehicleIdentification:
#   type: branch
#   description: Attributes that identify a vehicle
#
# - Vehicle.VehicleIdentification.VIN:
#   datatype: string
#   type: attribute
#   description: 17-character Vehicle Identification Number (VIN) as defined by ISO 3779

# IFEX, with its own namespace hierarchy, and explicit VSS reference:
namespaces:
  - name: vehicle_platform
    description: Main namespace for the VehiclePlatform subsystem

    namespaces:
      - name: veh_attributes
        description: Attributes that identify a vehicle

        properties:
          - name: VSS:Vehicle.VehicleIdentification.VIN  # Needs explicit VSS-reference, using fully-qualified VSS name
            datatype: string
            description: 17-character Vehicle Identification Number (VIN) as defined by ISO 3779
```

**TODO:  This concept of referencing an external definition realm (VSS: above) ought to be generalized.**


2.2 An alternative approach could be:
```yaml
        properties:
          - name: MyPropertyName
            vss-alias: VSS:Vehicle.VehicleIdentification.VIN
```


**To consider:  Both the reference of an external realm (`VSS:x.y.z`) and the keyword `vss-alias:` are automotive-environment specific things that might bet better suited to be part of a Layer, not in the core IDL.**

### Other notes

IFEX does not specify if a property is readable, writeable, or constant on the IFEX Core IDL level.  Such characteristics would be added through a Layer, that in turn get translated into an access-control mechanism on the running software.

# Discussion

It could be very useful to match the Namespaces to the VSS branch hierarchy, especially if the IFEX interfaces are used mostly to augment the VSS signals to add a few methods and other features, in other words if the system modeling starts from a strong VSS basis.

But that strategy is also likely to be very limiting in some cases:  Looking at the VSS Standard Catalog first, it is organized primarily to have reasonable groupings of data, and this has resulted in several branches mimicking the physical features of the the car design (Powertrain, Braking, Engine, etc.).   Namespaces in software on the other hand, are often organized according to software system composition and software-features: (User Interface, Application Servers, Bootup, Storage, Networking, Communication, "Base Platform", etc.) so when modeling a larger system (already existing or otherwise) the namespaces likely won't match the VSS branch hierarchy very well.

# Recommendation

**STILL TODO**: It is of course necessary to go through and understand if there are any semantic mismatches in for example the type definitions, and for namespaces it is necessary to choose between some of the alternatives (2.1 vs 2.2).  

However, as a preliminary for the namespace concept the recommendation is to support both strategy 1) **and** 2) because of the reasons given in the Discussions chapter:  Both strategies could be desirable, in different scenarios.  We could therefore provide the flexibility.

