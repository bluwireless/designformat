# Copyright (C) 2019 Blu Wireless Ltd.
# All Rights Reserved.
#
# This file is part of DesignFormat.
#
# DesignFormat is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# DesignFormat is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# DesignFormat. If not, see <https://www.gnu.org/licenses/>.
#

from designformat import DFConstants

from .base import DFBase

class DFAddressMapInitiator(DFBase):
    """
    DesignFormat description of an initiator within an address map, it defines
    any transformation (masking and offset) that is applied to the inbound request.
    """

    def __init__(self, port=None, port_index=0, mask=None, offset=None, map=None):
        """ Construct the address map initiator.

        Args:
            port      : The port initiating the transaction to the address map
            port_index: The index of the initiator signal within the port
            mask      : The mask applied to the inbound transaction by the map
            offset    : The signed offset applied to the inbound transaction
            map       : The DFAddressMap containing this initiator
        """
        # Construct an ID to represent this initiator
        id = None
        if port != None: id = "%s[%i]" % (port.hierarchicalPath(), port_index)

        # Call the DFBase constructor
        super(DFAddressMapInitiator, self).__init__(id, None)

        # Set other properties
        self.port       = port
        self.port_index = port_index
        self.mask       = mask
        self.offset     = offset
        self.map        = map

    def outboundAddress(self, address):
        """ Translate an inbound address using the mask and offset parameters

        Args:
            address: The address to translate
        """
        return ((address & self.mask) + self.offset)

    def translateAddress(self, address):
        """ Deprecated version of 'outboundAddress'

        Args:
            address: The address to translate
        """
        print(
            "WARNING: DFAddressMapInitiator's translateAddress is deprecated "
            "- please use outboundAddress instead"
        )
        return self.outboundAddress(address)

    def inboundAddress(self, address):
        """
        Translate an outbound address into an inbound address (out of the address
        map) using the offset parameters. Note that this is only a guess because
        an address loses information!

        Args:
            address: The address to translate
        """
        return (address - self.offset)

    def resolveAddress(self, address):
        """ Resolve an inbound address on the initiator to the correct target

        Args:
            address: The address to resolve
        """
        return self.map.resolveTarget(self.outboundAddress(address), initiator=self)

    def dumpObject(self, project):
        """ Dump out the initiator so that it can be reloaded

        Args:
            project: Project for resolving references
        """
        # Get our base object
        obj = super(DFAddressMapInitiator, self).dumpObject(project)

        # Attach extra details
        obj['mask']   = self.mask
        obj['offset'] = self.offset
        obj['port']   = {
            'block': self.port.block.hierarchicalPath(),
            'port' : self.port.name,
            'index': self.port_index
        }

        return obj

    def loadObject(self, obj, root):
        """ Reload a stored initiator

        Args:
            obj  : Description of this node
            root : Root object in the tree
            types: Map from class name to class definition
        """
        super(DFAddressMapInitiator, self).loadObject(obj, root)

        # Simple attributes
        self.mask   = int(obj['mask']) if 'mask' in obj else 0
        self.offset = int(obj['offset']) if 'offset' in obj else 0

        # Find the associated part
        port_path       = "%s[%s]" % (obj['port']['block'], obj['port']['port'])
        self.port       = root.resolvePath(port_path)
        self.port_index = int(obj['port']['index'])

        return self

