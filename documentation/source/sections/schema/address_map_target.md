# DFAddressMapTarget

`DFAddressMapTarget` describes an target within an address map - i.e. a point where transactions exit a block towards their intended destination, having originated from a [DFAddressMapInitiator](./address_map_initiator).

A [DFAddressMap](./address_map) can contain any number of initiators and targets, provided that there is at least one of each.

As with every tag, `DFAddressMapTarget` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_target",
    "description": "Free-form description",
    "attributes": { },
    "offset": 65536,
    "aperture": 8192,
    "port": {
        "block": "my_root.my_sub.my_block.my_noc",
        "port": "ram_t",
        "index": 2
    }
}
```

| Property   | Usage |
|------------|-------|
| offset     | Base of address window for accessing the target |
| aperture   | Size of the address window for accessing the target |
| port       | Details which port on the [DFAddressMap's](./address_map) block acts as the target |
| port.block | The hierarchical path to the port's parent block |
| port.port  | The name of the port acting as the target |
| port.index | Which signal index within the port acts as the target |

```eval_rst
.. note::
    While a `DFPort` usually carries only one signal, it is capable of carrying any number - this allows signal arrays with a common purpose to be referred to using one name and still separately selectable using an index.

    You can define a unique target for every signal carried by a `DFPort` - allowing you to separately place them within the address map.
```

## Python API

```eval_rst
.. autoclass:: designformat.address_map.DFAddressMapTarget
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFAddressMapTarget
    :members:
```