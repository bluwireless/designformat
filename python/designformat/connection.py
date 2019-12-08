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

import random

from .base import DFBase
from .constant_tie import DFConstantTie

class DFConnection(DFBase):
    """ DesignFormat representation of an interconnection between two points """

    def __init__(self, start_port=None, start_index=None, end_port=None, end_index=None):
        """ Constructor of the connection

        Args:
            start_port : Start point can be a DFPort or DFConstantTie
            start_index: Signal index within DFPort to connect
            end_port   : End point can only be a DFPort
            end_index  : Signal index within DFPort to connect
        """
        if (start_port != None) and (end_port != None):
            # Create an identifier for this connection
            id  = start_port.id + "[" + str(start_index) + "]"
            id += "-to-"
            id += end_port.id + "[" + str(end_index) + "]"

            # Call the constructor
            super(DFConnection, self).__init__(id)

            self.start_port  = start_port
            self.start_index = start_index if start_index != None else 0
            self.end_port    = end_port
            self.end_index   = end_index if end_index != None else 0

            if (self.start_port != None):
                self.start_port.addConnection(self)
            if (self.end_port   != None):
                self.end_port.addConnection(self)

            self.checkConnection()
        else:
            super(DFConnection, self).__init__('dfconnection-%s' % random.randint(0, 1000000))

    def checkConnection(self):
        """ Check that the connection is sane with sensible signal indexes """
        from .port import DFPort
        if isinstance(self.start_port, DFPort):
            if self.start_index < 0 or self.start_index >= self.start_port.count:
                raise Exception(
                    "Start index %i is out of range for port count %i" %
                    (self.start_index, self.start_port.count)
                )
        if isinstance(self.end_port, DFPort):
            if self.end_index < 0 or self.end_index >= self.end_port.count:
                raise Exception(
                    "End index %i is out of range for port count %i" %
                    (self.end_index, self.end_port.count)
                )

    def getInterconnectType(self):
        """ Returns the DFInterconnect type of the end points of this interconnect """
        return self.end_port.getInterconnectType()

    def isTieOff(self):
        """ Returns if this connection is a tie-off (i.e. start point is a DFConstantTie) """
        return isinstance(self.start_port, DFConstantTie)

    def dumpObject(self, project):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        from .port import DFPort
        obj = super(DFConnection, self).dumpObject(project)

        if isinstance(self.start_port, DFPort):
            obj['start_port'] = {
                'block': self.start_port.block.hierarchicalPath(),
                'port' : self.start_port.name
            }
        elif isinstance(self.start_port, DFConstantTie):
            obj['start_tie'] = self.start_port.dumpObject(project)

        obj['end_port'] = {
            'block': self.end_port.block.hierarchicalPath(),
            'port' : self.end_port.name
        }

        obj['start_index'] = self.start_index
        obj['end_index']   = self.end_index

        return obj

    def loadObject(self, obj, root):
        """ Reload this node from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
        """
        super(DFConnection, self).loadObject(obj, root)

        if 'start_port' in obj:
            start_path  = "%s[%s]" % (obj['start_port']['block'], obj['start_port']['port'])
            self.start_port = root.resolvePath(start_path)
        elif 'start_tie' in obj:
            self.start_port  = (DFConstantTie()).loadObject(obj['start_tie'], root)

        end_path  = "%s[%s]" % (obj['end_port']['block'], obj['end_port']['port'])
        self.end_port = root.resolvePath(end_path)

        self.start_port.addConnection(self)
        self.end_port.addConnection(self)

        self.start_index = int(obj['start_index']) if 'start_index' in obj else 0
        self.end_index   = int(obj['end_index']) if 'end_index' in obj else 0

        self.checkConnection()

        return self
