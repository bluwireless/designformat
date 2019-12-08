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
from .connection import DFConnection

class DFPort(DFBase):
    """ DesignFormat representation of a port (input, output or inout) """

    def __init__(self, name="", type=None, count=0, direction=None, block=None, description=None):
        """ Constructor for a port object.

        Args:
            name       : Name of the port
            type       : Interface type, which refers to a DFInterconnect
            count      : Number of signals carried by the port
            direction  : Whether an input or output
            block      : Reference to the parent DFBlock
            description: Human-readable description of the port
        """
        # Create an identifier for this port
        id = block.id + "[" + name + "]" if (block != None) else name
        super(DFPort, self).__init__(id, description)

        self.name      = name
        self.type      = type
        self.count     = count
        self.direction = direction
        self.block     = block

        self.connections = []

        if not None in [name, type, count, direction, block]:
            self.check()

    def getInterconnectType(self):
        """ Returns the DFInterconnect that this connection represents """
        project = self.block.getProject()
        if project != None:
            return project.getInterconnectType(self.type)
        else:
            return None

    def hierarchicalPath(self):
        """
        Returns a complete hierarchical path from the DFProject's root node all
        the way down to this port.
        """
        path = self.block.hierarchicalPath() + '[' + self.name + ']'
        return path

    def check(self):
        """ Sanity check that the direction is allowed """
        if self.direction not in DFConstants.DIRECTION.values():
            raise Exception("Unsupported DFPort direction: " + self.direction)


    def addConnection(self, conn):
        """
        Add a new connection to this port, either to another port or a DFConstantTie

        Args:
            conn: The connection
        """
        if not isinstance(conn, DFConnection):
            raise Exception("Connection not of type DFConnection")
        self.connections.append(conn)

    def getOutboundConnections(self):
        """ Return just the outbound connections (where we are the driver) """
        return [x for x in self.connections if x.start_port == self]

    def getInboundConnections(self):
        """ Return just the inbound connections (where we are being driven) """
        return [x for x in self.connections if x.end_port == self]

    def getReceiverPorts(self):
        """ Return a list of ports that are driven by this port """
        return [x.end_port for x in self.getOutboundConnections()]

    def getDriverPorts(self):
        """ Return a list of ports that are driving this port"""
        return [x.start_port for x in self.getInboundConnections()]

    def chaseConnection(self, index=0, path=None):
        """
        Chase a connection from the port to it's ultimate destination, note that
        this function returns a tuple containing the port and the signal index.

        Args:
            index: The signal index within the port to chase from
            path : The current path chased up to this point (used by recursive calls)
        """
        # Copy the path so that we don't modify a shared object
        path = path[:] if path else []
        # Add myself to the path
        path += [(self, index)]
        # If I'm an input to a leaf node, then return the path to this point
        if self in self.block.ports.input and self.block.getAttribute(DFConstants.ATTRIBUTES.LEAF_NODE):
            return [path]
        # Get all of my outbound connections for the right index
        outbound = [x for x in self.getOutboundConnections() if x.start_index == index]
        # For each outbound connection, recursively chase the connection
        destinations = []
        for conn in outbound:
            destinations += conn.end_port.chaseConnection(conn.end_index, path)
        # Return all of the destinations I found
        return destinations

    def resolveAddress(self, address, index=0):
        """
        If this port is an initiator in an address map, resolve an address as if
        part of a transaction initiated through this port.

        Args:
            address: The address to resolve
            index  : The index of the signal within the port initiating the
                     transaction (default: 0)
        """
        destinations = None
        # If the block has an address map and I'm an initiator
        if self.block.address_map and self.block.address_map.getInitiator(self, index):
            initiator = self.block.address_map.getInitiator(self, index)
            # Resolve the address to a target
            target = initiator.resolveAddress(address)
            if not target:
                raise Exception(
                    "No target in address map of " + self.block.hierarchicalPath()
                    + " resolves address " + hex(address)
                )
            # Apply initiator masking to the address
            address = initiator.outboundAddress(address)
            # Chase the outbound connection
            destinations = target.port.chaseConnection(target.port_index)
        # Otherwise I could be mid-link?
        else:
            destinations = self.chaseConnection(index)
        # If I don't have a unique destination, this is bad
        if len(destinations) > 1:
            raise Exception(
                "Cannot determine end-point for address " + hex(address) +
                ", found " + str(len(destinations)) + " destinations"
            )
        # If I have no destinations, then I must be the endpoint!
        elif len(destinations) == 0 or destinations[0][-1][0] == self:
            return self
        # Recursively hunt for the end-point
        return destinations[0][-1][0].resolveAddress(address, destinations[0][-1][1])

    def findConnectionPath(self, remote_port, local_index=0, remote_index=0, path=None):
        """
        Try to find a connection pathway between this port and a remote port,
        this procedure can use both basic connectivity information and the address
        map to try and find interconnections. A flood search is used, with the
        shortest path being preferred.

        Args:
            remote_port : The remote port we are trying to reach
            local_index : The index of the signal within this port
            remote_index: The index of the signal within the remote port
            path        : Used to track the path construction during recursion
        """
        # Copy the path so that we don't modify a shared object
        path = path[:] if path else []
        # Check that we haven't got stuck in a deadlock loop
        if len([x for x in path if x[0] == self and x[1] == local_index]) > 0:
            return None
        # Check that I'm not the destination?
        if remote_port == self and remote_index == local_index:
            return path
        # Chase any outbound connections from the port
        destinations = self.chaseConnection(local_index)
        # See if any of the destinations are the desired port
        for dest in destinations:
            if dest[-1][0] == remote_port and dest[-1][1] == remote_index:
                return path + dest
        # If we didn't find the port, see if we can use an address map
        pathways = []
        for dest in destinations:
            addr_map = dest[-1][0].block.address_map
            if addr_map:
                # See if the destination we have is an initiator
                init = addr_map.getInitiator(dest[-1][0], dest[-1][1])
                if init:
                    # Find the list of targets for this initiator
                    targets = addr_map.getTargetsForInitiator(init)
                    # For each target, see if it resolves to a destination
                    for target in targets:
                        full_path = target.port.findConnectionPath(
                            remote_port, target.port_index, remote_index,
                            path + dest
                        )
                        if full_path: pathways.append(full_path)
        # If we couldn't find the port, return None (dead-end)
        if len(pathways) == 0:
            return None
        # Otherwise return the shortest path
        else:
            return sorted(pathways, key=lambda x: len(x))[0]

    def getRelativeAddress(self, remote_port, local_index=0, remote_index=0):
        """
        Calculate the relative address to access a remote port via basic connectivity
        and any address maps. This leverages the findConnectionPath function to
        first identify a viable path, then works through the path to identify the
        base address of the port.

        Args:
            remote_port : The port to resolve
            local_index : Outbound signal index to start from
            remote_index: Inbound signal index of the target
        """
        # First calculate the path, and see if this is viable
        path = self.findConnectionPath(remote_port, local_index, remote_index)
        if path == None: return None
        # Extract just the nodes in the path that have associated address maps
        contributors = [x for x in path if x[0].block.address_map != None]
        # If there are no contributors to the address, return 0
        if len(contributors) == 0: return 0
        # Walk backwards through the path to assess the base address of the endpoint
        base_address = 0
        for node in contributors[::-1]:
            if node[0].block.address_map:
                init = node[0].block.address_map.getInitiator(node[0], node[1])
                tgt  = node[0].block.address_map.getTarget(node[0], node[1])
                if init and tgt:
                    raise Exception(
                        "Node in path is both initiator and target " +
                        node[0].hierarchicalPath()
                    )
                elif init:
                    base_address -= init.offset
                elif tgt:
                    base_address += tgt.offset
                else:
                    raise Exception(
                        "Node in path is not associated to the block's address map "
                        + node[0].hierarchicalPath()
                    )
        # If the last node in the list of contributors is an initiator, add back
        # in the offset (our addresses will be relative to this point)
        last_node = contributors[0]
        initiator = last_node[0].block.address_map.getInitiator(last_node[0], last_node[1])
        if initiator:
            base_address += initiator.offset
        return base_address

    def dumpObject(self, project):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        obj = super(DFPort, self).dumpObject(project)

        obj['name']      = self.name
        obj['type']      = self.type
        obj['count']     = self.count
        obj['direction'] = self.direction
        obj['block']     = self.block.hierarchicalPath()

        return obj

    def loadObject(self, obj, root):
        """ Reload this node from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
        """
        super(DFPort, self).loadObject(obj, root)

        self.name      = obj['name']
        self.type      = obj['type']
        self.count     = int(obj['count'])
        self.direction = obj['direction']
        if 'block' in obj:
            self.block = root.resolvePath(obj['block'])

        self.check()

        return self
