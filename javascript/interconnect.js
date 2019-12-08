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
    DFConstants = require('./constants.js').DFConstants;
    DFDefine = require('./define.js').DFDefine;
} catch(e) {
    // Pass
}

/**
 * DesignFormat representation for a component within a type of interconnection
 */
class DFInterconnectComponent extends DFBase {

    /**
     * Constructor for the interconnect component.
     * @param {string} id - Name of the interconnect component
     * @param {string} role - Whether the port is a slave or master
     * @param {string} description - Description of the component
     * @param {string} type - Whether this is simple or complex (references
     *                        another interconnect)
     * @param {any} width_or_ref - For simple connections, how many bits wide is
     *                             the component. For complex connections, what
     *                             DFInterconnect is referenced.
     * @param {integer} count - Number of instances of this component
     * @param {integer} def - For simple components, what is the default state
     *                        of this signal
     * @param {dictionary} enumlist - Enumeration of values that the component
     *                                can carry
     * @param {DFProject} project - Reference to the top level project (used for
     *                              lookups)
     */
    constructor(id, role, description, type, width_or_ref, count, def, enumlist, project) {
        super(id, description);

        this.role = role || DFConstants.ROLE.MASTER;
        this.type = type || DFConstants.COMPONENT.SIMPLE;
        this.width = (
            (this.type == DFConstants.COMPONENT.SIMPLE) ? (width_or_ref || 0) : 0
        );
        this.ref = (
            (this.type == DFConstants.COMPONENT.COMPLEX) ? width_or_ref : null
        );
        this.count = (count != null) ? count : 1;
        this.default = (
            (this.type == DFConstants.COMPONENT.SIMPLE) ? (def || 0) : 0
        );
        this.project = project;

        if (this.ref instanceof DFInterconnect) this.ref = this.ref.id;

        this.enum = enumlist || {};

        // Sanity checks
        this.checkRole();
        this.checkType();
    }

    /**
     * Checks that the configured role is valid (SLAVE or MASTER)
     */
    checkRole() {
        if (Object.values(DFConstants.ROLE).indexOf(this.role) < 0) {
            throw Error("Invalid role specified to DFInterconnectComponent: " + this.role);
        }
    }

    /**
     * Check that the component type is allowed.
     */
    checkType() {
        if (Object.values(DFConstants.COMPONENT).indexOf(this.type) < 0) {
            throw Error("Unknown DFInterconnectComponent type: " + this.type);
        } else if (this.type == DFConstants.COMPONENT.COMPLEX && !this.ref) {
            throw Error("Complex DFInterconnectComponent without reference!");
        }
    }

    /**
     * Return all the roles that are offered by this interconnect component,
     * takes account of the roles of any reference component.
     */
    getAllRoles() {
        if (this.type == DFConstants.COMPONENT.SIMPLE) {
            return [this.role];
        } else {
            var ref_roles = this.getReference().getAllRoles();
            var roles = [];
            var _this = this;
            ref_roles.forEach(function (role) {
                // If I'm a slave, then the returned roles need to be reversed
                if (_this.role == DFConstants.ROLE.SLAVE) {
                    if (role == DFConstants.ROLE.MASTER) {
                        roles.push(DFConstants.ROLE.SLAVE);
                    } else if (role == DFConstants.ROLE.SLAVE) {
                        roles.push(DFConstants.ROLE.MASTER);
                    } else {
                        roles.push(role);
                    }
                } else {
                    roles.push(role);
                }
            });
            return roles;
        }
    }

    /**
     * Checks that the interconnect component offers a specified role
     * @param {string} role - The role to lookup
     */
    hasRole(role) {
        return (this.getAllRoles().indexOf(role) >= 0);
    }

    /**
     * Checks that the interconnect component offers a MASTER role
     */
    hasMasterRole() {
        return (this.getAllRoles().indexOf(DFConstants.ROLE.MASTER) >= 0);
    }

    /**
     * Checks that the interconnect component offers a SLAVE role
     */
    hasSlaveRole() {
        return (this.getAllRoles().indexOf(DFConstants.ROLE.SLAVE) >= 0);
    }

    /**
     * Checks that the interconnect component offers a BIDIR role
     */
    hasBidirectionalRole() {
        return (this.getAllRoles().indexOf(DFConstants.ROLE.BIDIR) >= 0);
    }

    /**
     * Convert from the string ID reference to a DFInterconnect
     */
    getReference() {
        return this.project.findNode(this.ref, DFInterconnect);
    }

    /**
     * Return whether or not the component is complex (whether it references
     * another DFInterconnect).
     */
    isComplex() {
        return (this.type == DFConstants.COMPONENT.COMPLEX);
    }

    /**
     * Get the total width of the interconnect component as a master
     */
    getMasterWidth() {
        if (this.isComplex()) {
            // If this component has a SLAVE role, invert the sense
            if (this.role == DFConstants.ROLE.MASTER) {
                return this.getReference().getMasterWidth();
            } else {
                return this.getReference().getSlaveWidth();
            }
        } else if (this.role == DFConstants.ROLE.MASTER) {
            return this.width;
        } else {
            return 0;
        }
    }

