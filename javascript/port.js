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
    DFBase = require('./base.js').DFBase;
    DFConnection = require('./connection.js').DFConnection;
    DFConstants = require('./constants.js').DFConstants;
} catch(e) {
    // Pass
}

/**
 * DesignFormat representation of a port (input, output or inout)
 */
class DFPort extends DFBase {

    /**
     * Constructor for a port object.
     * @param {string} name - Name of the port
     * @param {string} type - Interface type, which refers to a DFInterconnect
     * @param {integer} count - Number of signals carried by the port
     * @param {string} direction - Whether an input or output
     * @param {DFBlock} block - Reference to the parent DFBlock
     * @param {string} description - Human-readable description of the port
     */
    constructor(name, type, count, direction, block, description) {
        // Create an identifier for this port
        var id = (block != null) ? block.id + "[" + name + "]" : name;
        super(id, description);

        this.name = name;
        this.type = type;
        this.count = count;
        this.direction = direction;
        this.block = block;

        this.connections = [];

        if (
            (name != undefined) &&
            (type != undefined) &&
            (count != undefined) &&
            (direction != undefined) &&
            (block != undefined)
        ) {
            this.check();
        }
    }

    /**
     * Returns the DFInterconnect that this connection represents
     */
    getInterconnectType() {
        var project = this.block.getProject();
        if (project != null) {
            return project.getInterconnectType(this.type);
        } else {
            return null;
        }
    }

    /**
     * Returns a complete hierarchical path from the DFProject's root node all
     * the way down to this port.
     */
    hierarchicalPath() {
        var path = this.block.hierarchicalPath() + '[' + this.name + ']';
        return path;
    }

    /**
     * Sanity check that the direction is allowed
     */
    check() {
        if (Object.values(DFConstants.DIRECTION).indexOf(this.direction) < 0) {
            throw Error("Unsupported DFPort direction: " + this.direction);
        }
    }

    /**
     * Add a new connection to this port, either to another port or a DFConstantTie
     * @param {DFConnection} conn - The connection
     */
    addConnection(conn) {
        if (!(conn instanceof DFConnection)) {
            throw Error("Connection not of type DFConnection");
        }
        this.connections.push(conn);
    }

    /**
     * Return just the outbound connections (where we are the driver)
     */
    getOutboundConnections() {
        var _this = this;
        return this.connections.filter(function (conn) {
            return conn.start_port == _this;
        });
    }

    /**
     * Return just the inbound connections (where we are being driven)
     */
    getInboundConnections() {
        var _this = this;
        return this.connections.filter(function (conn) {
            return conn.end_port == _this;
        });
    }

    /**
     * Return a list of ports that are driven by this port
     */
    getReceiverPorts() {
        var receivers = [];
        this.getInboundConnections().forEach(function (conn) {
            receivers.push(conn.end_port);
        });
        return receivers;
    }

    /**
     * Return a list of ports that are driving this port
     */
    getDriverPorts() {
        var drivers = [];
        this.getOutboundConnections().forEach(function (conn) {
            drivers.push(conn.start_port);
        });
        return receivers;
    }

    /**
     * Chase a connection from the port to it's ultimate destination, note that
     * this function returns a tuple containing the port and the signal index.
     * @param {integer} index - The signal index within the port to chase from
     * @param {list} path - The current path chased up to this point (used by
     *                      recursive calls)
     */
    chaseConnection(index, path) {
        // Default index
        index = index || 0;
        // Copy the path so that we don't modify a shared object
        path = path ? path.slice() : [];
        // Add myself to the path
        path.push([this, index]);
        // If I'm an input to a leaf node, then return the path to this point
        if (this.block.ports.input.includes(this) && this.block.getAttribute(DFConstants.ATTRIBUTES.LEAF_NODE)) {
            return [path];
        }
        // Get all of my outbound connections for the right index
        let outbound = this.getOutboundConnections().filter((item) => {
            return item.start_index == index;
        });
        // For each outbound connection, recursively chase the connection
        let destinations = [];
        for (let conn of outbound) {
            destinations = destinations.concat(
                conn.end_port.chaseConnection(conn.end_index, path)
            );
        }
        // Return all of the destinations I found
        return destinations;
    }

    /**
     * If this port is an initiator in an address map, resolve an address as if
     * part of a transaction initiated through this port.
     * @param {integer} address - The address to resolve
     * @param {integer} index - The index of the signal within the port initiating the
     *                          transaction (default: 0)
     */
    resolveAddress(address, index) {
        // Default index
        index = index || 0;
        // If the block has an address map and I'm an initiator
        let destinations = null;
        if (this.block.address_map && this.block.address_map.getInitiator(this, index)) {
            let initiator = this.block.address_map.getInitiator(this, index);
            // Resolve the address to a target
            let target = initiator.resolveAddress(address);
            if (!target) {
                throw new Error(
                    "No target in address map of " + this.block.hierarchicalPath()
                    + " resolves address 0x" + address.toString(16)
                );
            }
            // Apply initiator masking to the address
            address = initiator.outboundAddress(address);
            // Chase the outbound connection
            destinations = target.port.chaseConnection(target.port_index);
        // Otherwise I could be mid-link?
        } else {
            destinations = this.chaseConnection(index);
        }
        // If I don't have a unique destination, this is bad
        if (destinations.length > 1) {
            throw new Error(
                "Cannot determine end-point for address 0x" + address.toString(16) +
                "found " + destinations.length + " destinations"
            );
        // If I have no destinations, then I must be the endpoint!
        } else if (destinations.length == 0 || destinations[0].slice(-1)[0][0] == this) {
            return this;
        }
        // Recursively hunt for the end-point
        return destinations[0].slice(-1)[0][0].resolveAddress(address, destinations[0].slice(-1)[0][1]);
    }

