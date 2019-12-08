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

from .base import DFBase

class DFConstantTie(DFBase):
    """ DesignFormat representation of a tie to a constant value """

    def __init__(self, value="", reset=False, block=None):
        """ Constructor for the constant tie value

        Args:
            value: The constant value represented by this tie
            reset: Ignore the value field, instead tie to the DFInterconnect's
                   reset value.
            block: Reference to the block holding this tie
        """
        # Create an identifier for this port
        id = "tie-" + str(value)
        if block != None: id = block.id + "-" + id
        super(DFConstantTie, self).__init__(id)

        self.value = value
        self.reset = reset
        self.block = block

        self.connections = []

    def hierarchicalPath(self):
        """ Returns the full hierarchical path to this block from the root """
        path = self.block.hierarchicalPath() + '[' + self.name + ']'
        return path

    def addConnection(self, conn):
        """ Associate a DFConnection with this constant tie value

        Args:
            conn: The connection to associate
        """
        from .connection import DFConnection
        if not isinstance(conn, DFConnection):
            raise Exception("Connection not of type DFConnection")
        self.connections.append(conn)

    def dumpObject(self, project):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        obj = super(DFConstantTie, self).dumpObject(project)

        obj['value'] = self.value
        obj['reset'] = self.reset
        obj['block'] = self.block.hierarchicalPath()

        return obj

    def loadObject(self, obj, root):
        """ Reload this node from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
        """
        super(DFConstantTie, self).loadObject(obj, root)

        self.value = obj['value']

        if 'reset' in obj:
            self.reset = obj['reset']

        if 'block' in obj:
            self.block = root.resolvePath(obj['block'])

        return self
