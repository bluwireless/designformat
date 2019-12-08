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
    DFBase      = require('./base.js').DFBase;
} catch(e) {
    // Pass
}

/**
 * DesignFormat description of an initiator within an address map, it defines
 * any transformation (masking and offset) that is applied to the inbound request.
 */
class DFAddressMapInitiator extends DFBase {

    /**
     * Construct the address map initiator.
     * @param {DFPort} port - The port initiating the transaction to the address map
     * @param {integer} port_index - The index of the initiator signal within the port
     * @param {integer} mask - The mask applied to the inbound transaction by the map
     * @param {integer} offset - The signed offset applied to the inbound transaction
     * @param {DFAddressMap} map - The DFAddressMap containing this initiator
     */
    constructor(port, port_index, mask, offset, map) {
        // Construct an ID to represent this initiator
        let id = null;
        if (port) id = port.hierarchicalPath() + "[" + port_index + "]";

        // Call the DFBase constructor
        super(id, null);

        // Set other properties
        this.port       = port;
        this.port_index = port_index;
        this.mask       = mask;
        this.offset     = offset;
        this.map        = map;
    }

    /**
     * Translate an inbound address using the mask and offset parameters
     * @param {integer} address - The address to translate
     */
    outboundAddress(address) {
        return ((address & this.mask) + this.offset);
    }

    /**
     * Deprecated version of 'outboundAddress'
     * @deprecated
     * @param {*} address - The address to translate
     */
    translateAddress(address) {
        console.log(
            "WARNING: DFAddressMapInitiator's translateAddress is deprecated " +
            "- please use outboundAddress instead"
        );
        return this.outboundAddress(address);
    }

    /**
     * Translate an outbound address into an inbound address (out of the address
     * map) using the offset parameters. Note that this is only a guess because
     * an address loses information!
     * @param {integer} address - The address to translate
     */
    inboundAddress(address) {
        return (address - this.offset);
    }

    /**
     * Resolve an inbound address on the initiator to the correct target
     * @param {integer} address - The address to resolve
     */
    resolveAddress(address) {
        return this.map.resolveTarget(this.outboundAddress(address), this);
    }

    /**
     * Dump out the initiator so that it can be reloaded
     * @param {DFProject} project - Project for resolving references
     */
    dumpObject(project) {
        // Get our base object
        obj = super.dumpObject(project);

        // Attach extra details
        obj.mask   = this.mask;
        obj.offset = this.offset;
        obj.port   = {
            block: this.port.block.hierarchicalPath(),
            port : this.port.name,
            index: this.port_index
        };

        return obj;
    };

    /**
     * Reload a stored initiator
     * @param {object} obj - Description of this node
     * @param {DFBase} root - Root object in the tree
     * @param {object} types - Map from class name to class definition
     */
    loadObject(obj, root, types) {
        super.loadObject(obj, root, types);

        // Simple attributes
        this.mask   = obj.mask   ? parseInt(obj.mask)   : 0;
        this.offset = obj.offset ? parseInt(obj.offset) : 0;

        // Find the associated part
        let port_path   = obj.port.block + "[" + obj.port.port + "]";
        this.port       = root.resolvePath(port_path);
        this.port_index = parseInt(obj.port.index);

        return this;
    }
}

/**
 * DesignFormat description of a target within an address map, it defines the
 * offset and aperture size where the target will be selected for handling the
 * transaction.
 */
class DFAddressMapTarget extends DFBase {

    /**
     * Construct the address map target
     * @param {DFPort} port - The port accepting the transaction from the address map
     * @param {integer} port_index - The index of the initiator signal within the port
     * @param {integer} offset - The offset address of the aperture in the address map
     * @param {integer} aperture - The size of the aperture within the address map
     * @param {object} map - The DFAddressMap containing this target
     */
    constructor(port, port_index, offset, aperture, map) {
        // Construct an ID to represent this target
        let id = null;
        if (port) id = port.hierarchicalPath() + "[" + port_index + "]";

        // Call the DFBase constructor
        super(id, null);

        // Set other properties
        this.port       = port;
        this.port_index = port_index;
        this.offset     = offset;
        this.aperture   = aperture;
        this.map        = map;
    }

    /**
     * Indicates whether or not this target's aperture contains a specified
     * address.
     * @param {integer} address - The address to test for
     */
    acceptsAddress(address) {
        return (address >= this.offset) && (address < (this.offset + this.aperture));
    }

