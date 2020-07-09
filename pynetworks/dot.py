import re


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

    return '"' + re.sub(R'([\\"])', R'\\\1', string) + '"'


def dotgraph(isolated_nodes=None, edges=None, name=''):
    '''Generate a DOT graph out of nodes and edges.

    Parameters
    ----------
    isolated_nodes : list of :class:`Node`, optional
        Isolated nodes to graph.
    edges : list of :class:`Edge`, optional
        Edges to graph.
    name : optional
        Name of the returned DOT graph.

    Returns
    -------
    str
        A valid DOT graph of all the given nodes and edges with
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
    >>> print(dotgraph(edges=b.edges))
    graph {
        "B" -- "C" [label=5]
    }
    '''
    if isolated_nodes is None:
        isolated_nodes = []
    if edges is None:
        edges = []

    nodes = '\n\t'.join([escape_dot_id(node.name) for node in isolated_nodes])
    middle = '\n\t' if isolated_nodes and edges else ''
    edges = '\n\t'.join([con.dot() for con in edges])
    return (f'graph {f"{escape_dot_id(name)} " if name else ""}'
            f'{{\n\t{nodes}{middle}{edges}\n}}')
