{% if item.description != "" %}<!-- Event (D-Bus signal): {{ item.description }} -->{% endif %}
<signal name="{{item.name}}">
{% for x in item.input: %}
<arg type="{{ gen_dbus_type(x.datatype) }}" name="{{x.name}}"/>
{% endfor %}
</signal>
