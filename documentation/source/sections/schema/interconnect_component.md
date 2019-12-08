# DFInterconnectComponent

`DFInterconnectComponent` represents a component of a wider signal, which is modelled by a [DFInterconnect](./interconnect). The component can be either simple or complex:

 * A *simple* component can be regarded as a collection of wires of a specified width, for example an address field of a data bus.
 * A *complex* component is a collection of other components, which is represented by another [DFInterconnect](./interconnect).

For simple components the `DFInterconnectComponent` has properties of `width` and `count`, which specify how wide the component is and how many times it should be instanced. For complex components it retains the `count` property, but replaces `width` with `ref` - this new field references the name of another [DFInterconnect](./interconnect) that should be instantiated as the component.

As many layers of interconnect as required can be instantiated - so for example you could split an AXI bus into read and write "channels", and each of those channels into "request" and "response" buses, with each layer represented by a different [DFInterconnect](./interconnect). For example:

```
AXI4
 |-- Read Channel (COMPLEX, M->S)
 |    |-- Request Bus (COMPLEX, M->S)
 |    |    |-- ARADDR[31:0] (SIMPLE, M->S)
 |    |    |-- ARVALID (SIMPLE, M->S)
 |    |    |-- ARREADY (SIMPLE, S->M)
 |    |    ...
 |    |-- Response Bus (COMPLEX, M->S)
 |         |-- RDATA[31:0] (SIMPLE, S->M)
 |         |-- RVALID (SIMPLE, S->M)
 |         |-- RREADY (SIMPLE, M->S)
 |         ...
 |-- Write Channel (COMPLEX, M->S)
      |-- Request Bus (COMPLEX, M->S)
      |    |-- AWADDR[31:0] (SIMPLE, M->S)
      |    ...
      |-- Response Bus
           |-- BVALID (SIMPLE, S->M)
           ...
```

As with every tag, `DFInterconnectComponent` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

Firstly, an example showing a complex component instantiating a referenced [DFInterconnect](./interconnect) called `axi4_read_channel`:

```json
{
    "id": "read_channel",
    "description": "Read channel component of AMBA AXI4 bus",
    "attributes": { },
    "role": "MASTER",
    "type": "COMPLEX",
    "count": 1,
    "ref": "axi4_read_channel"
}
```

Secondly, an example showing a simple 32-bit `RDATA` component of the AMBA AXI4 bus, note that it has a `slave` role so will transfer data against the overall direction of the bus:

```json
{
    "id": "WDATA",
    "description": "32-bit write data component",
    "attributes": { },
    "role": "SLAVE",
    "type": "SIMPLE",
    "count": 1,
    "width": 32,
    "default": 0,
    "enum": { }
}
```

| Property | Usage |
|----------|-------|
| role     | Either `MASTER` or `SLAVE` to define whether data flows with or against the direction of the bus respectively. |
| type     | `SIMPLE` for basic components representing a bundle of wires, or `COMPLEX` when instantiating another [DFInterconnect](./interconnect). |
| count    | How many instances of this component should be placed |
| width    | For *simple* components, how wide is the data signal. |
| default  | For *simple* components, what value should they take at reset. |
| enum     | For *simple* components, the value can be enumerated using [DFDefine](./define) nodes - just like a [DFCommandField](./command_field). |

## Python API

```eval_rst
.. autoclass:: designformat.interconnect.DFInterconnectComponent
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFInterconnectComponent
    :members:
```