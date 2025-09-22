<!-- SPDX-FileCopyrightText: Copyright (c) 2025 Mercedes-Benz Tech Innovation GmbH -->
<!-- SPDX-FileCopyrightText: Copyright (c) 2022-2025 MBition GmbH -->
<!-- SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB -->
<!-- SPDX-FileCopyrightText: Copyright (c) 2022 COVESA -->
<!-- SPDX-FileCopyrightText: Copyright (c) 2021 Magnus Feuers -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# IFEX CORE SPECIFICATION

This document contains an introduction to the Interface Exchange (IFEX)
framework and specification of the core Interface Description Language/Model
(also known as ifex-idl and ifex-core). IFEX is the name for the _technology_
(language, tools, etc.) behind the Vehicle Service Catalog (VSC) project.

License: Creative Commons Attribution 4.0 International
License (CC-BY-4.0), described [here](https://creativecommons.org/licenses/by/4.0/)

---

[[toc]]

<!-- Features and introduction -->
<!--@include:./static-general-description.md-->

## FUNDAMENTAL TYPES

These are the supported fundamental (primitive) types, as generated from the source code model. These primitive types are identical to the types used in the VSS (Vehicle Signal Specification) model, and of course they should easily match typical datatypes in other interface description systems.

<!--@include:./generated-types.generated.md-->

<!-- Layers concept, IFEX File Syntax, semantics and structure -->
<!--@include:./static-files-and-layers.md-->

## NODE TYPES

The chapters that follow this one specify the node types for the core interface language/model. They are generated from a "source of truth" which is the actual python source code of `ifex_ast.py`. This means that while the examples are free-text and may need manual updating, the list of fields and optionality should always match the behavior of the tool(s). => Always trust the tables over the examples, and report any discrepancies.

<!--@include:./ast-structure.generated.md-->
