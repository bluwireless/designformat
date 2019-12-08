# DFInterconnect

`DFInterconnect` represents a signal type within the design - this can be as simple as a clock signal, or as complex as an AXI bus. Interconnects are able to carry an arbitrary number of components, and signals can either pass from the master to the slave or vice-versa.

`DFInterconnects` are stored as first class citizens in the [DFProject's](./project) node list, rather than being scattered throughout the design - this allows them to be referenced by [DFPort](./port) instances. Every [DFPort](./port) uses the `type` property to reference the `id` of the `DFInterconnect` it instantiates. Your library may choose to provide helper functions to convert from this reference into the `DFInterconnect` instance - for example in the Javascript and Python libraries you can use the `getInterconnectType()` function on a [DFPort](./port) to resolve the interconnect type.

As with every tag, `DFInterconnect` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json

{
    "id": "axi4",
    "description": "AMBA standardised interconnect",
    "attributes": { },
    "role": "MASTER",
    "components": [ ]
}
```

| Property   | Usage |
|------------|-------|
| role       | Overrides the role of the interconnect set when declaring a [DFPort](./port) |
| components | A list of dumped [DFInterconnectComponent](./interconnect_component) objects |

```eval_rst
.. warning::
    The `role` attribute is only included as a hang-over from previous versions of the BLADE YAML syntax. It will be deprecated shortly as it unnecessarily complicates the process of determining master/slave roles, where you could just as easily change the role of the DFPort.
```

## Python API

```eval_rst
.. autoclass:: designformat.interconnect.DFInterconnect
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFInterconnect
    :members:
```