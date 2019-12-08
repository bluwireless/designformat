# DFConstantTie

`DFConstantTie` represents a constant value that can be driven onto any port. It is used in conjuction with [DFConnection](./connection) to provide tie-offs and constant value inputs to ports of a [DFBlock](./block).

As with every tag, `DFConstantTie` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`). However `DFConstantTie` are not often named, or described, so the `id` and `description` properties may be left empty.

```json
{
    "id": "optional_id",
    "description": "Optional free-form description - not often populated",
    "value": 54531,
    "reset": false,
    "block": "my_root.my_block"
}
```

| Property | Usage |
|----------|-------|
| value    | If `reset` is `false`, then the port is tied to this value |
| reset    | When `reset` is `true`, the port is tied to the reset value of the [DFInterconnect](./interconnect) |
| block    | Hierarchical path to the block that holds this `DFConstantTie` |

## Python API

```eval_rst
.. autoclass:: designformat.constant_tie.DFConstantTie
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFConstantTie
    :members:
```