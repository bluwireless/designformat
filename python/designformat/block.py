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

import re

from designformat import DFConstants

from .address_map import DFAddressMap
from .base import DFBase
from .common import DFShortcutList, convert_to_class
from .connection import DFConnection
from .constant_tie import DFConstantTie
from .interconnect import DFInterconnect
from .port import DFPort
from .register_group import DFRegisterGroup

class DFBlock(DFBase):
    """ DesignFormat representation of a system block """

    def __init__(self, id=None, type=None, parent=None, description=None, address_map=None):
        """ Construct the block instance

        Args:
            id         : Instance identifier for this block
            type       : The module type (i.e. not the instantiation name)
            parent     : Pointer to the parent node of this block either a DFBlock
                         or a DFProject
            description: Human-readable description of the object
            address_map: Address map to associate
        """
        super(DFBlock, self).__init__(id, description)

        self.type     = type
        self.parent   = parent

        self.ports       = convert_to_class({
            'input' : DFShortcutList("name"), # Use shortcut list so that ports
            'output': DFShortcutList("name"), # can be accessed like:
            'inout' : DFShortcutList("name")  # block.ports.input.clk
        })
        self.children    = DFShortcutList("id")
        self.connections = []
        self.registers   = DFShortcutList("id")
        self.address_map = address_map

    def hierarchicalPath(self):
        """ Returns the full hierarchical path to this block from the root """
        path = self.id
        if self.parent != None and isinstance(self.parent, DFBlock):
            path = "%s.%s" % (self.parent.hierarchicalPath(), path)
        return path

    def getRootBlock(self):
        """ Returns the root block of the design (stopping before the DFProject) """
        if self.parent != None and isinstance(self.parent, DFBlock):
            return self.parent.getRootBlock()
        else:
            return self

    def getProject(self):
        """ Resolves the root block of the design, and then gets its parent DFProject """
        from .project import DFProject
        root = self.getRootBlock()
        if root != None and root.parent != None and isinstance(root.parent, DFProject):
            return root.parent
        else:
            return None

    def resolvePath(self, path):
        """ Return a DFPort or DFBlock definition based on a hierarchical path

        Args:
            path: The path to resolve
        """
        # We expect a path of the form: parent.child.grandchild[portname]
        #  - We can also support 'parent.child' and '[portname]'

        # Now extract lookup path segments
        parts     = re.compile(r"^([\w\.\-]+)?(\[[\w\-]+\])?$").search(path).groups()
        sections  = parts[0].split('.') if parts[0] != None else []
        port_name = re.sub(r"([\[\]]+)", "", parts[1]) if parts[1] != None else None

        if len(sections) > 0:
            next_id = sections[0]
            found = [x for x in self.children if x.id == next_id.strip()]
            if len(found) != 1:
                # Is this my ID?
                if next_id.strip() == self.id:
                    sub_path = ".".join(sections[1:])
                    if (port_name != None):
                        sub_path += '[' + port_name + ']'
                    return self.resolvePath(sub_path)
                else:
                    raise Exception(
                        "Unable to resolve block - 0 or more than 1 child available - path: "
                        + path + " (hierarchy " + self.hierarchicalPath() + ")"
                    )
            if len(sections) > 1 or port_name != None:
                sub_path = ".".join(sections[1:])
                if port_name != None:
                    sub_path += '[' + port_name + ']'
                return found[0].resolvePath(sub_path)
            else:
                return found[0]

        elif (len(sections) == 0) and (port_name != None):
            all_ports = self.ports.input + self.ports.output + self.ports.inout
            found = [x for x in all_ports if x.name == port_name]
            if len(found) != 1:
                raise Exception(
                    "Unable to resolve port - 0 or more than 1 option available - path: "
                    + path + " (hierarchy " + self.hierarchicalPath() + ")"
                )
            return found[0]

        elif len(sections) == 0:
            return self

        else:
            raise Exception(
                "Unable to resolve port - no path provided (hierarchy " + path + ")"
            )

        return None

    def addRegister(self, register):
        """ Attach a DFRegisterGroup to this block

        Args:
            register: The register group to attach
        """
        if not isinstance(register, DFRegisterGroup):
            raise Exception("Register is not of type DFRegister or DFRegisterGroup")
        register.block = self
        self.registers.append(register)

    def addChild(self, child):
        """ Attach a DFBlock to this block as a child node

        Args:
            child: The child to attach
        """
        if not isinstance(child, DFBlock):
            raise Exception("Child is not of type DFBlock")
        self.children.append(child)

    def addPort(self, port):
        """ Attach a new port to this block (can be input, output, or bidirectional)

        Args:
            port: The port to attach
        """
        if not isinstance(port, DFPort):
            raise Exception("Port is not of type DFPort")
        if port.direction == DFConstants.DIRECTION.INPUT:
            self.ports.input.append(port)
        elif port.direction == DFConstants.DIRECTION.OUTPUT:
            self.ports.output.append(port)
        elif port.direction == DFConstants.DIRECTION.INOUT:
            self.ports.inout.append(port)
        else:
            raise Exception("Unsupported port direction: " + port.direction)

    def getPrincipalSignal(self, intc_type):
        """
        Get the principal signal (input port or child output port) for a particular
        interconnect type.

        Args:
            intc_type: The interconnect to resolve
        """
        if isinstance(intc_type, DFInterconnect):
            intc_type = intc_type.id
        # Find all input ports matching the type
        of_type = [x for x in self.ports.input if x.type == intc_type]
        # Find all child output ports matching the type
        for child in self.children:
            of_type += [x for x in child.ports.output if x.type == intc_type]
        # Now filter out which (if any) port has been nominated as principal
        principal = [
            x for x in of_type if x.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL)
        ]
        # Assert that a maximum of only one principal exists
        assert len(principal) <= 1
        # If a principal exists, return it, else return nothing
        return principal[0] if (len(principal) > 0) else None

    def setPrincipalSignal(self, port):
        """
        Nominate an input port or child output port as the principal signal for a
        particular interconnect type (e.g. the main clock signal for a block is
        the 'principal' clock).

        Args:
            port: The port to nominate as principal
        """
        # Check this port actually exists?
        if isinstance(port, DFPort):
            if port.block == self:
                assert port in self.ports.input
            elif port.block in self.children:
                assert port in port.block.ports.output
            else:
                raise Exception("Port does not exist in this scope")
        # Check if we have a principal of this type already, clear it
        existing = self.getPrincipalSignal(port.type)
        if existing != None:
            existing.setAttribute(DFConstants.ATTRIBUTES.PRINCIPAL, False)
        # Setup the new principal
        port.setAttribute(DFConstants.ATTRIBUTES.PRINCIPAL, True)

    def getAllPorts(self):
        """ Return a concatenated list of all of the ports on the block """
        return sorted(self.ports.input + self.ports.output + self.ports.inout, key=lambda x: x.name)

    def getUnconnectedPorts(self):
        """ Return a list of all ports on this block that are not internally connected """
        return [x for x in self.getAllPorts() if (
            (
                (x.direction == DFConstants.DIRECTION.INPUT) and
                (len(x.getOutboundConnections()) == 0)
            ) or
            (
                (x.direction == DFConstants.DIRECTION.OUTPUT) and
                (len(x.getInboundConnections()) == 0)
            )
        )]

    def getUnconnectedChildPorts(self):
        """
        Return a list of all ports on child modules that are not connected within
        this block
        """
        ports = []
        for child in self.children:
            ports += [x for x in child.getAllPorts() if (
                (
                    (x.direction == DFConstants.DIRECTION.INPUT) and
                    (len(x.getInboundConnections()) == 0)
                ) or
                (
                    (x.direction == DFConstants.DIRECTION.OUTPUT) and
                    (len(x.getOutboundConnections()) == 0)
                )
            )]
        return ports

    def addConnection(self, start_port, start_index, end_port, end_index):
        """
        Create a connection between two ports - specifying which signal within
        each port is part of the connection (for ports with count > 1).

        Args:
            start_port : The port driving the connection
            start_index: Signal index within the driver port
            end_port   : The port being driven by the connection
            end_index  : Signal index within the driven port
        """
        if not isinstance(start_port, DFPort) or not isinstance(end_port, DFPort):
            raise Exception("Port is not of type DFPort")
        self.connections.append(DFConnection(
            start_port, start_index, end_port, end_index
        ))

    def addTieOff(self, port, signal_index, constant):
        """
        Create a connection between a port and a constant, specifying which signal
        within the port is part of the connection (for ports with count > 1)

        Args:
            port        : The port to drive
            signal_index: The signal index within the port to drive
            constant    : The constant value to drive onto the port
        """
        if not isinstance(port, DFPort):
            raise Exception("Port is not of type DFPort")
        elif not isinstance(constant, DFConstantTie):
            raise Exception("Constant is not of type DFConstantTie")
        self.connections.append(DFConnection(constant, 0, port, signal_index))

    def getInterconnectTypes(self, depth=None):
        """
        Return a list of all of the connection types used in this hierarchy. You
        can limit the depth of the query using the 'depth' parameter, not passing
        the value will return unlimited depth.

        Args:
            depth - How deep to retrieve (whether to query children)
        """
        all_types = []

        # Append all of my children's port types
        for port in self.getAllPorts():
            intc_type = self.getProject().getInterconnectType(port.type)
            all_types.append(intc_type)

        # Ask my children for their types
        if self.children and len(self.children) > 0 and (depth == None or depth > 0):
            for child in self.children:
                all_types += child.getInterconnectTypes(
                    depth=(None if depth == None else (depth-1)),
                )

        # Create an ordered, unique list of the types
        intc_types = sorted(list(set(all_types)), key=lambda x: x.id)

        return intc_types

    def getChildTypes(self, depth=None):
        """
        Return a list of all of the types of the child modules. You can limit the
        depth of the query using the 'depth' parameter, not passing the value will
        return unlimited depth.

        Args:
            depth: How deep to retrieve (whether to query children)
        """
        all_types = self.children[:]

        # Ask my children for their types
        if self.children and len(self.children) > 0 and (depth == None or depth > 0):
            for child in self.children:
                all_types += child.getChildTypes(
                    depth=(None if depth == None else (depth-1)),
                )

        # Create a unique set of examples of each type of DFBlock
        got_types    = []
        unique_types = []
        for block in all_types:
            if block.type not in got_types:
                got_types.append(block.type)
                unique_types.append(block)

        # Sort the list
        unique_types.sort(key=lambda x: x.id)

        return unique_types

    def setAddressMap(self, map):
        """
        Set the address map for this block. The address map models how initiator
        and target ports on the block are linked.

        Args:
            map: The address map
        """
        if not isinstance(map, DFAddressMap):
            raise Exception("Address map not of correct type " + type(map).__name__)
        elif self.address_map != None:
            raise Exception("An address map has already been configured for " + self.hierarchicalPath())
        self.address_map = map
        self.address_map.block = self

    def getRelativeAddress(self, remote, remote_index=0):
        """
        Use the ports and address map of this block to work out the relative
        address needed to access a specified remote point. If the remote point is
        a port, we just need to iterate through our outputs. If the remote point
        is a block then we need to iterate through our outputs and their inputs.

        Args:
            remote      : Either a DFBlock or a DFPort to find the address of
            remote_index: If the remote is a DFPort, this is used as the signal
                          index.
        """
        # Sanity checks
        if type(remote) not in [DFPort, DFBlock]:
            raise Exception("Remote is of invalid type " + type(remote).__name__)
        elif isinstance(remote, DFPort) and (remote_index < 0 or remote_index >= remote.count):
            raise Exception("Remote index is not valid %i" % remote_index)
        # Find all of the viable sources (ports on this block)
        sources = []
        for output in self.ports.output:
            sources += [(output, i) for i in range(output.count)]
        if len(sources) == 0:
            raise Exception("Failed to identify any sources for " + self.hierarchicalPath())
        # Find all of the viable targets (ports on the remote block)
        targets = []
        if isinstance(remote, DFPort):
            targets = [(remote, remote_index)]
        else:
            for input in remote.ports.input:
                targets += [(input, i) for i in range(input.count)]
        if len(targets) == 0:
            raise Exception("Failed to identify any targets for " + remote.hierarchicalPath())
        # Attempt to find a pairing between sources and targets that is linked
        for source in sources:
            for target in targets:
                path = source[0].findConnectionPath(target[0], source[1], target[1])
                if path:
                    return source[0].getRelativeAddress(target[0], source[1], target[1])
        # Otherwise there isn't a pathway
        return None

    def dumpObject(self, project):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        # Get our base object
        obj = super(DFBlock, self).dumpObject(project)

        # Attach extra details
        obj['path']   = self.hierarchicalPath()
        obj['type']   = self.type
        obj['parent'] = (
            self.parent.hierarchicalPath()
            if (self.parent != None and isinstance(self.parent, DFBlock)) else
            None
        )

        # Attach all ports
        obj['ports'] = {
            'input' : [x.dumpObject(project) for x in self.ports.input],
            'output': [x.dumpObject(project) for x in self.ports.output],
            'inout' : [x.dumpObject(project) for x in self.ports.inout]
        }

        # Attach all children
        obj['children'] = [x.dumpObject(project) for x in self.children]

        # Attach all connections
        obj['connections'] = [x.dumpObject(project) for x in self.connections]

        # Attach all registers
        obj['registers'] = [x.dumpObject(project) for x in self.registers]

        # Attach the address map if present
        if self.address_map:
            obj['address_map'] = self.address_map.dumpObject(project)

        # Return the object
        return obj

    def loadObject(self, obj, root=None):
        """ Reload this node from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
            types: Map from class name to class definition
        """
        super(DFBlock, self).loadObject(obj, root)

        # Work out if we're the root?
        root = root if root != None else self

        # Lookup our parent
        if 'parent' in obj and obj['parent']:
            self.parent = root.resolvePath(obj['parent'])

        self.type = obj['type']

        # At this point, register against my parent so that sub-blocks can use
        # path resolving.
        if self.parent != None:
            self.parent.children.append(self)

        if 'ports' in obj and 'input' in obj['ports']:
            for item in obj['ports']['input']:
                self.ports.input.append(
                    (DFPort(direction=DFConstants.DIRECTION.INPUT, block=self)).loadObject(item, root)
                )

        if 'ports' in obj and 'output' in obj['ports']:
            for item in obj['ports']['output']:
                self.ports.output.append(
                    (DFPort(direction=DFConstants.DIRECTION.OUTPUT, block=self)).loadObject(item, root)
                )

        if 'ports' in obj and 'inout' in obj['ports']:
            for item in obj['ports']['inout']:
                self.ports.inout.append(
                    (DFPort(direction=DFConstants.DIRECTION.INOUT, block=self)).loadObject(item, root)
                )

        if 'registers' in obj:
            for item in obj['registers']:
                self.addRegister((DFRegisterGroup()).loadObject(item, root))

        if 'children' in obj:
            for item in obj['children']:
                (DFBlock()).loadObject(item, root)

        # Build out interconnections between my children
        if 'connections' in obj:
            for item in obj['connections']:
                self.connections.append((DFConnection()).loadObject(item, root))

        # Reload the address map for the block
        if 'address_map' in obj:
            self.setAddressMap(DFAddressMap(self).loadObject(obj['address_map'], root))

        return self

    def __getattribute__(self, key):
        """
        By overriding __getattribute__ we can expose any child blocks or registers
        as if they were first class attributes of this object. Note that the code
        prioritises true class properties.

        Args:
            key: The key to resolve
        """
        try:
            return super(DFBlock, self).__getattribute__(key)
        except AttributeError as e:
            if len(self.children) > 0 and key in self.children.keys():
                return self.children[key]
            elif len(self.registers) > 0:
                # Does the key relate to one of our register groups?
                if key in self.registers.keys():
                    return self.registers[key]
                # Does the key relate to a register within one of the register groups?
                for reg_grp in self.registers:
                    if key in reg_grp.registers.keys():
                        return reg_grp.registers[key]
            # Otherwise, if we get this far without returning raise an exception
            raise e
