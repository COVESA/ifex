{# Protobuf template #}
{# (C) 2022 Robert Bosch GmbH #}
// protobuf code generated by AST_protobuf.tpl
{# https://developers.google.com/protocol-buffers/docs/proto#services #}
syntax = "proto3";

{# Define Types #}
{# Not all vsc types can be represented as is in protobuf  #}
{% set typedefs = dict() %}
{# Add all type conversion  #}
{% set x=typedefs.__setitem__("int16", "int32") %}
{% set x=typedefs.__setitem__("uint8", "uint32") %}
{% set x=typedefs.__setitem__("uint16", "uint32") %}
{% set x=typedefs.__setitem__("boolean", "bool") %}

{# Macro to convert IFEX types to protobuf, handling arrays #}
{% macro convert_type(datatype) -%}
  {%- if datatype in typedefs -%}
    {%- set base_type = typedefs[datatype] -%}
  {%- else -%}
    {%- set base_type = datatype -%}
  {%- endif -%}
  {%- if base_type.endswith('[]') -%}
    repeated {{ base_type[:-2]|replace(".", "_") }}
  {%- else -%}
    {{ base_type|replace(".", "_") }}
  {%- endif -%}
{%- endmacro %}

package swdv.{{item.name}};

// Generic result message
message operation_result {
  bool result = 1;
}

   {% for n in item.namespaces %}
// IFEX Namespace {{n.name}}
{# Typedefs and enum must be handled before structs, to convert types right #}
{# Limitation: for now we ignore namespaces #}
      {% for t in n.typedefs %}
// IFEX Typedef {{t.name}}
        {# Typedef - Just using base type, but check if that one also needs to be expanded #}          
        {% if t.datatype in typedefs %}
          {% set type = typedefs[t.datatype] %}
        {% else %}
          {% set type = t.datatype %}
        {% endif %}
        {% set x=typedefs.__setitem__(t.name, type) %}

      {% endfor %}
      {% for t in n.enumerations %}
// IFEX Enum {{t.name}}
enum {{t.name}} {
         {% for x in t.options %}
    {{ x.name }} = {{ loop.index - 1}};
         {% endfor %}
}

      {% endfor %}
      {% for x in n.structs %}
// IFEX Struct {{x.name}}
          {# Cannot use dots in names #}
message {{x.name}} {
          {% for m in x.members %}
  {{ convert_type(m.datatype) }} {{ m.name }} = {{ loop.index }};
          {% endfor %}
}

      {% endfor %}
      {% for x in n.methods %}
// IFEX Method {{x.name}}
message {{ x.name }}_request {
         {% for x in x.input %}
  {{ convert_type(x.datatype) }} {{ x.name }} = {{ loop.index }};
         {% endfor %}
}

message {{ x.name }}_response {
         {% for x in x.output %}
  {{ convert_type(x.datatype) }} {{ x.name }} = {{ loop.index }};
         {% endfor %}
}

service {{ x.name }}_service {
  rpc {{ x.name }}({{ x.name }}_request) returns ({{ x.name }}_response);
}

      {% endfor %}

      {% for x in n.events %}
// IFEX Event {{x.name}}
      {# Limitation: for now just creating a message #}
message {{ x.name }} {
         {% for x in x.input %}
  {{ convert_type(x.datatype) }} {{ x.name }} = {{ loop.index }};
         {% endfor %}
}

      {% endfor %}

      {% for x in n.properties %}
// IFEX Property {{x.name}}
message {{ x.name }}_value {
  {{ convert_type(x.datatype) }} value = 1;
}

// To request value in read operation
message {{ x.name }}_request {}

        {# With current specification all properties are read/write #}
service {{ x.name }} {
  rpc {{ x.name }}_read({{ x.name }}_request) returns ({{ x.name }}_value);
  rpc {{ x.name }}_write({{ x.name }}_value) returns (operation_result);
}

      {% endfor %}
   {% endfor %}


