
Types
=====


Int
---

.. py:class:: qit.Int()

Basic integer type. In C++ code it is translated as ``qint``, that is 32bit signed integer by default.::

    ctx = Qit()
    v = Int().value(10)
    ctx.run(v) # 10

    f = Function().takes(Int(), "a").returns(Int()).code("return a + 1;")
    ctx.run(f(10)) # 11

Struct
------

Vector
------


Set
---


Enum
----


Union
-----


Maybe
-----


KeyValue
--------
