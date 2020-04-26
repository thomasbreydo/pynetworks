# pynetworks

## Description

A package that provides structure for networks of interconnected nodes using the [DOT language](<https://en.wikipedia.org/wiki/DOT_(graph_description_language)>) for representation.

## Installation

The source code for **pynetworks** is hosted on [GitHub](https://github.com/thomasbreydo/pynetworks). You can install **pynetworks** with pip:

```zsh
pip install pynetworks
```

## Documentation

Read the full documentation for **pymastermind** [here](https://google.com).

## Example Usage

### `Node`

```python3
>>> a = Node('A')
>>> b = Node('B')
>>> a.connect(b, 3)
>>> print(a)
graph {
    "A" -- "B" [label=3]
}
```

### `shortest_path()`

```python3
>>> a = Node('A')
>>> b = Node('B')
>>> c = Node('C')
>>> a.connect(b, 3)
>>> b.connect(c, 5)
>>> path = shortest_path(a, c)
>>> path.weight
8
>>> print(path)
graph {
    "B" -- "C" [label=5]
    "A" -- "B" [label=3]
}
```

### Network

```python3
>>> a = Node('A')
>>> b = Node('B')
>>> c = Node('C')
>>> a.connect(b, 3)
>>> net = Network([a, b, c])
>>> print(net)
graph {
	"C"
	"A" -- "B" [label=3]
}
```

## License

[GNU](/LICENSE)
