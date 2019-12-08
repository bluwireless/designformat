# DFRegisterGroup

`DFRegisterGroup` represents a named collection of [DFRegisters](./register) that are related in some manner - for example a register block could be split into separate groups for controlling power state and for driving the block's "mission" mode. The group has an `offset` property, that defines the base address of the group within the overall register bank.

As with every tag, `DFRegisterGroup` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_reg_group",
    "description": "Free-form description",
    "attributes": { },
    "offset": 256,
    "registers": [ ]
}
```

| Property  | Usage |
|-----------|-------|
| offset    | Specifies the base address of the group relative to the start of the register bank |
| registers | List of [DFRegisters](./register) that form this group |

## Python API

```eval_rst
.. autoclass:: designformat.register_group.DFRegisterGroup
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFRegisterGroup
    :members:
```