{% if item.description != None %}
<!-- Enumeration {{item.name}} = {{item.description.strip()}} -->
{% endif %}
<!-- Enumeration {{item.name}} values are : {% for o in item.options %}{{o.name}} = {{o.value}}, {% endfor %} -->
