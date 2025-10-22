{% if item.interface != None %}
  {{gen(item.interface)}}
{% endif %}

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
