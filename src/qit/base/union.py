
from qit.base.type import Type
from qit.base.enum import Enum
from qit.base.int import Int
from qit.base.utils import stable_unique


class Union(Type):

    def __init__(self, types=None, **kw):
        if types is not None:
            self.tag_type = Int()
        else:
            tags = []
            types = []
            for k in sorted(kw.keys()):
                tags.append(k)
                types.append(kw[k])
            self.tag_type = Enum(*tags)
        self.types = tuple(types)
        assert self.types

    @property
    def childs(self):
        return tuple(t for t in self.types if t) + (self.tag_type,)

    @property
    def has_names(self):
        return isinstance(self.tag_type, Enum)

    @property
    def tags(self):
        if self.has_names:
            return self.tag_type.names
        else:
            return range(len(self.types))

    def is_python_instance(self, obj):
        return isinstance(obj, tuple) and len(obj) == 2

    def transform_python_instance(self, obj):
        tag, data = obj
        index = self.tags.index(tag)
        t = self.types[index]
        if t is None:
            return (self.tag_type.value(tag), None)
        else:
            return (self.tag_type.value(tag), t.value(data))

    def childs_from_value(self, value):
        if value[1] is None:
            return ()
        return (value[1],)

    def declare(self, builder):
        if builder.check_declaration_key(self):
            return
        utypes = stable_unique(self.types)

        types = list(zip(self.tags,
                     ((t, utypes.index(t) if t else None)
                          for t in self.types)))

        builder.write_code(
        """class {{self_type}} {
                public:
                {{self_type}}() : _tag({{init}}) {
                    {%- if _utypes[0] %}
                    new(&data.d0) {{b(_utypes[0])}}();
                    {%- endif %}
                }

                {{self_type}}(const {{self_type}} &other) : _tag(other._tag) {
                    switch (_tag) {
                        {%- for name, (t, i) in _types %}
                            case {{name}}:
                                {%- if t %}
                                    new(&data.d{{i}}) {{b(t)}}(other.data.d{{i}});
                                {%- endif %}
                                return;
                        {%- endfor %}
                    }
                    assert(0);
                }

                {%- for t in _utypes %}
                    {% if t %}
                    {{self_type}}({{tag_type}} tag, {{b(t)}} const &value) : _tag(tag) {
                        new(&data.d{{loop.index0}}) {{b(t)}}(value);
                    }
                    {% else %}
                    {{self_type}}({{tag_type}} tag) : _tag(tag) {}
                    {% endif %}
                {%- endfor %}

                ~{{self_type}}() {
                        free();
                    }

                {{tag_type}} tag() const {
                    return _tag;
                }

                {%- for name, (t, i) in _types %}
                    {%- if t %}
                    {{b(t)}}& get{{name}}() {
                        return data.d{{i}};
                    }
                    const {{b(t)}}& get{{name}}() const {
                        return data.d{{i}};
                    }

                    void set{{name}}(const {{b(t)}} &value) {
                        free();
                        _tag = {{name}};
                        {%- if t %}
                        new(&data.d{{i}}) {{b(t)}}(value);
                        {%- endif %}
                    }


                    {%- endif %}

                    void set{{name}}() {
                        free();
                        _tag = {{name}};
                        {%- if t %}
                        new(&data.d{{i}}) {{b(t)}}();
                        {%- endif %}
                    }
                {%- endfor %}

                bool operator==(const {{self_type}} &other) const {
                    if (other._tag != _tag) {
                        return false;
                    }
                    switch (_tag) {
                        {%- for name, (t, i) in _types %}
                            case {{name}}:
                                {%- if t %}
                                    return data.d{{i}} == other.data.d{{i}};
                                {%- else %}
                                    return true;
                                {%- endif %}
                        {%- endfor %}
                    }
                    assert(0);
                }

                bool operator<(const {{self_type}} &other) const {
                    if (_tag < other._tag) {
                        return true;
                    }
                    if (_tag == other._tag) {
                        switch (_tag) {
                            {%- for name, (t, i) in _types %}
                                {%- if t %}
                                case {{name}}:
                                        return data.d{{i}} < other.data.d{{i}};
                                {%- endif %}
                            {%- endfor %}
                        }
                    }
                    return false;
                }

                {{self_type}} & operator= (const {{self_type}} &other)
                {
                    if (this != &other)
                    {
                        switch (other.tag()) {
                            {%- for name, (t, i) in _types %}
                                case {{name}}:
                                    {%- if t %}
                                        set{{name}}(other.get{{name}}());
                                    {%- else %}
                                         set{{name}}();
                                    {%- endif %}
                                    break;
                            {%- endfor %}
                            default: assert(0);
                        }
                    }
                    return *this;
                }


                protected:

                void free() {
                    switch (_tag) {
                            {%- for name, (t, i) in _types %}
                                case {{name}}:
                                    {%- if t %}
                                    data.d{{i}}.{{t.build_destructor(_builder)}}();
                                    {%- endif %}
                                    return;
                            {%- endfor %}
                        }
                        assert(0);
                }

                {{tag_type}} _tag;
                union Data {
                    Data() {};
                    ~Data() {};
                {%- for t in _utypes %}
                    {%- if t %}
                    {{b(t)}} d{{loop.index0}};
                    {%- endif %}
                {%- endfor %}
                } data;
            };
        """, {"tag_type" : self.tag_type,
              "_types" : types,
              "_utypes" : utypes,
              "self_type" : self,
              "init" : self.tag_type.first() if self.has_names else self.tag_type.value(0) })

    def read(self, f):
        if self.has_names:
            tag_index = self.tag_type.read_index(f)
            tag = self.tag_type.names[tag_index]
        else:
            tag_index = self.tag_type.read(f)
            tag = tag_index
        if tag_index is None:
            return None
        t = self.types[tag_index]
        if t is None:
            return (tag, None)
        value = self.types[tag_index].read(f)
        assert value is not None
        return (tag, value)

    @property
    def write_function(self):
        functions = tuple(t.write_function if t else None for t in self.types)
        tag_functions=zip(self.tags, functions)
        f = self.prepare_write_function()
        f.code("""
            {{tag_type}} tag = value.tag();
            {{write_tag}}(output, tag);
        switch (tag) {
            {%- for name, f in _tag_functions %}
                {% if f %}
                case {{name}}:
                    {{b(f)}}(output, value.get{{name}}());
                    return;
                {% endif %}
            {%- endfor %}
        };
        """,
            _tag_functions=tag_functions,
            tag_type=self.tag_type,
            write_tag=self.tag_type.write_function)
        f.uses(filter(None, functions))
        return f

    def build_value(self, builder, value):
        tag, data = value
        if data is None:
            return "{}({})".format(
                    self.build(builder), tag.build(builder))
        else:
            return "{}({}, {})".format(
                    self.build(builder), tag.build(builder), data.build(builder))

def Maybe(type):
    return Union(Nothing=None, Just=type)
