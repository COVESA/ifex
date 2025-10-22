{% if item.description != None %}
{# Here is how real doc tags can be created #}
{# But comments are enough if the XML will not be used to generated docs #}
{# <doc:doc><doc:description><doc:para>{{item.description.strip(" \t\n")}}</doc:para></doc:description></doc:doc> #}
<!-- Method: {{item.name}} = {{item.description.strip(" \t\n")}} -->
{% endif %}
<method name="{{item.name}}">
 
{% for arg in item.input %}
{% if arg.description != None %}
<!-- Input: {{arg.name}} = {{arg.description.strip(" \t\n")}} -->
{% endif %}
<arg name="{{arg.name}}" direction="in" type="{{gen_dbus_type(arg.datatype)}}"/>
{% endfor %}

{% for arg in item.output %}
{% if arg.description != None %}
<!-- Output: {{arg.name}} = {{arg.description.strip(" \t\n")}} -->
{% endif %}
<arg name="{{arg.name}}" direction="out" type="{{gen_dbus_type(arg.datatype)}}"/>
{% endfor %}

{% for arg in item.errors %}
{% if arg.description != None %}
<!-- FIXME: Generate error here, {{arg.name}} ({{arg.description}}) -->
{% else %}
<!-- FIXME: Generate error here, {{arg.name}} -->
{% endif %}
{% endfor %}
</method>

