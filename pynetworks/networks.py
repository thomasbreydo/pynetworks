import random
from .dot import dotgraph
from .dot import escape_dot_id
from .pathfinding import path_exists


class Node:
    '''Contain a named node, with weighted connections.

    Parameters
    ----------
    name
        name of this :class:`Node`.


    Example
    -------
    >>> a = Node('A')
    >>> b = Node('B')
    >>> a.connect(b, 3)
    >>> print(a)
    graph {
        "A" -- "B" [label=3]
    }

    Attributes
    ---------
    name
    connections : list
        list of connected :class:`Node` objects.
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
        '''Add :class:`Edge` between ``self`` and ``other`` with
        ``weight``.

        Parameters
        ----------
        other : :class:`Node`
        weight : numerical, optional
        '''
        self.connections.append(Edge(self, other, weight))
        other.connections.append(Edge(other, self, weight))

    def disconnect(self, other, weight=None):
        '''Remove :class:`Edge` between ``self`` and ``other``
        with ``weight``.

        Parameters
        ----------
        other : :class:`Node`
        weight : numerical, optional
        '''
        self.connections.remove(Edge(self, other, weight))
        other.connections.remove(Edge(other, self, weight))

    def isolate(self):
        '''Disconnect from all connected :class:`Node` objects.'''
        self.connections = []


class Edge:
    '''Represent an optionally weighted connection between two
    :class:`Node` objects.

    Parameters
    ----------
    node1 : :class:`Node`
        first :class:`Node` in this :class:`Edge`.
    node2 : :class:`Node`
        second :class:`Node` in this :class:`Edge`.
    weight : numerical, optional
        weight of this :class:`Edge`.

    Attributes
    ----------
    node1
    node2
    weight
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
        '''
        Returns
        -------
        :class:`Edge`
            A :class:`Edge` with the same ``node1``, ``node2``,
            and ``weight`` but with ``node1`` and ``node2`` swapped.
        '''
        return Edge(self.node2, self.node1, self.weight)

    def dot(self):
        '''
        Returns
        -------
        str
            A DOT language representation of this :class:`Edge`
            object.
        '''
        unlabeled = (f'{escape_dot_id(self.node1.name)} -- '
                     f'{escape_dot_id(self.node2.name)}')
        if self.weight:
            return unlabeled + f' [label={self.weight}]'
        return unlabeled


class Network:
    '''Contain a network of interconnected :class:`Node` objects.

    Parameters
    ----------
    all_nodes : iterable, optional
        All nodes in this network. If left out, the network is
        initialized empty.
    name: optional
        The name of this network.

    Attributes
    ----------
    all_nodes
    name
    connections : list
        All connections in this :class:`Network`.
    isolated_nodes : set
        All nodes with no connections.
    '''

    def __init__(self, all_nodes=None, name=None):
        self.all_nodes = set(all_nodes) if all_nodes else set()
        self.name = str(name) if name else ''
        self.update()  # set self.isolated_nodes and self.connections

    def __str__(self):
        return dotgraph(self.isolated_nodes, self.connections, self.name)

    def __iter__(self):
        yield from self.all_nodes

    def update(self):
        '''Update ``connections`` and ``isolated_nodes``, to be used
        when :class:`Node` objects in this network have changed.
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


def generate_network(n_nodes=10, lower_bound=1, upper_bound=11,
                     connection_prob=0.8, force_connected=True):
    '''Create a :class:`Network` of  :class:`Node` objects.

    Parameters
    ----------
    n_nodes : int, optional
        Number of nodes in the returned network.
    lower_bound : int, optional
        Lower bound (inclusive) of range of connections' weights.
    upper_bound : int, optional
        Upper bound (exclusive) for range of connections' weights.
    connections_prob : float, optional
        Probability betweeen 0 and 1 of any two nodes being connected.
        If ``force_connected`` is set to ``True``, ``connections_prob``
        may be overridden to ensure a fully-connected network.
    force_connected : bool
        If ``False``, output does not need to be a full-connected
        network.

    Returns
    -------
    :class:`Network`
        A network ``n_nodes`` interconnected :class:`Node` objects.
    '''

    nodes = {Node(f'Node {i}') for i in range(int(n_nodes))}
    done = set()

    for cur_node in nodes:
        done.add(cur_node)
        for other_node in nodes:
            if other_node not in done and random.random() < connection_prob:
                cur_node.connect(other_node, random.randint(
                    lower_bound, upper_bound - 1))
    if force_connected:  # if network must be a connected network
        node_a = random.sample(done, 1)[0]
        others = done - {node_a}
        for node in others:
            if not path_exists(node_a, node):
                node.connect(node_a, random.randint(
                    lower_bound, upper_bound - 1))
                path_exists.clear_cache()

    return Network(done)


def fully_connected(network):
    '''Check if ``network`` is a fully connected network of
    nodes.

    Parameters
    ----------
    network : :class:`Network`

    Returns
    -------
    bool
        ``True`` if ``network`` is fully connected, otherwise
        ``False``.
    '''
    node_a = random.sample(network, 1)[0]
    others = network - {node_a}
    for node in others:
        if not path_exists(node_a, node):
            return False
    return True
