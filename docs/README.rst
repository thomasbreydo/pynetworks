Description
-----------

A Python package that provides structure for networks of interconnected
nodes using the `DOT
language <https://en.wikipedia.org/wiki/DOT_(graph_description_language)>`_
for representation.

Installation
------------

The source code for **pynetworks** is hosted on
`GitHub <https://github.com/thomasbreydo/pynetworks>`_. You can install
**pynetworks** with pip:

.. code:: zsh

    pip install pynetworks

Documentation
-------------

Read the full documentation for **pynetworks**
`here <https://pynetworks.readthedocs.io>`_.

Example Usage
-------------

``Node``
~~~~~~~~

.. code:: python3

    >>> a = Node('A')
    >>> b = Node('B')
    >>> a.connect(b, 3)

Printing ``a`` gives:

::

    graph {
        "A" -- "B" [label=3]
    }

``shortest_path()``
~~~~~~~~~~~~~~~~~~~

.. code:: python3

    >>> a = Node('A')
    >>> b = Node('B')
    >>> c = Node('C')
    >>> a.connect(b, 3)
    >>> b.connect(c, 5)
    >>> path = shortest_path(a, c)
    >>> path.weight
    8

Printing ``path`` gives:

::

    graph {
        "B" -- "C" [label=5]
        "A" -- "B" [label=3]
    }

``Network``
~~~~~~~~~~~

.. code:: python3

    >>> a = Node('A')
    >>> b = Node('B')
    >>> c = Node('C')
    >>> a.connect(b, 3)
    >>> net = Network([a, b, c])

Printing ``net`` gives:

::

    graph {
        "C"
        "A" -- "B" [label=3]
    }

License
-------

`GNU </LICENSE>`_.