class DFAddressMapTarget(DFBase):
    """
    DesignFormat description of a target within an address map, it defines the
    offset and aperture size where the target will be selected for handling the
    transaction.
    """

    def __init__(self, port=None, port_index=0, offset=None, aperture=None, map=None):
        """ Construct the address map target

        Args:
            port      : The port accepting the transaction from the address map
            port_index: The index of the initiator signal within the port
            offset    : The offset address of the aperture in the address map
            aperture  : The size of the aperture within the address map
            map       : The DFAddressMap containing this target
        """
        # Construct an ID to represent this target
        id = None
        if port != None: id = "%s[%i]" % (port.hierarchicalPath(), port_index)

        # Call the DFBase constructor
        super(DFAddressMapTarget, self).__init__(id, None)

        # Set other properties
        self.port       = port
        self.port_index = port_index
        self.offset     = offset
        self.aperture   = aperture
        self.map        = map

    def acceptsAddress(self, address):
        """ Indicates whether or not this target's aperture contains a specified address.

        Args:
            address: The address to test for
        """
        return (address >= self.offset) and (address < (self.offset + self.aperture))

    def dumpObject(self, project):
        """ Dump out this object into a plain JSON dictionary.

        Args:
            project: The project definition, used for calculating references
        """
        # Get our base object
        obj = super(DFAddressMapTarget, self).dumpObject(project)

        # Attach extra details
        obj['aperture'] = self.aperture
        obj['offset']   = self.offset
        obj['port']     = {
            'block': self.port.block.hierarchicalPath(),
            'port' : self.port.name,
            'index': self.port_index
        }

        return obj

    def loadObject(self, obj, root):
        """ Reload target from serialised object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
            types: Map from class name to class definition
        """
        super(DFAddressMapTarget, self).loadObject(obj, root)

        # Simple attributes
        self.aperture = int(obj['aperture']) if 'aperture' in obj else 0
        self.offset   = int(obj['offset']) if 'offset' in obj else 0

        # Find the associated part
        port_path       = "%s[%s]" % (obj['port']['block'], obj['port']['port'])
        self.port       = root.resolvePath(port_path)
        self.port_index = int(obj['port']['index'])

        return self

class DFAddressMapConstraint(DFBase):
    """
    DesignFormat description of a constraint in the address map, limiting the
    viable targets for a specific initiator.
    """

    def __init__(self, initiator=None, target=None):
        """ Constructor for an address map constraint

        Args:
            initiator: The initiator for the constraint
            target   : The target for the constraint
        """
        # Construct an ID for this constraint
        id = None
        if initiator != None and target != None:
            id = "%s<->%s" % (initiator.id, target.id)

        # Call the DFBase constructor
        super(DFAddressMapConstraint, self).__init__(id, None)

        # Set further properties
        self.initiator = initiator
        self.target    = target

    def dumpObject(self, project):
        """ Serialise constraint to a plain JSON object.

        Args:
            project: The project definition, used for calculating references
        """
        # Get our base object
        obj = super(DFAddressMapConstraint, self).dumpObject(project)

        # Attach extra details
        obj['initiator'] = {
            'block': self.initiator.port.block.hierarchicalPath(),
            'port' : self.initiator.port.name,
            'index': self.initiator.port_index
        }

        obj['target'] = {
            'block': self.target.port.block.hierarchicalPath(),
            'port' : self.target.port.name,
            'index': self.target.port_index
        }

        return obj

    def loadObject(self, obj, root, map):
        """ Reload a serialised constraint

        Args:
            obj  : Description of this node
            root : Root object in the tree
            types: Map from class name to class definition
            map  : Reference to the parent address map
        """
        super(DFAddressMapConstraint, self).loadObject(obj, root)

        # Find the associated initiator port
        init_port      = root.resolvePath("%s[%s]" % (obj['initiator']['block'], obj['initiator']['port']))
        self.initiator = map.getInitiator(init_port, int(obj['initiator']['index']))

        # Find the associated target port
        target_port = root.resolvePath("%s[%s]" % (obj['target']['block'], obj['target']['port']))
        self.target = map.getTarget(target_port, int(obj['target']['index']))

        return self

