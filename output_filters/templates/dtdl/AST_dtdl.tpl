{# DTDL template #}
{# (C) 2022 Robert Bosch GmbH #}
{# Limitations: Only one namespace expected #}
{# Global variables #}
{% set ns = namespace() %}
{% set ns.preceeding_items = 0 %}
{% set ns.current_type = "" %}
{% set ns.typedefs = dict() %}
{% macro optional_comma() %}
      {# Comma handling, TODO make it nicer #}
      {% if ns.preceeding_items > 0 %}
      {{- ',' -}}
      {% endif %}
      {% set ns.preceeding_items = 1 + ns.preceeding_items %}
{% endmacro %}
{% macro set_type(itemtype) -%}
  {% if itemtype in ns.typedefs %}
    {% set ns.current_type = ns.typedefs[itemtype] -%}
  {% else %}
    {% set ns.current_type = itemtype -%}
  {% endif %}
{%- endmacro %}

{% macro save_type(name,typename) -%}
  {% set x=ns.typedefs.__setitem__(name, typename) %}
{%- endmacro %}

{# Macro to strip newline in description #}
{% macro print_description(x) -%}
"description": "{{ x.description.strip().replace("\n", " ") }}"
{%- endmacro %}

{# Define Types #}
{# Not all ifex types can be represented in dtdl  #}
{# Add all type conversion  #}
{{ save_type("uint16", "integer") }}
{{ save_type("int16", "integer") }}
{{ save_type("uint8", "integer") }}
{{ save_type("boolean", "boolean") }}
{# Indentation off due to that service now is on top level #}
[
  {# Generate a component for every namespace #}
  {
     "@id": "dtmi:global:covesa:{{item.name}};1",
     "@type": "Interface",
     "displayName": "{{item.name}}",
     "contents": [
  {% for n in item.namespaces %}
       {
         "@type": "Component",
         "name": "{{n.name}}",
         "schema": "dtmi:global:covesa:{{item.name}}:{{n.name}};1"
       }
  {% endfor %}
     ],
     "@context": "dtmi:dtdl:context;2"
  },

  {# DTDL require commands to be listed first, before schemas so we need to do some analysis on types first#}
  {% for n in item.namespaces %}

    {% for t in n.typedefs %}
      {# Typedef - Just using base type, but check if that one also needs to be expanded #}
      {{- set_type(t.datatype) -}}
      {{- save_type(t.name, ns.current_type) -}}
    {% endfor %}
    {% for t in n.enumerations %}
      {# Enums - Will be represented, just add schema #}
      {% set full_name = "dtmi:global:covesa:" + item.name + ":" + n.name + ":" + t.name + ";1" %}
      {{- save_type(t.name, full_name) -}}
    {% endfor %}
    {% for x in n.structs %}
      {# Structs - Will be represented, just add schema #}
      {% set full_name = "dtmi:global:covesa:" + item.name + ":" + n.name + ":" + x.name + ";1" %}
      {{- save_type(x.name, full_name) -}}
    {% endfor %}
  {% endfor %}
 
  {# Generate an interface for every namespace #}
  {% for n in item.namespaces %}
  {
    "@id": "dtmi:global:covesa:{{item.name}}:{{n.name}};1",
    "@type": "Interface",
    "displayName": "{{n.name}}",
    "contents": [
    {# And each method #}
    {% for x in n.methods %}
      {{ optional_comma() }}
      {
        "@type": "Command",
        "name": "{{x.name}}",
        {{ print_description(x) -}},
        {# First in-parameters#}
        {% if x.input|length > 1 %}
        "request": {
          "name": "in",
          "comment": "Using generic name `in` when using inline struct",
          "schema": {
            "@type": "Object",
            "fields": [
          {% for m in x.input %}
              { 
                {{ set_type(m.datatype) -}}
                "name": "{{m.name}}",
                "schema": "{{ns.current_type}}",
                {{ print_description(m) }}
            {% if loop.last %}
              }
            {% else %}
              },
            {% endif %}
          {% endfor %}
            ]
          }
        }
        {% elif x.input|length == 1 %}
        {% set elem = x.input|first %}
        {{ set_type(elem.datatype) -}}
        "request": {
          "name": "{{elem.name}}",
          "schema": "{{ns.current_type}}",
          {{ print_description(elem) }}
        }
        {% endif %}
        {# Comma if needed#}
        {% if x.input|length != 0 %}
          {% if x.output|length != 0 %}
        ,
          {% endif %}
        {% endif %}
        {# Now out-parameters#}
        {% if x.output|length > 1 %}
        "response": {
          "name": "out",
          "comment": "Using generic name `out` when using inline struct",
          "schema": {
            "@type": "Object",
            "fields": [
          {% for m in x.output %}
              { 
            {{ set_type(m.datatype) -}}
                "name": "{{m.name}}",
                "schema": "{{ns.current_type}}",
                {{ print_description(m) }}
            {% if loop.last %}
              }
            {% else %}
              },
            {% endif %}
          {% endfor %}
            ]
          }
        }
        {% elif x.output|length == 1 %}
          {% set elem = x.output|first %}
          {{- set_type(elem.datatype) }}
        "response": {
          "name": "{{elem.name}}",
          "schema": "{{ns.current_type}}",
          {{ print_description(elem) }}
        }
        {% endif %}
      }
    {% endfor %}

    {# And each event #}
    {% for x in n.events %}
      {{ optional_comma() }}
      {
        "@type": "Telemetry",
        "name": "{{x.name}}",
        {{ print_description(x) -}},
        {# First in-parameters#}
        {% if x.input|length > 1 %}
        "schema": {
          "@type": "Object",
          "fields": [
          {% for m in x.input %}
            { 
            {{- set_type(m.datatype) }}
              "name": "{{m.name}}",
              "schema": "{{ns.current_type}}",
              {{ print_description(m) }}
            {% if loop.last %}
            }
            {% else %}
            },
            {% endif %}
          {% endfor %}
          ]
        }
        {% elif x.input|length == 1 %}
          {% set elem = x.input|first %}
          {{ set_type(elem.datatype) -}}
          "schema": "{{ns.current_type}}"
        {% endif %}
      }
    {% endfor %}

    {# And each property, for now always read/write#}
    {% for x in n.properties %}
      {{ optional_comma() }}
      {
        "@type": "Property",
        "writable": true,
        "name": "{{ x.name }}",
        {{ print_description(x) -}},
        {{ set_type(x.datatype) -}}
        "schema": "{{ns.current_type}}"
      }
    {% endfor %}
    ],
    "schemas": [
    {% set ns.preceeding_items = 0 %}
    {% for t in n.enumerations %}
      {{ optional_comma() }}
      {
        "@id": "{{ns.typedefs[t.name]}}",
        "@type": "Enum",
        {{ print_description(t) -}},
        {# TODO: Add functionality to support string schema as well, if wanted #}
        "valueSchema": "integer",
        "enumValues": [
        {% for x in t.options %}
          {
            "name": "{{x.name}}",
            "enumValue": {{ loop.index - 1}}
          {% if loop.last %}
          }
          {% else %}
          },
          {% endif %}
        {% endfor %}
        ]
      }
    {% endfor %}
    {% for x in n.structs %}
      {{ optional_comma() }}
      {
        "@id": "{{ns.typedefs[x.name]}}",
        "@type": "Object",
        {{ print_description(x) -}},
        "fields": [
        {% for m in x.members %}
          {{ set_type(m.datatype) -}}
          {
            "name": "{{m.name}}",
            "schema": "{{ns.current_type}}",
            {{ print_description(m) }}
          {% if loop.last %}
          }
          {% else %}
          },
          {% endif %}
        {% endfor %}
        ]
      }
    {% endfor %}
    ],
    "@context": "dtmi:dtdl:context;2"
  }
  {% endfor %}
]
