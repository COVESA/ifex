{% if item.description != None %}
<!-- Property: {{item.name}} = {{item.description.strip(" \t\n")}} -->
{% endif %}
<property name="{{item.name}}" type="{{gen_dbus_type(item.datatype)}}"/>
