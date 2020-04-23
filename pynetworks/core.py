import re
import random


class Network:
    '''Contain a network of interconnected `Node` objects.'''

    def __init__(self, all_nodes=None, name=None):
        self.all_nodes = set(all_nodes) if all_nodes else set()
        self.name = str(name) if name else ''
        self.update()  # set self.isolated_nodes and self.connections

    def __str__(self):
        return dotgraph(self.isolated_nodes, self.connections, self.name)

    def update(self):
        '''Update `self.connections` and `self.isolated_nodes`.'''
        self.isolated_nodes = set()
        self.connections = []
        seen = set()  # store reverses of seen connections
        for node in self.all_nodes:
            if node.connections:
                for con in node.connections:
                    if con.reverse() in seen:
                        continue  # opposite connection
                    else:
                        self.connections.append(con)
                        seen.add(con)
            else:
                self.isolated_nodes.add(node)

    def from_dotgraph(self, dotgraph):
        '''TODO: USE REG EXP to find and interpret a -- b [label=2].'''
        pass


class Connection:
    '''Represent an optionally weighted connection between two nodes.'''

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
        return Connection(self.node2, self.node1, self.weight)

    def edge(self):
        '''Return DOT language representation of this Connection.'''
        unlabeled = (f'{escape_dot_ID(self.node1.name)} -- '
                     f'{escape_dot_ID(self.node2.name)}')
        if self.weight:
            return unlabeled + f' [label={self.weight}]'
        return unlabeled


class Node:
    '''Contain a named node, with weighted connections.

    `connected_to` is a list of tuples of the form `(node, weight)`
    >>> Node('My Node', [(my_node1, 5), (my_node2, 4)])
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
        '''Add `Connection` between `self` and `other` with `weight`.'''
        self.connections.append(Connection(self, other, weight))
        other.connections.append(Connection(other, self, weight))

    def disconnect(self, other, weight=None):
        '''Remove `Connection` between `self` and `other` with `weight`.'''
        self.connections.remove(Connection(self, other, weight))
        other.connections.remove(Connection(other, self, weight))

    def isolate(self):
        '''Remove all connections from `self.connections`.'''
        self.connections = []


class Path:
    def __init__(self, connections=None):
        self.connections = list(connections) if connections else []

    @property
    def length(self):
        return sum(con.weight for con in self.connections)

    def __str__(self):
        return dotgraph(connections=self.connections)

    def __add__(self, other):
        return Path(self.connections + other.connections)


def memoize(shortest_path_func):
    memo = {}

    def memoized_shortest_path_func(start, end, visited=None):
        # visited doesn't affect memo, also it's unhashable
        key = (start, end)
        try:
            return memo[key]
        except KeyError:
            memo[key] = shortest_path_func(start, end, visited)
        return memo[key]

    def clear_cache():
        nonlocal memo  # uses memo from enclosing scope
        memo = {}

    memoized_shortest_path_func.clear_cache = clear_cache
    return memoized_shortest_path_func


@memoize
def shortest_path(start, end, visited=None):
    '''Find the shortest path between `start` and `end`.'''
    if start == end:
        return Path()
    if not visited:
        visited = set()

    paths = []
    for con in start.connections:
        if con.node2 not in visited:
            path = shortest_path(con.node2, end, visited | {
                                 start})
            if path:
                paths.append(path + Path([con]))

    try:
        return min(paths, key=lambda path: path.length)
    except ValueError:
        pass


def dotgraph(isolated_nodes=[], connections=[], name=''):
    '''DOT representation of undirected graph with inputted properties.'''
    nodes = '\n\t'.join([escape_dot_ID(node.name) for node in isolated_nodes])
    middle = '\n\t' if isolated_nodes and connections else ''
    edges = '\n\t'.join([con.edge() for con in connections])
    return (f'graph {f"{escape_dot_ID(name)} " if name else ""}'
            f'{{\n\t{nodes}{middle}{edges}\n}}')


def escape_dot_ID(string):
    '''Surround in double quotes and escape all double quotes.

    Ex. `A"B` becomes `"A\\"B"`
    '''

    return '"' + re.sub(r'([\\"])', r'\\\1', string) + '"'


def generate_map(n_nodes=10, lower_bound=1, upper_bound=11,
                 connection_prob=0.8):
    '''Return a set of `n_nodes` interconnected `Node` objects.

    Keyword arguments:

    n_nodes -- number of nodes (default 10)

    lower_bound -- inclusive lower bound for connection weight (default 
    1)

    upper_bound -- exclusive upper bound for connections weight (default
    11)

    connections_prob -- probability of any two nodes being connected (de
    fault 0.8)
    '''

    nodes = {Node(f'Node {i}') for i in range(n_nodes)}
    done = set()

    for cur_node in nodes:
        done.add(cur_node)
        for other_node in nodes:
            if other_node not in done and random.random() < connection_prob:
                try:
                    cur_node.connect(other_node, random.randint(
                        lower_bound, upper_bound - 1))
                except ValueError as err:
                    raise ValueError("'lower_bound' and 'upper_bound' must be"
                                     " positive integers with 'lower_bound' <"
                                     "= 'upper_bound'.")

    return done
