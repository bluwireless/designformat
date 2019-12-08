# DFAddressMapInitiator

`DFAddressMapInitiator` describes an initiator within an address map - i.e. a point where transactions enter a block for distribution to the correct [DFAddressMapTarget](./address_map_target).

A [DFAddressMap](./address_map) can contain any number of initiators and targets, provided that there is at least one of each.

As with every tag, `DFAddressMapInitiator` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_initiator",
    "description": "Free-form description",
    "attributes": { },
    "mask": 131071,
    "offset": 0,
    "port": {
        "block": "my_root.my_sub.my_block.my_noc",
        "port": "pcie_i",
        "index": 0
    }
}
```

| Property   | Usage |
|------------|-------|
| mask       | Mask applied to inbound address before looking up in address map |
| offset     | Offset applied to the masked inbound address before looking up in address map |
| port       | Details which port on the [DFAddressMap's](./address_map) block acts as the initiator |
| port.block | The hierarchical path to the port's parent block |
| port.port  | The name of the port acting as the initiator |
| port.index | Which signal index within the port acts as the initiator |

```eval_rst
.. note::
    While a `DFPort` usually carries only one signal, it is capable of carrying any number - this allows signal arrays with a common purpose to be referred to using one name and still separately selectable using an index.

    You can define a unique initiator for every signal carried by a `DFPort` - allowing you to uniquely specify masking and offsets.
```

## Python API

```eval_rst
.. autoclass:: designformat.address_map.DFAddressMapInitiator
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFAddressMapInitiator
    :members:
```