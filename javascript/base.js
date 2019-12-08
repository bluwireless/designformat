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
    DFConstants = require('./constants.js').DFConstants;
} catch(e) {
    // Pass
}

/**
 * Dump out an object of any type, if it is not a primitive type then encapulate
 * it within a dictionary that describes the type.
 * @param {object} obj - The object to dump
 * @param {DFProject} project - Project definition, used for resolving references
 */
var encapsulatedDump = function (obj, project) {
    if (obj instanceof DFBase) {
        var dump = {};
        dump[DFConstants.ATTRIBUTES.TYPE] = obj.constructor.name.toLowerCase().trim();
        dump[DFConstants.ATTRIBUTES.DUMP] = obj.dumpObject(project);
        return dump;
    } else if (obj instanceof Array) {
        var encapsulated = [];
        obj.forEach(function (item) {
            encapsulated.push(encapsulatedDump(item, project));
        });
        return encapsulated;
    } else if (obj.constructor == Object) {
        var encapsulated = {};
        Object.keys(obj).forEach(function (key) {
            encapsulated[key] = encapsulatedDump(obj[key], project);
        });
        return encapsulated;
    } else {
        return obj;
    }
};

/**
 * Load up an encapsulated object, if it is not a dictionary and contains an
 * encapsulation marker then it is loaded appropriately.
 * @param {*} dump - The dumped object to load
 * @param {*} root - Provide the root object, used for resolving references
 * @param {*} types - A map from class name to class definition
 */
var encapsulatedLoad = function (dump, root, types) {
    if (dump.constructor == Object) {
        if (dump[DFConstants.ATTRIBUTES.TYPE] != undefined) {
            var d_type = dump[DFConstants.ATTRIBUTES.TYPE].toLowerCase().trim();
            var d_data = dump[DFConstants.ATTRIBUTES.DUMP];
            var match = types.filter(function (type) {
                return type.prototype.constructor.name.toLowerCase().trim() == d_type;
            });
            if (match.length != 1) {
                throw new Error("Unable to resolve node type " + dump[DFConstants.ATTRIBUTES.TYPE]);
            }
            return (new match[0]()).loadObject(d_data, root);
        } else {
            var loaded = {};
            Object.keys(dump).forEach(function (key) {
                loaded[key] = encapsulatedLoad(dump[key], root, types);
            });
            return loaded;
        }
    } else if (dump instanceof Array) {
        var loaded = [];
        dump.forEach(function (item) {
            loaded.push(encapsulatedLoad(item, root, types));
        });
        return loaded;
    } else {
        return dump;
    }
};

/**
 * Base class of DesignFormat
 */
class DFBase {

    /**
     * Construct the base object
     * @param {string} id - Identifier of the object (alphanumeric and '_' only)
     * @param {string} description - Human-readable description of the object
     */
    constructor(id, description) {
        this.id = id;
        this.description = description;
        this.attributes = {};
    }

    /**
     * Dump out this object into a plain JSON dictionary, encapsulating any
     * nested objects. Encapsulation takes note of the object type as well as
     * the data it contains, allowing it to be reloaded correctly.
     * @param {DFProject} project - The project definition, used for calculating references
     */
    dumpObject(project) {
        var obj = {};

        // Take a local reference to 'this' so we don't lose scope in iterations
        var _this = this;

        // Attach the basic object properties
        obj.id = this.id;

        if (this.description && this.description.trim().length > 0) {
            obj.description = this.description;
        }

        // Attach attributes
        if (Object.keys(this.attributes).length > 0) {
            obj.attributes = {};
            Object.keys(this.attributes).forEach(function (attr) {
                obj.attributes[attr] = encapsulatedDump(_this.attributes[attr], project);
            });
        }

        return obj;
    }

    /**
     * Reload the base object parameters from the passed in object. Where
     * encapsulation is detected within attributes, a special loader is used
     * to evaluate any nested objects.
     * @param {object} obj - Description of this node
     * @param {DFBase} root - Root object in the tree
     * @param {object} types - Map from class name to class definition
     */
    loadObject(obj, root, types) {
        // Take a local reference to 'this' so we don't lose scope in iterations
        var _this = this;

        _this.id = obj.id;
        _this.description = obj.description;

        if (obj.attributes != null) Object.keys(obj.attributes).forEach(function (key) {
            _this.attributes[key] = encapsulatedLoad(obj.attributes[key], root, types);
        });

        return this;
    }

    /**
     * Add a named attribute to this node
     * @param {string} key - Key for the attribute
     * @param {*} value - Any serialisable object
     */
    setAttribute(key, value) {
        this.attributes[key] = value;
    }

    /**
     * Remove a named attribute from this node
     * @param {string} key - Key for the attribute to remove
     */
    removeAttribute(key) {
        delete this.attributes[key];
    }

    /**
     * Return the current value for a named attribute
     * @param {string} key - The key to lookup
     */
    getAttribute(key) {
        return this.attributes[key];
    }

}

try {
    module.exports.DFBase = DFBase;
} catch (e) {
    // Pass
}
