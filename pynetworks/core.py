import random
import re
import functools


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
        '''Add :class:`Connection` between ``self`` and ``other`` with
        ``weight``.

        Parameters
        ----------
        other : :class:`Node`
        weight : numerical, optional
        '''
        self.connections.append(Connection(self, other, weight))
        other.connections.append(Connection(other, self, weight))

    def disconnect(self, other, weight=None):
        '''Remove :class:`Connection` between ``self`` and ``other``
        with ``weight``.

        Parameters
        ----------
        other : :class:`Node`
        weight : numerical, optional
        '''
        self.connections.remove(Connection(self, other, weight))
        other.connections.remove(Connection(other, self, weight))

    def isolate(self):
        '''Disconnect from all connected :class:`Node` objects.'''
        self.connections = []


class Connection:
    '''Represent an optionally weighted connection between two
    :class:`Node` objects.

    Parameters
    ----------
    node1 : :class:`Node`
        first :class:`Node` in this :class:`Connection`.
    node2 : :class:`Node`
        second :class:`Node` in this :class:`Connection`.
    weight : numerical, optional
        weight of this :class:`Connection`.

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
        :class:`Connection`
            A :class:`Connection` with the same ``node1``, ``node2``,
            and ``weight`` but with ``node1`` and ``node2`` swapped.
        '''
        return Connection(self.node2, self.node1, self.weight)

    def dot(self):
        '''
        Returns
        -------
        str
            A DOT language representation of this :class:`Connection`
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


class Path:
    '''Store :class:`Connection` objects connecting two :class:`Node`
    objects.

    Parameters
    ----------
    connections : iterable, optional
        All :class:`Connection` objects in this :class:`Path`. If left
        out, the path is initialized empty.

    Attributes
    ----------
    connections
    '''

    def __init__(self, connections=None):
        self.connections = list(connections) if connections else []

    def __str__(self):
        return dotgraph(connections=self.connections)

    def __add__(self, other):
        return Path(self.connections + other.connections)

    def __lt__(self, other):
        return self.weight < other.weight

    @property
    def weight(self):
        '''Sum of the weights of all of the :class:`Connection`
        objects in this :class:`Path`.

        :type: numerical
        '''
        return sum(con.weight for con in self.connections)


def memoize(shortest_path_func):
    '''Memoize the path-finding function that can take \\*args and
    _visited.

    Used by :func:`shortest_path`,
    :func:`shortest_path_through_network`, and :func:`path_exists`.
    '''
    memo = {}

    @functools.wraps(shortest_path_func)
    def memoized_shortest_path_func(*args, _visited=None):
        # doesn't affect memo, also it's unhashable
        key = tuple(args)
        try:
            return memo[key]
        except KeyError:
            memo[key] = shortest_path_func(*args, _visited)
        return memo[key]

    memoized_shortest_path_func.clear_cache = memo.clear
    memoized_shortest_path_func.cache = memo

    return memoized_shortest_path_func


@memoize
def shortest_path(start, end, _visited=None):
    '''Find the shortest path between ``start`` and ``end``.

    Parameters
    ----------
    start : :class:`Node`
    end : :class:`Node`

    Returns
    -------
    :class:`Path` ``None``
        If a path exists from ``start`` to ``end``, return that
        :class:`Path` object. Otherwise, return ``None``.
    '''
    if start == end:
        return Path()
    if _visited is None:
        _visited = set()

    paths = []
    for con in start.connections:
        if con.node2 not in _visited:
            path = shortest_path(con.node2, end, _visited=_visited | {start})
            if path:
                paths.append(path + Path([con]))

    try:
        return min(paths)
    except ValueError:
        return


@memoize
def shortest_path_through_network(start, network, _visited=None):
    '''Find the shortest path from ``start`` through all other
    :class:`Node` objects in ``network``.

    Parameters
    ----------
    start : :class:`Node`
        Start of the returned :class:`Path`.
    network : :class:`Network`
        Fully-connected network through which the returned
        :class:`Path` travels.

    Returns
    -------
    :class:`Path` ``None``
        If a path exists from ``start`` to ``end``, return that
        :class:`Path` object. Otherwise, return ``None``.
    '''
    reduced_set = network.all_nodes - {start}
    if not reduced_set:
        return Path()
    if _visited is None:
        _visited = set()

    paths = []
    for con in start.connections:
        if con.node2 not in _visited:
            path = shortest_path_through_network(
                con.node2, Network(reduced_set), _visited=_visited | {start})
            if path:
                paths.append(path + Path([con]))

    try:
        return min(paths)
    except ValueError:
        return None


@memoize
def path_exists(start, end, _visited=None):
    '''Check if a path exists between ``start`` and ``end``.

    Parameters
    ----------
    start : :class:`Node`
    end : :class:`Node`

    Returns
    -------
    bool
        ``True`` if a path exists, otherwise ``False``.
    '''

    if start == end:
        return True
    if _visited is None:
        _visited = set()

    for con in start.connections:
        if con.node2 not in _visited:
            if path_exists(con.node2, end, _visited=_visited | {start}):
                return True
    return False


def escape_dot_id(string):
    '''Surround in double quotes and escape all double quotes.

    Parameters
    ----------
    string : str
        ID to escape.

    Returns
    -------
    str
        A valid, escaped ID for a DOT graph.

    Example
    -------
    >>> escape_dot_id('A"B')
    '"A\\"B"'
    '''

    return '"' + re.sub(r'([\\"])', r'\\\1', string) + '"'


def dotgraph(isolated_nodes=None, connections=None, name=''):
    '''Generate a DOT graph out of nodes and connections.

    Parameters
    ----------
    isolated_nodes : list of :class:`Node`, optional
        Isolated nodes to graph.
    connections : list of :class:`Connection`, optional
        Connections to graph.
    name : optional
        Name of the returned dotgraph.

    Returns
    -------
    str
        A valid DOT graph of all the given nodes and connections with
        name ``name``.

    Examples
    --------
    Graphing one isolated :class:`Node` object.

    >>> a = Node('A')
    >>> print(dotgraph(isolated_nodes=[a], name='My Graph'))
    graph "My Graph" {
        "A"
    }

    Graphing connected :class:`Node` objects.

    >>> b = Node('B')
    >>> c = Node('C')
    >>> b.connect(c, 5)
    >>> print(dotgraph(connections=b.connections))
    graph {
        "B" -- "C" [label=5]
    }
    '''
    if isolated_nodes is None:
        isolated_nodes = []
    if connections is None:
        connections = []

    nodes = '\n\t'.join([escape_dot_id(node.name) for node in isolated_nodes])
    middle = '\n\t' if isolated_nodes and connections else ''
    edges = '\n\t'.join([con.dot() for con in connections])
    return (f'graph {f"{escape_dot_id(name)} " if name else ""}'
            f'{{\n\t{nodes}{middle}{edges}\n}}')


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
