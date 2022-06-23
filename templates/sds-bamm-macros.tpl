{# Dictionary of created element to avoid duplicate elements #}
{% set bammElementDictonary = ({}) %}

{# Render the list of names as references for the given elements #}
{% macro element_names(elements, isProperty=false) %}
    {%if elements %}{%- for element in elements %} :{{ snake_to_camel(element.name.capitalize()) if not isProperty else snake_to_camel(element.name) }}{{ "" if not loop.last else " " }}{% endfor %}{% endif %}
{% endmacro %}

{# Convert a string from snake to camel case #}
{% macro snake_to_camel(name) %}
    {%- for x in name.split('_') -%}
        {% if x != "t" %}{{ x.capitalize() if not loop.first else x }}{% endif %}
    {% endfor %}
{% endmacro %}

{# Render an Aspect definition based on a VSC Namespace #}
{% macro render_aspect(element) %}
:{{ element.name.capitalize() }} a bamm:Aspect ;
    bamm:name "{{ element.name.capitalize() }}" ;
    bamm:description "{{ element.description }}"@en ;
    bamm:properties () ;
    bamm:operations ({{ element_names(element.methods) }}) ;
    bamm:events ({{ element_names(element.events) }}) .
{% endmacro %}

{# Render a Operation definition based on a VSC Method #}
{% macro render_operation( method) %}
{% if not method.name in bammElementDictonary %}
{%- set _ = bammElementDictonary.update({method.name: method}) -%}
:{{ snake_to_camel(method.name.capitalize()) }} a bamm:Operation ;
    bamm:name "{{ snake_to_camel(method.name.capitalize()) }}" ;
    bamm:description "{{ method.description }}"@en ;
    bamm:input ({{ element_names(method.in, true) }}) {{ ";" if method.out|length > 0 else "." }} 
    {% if method.out|length > 0 %}
    bamm:output {{ element_names([method.out[0]], true) }} .
    {% endif %}
{% endif %}
{% endmacro %}

{# Render a Property definition based on a VSC Member #}
{% macro render_property(member) %}
{% if not member.name in bammElementDictonary -%}
{%- set _ = bammElementDictonary.update({member.name: member}) -%}
:{{ snake_to_camel(member.name) }} a bamm:Property ;
    bamm:name "{{ snake_to_camel(member.name) }}" ;
    bamm:description "{{ member.description }}"@en ;
    bamm:characteristic :{{ _render_characteristic_name(member) }} .
{% endif -%}
{% endmacro %}

{# Render an Event definition based on a VSC Event #}
{% macro render_event(event) %}
{% if not event.name in bammElementDictonary %}
{%- set _ = bammElementDictonary.update({event.name: event}) -%}
:{{ snake_to_camel(event.name.capitalize()) }} a bamm:Event ;
    bamm:name "{{ snake_to_camel(event.name.capitalize()) }}" ;
    bamm:description "{{ event.description }}"@en ;
    bamm:parameters ({{ element_names(event.in, true) }}) .
{% endif %}
{% endmacro %}

{# Render an Entity definition based on a VSC Struct #}
{% macro render_entity(struct) %}
{% if not struct.name in bammElementDictonary %}
{%- set _ = bammElementDictonary.update({struct.name: struct}) -%}
:{{ snake_to_camel(struct.name.capitalize()) }} a bamm:Entity ;
    bamm:name "{{ snake_to_camel(struct.name.capitalize()) }}" ;
    bamm:description "{{ struct.description }}"@en ;
    bamm:properties ({{ element_names(struct.members, true) }}) .
{% endif %}
{% endmacro %}

{# Render a Characteristic definition based on a VSC Member #}
{% macro render_characteristic(member) %}
{% set characteristic_name = _render_characteristic_name(member) -%}
{% if not characteristic_name in bammElementDictonary %}
{%- set _ = bammElementDictonary.update({characteristic_name: member}) -%}
:{{ characteristic_name }} a {{ _render_characteristic_definition(member) }} ;
     bamm:name "{{ characteristic_name }}" ;
     bamm:description "{{ member.description }}"@en ;
     {% if (member.min is defined) and (member.min or member.max) %}
     bamm-c:baseCharacteristic :{{ characteristic_name }}Base ;
     bamm-c:constraint [
        {{ _render_range_constraint_definition(member) | indent }}
     ] .
     {% else -%}
     {% if member.datatype and not member.datatype.endswith("_t") %}
     bamm:dataType {{ _render_datatype(member.datatype) }} .
     {% else %}
     bamm:dataType {{ _render_characteristic_type(member) }} .
     {% endif %}
     {% endif -%}

{% if (member.min is defined) and (member.min or member.max) and not ((characteristic_name ~ "Base") in bammElementDictonary) %}

{{ render_characteristic({ "name": characteristic_name ~ "Base", "datatype": member.datatype, "description": member.description}) }}
{%- endif -%}
{% endif %}
{% endmacro %}

{% macro _render_range_constraint_definition(type) %}
a bamm-c:RangeConstraint ;
    {% if type.min %}
    bamm-c:minValue "{{ type.min }}"^^{{ _render_datatype(type.datatype) }} ;
    bamm-c:lowerBoundDefinition bamm-c:AT_LEAST;
    {% endif %}
    {% if type.max %}
    bamm-c:maxValue "{{ type.max }}"^^{{ _render_datatype(type.datatype) }} ;
    bamm-c:upperBoundDefinition bamm-c:AT_MOST;
    {%- endif -%}
{% endmacro -%}

{% macro _render_characteristic_definition(member) %}
{% set type = member.datatype -%}
{# With strict checking an error is received if trying to use min/max if not defined for the type #}
{% if (member.min is defined) and (member.min or member.max) %}
    {{- "bamm-c:Trait" -}}
{% elif type.endswith("[]") %}
    {{- "bamm-c:List" -}}
{% elif type.endswith("_t") %}
    {{- "bamm-c:SingleEntity" -}}
{% else %}
    {{- "bamm:Characteristic" -}}
{% endif %}
{% endmacro -%}

{# Render an Enumeration definition based on a VSC Enum #}
{% macro render_enumeration(enum) %}
{% set characteristic_name = _render_characteristic_name(enum) -%}
{% if not characteristic_name in bammElementDictonary %}
{%- set _ = bammElementDictonary.update({characteristic_name: enum}) -%}
:{{ characteristic_name }} a bamm-c:Enumeration ;
    bamm:name "{{ characteristic_name }}" ;
    bamm:dataType {{ _render_datatype(enum.datatype) }} ;
    bamm-c:values ( {% for option in enum.options %}{{ "\"" ~ option.value ~ "\"^^" ~ _render_datatype(enum.datatype) }}{{ " " if not loop.last else "" }}{% endfor %} ) .
{% endif %}    
{% endmacro %}

{# Render datatype #}
{%- macro _render_datatype(type) -%}
{%- if type == 'uint8' -%}
    xsd:unsignedByte
{%- elif type == 'int8' -%}
    xsd:byte
{%- elif type == 'uint16' -%}
    xsd:unsignedShort
{%- elif type == 'int16' -%}
    xsd:short
{%- elif type == 'int32' -%}
    xsd:int
{%- elif type == 'uint32' -%}
    xsd:unsignedInt
{%- elif type == 'int64' -%}
    xsd:long
{%- elif type == 'uint64' -%}
    xsd:unsignedLong
{%- elif type == 'boolean' -%}
    xsd:boolean
{%- elif type == 'float' -%}
    xsd:float
{%- elif type == 'double' -%}
    xsd:double
{%- elif type == 'string' -%}
    xsd:string
{%- elif type == 'byteBuffer' -%}
    xsd:base64Binary
{%- else -%}
    {{ type }}
{%- endif -%}    
{%- endmacro -%}

{# Render characteristic name #}
{%- macro _render_characteristic_name(member) -%}
{%- if member.name and member.name.startswith("Characteristic") -%}
{{ member.name }}
{%- elif member.datatype and member.datatype.endswith("_t") -%}
Characteristic{{ snake_to_camel(member.datatype.capitalize()) }}
{%- else -%}
Characteristic{{ snake_to_camel(member.name.capitalize()) }}
{%- endif -%}
{%- endmacro -%}

{# Render characteristic datatype #}
{%- macro _render_characteristic_type(member) -%}
:{{ snake_to_camel(member.datatype.capitalize()) }}
{%- endmacro -%}