    /**
     * Dump out this object into a plain JSON dictionary.
     * @param {*} project - The project definition, used for calculating references
     */
    dumpObject(project) {
        // Get our base object
        obj = super.dumpObject(project);

        // Attach extra details
        obj.aperture = this.aperture;
        obj.offset   = this.offset;
        obj.port     = {
            block: this.port.block.hierarchicalPath(),
            port : this.port.name,
            index: this.port_index
        };

        return obj;
    }

    /**
     * Reload target from serialised object.
     * @param {object} obj - Description of this node
     * @param {DFBase} root - Root object in the tree
     * @param {object} types - Map from class name to class definition
     */
    loadObject(obj, root, types) {
        super.loadObject(obj, root, types);

        // Simple attributes
        this.aperture = obj.aperture ? parseInt(obj.aperture) : 0;
        this.offset   = obj.offset   ? parseInt(obj.offset)   : 0;

        // Find the associated part
        let port_path   = obj.port.block + "[" + obj.port.port + "]";
        this.port       = root.resolvePath(port_path);
        this.port_index = parseInt(obj.port.index);

        root.resolvePath(port_path)

        return this;
    }

}

/**
 * DesignFormat description of a constraint in the address map, limiting the
 * viable targets for a specific initiator.
 */
class DFAddressMapConstraint extends DFBase {

    /**
     * Constructor for an address map constraint
     * @param {DFAddressMapInitiator} initiator - The initiator for the constraint
     * @param {DFAddressMapTarget} target - The target for the constraint
     */
    constructor(initiator, target) {
        // Construct an ID for this constraint
        let id = null;
        if (initiator && target) id = initiator.id + "<->" + target.id;

        // Call the DFBase constructor
        super(id, null);

        // Set further properties
        this.initiator = initiator;
        this.target    = target;
    }

    /**
     * Serialise constraint to a plain JSON object.
     * @param {DFProject} project - The project definition, used for calculating
     *                              references
     */
    dumpObject(project) {
        // Get our base object
        obj = super.dumpObject(project);

        // Attach extra details
        obj.initiator = {
            block: this.initiator.port.block.hierarchicalPath(),
            port : this.initiator.port.name,
            index: this.initiator.port_index
        };
        obj.target = {
            block: this.target.port.block.hierarchicalPath(),
            port : this.target.port.name,
            index: this.target.port_index
        };

        return obj;
    }

    /**
     * Reload a serialised constraint
     * @param {object} obj - Description of this node
     * @param {DFBase} root - Root object in the tree
     * @param {object} types - Map from class name to class definition
     * @param {DFAddressMap} map - Reference to the parent address map
     */
    loadObject(obj, root, types, map) {
        super.loadObject(obj, root, types);

        // Find the associated initiator port
        let init_port  = root.resolvePath(obj.initiator.block + "[" + obj.initiator.port + "]");
        this.initiator = map.getInitiator(init_port, parseInt(obj.initiator.index));

        // Find the associated target port
        let target_port = root.resolvePath(obj.target.block + "[" + obj.target.port + "]");
        this.target     = map.getInitiator(target_port, parseInt(obj.target.index));

        return this;
    }

}

/**
 * DesignFormat description of an address map aperture from a specific initiator
 * to a specific target. It also describes any translation that is performed to
 * the address as it passes through the block (masking and offset).
 */
class DFAddressMap extends DFBase {

    /**
     * Constructor for an address map
     * @param {DFBlock} block - The DFBlock this address map is associated with
     */
    constructor(block) {
        super(null, null);
        this.block       = block;
        this.initiators  = [];
        this.targets     = [];
        this.constraints = {};
    }

    /**
     * Add an initiator to this address map
     * @param {DFAddressMapInitiator} initiator - The initiator
     */
    addInitiator(initiator) {
        if (!(initiator instanceof DFAddressMapInitiator)) {
            throw new Error("Initiator is of invalid type " + initiator.constructor.name);
        } else if (this.initiators.includes(initiator)) {
            throw new Error("Initiator has already been added to map");
        } else if (this.getInitiator(initiator.port, initiator.port_index)) {
            throw new Error("An initiator has already been added for port " + initiator.id);
        } else if (this.getTarget(initiator.port, initiator.port_index)) {
            throw new Error("Port " + initiator.id + " cannot be added as initiator as it is already a target");
        }
        this.initiators.push(initiator);
        initiator.map = this;
    }

