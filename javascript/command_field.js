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
    DFDefine = require('./define.js').DFDefine;
} catch(e) {
    // Pass
}

/**
 * DesignFormat representation of a field of a command. This could be used to
 * represent a sub-field of an instruction for a CPU, or a parameter in a
 * microcode instruction for a DMA engine. Command fields have fixed widths,
 * with specified LSB alignments. The field's value can be enumerated if
 * required, to allow specific control values to be named.
 */
class DFCommandField extends DFBase {

    /**
     * Construct a command field object
     * @param {string} id - The name of the register field
     * @param {integer} lsb - Least significant bit position within the command
     * @param {integer} size - Width of the field in bits
     * @param {integer} reset - Value taken at reset (or default value)
     * @param {boolean} signed - Whether the value is signed
     * @param {string} description - Human-readable description
     */
    constructor(id, lsb, size, reset, signed, description) {
        super(id, description);

        if (lsb != null || size != null || reset != null) {
            if (isNaN(lsb))
                throw Error(this.constructor.name + " LSB must be an integer");
            if (isNaN(size))
                throw Error(this.constructor.name + " Size must be an integer");
            if (isNaN(reset))
                throw Error(this.constructor.name + " Reset must be an integer");

            this.lsb = parseInt(lsb);
            this.size = parseInt(size);
            this.reset = parseInt(reset);
            this.signed = signed || False;
            this.enum = {};

            this.check();
        }
    }

    /**
     * Check that the values assigned to the field are sensible
     */
    check() {
        if (isNaN(this.lsb) || this.lsb < 0) {
            throw Error(
                this.constructor.name + " " + this.id + " LSB " + this.lsb +
                " is out of range"
            );
        }

        if ((isNaN(this.size)) || (this.size < 1)) {
            throw Error(
                this.constructor.name + " " + this.id + " Size " + this.size +
                " is out of range - LSB=" + this.lsb
            );
        }

        if (isNaN(this.reset) || (!this.signed && this.reset < 0)) {
            throw Error(
                this.constructor.name + " " + this.id + " Reset Value " +
                this.reset + " is out of range"
            );
        }
    }

    /**
     * Create a new named value for the register
     * @param {string} key - Name of the value
     * @param {integer} value - Value to be associated
     * @param {string} description - Human-readable description
     */
    addEnumValue(key, value, description) {
        this.enum[key] = new DFDefine(key, value, description);
    }

    /**
     * Dump out this node so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        var obj = super.dumpObject(project);

        obj.lsb = this.lsb;
        obj.size = this.size;
        obj.reset = this.reset;
        obj.signed = this.signed;
        obj.enum = {};

        var _this = this;
        Object.keys(this.enum).forEach(function (key) {
            obj.enum[key] = _this.enum[key].dumpObject(project);
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

        this.lsb = parseInt(obj.lsb);
        this.size = parseInt(obj.size);
        this.reset = parseInt(obj.reset);
        this.signed = obj.signed;
        this.enum = {};

        if (obj.enum) {
            Object.keys(obj.enum).forEach(function (key) {
                _this.enum[key] = (new DFDefine()).loadObject(obj.enum[key], root, types);
            });
        }

        this.check();

        return this;
    }

}

try {
    module.exports.DFCommandField = DFCommandField;
} catch (e) {
    // Pass
}
