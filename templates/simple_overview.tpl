-----------------------------------------
Header
-----------------------------------------
{% for s in root.children %}
   Servicename: {{ s.name }}
   -> {{ s.description }}
   {% for i in s.interfaces %}
      Interface: {{ i.name }}
      -> {{ i.description }}
      {% for x in i.commands %}
         Command: {{ x.name }}
         -> {{ x.description }}
         {% for x in x.in_arguments %}
            in: {{ x.name }} (of type {{x.type}}) 
         {% endfor %}
      {% endfor %}
      {% for x in i.methods %}
         Method: {{ x.name }}
         -> {{ x.description }}
         {% for x in x.in_arguments %}
            in: {{ x.name }} (of type {{x.type}}) 
         {% endfor %}
         {% for x in x.out_arguments %}
            out: {{ x.name }} (of type {{x.type}}) 
         {% endfor %}
      {% endfor %}
      {% for x in i.events %}
         Event: {{ x.name }}
         -> {{ x.description }}
         {% for x in x.in_arguments %}
            in: {{ x.name }} (of type {{x.type}}) 
         {% endfor %}
      {% endfor %}
   {% endfor %}
{% endfor %}
-----------------------------------------
Footer
-----------------------------------------

