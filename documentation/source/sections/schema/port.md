# DFPort

`DFPorts` are used to declare the points of ingress into and egress out of a [DFBlock](./block) for different types of signals. The declaration of a `DFPort` instantiates a [DFInterconnect](./interconnect), the reference of which is attached to the root node of the [DFProject](./project).

Ports can be connected to each other within a hierarchy level (i.e. parent-to-child, child-to-parent, or child-to-child) where the child is within the immediate children of the parent. A [DFConnection](./connection) is used to describe the link between two `DFPorts`, or between a [DFConstantTie](./constant_tie) and a `DFPort` - the connection is attached to the [DFBlock](./block) within its `connections` array.

As with every tag, `DFPort` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_block[my_port]",
    "description": "Human readable description of the port",
    "attributes": { },
    "name": "my_port",
    "type": "axi4",
    "count": 1,
    "direction": "IN",
    "block": "my_root.my_block"
}
```

| Property  | Usage |
|-----------|-------|
| name      | Name of the port, this automatically generates an ID of the form `<BLOCK>[<PORT>]`. |
| type      | Type of the port, must refer to a [DFInterconnect](./interconnect). |
| count     | How many signals should this port carry - each can be connected individually. |
| direction | Is the port nominally `IN`, `OUT`, or `INOUT`. The [DFInterconnect's](./interconnect) `role` may reverse the data direction for some components. |
| block     | Hierarchical path to the parent block. |

```eval_rst
.. note::
    On the `DFBlock` page there is some discussion about the idea of "principal" ports, which allows ports like clock and reset to be nominated so that they can be easily identified by later stages of processing.
```

## Python API

```eval_rst
.. autoclass:: designformat.port.DFPort
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFPort
    :members:
```