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
    DFConstantTie = require('./constant_tie.js').DFConstantTie;
} catch(e) {
    // Pass
}

/**
 * DesignFormat representation of an interconnection between two points
 */
class DFConnection extends DFBase {

    /**
     * Constructor of the connection
     * @param {DFBase} start_port - Start point can be a DFPort or DFConstantTie
     * @param {integer} start_index - Signal index within DFPort to connect
     * @param {DFPort} end_port - End point can only be a DFPort
     * @param {integer} end_index - Signal index within DFPort to connect
     */
    constructor(start_port, start_index, end_port, end_index) {
        if (start_port != null && end_port != null) {
            // Create an identifier for this connection
            var id = start_port.id + "[" + start_index + "]";
            id += "-to-";
            id += end_port.id + "[" + end_index + "]";

            // Call the constructor
            super(id);

            this.start_port = start_port;
            this.start_index = start_index || 0;
            this.end_port = end_port;
            this.end_index = end_index || 0;

            if (this.start_port != null) this.start_port.addConnection(this);
            if (this.end_port != null) this.end_port.addConnection(this);

            this.checkConnection();
        } else {
            super('dfconnection-' + Math.floor(Math.random() * 1000000));
        }
    }

    /**
     * Check that the connection is sane with sensible signal indexes
     */
    checkConnection() {
        if (this.start_port.constructor.name == 'DFPort') {
            if (this.start_index < 0 || this.start_index >= this.start_port.count) {
                throw new Error("Start index " + this.start_index + " is out of range for port count " + this.start_port.count);
            }
        }
        if (this.end_port.constructor.name == 'DFPort') {
            if (this.end_index < 0 || this.end_index >= this.end_port.count) {
                throw new Error("End index " + this.end_index + " is out of range for port count " + this.end_port.count);
            }
        }
    }

    /**
     * Returns the DFInterconnect type of the end points of this interconnect
     */
    getInterconnectType() {
        return this.start_port.getInterconnectType();
    }

    /**
     * Returns if this connection is a tie-off (i.e. start point is a DFConstantTie)
     */
    isTieOff() {
        return (this.start_port instanceof DFConstantTie);
    }

    /**
     * Dump out this node so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        var obj = super.dumpObject(project);

        if (this.start_port instanceof DFPort) {
            obj.start_port = {
                block: this.start_port.block.hierarchicalPath(),
                port: this.start_port.name
            };
        } else if (this.start_port instanceof DFConstantTie) {
            obj.start_tie = this.start_port.dumpObject();
        }

        obj.end_port = {
            block: this.end_port.block.hierarchicalPath(),
            port: this.end_port.name
        };

        obj.start_index = this.start_index;
        obj.end_index = this.end_index;

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

        if (obj.start_port) {
            var start_path = obj.start_port.block + '[' + obj.start_port.port + ']';
            this.start_port = root.resolvePath(start_path);
        } else if (obj.start_tie) {
            this.start_port = (new DFConstantTie()).loadObject(obj.start_tie, root, types);
        }

        var end_path = obj.end_port.block + '[' + obj.end_port.port + ']';
        this.end_port = root.resolvePath(end_path);

        this.start_port.addConnection(this);
        this.end_port.addConnection(this);

        this.start_index = parseInt(obj.start_index || 0);
        this.end_index = parseInt(obj.end_index || 0);

        this.checkConnection();

        return this;
    }

}

try {
    module.exports.DFConnection = DFConnection;
} catch (e) {
    // Pass
}
