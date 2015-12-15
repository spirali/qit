from qit.base.type import Type

class Class(Type):

    autoname_prefix = "Class"

    def __init__(self, self_type, methods):
        self.self_type = self_type
        self.methods = tuple(methods)
        assert (m.name is not None for m in self.methods)
        assert (len(m.params) > 0 and m.params[0].type == self_type
                for m in self.methods)

    @property
    def childs(self):
        return self.methods

    def get_variables(self):
        return ()

    def is_python_instance(self, obj):
        return self.self_type.is_python_instance(obj)

    def transform_python_instance(self, obj):
        return self.self_type.value(obj)

    def build_value(self, builder, value):
        return "{}({})".format(self.build(builder), value.build(builder))

    def declare(self, builder):
        if not builder.check_declaration_key(self):
            return
        builder.write_code(
        """
            class {{class_type}} {
                public:
                {{class_type}}() {}
                {{class_type}}({{type}} self) : self(self) {}

                {%- for m in _methods %}
                {{ m.build_declaration(_builder, m.name, True) }}
                {%- if m.params[0].const %} const {% endif %}
                {
                    {% if m.return_type %}return {% endif %}
                    {{m.build_closure(_builder, "self.")}}(self
                    {%- for p in m.params[1:] %}
                        , {{p.name}}
                    {%- endfor %}
                    );
                }
                {%- endfor %}

                private:
                {{type}} self;
            };
        """, { "class_type" : self,
               "type" : self.self_type,
               "_methods" : self.methods})
