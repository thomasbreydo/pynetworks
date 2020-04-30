from .functions import dotgraph, escape_dot_id


class Node:
    '''Contain a named node, with weighted connections.

    Attributes
    --
    - `self.name`: name of this `Node` (type `str`).
    - `self.connections`: list of connected `Node` objects (inital
    value `[]`).

    Methods
    --
    - `self.connect(other, weight)`: add `Connection` between `self`
    and `other` with `weight`.
    - `self.disconnect(other, weight)`: remove `Connection` between
    `self` and `other` with `weight`.
    - `self.isolate()`: disconnect from all connected `Node` objects.

    Example:
    --
    >>> a = Node('A')
    >>> b = Node('B')
    >>> a.connect(b, 3)
    >>> print(a)
    graph {
        "A" -- "B" [label=3]
    }
    '''

    def __init__(self, name):
        self.name = str(name)
        self.connections = []

    def __str__(self):
        if self.connections:
            return dotgraph(connections=self.connections)
        return dotgraph(isolated_nodes=[self])

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return id(self) == id(other)

    def connect(self, other, weight=None):
        '''Add `Connection` between `self` and `other` with
        `weight`.
        '''
        self.connections.append(Connection(self, other, weight))
        other.connections.append(Connection(other, self, weight))

    def disconnect(self, other, weight=None):
        '''Remove `Connection` between `self` and `other` with
        `weight`.
        '''
        self.connections.remove(Connection(self, other, weight))
        other.connections.remove(Connection(other, self, weight))

    def isolate(self):
        '''Disconnect from all connected `Node` objects.'''
        self.connections = []


class Connection:
    '''Represent an optionally weighted connection between two `Node`
    objects.

    Attributes:
    --
    - `self.node1`: first `Node` in this `Connection`
    - `self.node2`: second `Node` in this `Connection`
    - `weight`: weight of this `Connection` (usually numerical, default
    `None`)

    Methods:
    --
    - `self.reverse()`: return a `Connection` with the same `node1`,
    `node2`, and `weight`, BUT `node1` and `node2` swap.
    - `self.dot()`: return DOT language representation of this
    `Connection` object.
    '''

    def __init__(self, node1, node2, weight=None):
        self.node1 = node1
        self.node2 = node2
        self.weight = weight

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.node1!r}, {self.node2!r}'
                f'{f", {self.weight!r}" if self.weight else ""})')

    def __str__(self):
        return dotgraph(connections=[self])

    def __hash__(self):
        return hash(self.node1) ^ hash(self.node2) ^ hash(self.weight)

    def __eq__(self, other):
        return (self.node1, self.node2, self.weight) == (other.node1,
                                                         other.node2,
                                                         other.weight)

    def reverse(self):
        '''Return:
        --
        A `Connection` with the same `node1`, `node2`, and `weight`,
        BUT `node1` and `node2` swap.'''
        return Connection(self.node2, self.node1, self.weight)

    def dot(self):
        '''Return:
        --
        A DOT language representation of this `Connection` object.'''
        unlabeled = (f'{escape_dot_id(self.node1.name)} -- '
                     f'{escape_dot_id(self.node2.name)}')
        if self.weight:
            return unlabeled + f' [label={self.weight}]'
        return unlabeled


class Network:
    '''Contain a network of interconnected `Node` objects.

    Attributes:
    --
    - `self.all_nodes`: `set` of all nodes in this network (default
    `set()`).
    - `self.name`: `name` of this network (type `str`, default `''`).
    - `self.isolated_nodes`: `set` of all nodes with no connections.
    - `self.connections`: `list` of all connections in this `Network`.

    Methods:
    --
    - `self.update()`: update `self.connections` and
    `self.isolated_nodes`; run when `Node` objects in this network have
    changed.
    '''

    def __init__(self, all_nodes=None, name=None):
        self.all_nodes = set(all_nodes) if all_nodes else set()
        self.name = str(name) if name else ''
        self.update()  # set self.isolated_nodes and self.connections

    def __str__(self):
        return dotgraph(self.isolated_nodes, self.connections, self.name)

    def update(self):
        '''Update `self.connections` and `self.isolated_nodes`; run
        when `Node` objects in this network have changed.
        '''
        self.isolated_nodes = set()
        self.connections = []
        seen = set()  # store reverses of seen connections
        for node in self.all_nodes:
            if node.connections:
                for con in node.connections:
                    if con.reverse() in seen:
                        # just node2 of an already-stored connection -> ignore
                        continue
                    else:
                        self.connections.append(con)
                        seen.add(con)
            else:
                self.isolated_nodes.add(node)


class Path:
    '''Store `Connection` objects connecting two `Node` objects.

    Attributes
    --
    - `self.connections`: `list` of all `Connection` objects in this
    `Path`.
    - `self.weight`: sum of the weights of all `Connection` objects in
    this `Path` (usually numerical).

    Methods
    --
    - `self.__add__(other)`: return a combined `Path` of `self` and
    `other`.
    '''

    def __init__(self, connections=None):
        self.connections = list(connections) if connections else []

    def __str__(self):
        return dotgraph(connections=self.connections)

    def __add__(self, other):
        '''Return:
        --
        - A combined `Path` of `self` and `other`.
        '''
        return Path(self.connections + other.connections)

    @property
    def weight(self):
        '''Property attribute: sum of the weights of all of the
        `Connection` objects in this `Path` (type: `int`).
        '''
        return sum(con.weight for con in self.connections)
