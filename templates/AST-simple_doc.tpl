{% for x in item.children: %}
{{ gen(x, Service) }}
{% endfor %}
