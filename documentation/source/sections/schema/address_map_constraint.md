# DFAddressMapConstraint

`DFAddressMapConstraint` specifies an access constraint between a specific initiator and a specific target. This gives the flexibility required to describe an incomplete cross-bar architecture (i.e. where certain traffic pathways through the address map are banned).

A [DFAddressMap](./address_map) can contain as many constraints as there are unique [DFAddressMapInitiator](./address_map_initiator)-[DFAddressMapTarget](./address_map_target) pairings. Constraints are optional - if no constraints are configured for an initiator then all un-constrained targets are accessible, likewise if no constraints are configured for a target all un-constrained initiators can access it.

As with every tag, `DFAddressMapConstraint` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_constraint",
    "description": "Free-form description",
    "attributes": { },
    "initiator": {
        "block": "my_root.my_sub.my_block.my_noc",
        "port": "pcie_i",
        "index": 0
    },
    "target": {
        "block": "my_root.my_sub.my_block.my_noc",
        "port": "ram_t",
        "index": 2
    }
}
```

| Property        | Usage |
|-----------------|-------|
| initiator       | Details which port on the [DFAddressMap's](./address_map) block acts as the initiator |
| initiator.block | The hierarchical path to the port's parent block |
| initiator.port  | The name of the port acting as the initiator |
| initiator.index | Which signal index within the port acts as the initiator |
| target          | Details which port on the [DFAddressMap's](./address_map) block acts as the target |
| target.block    | The hierarchical path to the port's parent block |
| target.port     | The name of the port acting as the target |
| target.index    | Which signal index within the port acts as the target |

```eval_rst
.. note::
    Take note that the constraint refers to the underlying `DFPorts` of the initiator and target, rather than referring to the `DFAddressMapInitiator` and `DFAddressMapTarget` instances - but it will not implicitly them!

    Constraints should always be the last node types processed when reloading a `DFAddressMap`, so that all required initiators and targets exist.
```

## Python API

```eval_rst
.. autoclass:: designformat.address_map.DFAddressMapConstraint
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFAddressMapConstraint
    :members:
```