import functools
from .dot import dotgraph
from . import networks


class Path:
    '''Store :class:`Edge` objects connecting two :class:`Node`
    objects.

    Parameters
    ----------
    connections : iterable, optional
        All :class:`Edge` objects in this :class:`Path`. If left
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
        '''Sum of the weights of all of the :class:`Edge`
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
                con.node2, networks.Network(reduced_set),
                _visited=_visited | {start})
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
