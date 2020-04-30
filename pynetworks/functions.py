import random
import re
from .classes import Node, Path


def memoize(shortest_path_func):
    '''Memoize the path-finding functions: `shortest_path()`,
    `path_exists`.
    '''
    memo = {}

    def memoized_shortest_path_func(start, end, _visited=None):
        # _visited doesn't affect memo, also it's unhashable
        key = (start, end)
        try:
            return memo[key]
        except KeyError:
            memo[key] = shortest_path_func(start, end, _visited)
        return memo[key]

    def clear_cache():
        nonlocal memo  # uses memo from enclosing scope
        memo = {}

    memoized_shortest_path_func.clear_cache = clear_cache
    memoized_shortest_path_func.__doc__ = shortest_path_func.__doc__

    return memoized_shortest_path_func


@memoize
def shortest_path(start, end, _visited=None):
    '''Find the shortest path between `start` and `end`.

    Arguments:
    --
    - `start`: starting `Node` object (type: `Node`).
    - `end`: final `Node` object (type: `Node`).

    Return:
    --
    If a path exists from `start` to `end`, return that `Path` object.
    Otherwise, return `None`.
    '''
    if start == end:
        return Path()
    if not _visited:
        _visited = set()

    paths = []
    for con in start.connections:
        if con.node2 not in _visited:
            path = shortest_path(con.node2, end, _visited | {start})
            if path:
                paths.append(path + Path([con]))

    try:
        return min(paths, key=lambda path: path.weight)
    except ValueError:
        pass


@memoize
def path_exists(start, end, _visited=None):
    '''Check if a path exists between `start` and `end`.

    Arguments:
    --
    - `start`: starting `Node` object (type: `Node`).
    - `end`: final `Node` object (type: `Node`).

    Return:
    --
    `True` if a path exists, otherwise `False`.
    '''

    if start == end:
        return True
    if not _visited:
        _visited = set()

    for con in start.connections:
        if con.node2 not in _visited:
            if path_exists(con.node2, end, _visited | {start}):
                return True
    return False


def escape_dot_id(string):
    '''Surround in double quotes and escape all double quotes.

    Arguments:
    --
    - `string`: the id to escape (type `str`).

    Return:
    --
    A valid, escaped id for a DOT graph (type `str`).

    Example:
    --
    >>> escape_dot_id('A"B')
    '"A\\"B"'
    '''

    return '"' + re.sub(r'([\\"])', r'\\\1', string) + '"'


def dotgraph(isolated_nodes=None, connections=None, name=''):
    '''Generate a DOT graph out of nodes and connections.

    Arguments:
    --
    - `isolated_nodes`: list of `Node` objects with no connections to
    graph (type `list`, default `[]`).
    - `connections`: list of `Connection` objects to graph (type `list`,
    default `[]`).
    - `name`: name of returned dotgraph (type `str`, default `''`).

    Return:
    --
    A valid DOT graph (`str`).

    Examples:
    --
    # One isolated `Node` object.
    >>> a = Node('A')
    >>> print(dotgraph(isolated_nodes=[a], name='My Graph'))
    graph "My Graph" {
        "A"
    }

    # Two connected `Node` objects.
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
    '''Arguments:
    --
    - `n_nodes`: number of nodes (type `int`, default `10`).
    - `lower_bound`:  lower bound (inclusive) of range of connections'
    weights (type `int`, default `1`).
    - `upper_bound`: upper bound (exclusive) for range of connections'
    weights (type `int`, default `11`).
    - `connections_prob`: probability betweeen 0 and 1 of any two nodes
    being connected (type `float`, default `0.8`). If `force_connected`
    is set to `True`, this setting might be overridden.
    - `force_connected`: if `False`, output can be a disconnected
    network (type `bool`, default `True`).

    Return:
    --
    A `set` of `n_nodes` interconnected `Node` objects.
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
        connected = False
        while not connected:
            connected = True
            for node in done:
                for other_node in done - {node}:
                    if not path_exists(node, other_node):
                        node.connect(other_node, random.randint(
                            lower_bound, upper_bound - 1))
                        path_exists.clear_cache()
                        connected = False

    return done
