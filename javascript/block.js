// Copyright (C) 2019 Blu Wireless Ltd.
// All Rights Reserved.
//
// This file is part of DesignFormat.
//
// DesignFormat is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation, either version 3 of the License, or (at your option) any later
// version.
//
// DesignFormat is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License along with
// DesignFormat. If not, see <https://www.gnu.org/licenses/>.
//

try {
    DFAddressMap    = require('./address_map.js').DFAddressMap;
    DFBase          = require('./base.js').DFBase;
    DFConnection    = require('./connection.js').DFConnection;
    DFConstants     = require('./constants.js').DFConstants;
    DFPort          = require('./port.js').DFPort;
    DFRegisterGroup = require('./register_group.js').DFRegisterGroup;
} catch(e) {
    // Pass
}

//------------------------------------------------------------------------------
// DFBlock:
//  - ID         : Instance identifier for this block
//  - ROOTPATH   : Hierarchical path to this instance
//  - TYPE       : The module type (i.e. not the instantiation name)
//  - DESCRIPTION: Description of the block
//------------------------------------------------------------------------------

/**
 * DesignFormat representation of a system block
 */
class DFBlock extends DFBase {

    /**
     * Construct the block instance
     * @param {string} id - Instance identifier for this block
     * @param {string} type - The module type (i.e. not the instantiation name)
     * @param {DFBase} parent - Pointer to the parent node of this block either
     *                          a DFBlock or a DFProject
     * @param {string} description - Human-readable description of the object
     * @param {DFAddressMap} address_map - Address map to associate
     */
    constructor(id, type, parent, description, address_map) {
        super(id, description);

        this.type = type;
        this.parent = parent;

        this.ports = { input: [], output: [], inout: [] };
        this.children = [];
        this.connections = [];
        this.registers = [];
        this.address_map = address_map;

        // Use a Proxy to allow direct access to child nodes and attributes
        try {
            return new Proxy(this, {
                get: (target, key) => {
                    // If it's a direct attribute, return that
                    if (key in target) return target[key];
                    // Otherwise look to see if a child matches
                    for (let c of target.children) if (c.id == key) return c;
                    // Look to see if a register matches
                    for (let r of target.registers) if (r.id == key) return r;
                    // Otherwise return nothing
                    return undefined;
                }
            });
        } catch(e) {
            return this;
        }
    }

    /**
     * Returns the full hierarchical path to this block from the root
     */
    hierarchicalPath() {
        var path = this.id;
        if (this.parent != null && (this.parent instanceof DFBlock)) {
            path = this.parent.hierarchicalPath() + "." + path;
        }
        return path;
    }

    /**
     * Returns the root block of the design (stopping before the DFProject)
     */
    getRootBlock() {
        if (this.parent != null && (this.parent instanceof DFBlock)) {
            return this.parent.getRootBlock();
        } else {
            return this;
        }
    }

    /**
     * Resolves the root block of the design, and then gets its parent DFProject
     */
    getProject() {
        var root = this.getRootBlock();
        if (root != null && root.parent != null && (root.parent instanceof DFProject)) {
            return root.parent;
        } else {
            return null;
        }
    }

    /**
     * Return a DFPort or DFBlock definition based on a hierarchical path
     * @param {*} path - The path to resolve
     */
    resolvePath(path) {
        // We expect a path of the form: parent.child.grandchild[portname]
        //  - We can also support 'parent.child' and '[portname]'

        // Now extract lookup path segments
        var parts = /^([\w\.\-]+)?(\[[\w\-]+\])?$/g.exec(path);
        var sections = (parts[1] != undefined) ? parts[1].split('.') : [];
        var port_name = (parts[2] != undefined) ? parts[2].replace(/([\[\]]+)/g, '') : null;

        if (sections.length > 0) {
            var next_id = sections[0];
            var found = this.children.filter(function (child) {
                return (child.id == next_id.trim());
            });
            if (found.length != 1) {
                // Is this my ID?
                if (next_id.trim() == this.id) {
                    var sub_path = sections.slice(1).join(".");
                    if (port_name != null) sub_path += '[' + port_name + ']';
                    return this.resolvePath(sub_path);
                } else {
                    throw Error(
                        "Unable to resolve block - 0 or more than 1 child available - path: "
                        + path + " (hierarchy " + this.hierarchicalPath() + ")"
                    );
                }
            }
            if (sections.length > 1 || port_name != null) {
                var sub_path = sections.slice(1).join(".");
                if (port_name != null) sub_path += '[' + port_name + ']';
                return found[0].resolvePath(sub_path);
            } else {
                return found[0];
            }

        } else if (sections.length == 0 && port_name != null) {
            var all_ports = this.ports.input.concat(this.ports.output, this.ports.inout);
            var found = all_ports.filter(function (port) {
                return (port.name == port_name);
            });
            if (found.length != 1) {
                throw Error(
                    "Unable to resolve port - 0 or more than 1 option available - path: "
                    + path + " (hierarchy " + this.hierarchicalPath() + ")"
                );
            }
            return found[0];

        } else if (sections.length == 0) {
            return this;

        } else {
            throw Error(
                "Unable to resolve port - no path provided (hierarchy " + path + ")"
            );
        }

        return NULL;
    }

