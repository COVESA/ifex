# Comments on the LICENSE file of this directory.

## Applicability:

- `LICENSE.json-schema` (Revised BSD license) applies ONLY to the file `json-schema.org_draft_2020-12_schema`
- All _other_ files in this directory are subject to the license of the IFEX project repository, and information can be found in the root directory of the repository.

## Additional information

JSON-Schema is a specification published by the Internet Engineering Task Force (IETF) at this location: https://json-schema.org/specification

The IFEX project includes a file named `json-schema.org_draft_2020-12_schema` which is a copy of the meta-schema ("JSON-schema for JSON-schemas")
It is used to validate that the JSON schema we generate is itself valid against the specification.

The meta-schema, has been downloaded from this standard well-known URL:  https://json-schema.org/draft/2020-12/schema
(The link to this file and to specifications can otherwise be found at: https://json-schema.org/specification-links) 

The JSON Schema Core Specification, specifically the one stored here: https://json-schema.org/draft/2020-12/json-schema-core is at the time of writing the following version:

   Internet-Draft: draft-bhutton-json-schema-01
   Published: 16 June 2022

That specification states:

> "Code Components extracted from this document must include Revised BSD License text as described in Section 4.e of the Trust Legal Provisions"

It references this address for the legal provisions:  `https://trustee.ietf.org/documents/trust-legal-provisions/`

The legal provisions include the Revised BSD license text, which is provided here in `LICENSE.json-schema`

- Since JSON documents cannot include comments, the actual meta-schema file itself does not include any Copyright/License information.
- It is interpreted as being a "code component" deriving from the JSON-Schema Specification, as per the above description.
- Thus, the file is subject to the Revised BSD License text as described in the Trust Legal Provisions. The license text is stored in the file `LICENSE.json-schema` in this directory.