    /**
     * Try to find a connection pathway between this port and a remote port,
     * this procedure can use both basic connectivity information and the address
     * map to try and find interconnections. A flood search is used, with the
     * shortest path being preferred.
     * @param {DFPort} remote_port - The remote port we are trying to reach
     * @param {integer} local_index - The index of the signal within this port
     * @param {integer} remote_index - The index of the signal within the remote port
     * @param {list} path - Used to track the path construction during recursion
     */
    findConnectionPath(remote_port, local_index, remote_index, path) {
        // Defaults
        local_index  = local_index || 0;
        remote_index = remote_index || 0;
        // Copy the path so that we don't modify a shared object
        path = path ? path.slice() : [];
        // Check that we haven't got stuck in a deadlock loop
        for (let item of path) {
            if (item[0] == this && item[1] == local_index) return null;
        }
        // Check that I'm not the destination?
        if (remote_port == this && remote_index == local_index) {
            return path;
        }
        // Chase any outbound connections from the port
        let destinations = this.chaseConnection(local_index);
        // See if any of the destinations are the desired port
        for (let dest of destinations) {
            if (dest.slice(-1)[0][0] == remote_port && dest.slice(-1)[0][1] == remote_index) {
                return path.concat(dest);
            }
        }
        // If we didn't find the port, see if we can use an address map
        let pathways = [];
        for (let dest of destinations) {
            let addr_map = dest.slice(-1)[0][0].block.address_map
            if (addr_map) {
                // See if the destination we have is an initiator
                let stop = dest.slice(-1)[0];
                let init = addr_map.getInitiator(stop[0], stop[1]);
                if (init) {
                    // Find the list of targets for this initiator
                    let targets = addr_map.getTargetsForInitiator(init);
                    // For each target, see if it resolves to a destination
                    for (let target of targets) {
                        let full_path = target.port.findConnectionPath(
                            remote_port, target.port_index, remote_index,
                            path.concat(dest)
                        );
                        if (full_path) pathways.push(full_path);
                    }
                }
            }
        }
        // If we couldn't find the port, return null (dead-end)
        if (pathways.length == 0) return null;
        // Otherwise return the shortest path
        else return pathways.sort((a, b) => { return a.length - b.length; })[0];
    }

    /**
     * Calculate the relative address to access a remote port via basic connectivity
     * and any address maps. This leverages the findConnectionPath function to
     * first identify a viable path, then works through the path to identify the
     * base address of the port.
     * @param {DFPort} remote_port - The port to resolve
     * @param {integer} local_index - Outbound signal index to start from
     * @param {integer} remote_index - Inbound signal index of the target
     */
    getRelativeAddress(remote_port, local_index, remote_index) {
        // Default values
        local_index  = local_index || 0;
        remote_index = remote_index || 0;
        // First calculate the path, and see if this is viable
        let path = this.findConnectionPath(remote_port, local_index, remote_index)
        if (!path) return null;
        // Extract just the nodes in the path that have associated address maps
        let contributors = path.filter((item) => { return item[0].block.address_map; });
        // If there are no contributors to the address, return 0
        if (contributors.length == 0) return 0;
        // Walk backwards through the path to assess the base address of the endpoint
        let base_address = 0
        for (let node of contributors.slice().reverse()) {
            if (node[0].block.address_map) {
                let init = node[0].block.address_map.getInitiator(node[0], node[1]);
                let tgt  = node[0].block.address_map.getTarget(node[0], node[1]);
                if (init && tgt) {
                    throw new Error(
                        "Node in path is both initiator and target " + node[0].hierarchicalPath()
                        );
                } else if (init) {
                    base_address -= init.offset;
                } else if (tgt) {
                    base_address += tgt.offset
                } else {
                    throw new Error(
                        "Node in path is not associated to the block's address map "
                        + node[0].hierarchicalPath()
                    );
                }
            }
        }
        // If the last node in the list of contributors is an initiator, add back
        // in the offset (our addresses will be relative to this point)
        let last_node = contributors[0];
        let initiator = last_node[0].block.address_map.getInitiator(last_node[0], last_node[1]);
        if (initiator) base_address += initiator.offset;
        return base_address;
    }

    /**
     * Dump out this node so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        var obj = super.dumpObject(project);

        obj.name = this.name;
        obj.type = this.type;
        obj.count = this.count;
        obj.direction = this.direction;
        obj.block = this.block.hierarchicalPath();

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

        this.name = obj.name;
        this.type = obj.type;
        this.count = parseInt(obj.count);
        this.direction = obj.direction;
        if (obj.block != null) this.block = root.resolvePath(obj.block);

        this.check();

        return this;
    }

}

try {
    module.exports.DFPort = DFPort;
} catch (e) {
    // Pass
}
