{% for x in item.children: %}
{{ gen(x) }}
{% endfor %}
