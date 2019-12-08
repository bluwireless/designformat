# DFDefine

`DFDefine` is used to create a named constant value which can be used by the design implementation so that constants are guaranteed to be consistent.

As with every tag, `DFDefine` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_block_id",
    "description": "The bus ID of my block",
    "attributes": { },
    "value": 123456
}
```

| Property | Usage |
|----------|-------|
| value    | The value that the `DFDefine` represents - can be integer or otherwise |

## Python API

```eval_rst
.. autoclass:: designformat.define.DFDefine
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFDefine
    :members:
```