    /**
     * Attach a DFRegisterGroup to this block
     * @param {DFRegisterGroup} register - The register group to attach
     */
    addRegister(register) {
        if (!(register instanceof DFRegisterGroup)) {
            throw Error("Register is not of type DFRegister or DFRegisterGroup");
        }
        register.block = this;
        this.registers.push(register);
    }

    /**
     * Attach a DFBlock to this block as a child node
     * @param {DFBlock} child - The child to attach
     */
    addChild(child) {
        if (!(child instanceof DFBlock)) {
            throw Error("Child is not of type DFBlock");
        }
        this.children.push(child);
    }

    /**
     * Attach a new port to this block (can be input, output, or bidirectional)
     * @param {DFPort} port - The port to attach
     */
    addPort(port) {
        if (!(port instanceof DFPort)) {
            throw Error("Port is not of type DFPort");
        }
        switch (port.direction) {
            case DFConstants.DIRECTION.INPUT: {
                this.ports.input.push(port);
                break;
            }
            case DFConstants.DIRECTION.OUTPUT: {
                this.ports.output.push(port);
                break;
            }
            case DFConstants.DIRECTION.INOUT: {
                this.ports.inout.push(port);
                break;
            }
            default: {
                throw Error("Unsupported port direction: " + port.direction);
            }
        }
    }

