# pynetworks

A Python package that provides structure for networks of interconnected nodes using the [DOT language](<https://en.wikipedia.org/wiki/DOT_(graph_description_language)>) for representation.

## Classes

### Node

Contain a named node, with weighted connections.

#### Attributes

- `self.name`: name of this `Node` (type `str`).
- `self.connections`: list of connected `Node` objects (inital
  value `[]`).

#### Methods

- `self.connect(other, weight)`: add `Connection` between `self`
  and `other` with `weight`.
- `self.disconnect(other, weight)`: remove `Connection` between
  `self` and `other` with `weight`.
- `self.isolate()`: disconnect from all connected `Node` objects.

#### Example:

```python3
>>> a = Node('A')
>>> b = Node('B')
>>> a.connect(b, 3)
>>> print(a)
graph {
    "A" -- "B" [label=3]
}
```

### Connection

Represent an optionally weighted connection between two `Node`
objects.

#### Attributes:

- `self.node1`: first `Node` in this `Connection`
- `self.node2`: second `Node` in this `Connection`
- `weight`: weight of this `Connection` (usually numerical, default
  `None`)

#### Methods:

- `self.reverse()`: return a `Connection` with the same `node1`,
  `node2`, and `weight`, BUT `node1` and `node2` swap.
- `self.dot()`: return DOT language representation of this
  `Connection` object.

### Network

Contain a network of interconnected `Node` objects.

#### Attributes:

- `self.all_nodes`: `set` of all nodes in this network (default
  `set()`).
- `self.name`: `name` of this network (type `str`, default `''`).
- `self.isolated_nodes`: `set` of all nodes with no connections.
- `self.connections`: `list` of all connections in this `Network`.

#### Methods:

- `self.update()`: update `self.connections` and
  `self.isolated_nodes`; run when `Node` objects in this network have
  changed.

### Path

Store `Connection` objects connecting two `Node` objects.

#### Attributes

- `self.connections`: `list` of all `Connection` objects in this
  `Path`.
- `self.weight`: sum of the weights of all `Connection` objects in
  this `Path` (usually numerical).

#### Methods

- `self.__add__(other)`: return a combined `Path` of `self` and `other`.

## Functions

### shortest_path

Find the shortest path between `start` and `end`.

#### Arguments:

- `start`: starting `Node` object (type: `Node`).
- `end`: final `Node` object (type: `Node`).

#### Return:

If a path exists from `start` to `end`, return that `Path` object. Otherwise, return `None`.

###

Generate a DOT graph out of nodes and connections.

#### Arguments:

- `isolated_nodes`: list of `Node` objects with no connections to
  graph (type `list`, default `[]`).
- `connections`: list of `Connection` objects to graph (type `list`,
  default `[]`).
- `name`: name of returned dotgraph (type `str`, default `''`).

#### Return:

A valid DOT graph (`str`).

#### Examples:

##### One isolated `Node` object.

```python3
>>> a = Node('A')
>>> print(dotgraph(isolated_nodes=[a], name='My Graph'))
>>> graph "My Graph" {
    "A"
}
```

##### Two connected `Node` objects.

```python3
>>> b = Node('B')
>>> c = Node('C')
>>> b.connect(c, 5)
>>> print(dotgraph(connections=b.connections))
>>> graph {
    "B" -- "C" [label=5]
}
```

### escape_dot_id

Surround in double quotes and escape all double quotes.

#### Arguments:

- `string`: the id to escape (type `str`).

#### Return:

A valid, escaped id for a DOT graph (type `str`).

#### Example:

```python3
>>> escape_dot_id('A"B')
>>> '"A\\"B"'
```

### generate_network

#### Arguments:

- `n_nodes`: number of nodes (type `int`, default `10`).
- `lower_bound`: lower bound (inclusive) of range of connections' weights (type `int`, default `1`).
- `upper_bound`: upper bound (exclusive) for range of connections' weights (type `int`, default `11`).
- `connections_prob`: probability betweeen 0 and 1 of any two nodes being connected (type `float`, default `0.8`). If `force_connected` is set to `True`, this setting might be overridden.
- `force_connected`: if `False`, output can be a disconnected network (type `bool`, default `True`).

#### Return:

A `set` of `n_nodes` interconnected `Node` objects.
