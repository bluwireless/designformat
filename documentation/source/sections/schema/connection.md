# DFConnection

`DFConnection` is used to represent a connection between two [DFPorts](./port) or a tie-off where a [DFConstantTie](./constant_tie) drives a [DFPort](./port). [DFBlocks](./block.md) contain a list of connections, only ever spanning between its boundary ports and the boundary ports of its children (i.e. connections should not traverse a hierarchy).

As with every tag, `DFConnection` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`). However `DFConnections` are not often named, or described, so the `id` and `description` properties may be left empty.

The structures for a connection between two [DFPorts](./port.md) and those involving a [DFConstantTie](./constant_tie) differ slightly - firstly for a connection between two [DFPorts](./port.md):

```json
{
    "id": "optional_id",
    "description": "Optional free-form description - not often populated",
    "attributes": { },
    "start_port": {
        "block": "my_root.my_block",
        "port": "clocks"
    },
    "start_index": 2,
    "end_port": {
        "block": "my_root.my_block.my_child",
        "port": "clk_root"
    },
    "end_index": 0
}
```

And then for connections driven by a [DFConstantTie](./constant_tie):

```json
{
    "id": "optional_id",
    "description": "Optional free-form description - not often populated",
    "attributes": { },
    "start_tie": { },
    "end_port": {
        "block": "my_root.my_block.my_child",
        "port": "block_id"
    },
    "end_index": 0
}
```

| Property | Usage |
|----------|-------|
| start_port.block | Hierarchical path to the block where the connection begins |
| start_port.port  | Name of the port that drives the connection |
| start_index      | Index of the signal within the port that drives the connection |
| start_tie        | Dump of a [DFConstantTie](./constant_tie) object that describes the value to drive onto the end port |
| end_port.block   | Hierarchical path to the block where the connection ends |
| end_port.port    | Name of the port that is driven by the connection |
| end_index        | Index of the signal within the port that is driven by the connection |

```eval_rst
.. note::
    The properties of `start_port` and `start_tie` are mutually exclusive, while `end_port` is always present. The `start_port` property is used where one DFPort drives another (for example where a clock signal is distributed from a boundary port to an input port on each child). The `start_tie` property is used where the driven port is held at a constant value (for example where the value is static, or the pin is an unused input in this particular scenario).
```

## Python API

```eval_rst
.. autoclass:: designformat.connection.DFConnection
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFConnection
    :members:
```