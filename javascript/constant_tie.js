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
} catch(e) {
    // Pass
}

/**
 * DesignFormat representation of a tie to a constant value
 */
class DFConstantTie extends DFBase {

    /**
     * Constructor for the constant tie value
     * @param {integer} value - The constant value represented by this tie
     * @param {boolean} reset - Ignore the value field, instead tie to the
     *                          DFInterconnect's reset value.
     * @param {DFBlock} block - Reference to the block holding this tie
     */
    constructor(value, reset, block) {
        // Create an identifier for this port
        var id = (block != null) ? (block.id + '-tie-' + value) : ('tie-' + value);
        super(id);

        this.value = value;
        this.reset = reset;
        this.block = block;

        this.connections = [];
    }

    /**
     * Returns the full hierarchical path to this block from the root
     */
    hierarchicalPath() {
        var path = this.block.hierarchicalPath() + '[' + this.name + ']';
        return path;
    }

    /**
     * Associate a DFConnection with this constant tie value
     * @param {DFConnection} conn - The connection to associate
     */
    addConnection(conn) {
        if (conn.constructor.name != 'DFConnection') {
            throw Error("Connection not of type DFConnection");
        }
        this.connections.push(conn);
    }

    /**
     * Dump out this node so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        var obj = super.dumpObject(project);

        obj.value = this.value;
        obj.reset = this.reset;
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

        this.value = obj.value;
        this.reset = obj.reset || false;
        if (obj.block != null) this.block = root.resolvePath(obj.block);

        return this;
    }

}

try {
    module.exports.DFConstantTie = DFConstantTie;
} catch (e) {
    // Pass
}
