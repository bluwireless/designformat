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
    DFConstants             = require('./constants.js').DFConstants;
    DFBase                  = require('./base.js').DFBase;
    DFDefine                = require('./define.js').DFDefine;
    DFCommand               = require('./command.js').DFCommand;
    DFCommandField          = require('./command_field.js').DFCommandField;
    DFInterconnect          = require('./interconnect.js').DFInterconnect;
    DFInterconnectComponent = require('./interconnect.js').DFInterconnectComponent;
    DFBlock                 = require('./block.js').DFBlock;
    DFPort                  = require('./port.js').DFPort;
    DFConstantTie           = require('./constant_tie.js').DFConstantTie;
    DFConnection            = require('./connection.js').DFConnection;
    DFRegisterGroup         = require('./register_group.js').DFRegisterGroup;
    DFRegister              = require('./register.js').DFRegister;
    DFRegisterField         = require('./register.js').DFRegisterField;
} catch(e) {
    // Pass
}

// Define a list of types that can be stored as nodes in a DFProject, or within
// the attributes bundle of any object.
var subnode_types = [
    DFBlock, DFConnection, DFConstantTie, DFInterconnect,
    DFInterconnectComponent, DFPort, DFRegisterGroup, DFRegister,
    DFRegisterField, DFDefine, DFCommand, DFCommandField
];

/**
 * DesignFormat top level project container, can collect nodes of different types
 * which can be dumped out as a single entity and re-imported, automatically
 * classifying the nodes. Nodes can be marked as 'principal' entities, in order
 * to specify a focus for downstream tools.
 */
class DFProject extends DFBase {

    /**
     * Constructor for the project object.
     * @param {string} id - Name for the project
     * @param {string} path - Path to the source file used to create the project
     */
    constructor(id, path) {
        super(id);

        this.created = new Date();
        this.path = path;
        this.version = DFConstants.FORMAT.VERSION;

        this.nodes = {};
    }

    /**
     * Return a port or block definition based on a hierarchical path, only
     * examines principal DFBlock nodes.
     * @param {string} path - The hierarchical path to resolve
     */
    resolvePath(path) {
        // Get all of the root blocks
        var root_blocks = this.getAllPrincipalNodes(DFBlock);

        // Now extract lookup path segments
        var parts = /^([\w\.\-]+)?(\[[\w\-]+\])?$/g.exec(path);
        var sections = (parts[1] != undefined) ? parts[1].split('.') : [];
        var port_name = (parts[2] != undefined) ? parts[2].replace(/([\[\]]+)/g, '') : null;

        if (sections.length > 0) {
            var next_id = sections[0];
            var found = root_blocks.filter(function (child) {
                return (child.id == next_id.trim());
            });
            if (found.length != 1) {
                throw Error(
                    "Unable to resolve block - 0 or more than 1 child available for path: "
                    + path + " (@ top level)"
                );
            }
            if (sections.length > 1 || port_name != null) {
                var sub_path = sections.slice(1).join(".");
                if (port_name != null) sub_path += '[' + port_name + ']';
                return found[0].resolvePath(sub_path);
            } else {
                return found[0];
            }

        } else {
            throw Error("Unable to resolve block - no path provided");
        }

        return NULL;
    }

    /**
     * Add a new principal node to the project. The principal attribute can be
     * applied to as many nodes as required, but should be used to provide a
     * focus for downstream tools.
     * @param {DFBase} node - Any instance inheriting from DFBase
     */
    addPrincipalNode(node) {
        if (
            subnode_types.filter(function (type) {
                return (node instanceof type);
            }).length != 1
        ) {
            throw new Error("Unsupported node type " + node.constructor.name);
        }
        if (!node.parent) node.parent = this;
        if (!node.project) node.project = this;
        node.setAttribute(DFConstants.ATTRIBUTES.PRINCIPAL, true);
        this.nodes[node.id] = node;
    }

    /**
     * Add a new non-principal node, this should be used for object types that
     * are referenced by another object in the design. For example, it can be
     * used to store an interconnect definition, which can then be referred to
     * by a port.
     * @param {DFBase} node - Any instance inheriting from DFBase
     */
    addReferenceNode(node) {
        if (
            subnode_types.filter(function (type) {
                return (node instanceof type);
            }).length != 1
        ) {
            throw new Error("Unsupported node type " + node.constructor.name);
        }
        if (node.parent != undefined) node.parent = this;
        if (node.project != undefined) node.project = this;
        this.nodes[node.id] = node;
    }

    /**
     * Return a node matching a specific ID and type
     * @param {string} id - The ID value to match
     * @param {class} type - The class type to match
     */
    findNode(id, type) {
        return (
            (this.nodes[id] != undefined && (this.nodes[id] instanceof type))
                ? this.nodes[id] : null
        );
    }

