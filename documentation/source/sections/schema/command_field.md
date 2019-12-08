# DFCommandField

`DFCommandField` represents a single field within a [DFCommand](./command). It specifies its width and position within the field, and it can be enumerated if it takes discrete values.

As with every tag, `DFCommandField` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_command_field",
    "description": "Free-form description",
    "attributes": { },
    "lsb": 4,
    "size": 2,
    "reset": 0,
    "signed": false,
    "enum": { }
}
```

| Property | Usage |
|----------|-------|
| lsb      | Least significant bit position within the field |
| size     | Width of the field in bits |
| reset    | Default value, or the value taken at reset |
| signed   | Whether the field's value should be treated as a signed integer |
| enum     | A dictionary mapping names to dumps of [DFDefine](./define) values |

## Python API

```eval_rst
.. autoclass:: designformat.command_field.DFCommandField
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFCommandField
    :members:
```