# DFCommand

`DFCommand` can be used to represent an instruction or microcode command used by a block's architecture. Commands contain a collection of [DFCommandFields](./command_field), which represent the different arguments. Commands have a flexible width, from as little as 1 bit wide, and can be broken into as many fields as required providing each field contains at least one bit. Fields are allowed to overlap, to give some support for overloading.

As with every tag, `DFCommand` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_command",
    "description": "Free-form description",
    "attributes": { },
    "width": 24,
    "fields": [ ]
}
```

| Property | Usage |
|----------|-------|
| width    | Specifies the full bit width of the command, fields do not have to fill the entire command |
| fields   | A list of [DFCommandField](./command_field) objects. |

## Python API

```eval_rst
.. autoclass:: designformat.command.DFCommand
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFCommand
    :members:
```