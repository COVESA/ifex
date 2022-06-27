-----------------------------------------
Header
-----------------------------------------
{% for s in item.children %}
   Servicename: {{ s.name }}
   -> {{ s.description }}
   {% for n in s.namespaces %}
      Namespace: {{ n.name }}
      -> {{ n.description }}
      {% for x in n.structs %}
         Struct: {{ x.name }}
         -> {{ x.description }}
         {% for x in x.members %}
            member: {{ x.name }} (of type {{x.datatype}}) 
         {% endfor %}
      {% endfor %}
      {% for x in n.typedefs %}
         Typedef: {{ x.name }}
         -> {{ x.description }} 
         -> Datatype: {{ x.datatype }}
         -> Min: {{ x.min }}
         -> Max: {{ x.max }}
      {% endfor %}
      {% for x in n.enumerations %}
         Enum: {{ x.name }}
         -> {{ x.description }} 
         {% for x in x.options %}
            Options name: {{ x.name }} (of value {{x.value}}) 
         {% endfor %}
      {% endfor %}
      {% for x in n.methods %}
         Method: {{ x.name }}
         -> {{ x.description }}
         {% for x in x.in %}
            in: {{ x.name }} (of type {{x.datatype}}) 
         {% endfor %}
         {% for x in x.out %}
            out: {{ x.name }} (of type {{x.datatype}}) 
         {% endfor %}
      {% endfor %}
      {% for x in n.events %}
         Event: {{ x.name }}
         -> {{ x.description }}
         {% for x in x.in %}
            in: {{ x.name }} (of type {{x.datatype}}) 
         {% endfor %}
      {% endfor %}
      {% for x in n.properties %}
         Property: {{ x.name }}
         -> {{ x.description }}
         -> Type: {{ x.datatype }}
      {% endfor %}
   {% endfor %}
{% endfor %}
-----------------------------------------
Footer
-----------------------------------------

