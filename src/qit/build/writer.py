

class CppWriter(object):

    def __init__(self):
        self.lines = []
        self.indent = ""

    def line(self, string, *a, **kw):
        self.lines.append(self.indent + string.format(*a, **kw))

    def emptyline(self):
        self.lines.append("")

    def indent_push(self):
        self.indent += "\t"

    def indent_pop(self):
        self.indent = self.indent[:-1]

    def iterate_end(self):
        self.block_end()

    def block_end(self):
        self.indent_pop()
        self.line("}}")

    def block_begin(self):
        self.line("{{")
        self.indent_push()

    def class_end(self):
        self.indent_pop()
        self.line("}};")

    def class_begin(self, name):
        self.line("class {} {{", name)
        self.indent_push()

    def if_begin(self, expr, *args, **kw):
        self.line("if ({}) {{", expr.format(*args, **kw))
        self.indent_push()

    def else_begin(self):
        self.indent_pop()
        self.line("}} else {{")
        self.indent_push()

    def get_string(self):
        return "\n".join(self.lines) + "\n"
