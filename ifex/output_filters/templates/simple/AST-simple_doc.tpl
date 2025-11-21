AST: {{item.name}}
     {{item.minor_version}}
     {{item.major_version}}
     Descr: {{item.description}}
     Includes:
{% for i in item.includes: %}
        File: {{i.file}} ({{i.description}})
{% endfor %}
{% for n in item.namespaces: %}
{{ gen(n) }}
{% endfor %}
