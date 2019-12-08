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
 * Defines a named constant value related to the design.
 */
class DFDefine extends DFBase {

    /**
     * Constructor for the defined value.
     * @param {string} id - Name of the constant
     * @param {any} value - Value of the constant (can be integer, or otherwise)
     * @param {string} description - Human-readable description of the definition
     */
    constructor(id, value, description) {
        super(id, description);
        this.value = value;
    }

    /**
     * Dump out this node so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        // Get our base object
        var obj = super.dumpObject(project);

        // Attach the carried value
        obj.value = this.value;

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

        // Reload the carried value
        this.value = obj.value;

        // Return this for chaining
        return this;
    }
}

try {
    module.exports.DFDefine = DFDefine;
} catch (e) {
    // Pass
}
