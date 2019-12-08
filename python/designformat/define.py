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

class DFDefine(DFBase):
    """ Defines a named constant value related to the design. """

    def __init__(self, id=None, value=None, description=None):
        """ Constructor for the defined value.

        Args:
            id         : Name of the constant
            value      : Value of the constant (can be integer, or otherwise)
            description: Human-readable description of the definition
        """
        super(DFDefine, self).__init__(id, description)

        self.value = value

    def dumpObject(self, project=None):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        # Get our base object
        obj = super(DFDefine, self).dumpObject(project)

        # Attach the carried value
        obj['value'] = self.value

        # Return the object
        return obj

    def loadObject(self, obj, root=None):
        """ Reload this node from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
        """
        super(DFDefine, self).loadObject(obj, root)

        # Reload the carried value
        self.value = obj['value']

        # Return self for chaining
        return self

    def __repr__(self, depth=0, max_depth=2, max_list=2):
        return str(self.value)

    def __str__(self):
        return str(self.value)