class DFAddressMap(DFBase):
    """
    DesignFormat description of an address map aperture from a specific initiator
    to a specific target. It also describes any translation that is performed to
    the address as it passes through the block (masking and offset).
    """

    def __init__(self, block=None):
        """ Constructor for an address map

        Args:
            block: The DFBlock this address map is associated with
        """
        super(DFAddressMap, self).__init__(None, None)
        self.block       = block
        self.initiators  = []
        self.targets     = []
        self.constraints = {}

    def addInitiator(self, initiator):
        """ Add an initiator to this address map

        Args:
            initiator: The initiator
        """
        if not isinstance(initiator, DFAddressMapInitiator):
            raise Exception("Initiator is of invalid type " + type(initiator).__name__)
        elif initiator in self.initiators:
            raise Exception("Initiator has already been added to map")
        elif initiator.port in [x.port for x in self.initiators if x.port_index == initiator.port_index]:
            raise Exception("An initiator has already been added for port " + initiator.id)
        elif initiator.port in [x.port for x in self.targets if x.port_index == initiator.port_index]:
            raise Exception("Port " + initiator.id + " cannot be added as initiator as it is already a target")
        self.initiators.append(initiator)
        initiator.map = self

    def addTarget(self, target):
        """ Add a target to this address map

        Args:
            target: The target
        """
        if not isinstance(target, DFAddressMapTarget):
            raise Exception("Target is of invalid type " + type(target).__name__)
        elif target in self.targets:
            raise Exception("Target has already been added to map")
        elif target.port in [x.port for x in self.targets if x.port_index == target.port_index]:
            raise Exception("A target has already been added for port " + target.id)
        elif target.port in [x.port for x in self.initiators if x.port_index == target.port_index]:
            raise Exception("Port " + target.id + " cannot be added as target as it is already a initiator")
        self.targets.append(target)
        target.map = self

    def addConstraint(self, initiator, target):
        """ Add a constraint to limit which targets can be accessed from an initiator

        Args:
            initiator: The initiator
            target   : The target
        """
        # Check the initiator
        if not isinstance(initiator, DFAddressMapInitiator):
            raise Exception("Initiator is of invalid type " + type(initiator).__name__)
        elif initiator not in self.initiators:
            raise Exception("Initiator has not been added to map")
        # Check the target
        if not isinstance(target, DFAddressMapTarget):
            raise Exception("Target is of invalid type " + type(target).__name__)
        elif target not in self.targets:
            raise Exception("Target has not been added to map")
        # Check this exact constraint doesn't exist
        if len([x for x in self.constraints.values() if x.initiator == initiator and x.target == target]) > 0:
            raise Exception(
                "Constraint between " + initiator.id + " and " + target.id +
                " already exists"
            )
        # Create and add the constraint
        # NOTE: We use a unique key for the initiator-target pairing
        self.constraints[initiator.id+"-"+target.id] = DFAddressMapConstraint(initiator, target)

    def getInitiator(self, port, index):
        """ Get the DFAddressMapInitiator associated to a specific port and index

        Args:
            port : Port to lookup
            index: Signal index within the port
        """
        found = [x for x in self.initiators if x.port == port and x.port_index == index]
        if len(found) > 1:
            raise Exception(
                "Found multiple initiators for port %s[%i]" % (port.hierarchicalPath(), index)
            )
        return found[0] if (len(found) == 1) else None

    def getTarget(self, port, index):
        """ Get the DFAddressMapTarget associated to a specific port

        Args:
            port : Port to lookup
            index: Signal index within the port
        """
        found = [x for x in self.targets if x.port == port and x.port_index == index]
        if len(found) > 1:
            raise Exception(
                "Found multiple targets for port %s[%i]" % (port.hierarchicalPath(), index)
            )
        return found[0] if (len(found) == 1) else None

    def getInitiatorsForTarget(self, target):
        """
        Get all of the initiators in the address map that can reach a particular
        target, taking into account constraints on either initiator or target.

        Args:
            target: The target to search for
        """
        # Sanity check the target
        if not isinstance(target, DFAddressMapTarget):
            raise Exception("Target provided not of correct type: " + type(target).__name__)
        elif target not in self.targets:
            raise Exception("Target is not part of this address map")
        # Find any constraints that pertain to this target
        t_cons = [x for x in self.constraints.values() if x.target == target]
        # If constraints have been found, only return compliant initiators
        if len(t_cons) > 0: return [x.initiator for x in t_cons]
        # Find any initiators that allow this target
        viable = []
        for init in self.initiators:
            # Find any constraints that pertain to this initiator
            i_cons = [x for x in self.constraints.values() if x.initiator == init]
            # If our target appears in the constraints, or there are no
            # constraints, then include the initiator
            if len(i_cons) == 0 or target in [x.target for x in i_cons]:
                viable.append(init)
        return viable

    def getTargetsForInitiator(self, initiator):
        """
        Get all of the targets in the address map that can be reached from a
        particular initiator, taking into account constraints on either initiator
        or target.

        Args:
            initiator: The initiator to search for
        """
        # Sanity check the initiator
        if not isinstance(initiator, DFAddressMapInitiator):
            raise Exception("Initiator provided not of correct type: " + type(initiator).__name__)
        elif initiator not in self.initiators:
            raise Exception("Initiator is not part of this address map")
        # Find any constraints that pertain to this initiator
        i_cons = [x for x in self.constraints.values() if x.initiator == initiator]
        # If constraints have been found, only return compliant targets
        if len(i_cons) > 0: return [x.target for x in i_cons]
        # Find any targets that allow this initiator
        viable = []
        for tgt in self.targets:
            # Find any constraints that pertain to this target
            t_cons = [x for x in self.constraints.values() if x.target == tgt]
            # If our initiator appears in the constraints, or there are no
            # constraints, then include the target
            if len(t_cons) == 0 or initiator in [x.initiator for x in i_cons]:
                viable.append(tgt)
        return viable

    def resolveTarget(self, address, initiator=None):
        """
        Resolve the target port in the address map from a given address. The
        address is assumed to be relative to the address map, if an initiator
        is provided then any known constraints will be applied.

        Args:
            address  : Address being accessed
            initiator: Which initiator is handling the access
        """
        # Find viable targets for the address
        viable = [x for x in self.targets if x.acceptsAddress(address)]
        # If an initiator is provided, constrain as required
        if initiator and initiator.id in self.constraints:
            # Get the list of target this initiator is allowed to access
            valid_targets = [x.target for x in self.constraints[initiator.id]]
            # Filter out only the viable targets that are allowed
            viable        = [x for x in viable if x in valid_targets]
        # If no viable targets exist, return None
        if len(viable) == 0: return None
        # Otherwise we return the first viable target
        # NOTE: This allows us to have address maps with sections that overlap.
        #       When declaring address maps if one target has a small aperture
        #       that is contained within a second target's larger aperture, then
        #       the smaller aperture must be declared first.
        return viable[0]

    def dumpObject(self, project):
        """ Dump out the address map so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        # Get our base object
        obj = super(DFAddressMap, self).dumpObject(project)

        # Attach all initiators and targets
        obj['initiators'] = [x.dumpObject(project) for x in self.initiators]
        obj['targets']    = [x.dumpObject(project) for x in self.targets]

        # Attach all constraints
        obj['constraints'] = {}
        for key in self.constraints.keys():
            obj['constraints'][key] = self.constraints[key].dumpObject(project)

        return obj

    def loadObject(self, obj, root):
        """ Reload the address map from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
            types: Map from class name to class definition
        """
        super(DFAddressMap, self).loadObject(obj, root)

        # Load all initiators
        if 'initiators' in obj:
            for item in obj['initiators']:
                self.addInitiator(DFAddressMapInitiator().loadObject(item, root))

        # Load all targets
        if 'targets' in obj:
            for item in obj['targets']:
                self.addTarget(DFAddressMapTarget().loadObject(item, root))

        # Load all constraints
        if 'constraints' in obj:
            for key in obj['constraints'].keys():
                constraint = DFAddressMapConstraint().loadObject(obj['constraints'][key], root, self)
                self.constraints[constraint.initiator.id] = constraint

        return self
