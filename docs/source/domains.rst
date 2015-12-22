
Domains
=======

Domain is ...


Basic class `Domain`
--------------------

.. py:class:: qit.Domain(type, iterator=None, generator=None, size=None, indexer=None)

   Basic class for domains

   .. py:method:: generate()

   Returns iterator that calls the generator of the domain if domain is generable, otherwise throws an exception.

   .. py:method:: generate_one()

   Returns generator of the domain if domain is generable, otherwise throws an exception.

   .. py:method:: is_generable()

   Returns True if the domain has an generator

   .. py:method :: is_iterable()

   Returns True if the domain has an iterator

   .. py:method:: iterate()

   Return the iterator of the domain if domain is iterable, otherwise throws an exception.

   .. py:method:: values(*values)

   Makes :class:`qit.Values` domain where self.type is used as underlying type

   .. py:method:: variable(name)

   Create variable of domain’s type

   .. py:attribute:: size

   Number of elements in domain ::

        ctx = Qit()
        ctx.run(Range(2, 5)) # 3


Range
-----

.. py:class:: qit.Range(stop)
.. py:class:: qit.Range(start, stop)
.. py:class:: qit.Range(start, stop, step)

Range represents a linear set of integers (similar to :func:`range` in Python).
`Iterator` iterates from the minimal element to maximal with defined step.
`Generator` generates a random integer from the range. The domain type is :class:`qit.Int`. ::

    ctx = Qit()
    ctx.run(Range(4).iterate())        # [0, 1, 2, 3]
    ctx.run(Range(2, 6).iterate())     # [2, 3, 4, 5]
    ctx.run(Range(1, 10, 2).iterate()) # [1, 3, 5, 7, 9]


Product
-------

.. py:class:: qit.Product(domain1, domain2, ...)
.. py:class:: qit.Product((domain1, name1), (domain2, name1), ...)


Cartesian product of zero or more domains. It can be created explicitly by `Domain` constructor
or implicitly by `*` operator.::

    ctx = Qit()

    r2 = Range(2)
    p1 = Product(r, r, r)
    ctx.run(p1.iterate()) # [ (0, 0, 0), (0, 0, 1), (0, 1, 0), ... ]

    p2 = r * r * r
    p1 == p2 # True

    # Named product
    p3 = Product((r, "x"), (r, "y"), (r, "z"))
    p3.type == Struct((r, "x"), (r, "y"), (r, "z")) # True


Sequence
--------


Values
------

.. py:class:: qit.Values(type, *values)


Join
----


Enumerate
---------


Mapping
-------