    /**
     * Get the total width of the interconnect component as a slave
     */
    getSlaveWidth() {
        if (this.isComplex()) {
            // If this component has a SLAVE role, invert the sense
            if (this.role == DFConstants.ROLE.MASTER) {
                return this.getReference().getSlaveWidth();
            } else {
                return this.getReference().getMasterWidth();
            }
        } else if (this.role == DFConstants.ROLE.SLAVE) {
            return this.width;
        } else {
            return 0;
        }
    }

    /**
     * Get the total bidirectional width of the interconnect
     */
    getBidirectionalWidth() {
        if (this.isComplex()) {
            return self.getReference().getBidirectionalWidth();
        } else if (this.role == DFConstants.ROLE.BIDIR) {
            return this.width;
        } else {
            return 0;
        }
    }

    /**
     * Get the total width of the interconnect in a particular role
     * @param {string} role - The role to resolve
     */
    getRoleWidth(role) {
        if (role.toUpperCase() == DFConstants.ROLE.MASTER)
            return self.getMasterWidth();
        else if (role.toUpperCase() == DFConstants.ROLE.SLAVE)
            return self.getSlaveWidth();
        else if (role.toUpperCase() == DFConstants.ROLE.BIDIR)
            throw new Error("Unknown role when calling getRoleWidth: " + role);
    }

    /**
     * Add a new enumerated value for the value of this interconnect (if simple)
     * @param {string} key - Name of the value to enumerate
     * @param {integer} value - Value to name
     * @param {string} description - Human-readable description of the value
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

        // Attach extra details
        obj.role = this.role;
        obj.type = this.type;
        obj.count = this.count;
        obj.enum = {};

        var _this = this;
        Object.keys(this.enum).forEach(function (key) {
            obj.enum[key] = _this.enum[key].dumpObject(project);
        });

        if (this.width != null) obj.width = this.width;
        if (this.default != null) obj.default = this.default;

        // For a referenced DFInterconnect, store just the ID
        if (this.type == DFConstants.COMPONENT.COMPLEX && this.ref != null) {
            obj.ref = this.ref;
        }

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

        // Reload extra details
        this.role = obj.role;
        this.type = obj.type;
        this.width = obj.width;
        this.count = obj.count;
        this.default = obj.default;
        this.ref = obj.ref;
        this.enum = {};

        if (obj.enum) {
            Object.keys(obj.enum).forEach(function (key) {
                _this.enum[key] = (new DFDefine()).loadObject(obj.enum[key], root, types);
            });
        }

        // Perform a sanity check
        this.checkRole();
        this.checkType();

        // For chaining
        return this;
    }

}

/**
 * DesignFormat representation of a type of interconnection
 */
class DFInterconnect extends DFBase {

    /**
     * Constructor for the interconnect type
     * @param {string} id - Name of the interconnect type
     * @param {string} role - The role - one of 'MASTER', 'SLAVE' or 'BIDIR'
     * @param {string} description - Human-readable description of the interconnect
     * @param {DFProject} project - Reference to the top-level DFProject
     */
    constructor(id, role, description, project) {
        super(id, description);

        this.role = role || DFConstants.ROLE.MASTER;
        this.project = project;

        this.components = []; // Constituent components of the interconnect

        // Sanity check
        this.checkRole();
    }

    /**
     * Checks that the configured role is valid (SLAVE, MASTER, or BIDIR)
     */
    checkRole() {
        if (Object.values(DFConstants.ROLE).indexOf(this.role) < 0) {
            throw Error("Invalid role specified to DFInterconnect: " + this.role);
        }
    }

    /**
     * Return all of the roles offered by this interconnect type, taking account
     * of any child components and interconnects they may reference.
     */
    getAllRoles() {
        var roles = [];
        var _this = this;
        this.components.forEach(function (comp) {
            var comp_roles = comp.getAllRoles();
            // If I have a SLAVE role, then I need to invert my roles
            comp_roles.forEach(function (role) {
                if (_this.role == DFConstants.ROLE.SLAVE) {
                    if (role == DFConstants.ROLE.MASTER) {
                        roles.push(DFConstants.ROLE.SLAVE);
                    } else if (role == DFConstants.ROLE.SLAVE) {
                        roles.push(DFConstants.ROLE.MASTER);
                    } else {
                        roles.push(role);
                    }
                } else {
                    roles.push(role);
                }
            });
        });
        return Array.from(new Set(roles));
    }

    /**
     * Checks that the interconnect has components of the specified role.
     * @param {string} role - The role to check for
     */
    hasRole(role) {
        return (this.getAllRoles().indexOf(role) >= 0);
    }

    /**
     * Checks that the interconnect has components with the Master role
     */
    hasMasterRole() {
        return (this.getAllRoles().indexOf(DFConstants.ROLE.MASTER) >= 0);
    }

