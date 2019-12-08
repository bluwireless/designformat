# DFBlock

`DFBlock` describes a hardware module within a system with the ports, children, registers, address map, and interconnectivity all captured. Blocks are completely instantiated within the description - while different instances can refer to a common type, no work needs to be done to elaborate the design at runtime. This choice of making the stored design more verbose was deliberate, as it makes the JSON description easier for a human to read and modify without constantly referencing inherited descriptions.

As with every tag, `DFBlock` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_block",
    "description": "Free-form description",
    "attributes": { },
    "path": "the_root.child_a.my_block",
    "parent": "the_root.child_a",
    "type": "an_engine",
    "ports": {
        "input": [ ],
        "output": [ ],
        "inout": [ ]
    },
    "children": [ ],
    "connections": [ ],
    "registers": [ ],
    "address_map": { }
}
```

| Property     | Usage |
|--------------|-------|
| path         | Hierarchical path to where this block is located in the design |
| parent       | Hierarchical path to the parent block, resolved during reload to a pointer |
| type         | Type of the block, this is just a string |
| ports.input  | A list of this block's input [DFPort](./port) objects |
| ports.output | A list of this block's output [DFPort](./port) objects |
| ports.inout  | A list of this block's bidirectional [DFPort](./port) objects |
| children     | A list of the this block's children as DFBlock objects |
| connections  | A list of [DFConnection](./connection) objects describing interconnectivity |
| registers    | A list of [DFRegisterGroup](./register_group) objects describing this block's registers |
| address_map  | An instance of [DFAddressMap](./address_map) describing address relationship between boundary IO ports |

DesignFormat has a concept of 'principal' ports, which allows one input port of a certain type to be nominated as the default connection point. One example use case for this is nominating the main clock and reset ports of a block, which can then be used by other tools to determine the main clocking structure. Only one input port of each type (e.g. where `type` is set to 'clock', or 'reset', etc.) can be nominated as a principal at any time - but you can have as many different principal types active as required.

Principal ports are identified by having an attribute of `PRINCIPAL` set to `true` in their `attributes` dictionary - for example (see [DFPort](./port) for further details):

```json
{
    "id": "my_block",
    "ports": {
        "input": [
            {
                "id": "my_block[clk]",
                "name": "clk",
                "type": "clock",
                "attributes": { "PRINCIPAL": true }
            }
        ]
    }
}
```

## Python API

```eval_rst
.. autoclass:: designformat.block.DFBlock
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFBlock
    :members:
```