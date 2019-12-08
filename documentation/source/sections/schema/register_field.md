# DFRegisterField

`DFRegisterField` represents a single field within a [DFRegister](./register) and inherits from [DFCommandField](./command_field) and has exactly the same attributes. It only exists as a distinct entity so that it can be extended in later versions of the specification with new attributes.

As with every tag, `DFRegisterField` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_register_field",
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
.. autoclass:: designformat.register.DFRegisterField
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFRegisterField
    :members:
```