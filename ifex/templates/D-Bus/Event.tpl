{% if item.description != "" %}<!-- Event (D-Bus signal): {{ item.description }} -->{% endif %}
<signal name="{{item.name}}">
{% for x in item.output: %}
      <arg direction="in" type="{{ gen_dbus_type(x.datatype) }}" name="{{x.name}}"/>
{% endfor %}
{% for x in item.input: %}
      <arg direction="out" type="{{ gen_dbus_type(x.datatype) }}" name="{{x.name}}"/>
{% endfor %}
</signal>
