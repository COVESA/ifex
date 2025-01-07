{# Collect namespace names for naming of interface.  (This does not generate any text) #}
{% for n in item.namespaces %}
{{ add_namespace(n) }}
{% endfor %}

{# Start of generation here #}
<!DOCTYPE node PUBLIC
    "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
    "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd" >
<node xmlns:doc="http://www.freedesktop.org/dbus/1.0/doc.dtd">
{% for n in item.namespaces %}
{{ gen(n) }}
{% endfor %}
</node>
