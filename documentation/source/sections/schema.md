# Node Schema
DesignFormat stores each node using a standard schema, with every node's schema inheriting from a single base class [DFBase](./schema/base).

This section of the documentation details the full schema, along with examples of how each node may be described:

 * [DFAddressMap](schema/address_map) - declares an address map within a block containing a number of [DFAddressMapInitiators](schema/address_map_initiator) and [DFAddressMapTargets](schema/address_map_target) that are associated to the boundary IO.
 * [DFAddressMapConstraint](schema/address_map_constraint) - represents a constraint between an [DFAddressMapInitiator](schema/address_map_initiator) and a [DFAddressMapTarget](schema/address_map_target).
 * [DFAddressMapInitiator](schema/address_map_initiator) - represents a bus initiator into an [DFAddressMap](schema/address_map).
 * [DFAddressMapTarget](schema/address_map_target) - represents a bus target from an [DFAddressMap](schema/address_map).
 * [DFBase](schema/base) - the base class from which all other schema classes inherit.
 * [DFBlock](schema/block) - describes a hardware block with ports, children, connectivity, registers, and an address map.
 * [DFCommand](schema/command) - details a command handled by the hardware such as microcode or an instruction.
 * [DFCommandField](schema/command_field) - represents a field within a [DFCommand](schema/command) that carries specific information.
 * [DFConnection](schema/connection) - a connection between two [DFPorts](schema/port) or a [DFPort](schema/port) and a [DFConstantTie](schema/constant_tie).
 * [DFConstantTie](schema/constant_tie) - ties a [DFPort](schema/port) to a constant value.
 * [DFDefine](schema/define) - a named constant value.
 * [DFInterconnect](schema/interconnect) - describes a signal type for ports and connections, from a single wire to a complex bus.
 * [DFInterconnectComponent](schema/interconnect_component) - one component of a [DFInterconnect](schema/interconnect) which can be simple (just a wire) or complex (referring to another [DFInterconnect](schema/interconnect)).
 * [DFPort](schema/port) - a single port on a [DFBlock](schema/block), which instantiates a [DFInterconnect](schema/interconnect).
 * [DFProject](schema/project) - the root container for an elaborated design.
 * [DFRegister](schema/register) - represents a register formed of a collection of [DFRegisterField](schema/register).
 * [DFRegisterField](schema/register_field) - a single field within a [DFRegister](schema/register).
 * [DFRegisterGroup](schema/register_group) - a named collection of [DFRegisters](schema/register).

```eval_rst
.. Declare a real ToC so that we can navigate using the sidebar, but make it hidden so we can use the custom version above - which has descriptions for each item!
.. toctree::
    :maxdepth: 1
    :hidden:

    schema/address_map
    schema/address_map_constraint
    schema/address_map_initiator
    schema/address_map_target
    schema/base
    schema/block
    schema/command
    schema/command_field
    schema/connection
    schema/constant_tie
    schema/define
    schema/interconnect
    schema/interconnect_component
    schema/port
    schema/project
    schema/register
    schema/register_field
    schema/register_group
```
