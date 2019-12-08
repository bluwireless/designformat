# DFAddressMap

`DFAddressMap` specifies the address map between input and output boundary ports on a leaf [DFBlock](./block). It is formed of [DFAddressMapInitiators](./address_map_initiator), [DFAddressMapTargets](./address_map_target), and [DFAddressMapConstraints](./address_map_constraint) - which together provide a flexible scheme for describing the translations, apertures, and access limitations of an arbitrary transaction distributor or aggregator.

The use of [DFAddressMapConstraints](./address_map_constraint) is optional, if they are omitted then every [DFAddressMapInitiator](./address_map_initiator) can access every [DFAddressMapTarget](./address_map_target). Partial use is also possible, in which case an unconstrained initiator can access every unconstrained target, but constrained initiators can only access an allowed set of targets and equally constrained targets can only be accessed by an allowed set of initiators.

As with every tag, `DFAddressMap` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_address_map",
    "description": "Free-form description",
    "attributes": { },
    "initiators": [ ],
    "targets": [ ],
    "constraints": { }
}
```

| Property    | Usage |
|-------------|-------|
| initiators  | Contains a list of [DFAddressMapInitiators](./address_map_initiator) |
| targets     | Contains a list of [DFAddressMapTargets](./address_map_target) |
| constraints | A map of [DFAddressMapConstraints](./address_map_constraint), keyed uniquely using the form "<INITIATOR.ID>-<TARGET.ID>" - eg. "pcie_init_0-mem_tgt_2" |

## Python API

```eval_rst
.. autoclass:: designformat.address_map.DFAddressMap
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFAddressMap
    :members:
```