    /**
     * Add a target to this address map
     * @param {DFAddressMapTarget} target - The target
     */
    addTarget(target) {
        if (!(target instanceof DFAddressMapTarget)) {
            throw new Error("Target is of invalid type " + target.constructor.name);
        } else if (this.targets.includes(target)) {
            throw new Error("Target has already been added to map");
        } else if (this.getTarget(target.port, target.port_index)) {
            throw new Error("A target has already been added for port " + target.id);
        } else if (this.getInitiator(target.port, target.port_index)) {
            throw new Error("Port " + target.id + " cannot be added as target as it is already a initiator");
        }
        this.targets.push(target);
        target.map = this;
    }

    /**
     * Add a constraint to limit which targets can be accessed from an initiator
     * @param {DFAddressMapInitiator} initiator - The initiator
     * @param {DFAddressMapTarget} target - The target
     */
    addConstraint(initiator, target) {
        // Check the initiator
        if (!(initiator instanceof DFAddressMapInitiator)) {
            throw new Error("Initiator is of invalid type " + initiator.constructor.name);
        } else if (!this.initiators.includes(initiator)) {
            throw new Error("Initiator has not been added to map");
        }
        // Check the target
        if (!(target instanceof DFAddressMapTarget)) {
            throw new Error("Target is of invalid type " + target.constructor.name);
        } else if (!this.targets.includes(target)) {
            throw new Error("Target has not been added to map");
        }
        // Check this exact constraint doesn't exist
        let clashes = this.constraints.filter((item) => {
            return (item.initiator == initiator && item.target == target);
        });
        if (clashes.length > 0) {
            throw new Error(
                "Constraint between " + initiator.id + " and " + target.id +
                " already exists"
            );
        }
        // Create and add the constraint
        // NOTE: We use a unique key for the initiator-target pairing
        this.constraints[initiator.id+"-"+target.id] = new DFAddressMapConstraint(initiator, target);
    }

    /**
     * Get the DFAddressMapInitiator associated to a specific port and index
     * @param {DFPort} port - Port to lookup
     * @param {integer} index - Signal index within the port
     */
    getInitiator(port, index) {
        let found = this.initiators.filter((item) => {
            return (item.port == port && item.port_index == index);
        });
        if (found.length > 1) {
            throw new Error(
                "Found multiple initiators for port " + port.hierarchicalPath()
                + "[" + index + "]"
            );
        }
        return (found.length == 1) ? found[0] : null;
    }

    /**
     * Get the DFAddressMapTarget associated to a specific port
     * @param {DFPort} port - Port to lookup
     * @param {integer} index - Signal index within the port
     */
    getTarget(port, index) {
        let found = this.targets.filter((item) => {
            return (item.port == port && item.port_index == index);
        });
        if (found.length > 1) {
            throw new Error(
                "Found multiple targets for port " + port.hierarchicalPath() +
                "[" + index + "]"
            );
        }
        return (found.length == 1) ? found[0] : null;
    }

    /**
     * Get all of the initiators in the address map that can reach a particular
     * target, taking into account constraints on either initiator or target.
     * @param {DFAddressMapTarget} target - The target to search for
     */
    getInitiatorsForTarget(target) {
        // Sanity check the target
        if (!(target instanceof DFAddressMapTarget)) {
            throw new Error("Target is of invalid type " + target.constructor.name);
        } else if (!this.targets.includes(target)) {
            throw new Error("Target is not part of this address map");
        }
        // Find any constraints that pertain to this target
        let t_cons = Object.values(this.constraints).filter((item) => {
            return (item.target == target);
        });
        // If constraints have been found, only return compliant initiators
        if (t_cons.length > 0) {
            let initiators = [];
            for (let item of t_cons) initiators.push(item.initiator);
            return initiators;
        }
        // Find any initiators that allow this target
        let viable = [];
        for (let init of this.initiators) {
            // Find any constraints that pertain to this initiator
            let i_cons = Object.values(this.constraints).filter((item) => {
                return (item.initiator == init);
            });
            let con_tgts = [];
            for (let item of i_cons) con_tgts.push(item.target);
            // If our target appears in the constraints, or there are no
            // constraints, then include the initiator
            if (i_cons.length == 0 || con_tgts.includes(target)) viable.push(init);
        }
        return viable;
    }

