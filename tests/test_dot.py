import pytest
from random import randint
from pynetworks import Edge, Node
from pynetworks import dotgraph, escape_dot_id

ISOLATED_NODE_NAMES = ['N1', '#2', 'node a', 'jAmes']


@pytest.fixture
def isolated_nodes():
    return [Node(name) for name in ISOLATED_NODE_NAMES]


def test_escape_dot_id_empty():
    assert escape_dot_id('') == '""'
    assert escape_dot_id('   ') == '"   "'


def test_escape_dot_id_without_quotes():
    assert escape_dot_id('dfj* LF!') == '"dfj* LF!"'


def test_escape_dot_id_with_quotes():
    assert escape_dot_id('Node "1"') == R'"Node \"1\""'


def test_dotgraph_with_just_isolated_nodes(isolated_nodes):
    assert (dotgraph(isolated_nodes=isolated_nodes) ==
            'graph {\n\t"N1"\n\t"#2"\n\t"node a"\n\t"jAmes"\n}')
    assert (dotgraph(isolated_nodes=isolated_nodes, name='test') ==
            'graph "test" {\n\t"N1"\n\t"#2"\n\t"node a"\n\t"jAmes"\n}')


def test_dotgraph_with_isolated_nodes_and_edges(isolated_nodes):
    james = isolated_nodes.pop()
    node_a = isolated_nodes.pop()
    node_a.connect(james, 3.5)
    assert (dotgraph(isolated_nodes=isolated_nodes, edges=node_a.edges,
                     name='NAME')
            == 'graph "NAME" {\n\t"N1"\n\t"#2"\n\t"node a" -- "jAmes" [label=3'
               '.5]\n}')


def test_dotgraph_with_just_edges(isolated_nodes):
    first = isolated_nodes[0]
    others = isolated_nodes[1:]
    for i, other in enumerate(others):
        first.connect(other, i)
    assert (dotgraph(edges=first.edges) == 'graph {\n\t"N1" -- "#2" [label=0]'
            '\n\t"N1" -- "node a" [label=1]\n\t"N1" -- "jAmes" [label=2]\n}')
