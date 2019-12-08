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
    DFCommandField = require('./command_field.js').DFCommandField;
} catch(e) {
    // Pass
}

/**
 * DesignFormat representation of a command. This could be used to
 * represent an instruction set for a CPU, or microcode for a DMA engine.
 * Commands can have arbitrary width, and fields can be positioned anywhere in
 * the bitmap. Fields can overlap if necessary (for commands with multiple
 * parameter options).
 */
class DFCommand extends DFBase {

    /**
     * Construct a command object
     * @param {string} id - Name of the command
     * @param {integer} width - Bit width of the command
     * @param {string} description - Human-readable description
     */
    constructor(id, width, description) {
        super(id, description);

        this.width = width;
        this.fields = [];
        this.__fieldtype = DFCommandField;

        // Use a Proxy to allow direct access to fields
        try {
            return new Proxy(this, {
                get: (target, key) => {
                    // If it's a direct attribute, return that
                    if (key in target) return target[key];
                    // Look to see if a register matches
                    for (let f of target.fields) if (f.id == key) return f;
                    // Otherwise return nothing
                    return undefined;
                }
            });
        } catch(e) {
            return this;
        }
    }

    /**
     * Add a field to the command store and sort the field store by LSB
     * @param {DFCommandField} field - The field to add
     */
    addField(field) {
        if (!(field instanceof this.__fieldtype)) {
            throw Error(
                "Tried to append non-" + this.__fieldtype.name + " to " +
                this.constructor.name
            );
        }
        this.fields.push(field);
        this.sortFields();
    }

    /**
     * Ensures fields are in ascending LSB order.
     */
    sortFields() {
        // Perform a sort on LSB
        this.fields.sort(function (a, b) {
            if (a.lsb < b.lsb) return -1;
            else if (a.lsb > b.lsb) return 1;
            else return 0;
        });
    }

    /**
     * Dump out this node so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        var obj = super.dumpObject(project);

        obj.width = this.width;
        obj.fields = [];
        this.fields.forEach(function (field) {
            obj.fields.push(field.dumpObject(project));
        });

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

        this.width = obj.width;

        var _this = this;
        if (obj.fields != null) obj.fields.forEach(function (field) {
            _this.addField((new _this.__fieldtype()).loadObject(field, types));
        });

        _this.sortFields();

        return this;
    }

}

try {
    module.exports.DFCommand = DFCommand;
} catch(e) {
    // Pass
}
