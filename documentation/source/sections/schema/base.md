# DFBase

All DesignFormat schema classes inherit from `DFBase`, so they all have the same core properties:

```json
{
    "id": "my_id",
    "description": "Free-form description of this node",
    "attributes": {
        "key_a": "value_a",
        "key_b": 2,
        "key_c": true
    }
}
```

| Property    | Usage |
|-------------|-------|
| id          | The node's ID formed of alphanumeric characters and '_' |
| description | Free-form human readable description, not machine parseable |
| attributes  | A key-value mapping. Values can be any serialisable object, even other DesignFormat nodes! |

```eval_rst
.. note::
    If a complex type like a DesignFormat node is stored as an attribute value, then it will be encapsulated using the same method as described in the Storage Format section.
```

## Python API

```eval_rst
.. automodule:: designformat.base
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFBase
    :members:
```