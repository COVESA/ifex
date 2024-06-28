# VSC -> IFEX history and renaming

April, 2023:

IFEX is the new name of the _technology_ originally developed under the VSC project, which still exists (see below for details).

## History and background:

When the **Vehicle Service Catalog** (VSC) project was started the intention was, and still is, to create a project similar to the Vehicle Signal Specification (VSS) which deals with common data definitions.

Both VSS and the original VSC project worked on two separate and complementing activities:

1) Create a common collection of data (VSS) and service/function (VSC) definitions, which are shared across the automotive industry.

2) Create, or find and adopt, a suitable file format to describe the list of data (VSS) and services (VSC) in 1).  For VSS and VSC respectively, these are two potentially common languages for precise definition of data and interfaces to enable more efficient exchange between companies.   Such a common language is valuable to have both for the VSS/VSC common catalog _and_ for other catalogs of data/services, both shared and proprietary.  Having a _common language_ is valuable beyond only the specific common catalog.

For VSC, the creation of shared APIs waited partly on agreeing on the description format, but also on slow uptake in the automotive industry of the creation of the common catalog of interfaces/services.  While it might not be the original root cause, the slow progress was often described in terms of not understanding the goals of the project and getting hung up the details such as if a new IDL should be created or not. The combined goals seemed to increase a wait-and-see attitude from potential contributors.

The technical approach progressed from the idea of creating a new interface description language (IDL), to evaluating if any of the existing IDLs could be adopted instead, and finally to a need for creating a common interface description model that can act as a bridge between all the existing ones.   Many of the currently used technologies are specialized for certain areas and also lack the "layered approach" that is key to IFEX.  They were therefore not appropriate to select as the one-and-only choice.  Others, such as Franca IDL were designed to be the common language, and bridge-technology, but some details were not completed.  (In many areas, IFEX continues the legacy from Franca IDL and further develops its concepts).  

It was identified early that the VSC project name suffered from
the ambiguity between the "catalog" and the technology.  (VSS
suffers from the same setup, but has managed to find success in
spite of it).  This concern was increased by the deeper
understanding of the direction the technology needs to take.

The common catalog started with a focus on external "services" that vehicles may expose to common infrastructure, whereas the developed technology really is more generic and could be applicable on all types of software interfaces in many levels of the system.

These things lead to up to at least 3 reasons for renaming the technology:

1. The technology should be separated from the creation of common _catalogs_ to avoid confusion about the goals of the project and to avoid that one goal is holding back the progress of the other.

2. Complaints about the automotive industry creating its own solutions may still apply (we are not oblivious to this fact). It is in any case worthwhile to remove "Vehicle" from the technology name because the technology is not limited to that domain, and it should strive to align with common non-automotive software technologies.

3. Finally, the word "service" might be limiting or it may have different meanings for different people.  The IFEX technology aims to support any and all types of _software interfaces_, including service descriptions, APIs, and other terms that may be used.

### What is **IFEX**?

The Interface Exchange framework (IFEX) is the new name of the _technology development part_ of the previous VSC.

The name accurately suggests the reasons for the development, which is in part to enable a powerful way of describing software interfaces, but also to enable_exchange_ of interfaces with several meanings:  It enables translation between interface descriptions, and interoperable communication between systems that use different interface descriptions. Finally "framework" suggests that software tools are to be developed, and it's not only a specification of a family of languages.

### What is **VSC** now?

The Vehicle Service Catalog project remains with its purpose of creating a catalog/collection of service/API descriptions, that are agreed upon and standardized among vehicle manufacturers.  It seems likely (but is open to VSC project stakeholders to decide) that IFEX would be adopted as the description format and technology used by VSC.

### How does **vsc-tools** relate?

The repository vsc-tools was renamed to ifex to keep history and content.

Already before the rename, vsc-tools had been moving towards a formal language specification encoded in machine-readable files and source code that were actually part of the tool implementations.  Because of this tight link, the definition of the "VSC specification" (meaning the technology and description language) was already in practice shifting over from the VSC to the VSC-Tools repository.

After the name change all specifications for the IFEX core language and extensions, will be kept in the IFEX repository together with tool implementations.  The "VSC language" specification should be removed from the VSC project since it is now part of IFEX.  As explained above, the VSC project is free to continue gathering a catalog of services, and refer to IFEX as the chosen format and technology if that is still desired.

