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
from .common import DFShortcutList
from .command_field import DFCommandField

class DFCommand(DFBase):
    """
    DesignFormat representation of a command. This could be used to represent an
    instruction set for a CPU, or microcode for a DMA engine. Commands can have
    arbitrary width, and fields can be positioned anywhere in the bitmap. Fields
    can overlap if necessary (for commands with multiple parameter options).
    """

    def __init__(self, id=None, width=None, description=None):
        """ Construct a command object

        Args:
            id         : Name of the command
            width      : Bit width of the command
            description: Human-readable description
        """
        super(DFCommand, self).__init__(id, description)
        self.width     = width
        self.fields    = DFShortcutList('id')
        self.fieldtype = DFCommandField

    def addField(self, field):
        """ Add a field to the command store and sort the field store by LSB

        Args:
            field: The field to add
        """
        if not isinstance(field, self.fieldtype):
            raise Exception(
                "Tried to append non " + self.fieldtype.__name__ + " to " +
                type(self).__name__
            )
        self.fields.append(field)
        self.sortFields()

    def sortFields(self):
        """ Ensures fields are in ascending LSB order. """
        self.fields.sort(key=lambda x: x.lsb)

    def dumpObject(self, project):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        obj = super(DFCommand, self).dumpObject(project)

        obj['width']  = self.width
        obj['fields'] = [x.dumpObject(project) for x in self.fields]

        return obj

    def loadObject(self, obj, root):
        """ Reload this node from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
            types: Map from class name to class definition
        """
        super(DFCommand, self).loadObject(obj, root)

        if 'width' in obj:
            self.width = obj['width']

        if 'fields' in obj:
            for field in obj['fields']:
                self.addField((self.fieldtype()).loadObject(field, root))

        self.sortFields()

        return self

    def __getattribute__(self, key):
        """
        By overriding __getattribute__ we can expose all fields as if they were
        first class attributes of this object. Note true first-class properties
        are prioritised over child fields.
        """
        try:
            result = super(DFCommand, self).__getattribute__(key)
            return result
        except AttributeError as e:
            return self.fields[key]
