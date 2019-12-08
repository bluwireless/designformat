# DFRegister

`DFRegister` represents a register of a specific [DFBlock](./block). Registers have a specified width, broken up into multiple non-overlapping [DFRegisterFields](./register_field). Due to their similarities, `DFRegister` inherits a lot of its attributes from [DFCommand](./command) - but gains properties of an address and access constraints. Additionally, as fields are not allowed to overlap, the `width` parameter of [DFCommand](./command) is not used and instead the width is derived from the contained [DFRegisterFields](./register_field).

As with every tag, `DFRegister` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_register",
    "description": "Free-form description",
    "attributes": { },
    "offset": 16,
    "access": {
        "bus": "AR",
        "block": "RO",
        "inst": "RW"
    },
    "fields": [ ]
}
```

| Property     | Usage |
|--------------|-------|
| offset       | Offset from the base address of the [DFRegisterGroup](./register_group) |
| access.bus   | Supported access mode from an external register bus (e.g. AXI4) |
| access.block | Supported access mode from the block |
| access.inst  | Supported access mode from instructions executing within the block |
| fields       | A list of [DFRegisterField](./register_field) objects |

For the access parameters, a number of different modes are defined - some of which are only valid for the different access classes:

| Mode | Bus | Block | Inst | Usage |
|:----:|:---:|:-----:|:----:|-------|
| NONE | Y   | Y     | Y    | Access prohibited to this register |
| RW   | Y   | Y     | Y    | Read-write access allowed |
| RO   | Y   | Y     | Y    | Read-only access allowed |
| WO   | Y   | Y     | Y    | Write-only access  |
| AR   | Y   | N     | N    | Read-only access allowed, with strobe on access |
| AW   | Y   | N     | N    | Write-only access allowed, with strobe on write |
| ARW  | Y   | N     | N    | Read-write access allowed, with separate strobes for read and write accesses |
| WC   | Y   | N     | N    | Write mask to clear bits within a stored value |
| WS   | Y   | N     | N    | Write mask to set bits within a stored value |

## Python API

```eval_rst
.. autoclass:: designformat.register.DFRegister
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFRegister
    :members:
```