    /**
     * Return a list of principal nodes held in the project, optionally
     * filtering for a specific type of object.
     * @param {class} desired - The optional object type to filter for
     */
    getAllPrincipalNodes(desired) {
        if (desired != undefined) {
            return Object.values(this.nodes).filter(function (item) {
                return (
                    item.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL) &&
                    (item instanceof desired)
                );
            });
        } else {
            return Object.values(this.nodes).filter(function (item) {
                return item.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL);
            });
        }
    }

    /**
     * Return a DFInterconnect matching a specific identifier.
     * @param {string} intc_id - The ID to match
     */
    getInterconnectType(intc_id) {
        return this.findNode(intc_id, DFInterconnect);
    }

    /**
     * Return a DFDefine matching a specific identifier
     * @param {string} def - The name of the define to match
     */
    getDefinition(def) {
        return this.findNode(def, DFDefine);
    }

    /**
     * Return a unique, ordered list of all of the interconnect types used in
     * the design. This is not the same as a list of all interconnect types
     * stored in the project, as the project may contain interconnects that are
     * not instantiated.
     */
    getAllUsedInterconnectionTypes() {
        var types = [];
        this.getAllPrincipalNodes(DFBlock).forEach(function (root) {
            types = types.concat(root.getInterconnectTypes());
        });
        var unique_types = Array.from(new Set(types));
        return unique_types.sort();
    }

    /**
     * Merge another DFProject with this project
     * @param {DFProject} project - The DFProject instance to merge with
     */
    mergeProject(project) {
        var _this = this;
        if (!(project instanceof DFProject)) {
            throw new Error('Cannot merge with type other than DFProject');
        }
        if (this.version != project.version) {
            throw new Error('Cannot merge with incompatible version ' + project.version);
        }
        if (!this.id) this.id = project.id;
        if (!this.created) this.created = project.created;
        if (!this.path) this.path = project.path;
        Object.values(project.nodes).forEach(function (node) {
            if (node.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL)) {
                _this.addPrincipalNode(node);
            } else {
                _this.addReferenceNode(node);
            }
        });
        return this;
    }

    /**
     * Dump out the project into a primitive dictionary, suitable for reloading
     * at a later date. This dictionary can be separately saved to file as JSON.
     */
    dumpObject() {
        // Get our base object
        var obj = super.dumpObject(self);

        // Keep reference to project
        var _this = this;

        // Attach attributes
        obj.created = this.created.getTime();
        obj.path = this.path;
        obj.version = this.version;

        // Attach all nodes
        obj.nodes = [];
        Object.values(this.nodes).forEach(function (node) {
            var dump = {};
            dump[DFConstants.ATTRIBUTES.TYPE] = node.constructor.name.toLowerCase().trim();
            dump[DFConstants.ATTRIBUTES.DUMP] = node.dumpObject(_this);
        });

        // Return the object
        return obj;
    }

    /**
     * Populate this project with data from a primitive dictionary that has been
     * previously dumped. This will construct child nodes, and then populate them
     * with relevant details.
     * @param {object} obj - The dictionary to reload from
     */
    loadObject(obj) {
        super.loadObject(obj, this, subnode_types);

        // Take a reference to the project, so that we can access in reload
        var _this = this;

        // Check the versions match up
        if (this.version != obj.version) {
            throw new Error('Cannot load DFProject with version ' + obj.version);
        }

        // Restore attributes
        if (obj.created) this.created = new Date(obj.created);
        this.path = obj.path;

        if (obj.nodes) {
            // First reload interconnects (as blocks may reference them)
            obj.nodes.filter(function (item) {
                return (
                    item[DFConstants.ATTRIBUTES.TYPE].toLowerCase().trim() ==
                    DFInterconnect.name.toLowerCase().trim()
                );
            }).forEach(function (intc) {
                var new_intc = new DFInterconnect();
                new_intc.loadObject(intc[DFConstants.ATTRIBUTES.DUMP], _this, subnode_types);
                if (new_intc.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL)) {
                    _this.addPrincipalNode(new_intc);
                } else {
                    _this.addReferenceNode(new_intc);
                }
            });

            // Second reload definitions (as blocks may reference them)
            obj.nodes.filter(function (item) {
                return (
                    item[DFConstants.ATTRIBUTES.TYPE].toLowerCase().trim() ==
                    DFDefine.name.toLowerCase().trim()
                );
            }).forEach(function (def) {
                var new_def = new DFDefine();
                new_def.loadObject(def[DFConstants.ATTRIBUTES.DUMP], null, subnode_types);
                if (new_def.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL)) {
                    _this.addPrincipalNode(new_def);
                } else {
                    _this.addReferenceNode(new_def);
                }
            });

            // Now reload all other nodes
            obj.nodes.filter(function (item) {
                return ([
                    DFInterconnect.name.toLowerCase().trim(),
                    DFDefine.name.toLowerCase().trim(),
                ].indexOf(item[DFConstants.ATTRIBUTES.TYPE].toLowerCase().trim()) < 0);
            }).forEach(function (node) {
                var match = subnode_types.filter(function (type) {
                    return (
                        type.prototype.constructor.name.toLowerCase().trim() ==
                        node[DFConstants.ATTRIBUTES.TYPE].toLowerCase().trim()
                    );
                });
                if (match.length != 1) {
                    throw new Error("Unable to resolve node type " + node[DFConstants.ATTRIBUTES.TYPE]);
                }
                var new_node = (new match[0]()).loadObject(node[DFConstants.ATTRIBUTES.DUMP], null, subnode_types);
                if (new_node.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL)) {
                    _this.addPrincipalNode(new_node);
                } else {
                    _this.addReferenceNode(new_node);
                }
            });
        }

        return this;
    }

}

try {
    module.exports.DFProject = DFProject;
} catch(e) {
    // Pass
}
