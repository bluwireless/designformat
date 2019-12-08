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
    DFConstants    = require('./constants.js').DFConstants;
    DFCommand      = require('./command.js').DFCommand;
    DFCommandField = require('./command_field.js').DFCommandField;
} catch(e) {
    // Pass
}

/**
 * DesignFormat representation of a register field. This is treated as a special
 * case of a DFCommandField. Currently no extra parameters are necessary, but
 * the class is created for future extensibility.
 */
class DFRegisterField extends DFCommandField {

    /**
     * Constructor for the register field object
     * @param {string} id - The name of the register field
     * @param {integer} lsb - Least significant bit position within the command
     * @param {integer} size - Width of the field in bits
     * @param {integer} reset - Value taken at reset (or default value)
     * @param {boolean} signed - Whether the value is signed
     * @param {string} description - Human-readable description
     */
    constructor(id, lsb, size, reset, signed, description) {
        super(id, lsb, size, reset, signed, description);
    }

}

/**
 * DesignFormat representation of a register. This is treated as a special case
 * of DFCommand, with extra parameters for its offset and access conditions.
 * However, unlike with commands, register fields should never overlap.
 */
class DFRegister extends DFCommand {

    /**
     * Constructor for the register object
     * @param {string} id - Name of the register
     * @param {integer} offset - Offset from the register group's base address
     * @param {string} bus_access - Type of software access to the register
     *                              (e.g. RW, RO, WO, etc)
     * @param {string} block_access - Type of hardware access to the register
     *                                (e.g. RO, WO, ...)
     * @param {string} inst_access - Type of instruction access to the register
     *                               (e.g. RO, WO, ...)
     * @param {DFRegisterGroup} group - The parent group of this register
     * @param {string} description - Human read-able description of the register
     */
    constructor(id, offset, bus_access, block_access, inst_access, group, description) {
        super(id, 0, description);
        this.__fieldtype = DFRegisterField;

        this.offset = offset;
        this.group = group;
        this.access = {
            bus  : bus_access   || DFConstants.ACCESS.RW,
            block: block_access || DFConstants.ACCESS.RW,
            inst : inst_access  || DFConstants.ACCESS.RW
        };

        var _this = this;
        Object.keys(this.access).forEach(function (key) {
            if (Object.values(DFConstants.ACCESS).indexOf(_this.access[key]) < 0) {
                throw Error("DFRegister does not support access type " + _this.access[key]);
            }
        });

        this.fields = [];

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
     * Ensures fields are in ascending bit order - also checks for overlaps.
     */
    sortFields() {
        // Use the default sorting order
        super.sortFields();

        // Now walk up the set and check for overlaps
        var last_lsb = -1;
        this.fields.forEach(function (field) {
            if (field.lsb <= last_lsb) {
                throw Error("LSB of two DFRegisterFields overlap!");
            }
            last_lsb = field.lsb + field.size - 1;
        });
    }

    /**
     * Calculate the total offset of this register from the register bank's base
     * address, taking into account the parent group's offset.
     */
    getOffset() {
        var offset = this.offset;
        if (this.group.constructor.name == "DFRegisterGroup") offset += this.group.offset;
        return offset;
    }

    /**
     * Get the address of this register relative to a port or block somewhere
     * else in the design. This leverages connectivity and address maps to
     * determine how the two points are related.
     * @param {DFBase} remote - DFPort or DFBlock to measure relative address from
     */
    getRelativeAddress(remote) {
        // Sanity checks
        if (["DFPort", "DFBlock"].indexOf(remote.constructor.name) < 0) {
            throw new Error("Remote is of invalid type " + remote.constructor.name);
        }
        // Find the handle to the remote block
        let remote_block = (remote.constructor.name == "DFBlock") ? remote : remote.block;
        // Leverage the block's getRelativeAddress function
        let base_addr = remote_block.getRelativeAddress(this.group.block);
        if (base_addr == null) return null;
        // Add in the offset of this register from the base of the register set
        return (base_addr + this.getOffset());
    }

    /**
     * Dump out this node so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        var obj = super.dumpObject(project);
        delete obj['width'];

        obj.offset = this.offset;
        obj.access = this.access;

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

        this.offset = obj.offset;
        this.access = obj.access;

        return this;
    }

}

try {
    module.exports.DFRegisterField = DFRegisterField;
    module.exports.DFRegister      = DFRegister;
} catch(e) {
    // Pass
}