    /**
     * Checks that the interconnect has components with the Slave role
     */
    hasSlaveRole() {
        return (this.getAllRoles().indexOf(DFConstants.ROLE.SLAVE) >= 0);
    }

    /**
     * Attach a component to the interconnect
     * @param {DFInterconnectComponent} comp - The component to attach
     */
    addComponent(comp) {
        if (!(comp instanceof DFInterconnectComponent)) {
            throw Error("Component is not of type DFInterconnectComponent");
        }
        comp.project = this.project;
        this.components.push(comp);
    }

    /**
     * Returns a list of only the components with a master role
     */
    getMasterComponents() {
        return this.components.filter(function (comp) {
            return comp.hasMasterRole();
        });
    }

    /**
     * Returns a list of only the components with a slave role
     */
    getSlaveComponents() {
        return this.components.filter(function (comp) {
            return comp.hasSlaveRole();
        });
    }

    /**
     * Returns a list of only the components with a bidirectional role
     */
    getBidirectionalComponents() {
        return this.components.filter(function (comp) {
            return comp.hasBidirectionalRole();
        });
    }

    /**
     * Returns only the components of the interconnect matching a particular role.
     * @param {string} role - The role to lookup
     */
    getRoleComponents(role) {
        if (role.toUpperCase() == DFConstants.ROLE.MASTER)
            return self.getMasterComponents();
        else if (role.toUpperCase() == DFConstants.ROLE.SLAVE)
            return self.getSlaveComponents();
        else if (role.toUpperCase() == DFConstants.ROLE.BIDIR)
            return self.getBidirectionalComponents();
        else
            throw new Error("Unsupported role when calling getRoleComponents: " + role);
    }

    /**
     * Checks if the interconnect contains any simple components
     */
    hasSimpleComponents() {
        var found = false;
        for (var i = 0; i < this.components.length; i++) {
            if (!this.components[i].isComplex()) {
                found = true;
                break;
            }
        }
        return found;
    }

    /**
     * Check if the interconnect contains any complex components
     */
    hasComplexComponents() {
        var found = false;
        for (var i = 0; i < this.components.length; i++) {
            if (this.components[i].isComplex()) {
                found = true;
                break;
            }
        }
        return found;
    }

    /**
     * Get the total width of the interconnect as a master
     */
    getMasterWidth() {
        var _this = this;
        var width = 0;
        this.components.forEach(function (comp) {
            if (_this.role == DFConstants.ROLE.MASTER && comp.hasMasterRole()) {
                width += comp.getMasterWidth() * comp.count;
            } else if (_this.role == DFConstants.ROLE.SLAVE && comp.hasSlaveRole()) {
                width += comp.getSlaveWidth() * comp.count;
            }
        });
        return width;
    }

    /**
     * Get the total width of the interconnect as a slave
     */
    getSlaveWidth() {
        var _this = this;
        var width = 0;
        this.components.forEach(function (comp) {
            if (_this.role == DFConstants.ROLE.MASTER && comp.hasSlaveRole()) {
                width += comp.getSlaveWidth() * comp.count;
            } else if (_this.role == DFConstants.ROLE.SLAVE && comp.hasMasterRole()) {
                width += comp.getMasterWidth() * comp.count;
            }
        });
        return width;
    }

    /**
     * Get the total bidirectional width of the interconnect
     */
    getBidirectionalWidth() {
        var width = 0;
        this.components.forEach(function (comp) {
            if (comp.hasBidirectionalRole()) {
                width += comp.getBidirectionalWidth() * comp.count;
            }
        });
        return width;
    }

    /**
     * Get the total width of the interconnect in a particular role
     * @param {string} role - The role to lookup
     */
    getRoleWidth(role) {
        if (role.toUpperCase() == DFConstants.ROLE.MASTER)
            return this.getMasterWidth();
        else if (role.toUpperCase() == DFConstants.ROLE.SLAVE)
            return this.getSlaveWidth();
        else if (role.toUpperCase() == DFConstants.ROLE.BIDIR)
            throw new Error("Unknown role when calling getRoleWidth: " + role);
    }

    /**
     * Dump out this node so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        // Get base object
        var obj = super.dumpObject(project);

        // Attach extra details
        obj.role = this.role;

        // Attach each component
        obj.components = [];
        this.components.forEach(function (comp) { obj.components.push(comp.dumpObject(project)); });

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

        // Reload attributes
        this.role = obj.role;
        this.project = root;
        // Sanity checks
        this.checkRole();

        // Reload each component
        var _this = this;
        obj.components.forEach(function (comp) {
            var new_comp = new DFInterconnectComponent();
            new_comp.loadObject(comp, root, types);
            _this.addComponent(new_comp);
        });

        return this;
    }

}

try {
    module.exports.DFInterconnect          = DFInterconnect;
    module.exports.DFInterconnectComponent = DFInterconnectComponent;
} catch(e) {
    // Pass
}