    /**
     * Get all of the targets in the address map that can be reached from a
     * particular initiator, taking into account constraints on either initiator
     * or target.
     * @param {DFAddressMapInitiator} initiator - The initiator to search for
     */
    getTargetsForInitiator(initiator) {
        // Sanity check the initiator
        if (!(initiator instanceof DFAddressMapInitiator)) {
            throw new Error("Initiator is of invalid type " + initiator.constructor.name);
        } else if (!this.initiators.includes(initiator)) {
            throw new Error("Initiator is not part of this address map");
        }
        // Find any constraints that pertain to this initiator
        let i_cons = Object.values(this.constraints).filter((item) => {
            return (item.initiator == initiator);
        });
        // If constraints have been found, only return compliant targets
        if (i_cons.length > 0) {
            let targets = [];
            for (let item of i_cons) targets.push(item.target);
        }
        // Find any targets that allow this initiator
        let viable = [];
        for (let tgt of this.targets) {
            // Find any constraints that pertain to this target
            let t_cons = Object.values(this.constraints).filter((item) => {
                return (item.target == tgt);
            });
            let con_inits = [];
            for (let item of t_cons) con_inits.push(item.initiator);
            // If our initiator appears in the constraints, or there are no
            // constraints, then include the target
            if (t_cons.length == 0 || con_inits.includes(initiator)) {
                viable.push(tgt);
            }
        }
        return viable;
    }

    /**
     * Resolve the target port in the address map from a given address. The
     * address is assumed to be relative to the address map, if an initiator
     * is provided then any known constraints will be applied.
     * @param {*} address - Address being accessed
     * @param {*} initiator - Which initiator is handling the access
     */
    resolveTarget(address, initiator) {
        // Find viable targets for the address
        let viable = this.targets.filter((item) => {
            return item.acceptsAddress(address)
        });
        // If an initiator is provided, constrain as required
        if (initiator && this.constraints[initiator.id]) {
            // Get the list of target this initiator is allowed to access
            let valid_targets = [];
            for (let item of self.constraints[initiator.id]) {
                valid_targets.push(item.target);
            }
            // Filter out only the viable targets that are allowed
            viable = viable.filter((item) => {
                return valid_targets.includes(item);
            });
        }
        // If no viable targets exist, return null
        if (viable.length == 0) return null;
        // Otherwise we return the first viable target
        // NOTE: This allows us to have address maps with sections that overlap.
        //       When declaring address maps if one target has a small aperture
        //       that is contained within a second target's larger aperture, then
        //       the smaller aperture must be declared first.
        return viable[0];
    }

    /**
     * Dump out the address map so that it can be reloaded
     * @param {DFProject} project - Project definition used to calculate references
     */
    dumpObject(project) {
        // Get our base object
        let obj = super.dumpObject(project);

        // Attach all initiators and targets
        obj.initiators = [];
        for (let item in this.initiators) obj.initiators.push(item.dumpObject(project));
        obj.targets = [];
        for (let item in this.targets) obj.targets.push(item.dumpObject(project));

        // Attach all constraints
        obj.constraints = {};
        for (let key in Object.keys(this.constraints)) {
            obj.constraints[key] = this.constraints[key].dumpObject(project);
        }

        return obj;
    }

    /**
     * Reload the address map from passed in object.
     * @param {object} obj - Description of this node
     * @param {DFBase} root - Root object in the tree
     * @param {object} types - Map from class name to class definition
     */
    loadObject(obj, root, types) {
        super.loadObject(obj, root, types)

        // Load all initiators
        if (obj.initiators) {
            for (let item of obj.initiators) {
                this.addInitiator((new DFAddressMapInitiator()).loadObject(item, root, types));
            }
        }

        // Load all targets
        if (obj.targets) {
            for (let item of obj.targets) {
                this.addTarget((new DFAddressMapTarget()).loadObject(item, root, types));
            }
        }

        // Load all constraints
        if (obj.constraints) {
            for (let key of Object.keys(obj.constraints)) {
                let constraint = (new DFAddressMapConstraint()).loadObject(
                    obj.constraints[key], root, types, this
                )
                this.constraints[constraint.initiator.id] = constraint;
            }
        }

        return this;
    }
}

try {
    module.exports.DFAddressMapInitiator  = DFAddressMapInitiator;
    module.exports.DFAddressMapTarget     = DFAddressMapTarget;
    module.exports.DFAddressMapConstraint = DFAddressMapConstraint;
    module.exports.DFAddressMap           = DFAddressMap;
} catch(e) {
    // Pass
}
