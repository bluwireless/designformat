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
    DFRegister = require('./register.js').DFRegister;
} catch(e) {
    // Pass
}

/**
 * DesignFormat representation of a named group of registers
 */
class DFRegisterGroup extends DFBase {

    /**
     * Constructor for the register group object.
     * @param {string} id - Name of the group
     * @param {integer} offset - Offset from the register bank's base address
     * @param {DFBlock} block - The DFBlock which is holding this register group
     * @param {string} description - Human-readable description of this group
     */
    constructor(id, offset, block, description) {
        super(id, description);

        this.offset = offset;
        this.block = block;

        this.registers = [];

        // Use a Proxy to allow direct access to registers
        try {
            return new Proxy(this, {
                get: (target, key) => {
                    // If it's a direct attribute, return that
                    if (key in target) return target[key];
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
     * Add a new register and sort the list by ascending address
     * @param {DFRegister} reg - The register to add
     */
    addRegister(reg) {
        if (!(reg instanceof DFRegister)) {
            throw Error("Tried to append non-DFRegister to DFRegisterGroup");
        } else if (reg.offset < 0) {
            throw Error("Invalid offset of %s for register %s", reg.offset, reg.id);
        }
        reg.group = this;
        this.registers.push(reg);
        this.sortRegisters();
    }

    /**
     * Ensures the register list is in acsending address order and checks that
     * there are no overlaps.
     */
    sortRegisters() {
        // Perform a sort on LSB
        this.registers.sort(function (a, b) {
            return (a.offset - b.offset);
        });

        // Now walk up the list and check for overlaps
        var last_reg = null;
        this.registers.forEach(function (register) {
            if (last_reg != null && register.offset <= last_reg.offset) {
                throw Error(
                    "Addresses of registers %s and %s overlap!",
                    register.id, last_reg.id
                );
            }
            last_reg = register;
        });
    }

    /**
     * Return this register group's offset
     */
    getOffset() {
        return this.offset;
    }

    /**
     * Dump out this node so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        var obj = super.dumpObject(project);

        obj.offset = this.offset;

        obj.registers = [];
        this.registers.forEach(function (register) {
            obj.registers.push(register.dumpObject(project));
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

        var _this = this;

        if (obj.offset != null) this.offset = obj.offset;

        if (obj.registers != null) obj.registers.forEach(function (register) {
            _this.addRegister((new DFRegister()).loadObject(register, root, types));
        });

        this.sortRegisters();

        return this;
    }

}

try {
    module.exports.DFRegisterGroup = DFRegisterGroup;
} catch(e) {
    // Pass
}
