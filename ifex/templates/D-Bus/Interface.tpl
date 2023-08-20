<interface name="{{get_interface_name(item.name)}}">
{% for x in item.methods + item.properties + item.events %}
{{ gen(x) }}
{% endfor %}

{# Definition of named structs and other datatypes have little meaning in D-Bus, but we can generate some comments about them: #}
{% for x in item.structs %}
{{gen(x)}}
{% endfor %}

{% for x in item.typedefs %}
{{gen(x)}}
{% endfor %}

{% for x in item.enumerations %}
{{gen(x)}}
{% endfor %}
</interface>