    /**
     * Get the principal signal (input port or child output port) for a particular
     * interconnect type.
     * @param {DFInterconnect} intc_type - The interconnect to resolve
     */
    getPrincipalSignal(intc_type) {
        if (intc_type instanceof DFInterconnect) intc_type = intc_type.id;
        // Find all input ports matching the type
        var of_type = this.ports.input.filter(function (x) {
            return (x.type == intc_type);
        });
        // Find all child output ports matching the type
        this.children.forEach(function (child) {
            of_type = of_type.concat(child.ports.output.filter(function (x) {
                return (x.type == intc_type);
            }));
        });
        // Now filter out which (if any) port has been nominated as principal
        var principal = of_type.filter(function (x) {
            return x.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL);
        });
        // Assert that a maximum of only one principal exists
        if (principal.length > 1) {
            throw new Error("More than one principal port of type " + intc_type);
        }
        // If a principal exists, return it, else return nothing
        return (principal.length > 0) ? principal[0] : null;
    }

    /**
     * Nominate an input port or child output port as the principal signal for a
     * particular interconnect type (e.g. the main clock signal for a block is
     * the 'principal' clock).
     * @param {DFPort} port - The port to nominate as principal
     */
    setPrincipalSignal(port) {
        // Check this port actually exists?
        var real_port = null;
        if (port instanceof DFPort) {
            real_port = port;
            if (this.ports.input.indexOf(real_port) < 0) {
                throw new Error("Port is not one of the input ports of this block");
            }
        } else {
            var found = this.ports.input.filter(function (x) {
                return (x.name == port);
            });
            if (found.length != 1) {
                throw new Error("Port is not one of the input ports of this block");
            }
            real_port = found[0];
        }
        // Check if we have a principal of this type already, clear it
        var existing = this.getPrincipalSignal(port.type);
        if (existing != null) {
            existing.setAttribute(DFConstants.ATTRIBUTES.PRINCIPAL, false);
        }
        // Setup the new principal
        real_port.setAttribute(DFConstants.ATTRIBUTES.PRINCIPAL, true);
    }

    /**
     * Return a concatenated list of all of the ports on the block
     */
    getAllPorts() {
        return this.ports.input.concat(this.ports.output).concat(this.ports.inout).sort(function (a, b) {
            return a.name < b.name;
        });
    }

    /**
     * Return a list of all ports on this block that are not internally connected
     */
    getUnconnectedPorts() {
        var ports = [];
        this.getAllPorts().forEach(function (port) {
            if (
                (
                    (port.direction == DFConstants.DIRECTION.INPUT) &&
                    (port.getOutboundConnections().length == 0)
                ) ||
                (
                    (port.direction == DFConstants.DIRECTION.OUTPUT) &&
                    (port.getInboundConnections().length == 0)
                )
            ) {
                ports.push(port);
            }
        });
        return ports;
    }

    /**
     * Return a list of all ports on child modules that are not connected within
     * this block
     */
    getUnconnectedChildPorts() {
        var ports = [];
        this.children.forEach(function (child) {
            child.getAllPorts().forEach(function (port) {
                if (
                    (
                        (port.direction == DFConstants.DIRECTION.INPUT) &&
                        (port.getInboundConnections().length == 0)
                    ) ||
                    (
                        (port.direction == DFConstants.DIRECTION.OUTPUT) &&
                        (port.getOutboundConnections().length == 0)
                    )
                ) {
                    ports.push(port);
                }
            });
        });
        return ports;
    }

    /**
     * Create a connection between two ports - specifying which signal within
     * each port is part of the connection (for ports with count > 1).
     * @param {DFPort} start_port - The port driving the connection
     * @param {DFPort} start_index - Signal index within the driver port
     * @param {integer} end_port - The port being driven by the connection
     * @param {integer} end_index - Signal index within the driven port
     */
    addConnection(start_port, start_index, end_port, end_index) {
        if (!(start_port instanceof DFPort) || !(end_port instanceof DFPort)) {
            throw Error("Port is not of type DFPort");
        }
        this.connections.push(
            new DFConnection(start_port, start_index, end_port, end_index)
        );
    }

    /**
     * Create a connection between a port and a constant, specifying which signal
     * within the port is part of the connection (for ports with count > 1)
     * @param {DFPort} port - The port to drive
     * @param {integer} signal_index - The signal index within the port to drive
     * @param {DFConstantTie} constant - The constant value to drive onto the port
     */
    addTieOff(port, signal_index, constant) {
        if (!(port instanceof DFPort)) {
            throw Error("Port is not of type DFPort");
        } else if (!(constant instanceof DFConstantTie)) {
            throw Error("Constant is not of type DFConstantTie");
        }
        this.connections.push(new DFConnection(constant, 0, port, signal_index));
    }

    /**
     * Return a list of all of the connection types used in this hierarchy. You
     * can limit the depth of the query using the 'depth' parameter, not passing
     * the value will return unlimited depth.
     * @param {integer} depth - How deep to retrieve (whether to query children)
     */
    getInterconnectTypes(depth) {
        var all_types = [];
        var _this = this;

        // Append all of my children's port types
        this.getAllPorts().forEach(function (port) {
            all_types.push(_this.getProject().getInterconnectType(port.type));
        });

        // Ask my children for their types
        if (this.children && this.children.length > 0 && (depth == undefined || depth > 0)) {
            this.children.forEach(function (child) {
                all_types = all_types.concat(child.getInterconnectTypes(
                    ((depth == undefined) ? undefined : (depth - 1))
                ));
            });
        }

        // Create an ordered, unique list of the types
        var intc_types = Array.from(new Set(all_types)).sort(function (a, b) {
            return (a.id > b.id);
        });

        return intc_types;
    }

    /**
     * Return a list of all of the types of the child modules. You can limit the
     * depth of the query using the 'depth' parameter, not passing the value will
     * return unlimited depth.
     * @param {integer} depth  - How deep to retrieve (whether to query children)
     */
    getChildTypes(depth) {
        var all_types = this.children.slice();

        // Ask my children for their types
        if (this.children && this.children.length > 0 && (depth == undefined || depth > 0)) {
            this.children.forEach(function (child) {
                all_types = all_types.concat(child.getChildTypes(
                    ((depth == undefined) ? undefined : (depth - 1))
                ));
            });
        }

        // Create a unique set of examples of each type of DFBlock
        var got_types = [];
        var unique_types = [];
        all_types.forEach(function (block) {
            if (got_types.indexOf(block.type) < 0) {
                got_types.push(block.type);
                unique_types.push(block);
            }
        });

        // Sort the list
        unique_types = unique_types.sort(function (a, b) {
            return (a.id > b.id);
        });

        return unique_types;
    }

    /**
     * Set the address map for this block. The address map models how initiator
     * and target ports on the block are linked.
     * @param {DFAddressMap} map - The address map
     */
    setAddressMap(map) {
        if (!(map instanceof DFAddressMap)) {
            throw new Error("Address map not of correct type " + map.constructor.name)
        } else if (this.address_map) {
            throw new Error("An address map has already been configured for " + this.hierarchicalPath());
        }
        this.address_map = map
        this.address_map.block = this;
    }

    /**
     * Use the ports and address map of this block to work out the relative
     * address needed to access a specified remote point. If the remote point is
     * a port, we just need to iterate through our outputs. If the remote point
     * is a block then we need to iterate through our outputs and their inputs.
     * @param {DFBase} remote - Either a DFBlock or a DFPort to find the address of
     * @param {integer} remote_index - If the remote is a DFPort, this is used as
     *                                 the signal index.
     */
    getRelativeAddress(remote, remote_index) {
        // Default the remote index value to 0
        remote_index = remote_index || 0;
        // Sanity checks
        if (!(remote instanceof DFPort) && !(remote instanceof DFBlock)) {
            throw new Error("Remote is of invalid type " + remote.constructor.name);
        } else if ((remote instanceof DFPort ) && (remote_index < 0 || remote_index >= remote.count)) {
            throw new Error("Remote index is not valid " + remote_index);
        }
        // Find all of the viable sources (ports on this block)
        let sources = [];
        for (let output of this.ports.output) {
            for (let i = 0; i < output.count; i++) sources.push([output, i]);
        }
        if (sources.length == 0) {
            throw new Error("Failed to identify any sources for " + this.hierarchicalPath());
        }
        // Find all of the viable targets (ports on the remote block)
        let targets = [];
        if (remote instanceof DFPort) {
            targets.push([remote, remote_index]);
        } else {
            for (let input of remote.ports.input) {
                for (let i = 0; i < input.count; i++) targets.push([input, i]);
            }
        }
        if (targets.length == 0) {
            throw new Error("Failed to identify any targets for " + remote.hierarchicalPath());
        }
        // Attempt to find a pairing between sources and targets that is linked
        for (let source of sources) {
            for (let target of targets) {
                let path = source[0].findConnectionPath(target[0], source[1], target[1]);
                if (path) {
                    return source[0].getRelativeAddress(target[0], source[1], target[1]);
                }
            }
        }
        // Otherwise there isn't a pathway
        return None
    }

    /**
     * Dump out this node so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        // Get our base object
        var obj = super.dumpObject(project);

        // Attach extra details
        obj.path = this.hierarchicalPath();
        obj.type = this.type;
        obj.parent = (
            (this.parent != null && this.parent instanceof DFBlock)
                ? this.parent.hierarchicalPath() : null
        );

        // Attach all ports
        obj.ports = { input: [], output: [], inout: [] };
        this.ports.input.forEach(function (port) { obj.ports.input.push(port.dumpObject(project)); });
        this.ports.output.forEach(function (port) { obj.ports.output.push(port.dumpObject(project)); });
        this.ports.inout.forEach(function (port) { obj.ports.inout.push(port.dumpObject(project)); });

        // Attach all children
        obj.children = [];
        this.children.forEach(function (child) { obj.children.push(child.dumpObject(project)); });

        // Attach all connections
        obj.connections = [];
        this.connections.forEach(function (conn) { obj.connections.push(conn.dumpObject(project)); });

        // Attach all registers
        obj.registers = [];
        this.registers.forEach(function (reg) { obj.registers.push(reg.dumpObject(project)); });

        // Attach the address map if present
        if (this.address_map) obj['address_map'] = this.address_map.dumpObject(project);

        // Return the object
        return obj;
    }

    /**
     * Reload this node from passed in object.
     * @param {object} obj - Description of this node
     * @param {DFBase} root - Root object in the tree
     * @param {object} types - Map from class name to class definition
     */
    loadObject(obj, root, types) {
        super.loadObject(obj, root, types);

        // Work out if we're the root?
        root = (root != null) ? root : this;

        // Lookup our parent
        if (obj.parent != null) {
            this.parent = root.resolvePath(obj.parent);
        }

        this.type = obj.type;

        // At this point, register against my parent so that sub-blocks can use
        // path resolving.
        if (this.parent) this.parent.children.push(this);

        var _this = this;

        if (obj.ports != null && obj.ports.input != null) obj.ports.input.forEach(function (item) {
            _this.ports.input.push((new DFPort(null, null, DFConstants.DIRECTION.INPUT, _this)).loadObject(item, root, types));
        });
        if (obj.ports != null && obj.ports.output != null) obj.ports.output.forEach(function (item) {
            _this.ports.output.push((new DFPort(null, null, DFConstants.DIRECTION.OUTPUT, _this)).loadObject(item, root, types));
        });
        if (obj.ports != null && obj.ports.inout != null) obj.ports.inout.forEach(function (item) {
            _this.ports.inout.push((new DFPort(null, null, DFConstants.DIRECTION.INOUT, _this)).loadObject(item, root, types));
        });
        if (obj.registers != null) obj.registers.forEach(function (item) {
            _this.addRegister((new DFRegisterGroup()).loadObject(item, root, types));
        });

        if (obj.children != null) obj.children.forEach(function (item) {
            (new DFBlock()).loadObject(item, root, types);
        });

        // Build out interconnections between my children
        if (obj.connections != null) obj.connections.forEach(function (item) {
            _this.connections.push((new DFConnection()).loadObject(item, root, types));
        });

        // Reload the address map for the block
        if (obj.address_map) {
            this.setAddressMap((new DFAddressMap()).loadObject(obj.address_map, root, types));
        }

        return this;
    }

}

try {
    module.exports.DFBlock = DFBlock;
} catch (e) {
    // Pass
}
