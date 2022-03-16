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
{% macro set_type(itemtype) %}
  {% if itemtype in ns.typedefs %}
    {% set ns.current_type = ns.typedefs[itemtype] %}
  {% else %}
    {% set ns.current_type = itemtype %}
  {% endif %}
{% endmacro %}
{% macro save_type(name,typename) %}
  {% set x=ns.typedefs.__setitem__(name, typename) %}
{% endmacro %}
{# Define Types #}
{# Not all vsc types can be represented in dtdl  #}
{# Add all type conversion  #}
{{ save_type("int16", "integer") }}
{{ save_type("uint8", "integer") }}
{{ save_type("boolean", "boolean") }}
{% for s in item.children %}
[
  {# Generate a component for every namespace #}
  {
     "@id": "dtmi:global:covesa:{{s.name}};1",
     "@type": "Interface",
     "displayName": "{{s.name}}",
     "contents": [
  {% for n in s.namespaces %}
       {
         "@type": "Component",
         "name": "seats",
         "schema": "dtmi:global:covesa:{{s.name}}:{{n.name}};1"
       }
  {% endfor %}
     ],
     "@context": "dtmi:dtdl:context;2"
  },

  {# DTDL require commands to be listed first, before schemas so we need to do some analysis on types first#}
  {% for n in s.namespaces %}

    {% for t in n.typedefs %}
      {# Typedef - Just using base type, but check if that one also needs to be expanded #}
      {{- set_type(t.datatype) -}}
      {{- save_type(t.name, ns.current_type) -}}
    {% endfor %}
    {% for t in n.enums %}
      {# Enums - Will be represented, just add schema #}
      {% set full_name = "dtmi:global:covesa:" + s.name + ":" + n.name + ":" + t.name + ";1" %}
      {{- save_type(t.name, full_name) -}}
    {% endfor %}
    {% for x in n.structs %}
      {# Structs - Will be represented, just add schema #}
      {% set full_name = "dtmi:global:covesa:" + s.name + ":" + n.name + ":" + x.name + ";1" %}
      {{- save_type(x.name, full_name) -}}
    {% endfor %}
  {% endfor %}
 
  {# Generate an interface for every namespace #}
  {% for n in s.namespaces %}
  {
    "@id": "dtmi:global:covesa:{{s.name}}:{{n.name}};1",
    "@type": "Interface",
    "displayName": "{{n.name}}",
    "contents": [
    {# And each method #}
    {% for x in n.methods %}
      {{ optional_comma() }}
      {
        "@type": "Command",
        "name": "{{x.name}}",
        "description": "{{ x.description }}",
        {# First in-parameters#}
        {% if x.in_arguments|length > 1 %}
        "request": {
          "name": "in",
          "comment": "Using generic name `in` when using inline struct",
          "schema": {
            "@type": "Object",
            "fields": [
          {% for m in x.in_arguments %}
              { 
            {{ set_type(m.type) }}
                "name": "{{m.name}}",
                "schema": "{{ns.current_type}}",
                "description": "{{m.description}}"
            {% if loop.last %}
              }
            {% else %}
              },
            {% endif %}
          {% endfor %}
            ]
          }
        }
        {% elif x.in_arguments|length == 1 %}
          {% set elem = x.in_arguments|first %}
          {{ set_type(elem.type) }}
        "request": {
          "name": "{{elem.name}}",
          "schema": "{{ns.current_type}}",
          "description": "{{ elem.description }}"
        }
        {% endif %}
        {# Comma if needed#}
        {% if x.in_arguments|length != 0 %}
          {% if x.out_arguments|length != 0 %}
        ,  
          {% endif %}
        {% endif %}
        {# Now out-parameters#}
        {% if x.out_arguments|length > 1 %}
        "response": {
          "name": "out",
          "comment": "Using generic name `out` when using inline struct",
          "schema": {
            "@type": "Object",
            "fields": [
          {% for m in x.out_arguments %}
              { 
            {{ set_type(m.type) }}
                "name": "{{m.name}}",
                "schema": "{{ns.current_type}}",
                "description": "{{m.description}}"
            {% if loop.last %}
              }
            {% else %}
              },
            {% endif %}
          {% endfor %}
            ]
          }
        }
        {% elif x.out_arguments|length == 1 %}
          {% set elem = x.out_arguments|first %}
          {{ set_type(elem.type) }}
        "response": {
          "name": "{{elem.name}}",
          "schema": "{{ns.current_type}}",
          "description": "{{ elem.description }}"
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
        "description": "{{ x.description }}",
        {# First in-parameters#}
        {% if x.in_arguments|length > 1 %}
        "schema": {
          "@type": "Object",
          "fields": [
          {% for m in x.in_arguments %}
            { 
            {{ set_type(m.type) }}
              "name": "{{m.name}}",
              "schema": "{{ns.current_type}}",
              "description": "{{m.description}}"
            {% if loop.last %}
            }
            {% else %}
            },
            {% endif %}
          {% endfor %}
          ]
        }
        {% elif x.in_arguments|length == 1 %}
          {% set elem = x.in_arguments|first %}
          {{ set_type(elem.type) }}
        "schema": "{{ns.current_type}}"
        {% endif %}
      }
    {% endfor %}

    {# And each property#}
    {% for x in n.properties %}
      {{ optional_comma() }}
      {
      {% if x.type == "sensor" %}
        "@type": "Telemetry",
      {% else %}
        "@type": "Property",
        {% if x.type == "actuator" %}
        "writable": true,
        {% else %}
        "writable": false,
        {% endif %}
      {% endif %}
        "name": "{{ x.name }}",
        "description": "{{ x.description }}",
      {{ set_type(x.datatype) }}
        "schema": "{{ns.current_type}}"
      }
    {% endfor %}
    ],
    "schemas": [
    {% set ns.preceeding_items = 0 %}
    {% for t in n.enums %}
      {{ optional_comma() }}
      {
        "@id": "{{ns.typedefs[t.name]}}",
        "@type": "Enum",
        "description": "{{ t.description }}",
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
        "description": "{{ x.description }}",
        "fields": [
        {% for m in x.members %}
          {{ set_type(m.type) }}
          {
            "name": "{{m.name}}",
            "schema": "{{ns.current_type}}",
            "description": "{{ m.description }}"
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
{% endfor %}
