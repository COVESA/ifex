{% if item.description != None %}
<!-- member {{item.name}} of type {{item.datatype}} = {{item.description.strip()}} -->
{% else %}
<!-- member {{item.name}} of type {{item.datatype}} -->
{% endif %}
