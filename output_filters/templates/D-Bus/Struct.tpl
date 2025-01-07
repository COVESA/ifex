{% if item.description != None %}
<!-- Struct {{item.name}} = {{item.description.strip()}} -->
{% endif %}
<!-- Struct {{item.name}} defined as: { {% for m in item.members %}{{m.name}} ({{m.datatype}}), {% endfor %} } -->
<!-- Struct {{item.name}} members details: -->
{% for m in item.members %}
{% if m.description != None %}
<!-- member {{item.name}}:{{m.name}} of type {{m.datatype}} = {{m.description.strip()}} -->
{% else %}
<!-- member {{item.name}}:{{m.name}} of type {{m.datatype}} -->
{% endif %}
{% endfor %}
