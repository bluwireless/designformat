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
from .common import convert_to_class, isNaN
from .define import DFDefine

class DFCommandField(DFBase):
    """
    DesignFormat representation of a field of a command. This could be used to
    represent a sub-field of an instruction for a CPU, or a parameter in a
    microcode instruction for a DMA engine. Command fields have fixed widths,
    with specified LSB alignments. The field's value can be enumerated if
    required, to allow specific control values to be named.
    """

    def __init__(
        self, id=None, lsb=None, size=None, reset=None, signed=False,
        description=None
    ):
        """ Construct a command field object
        Args:
            id         : The name of the register field
            lsb        : Least significant bit position within the command
            size       : Width of the field in bits
            reset      : Value taken at reset (or default value)
            signed     : Whether the value is signed
            description: Human-readable description
        """
        super(DFCommandField, self).__init__(id, description)

        self.enum = convert_to_class({})

        if (lsb != None) or (size != None) or (reset != None):
            if (isNaN(lsb)):
                raise Exception(type(self).__name__ + " LSB must be an integer")
            if (isNaN(size)):
                raise Exception(type(self).__name__ + " Size must be an integer")
            if (isNaN(reset)):
                raise Exception(type(self).__name__ + " Reset must be an integer")

            self.lsb    = int(lsb)
            self.size   = int(size)
            self.reset  = int(reset)
            self.signed = signed

            self.check()

    def check(self):
        """ Check that the values assigned to the field are sensible """
        if isNaN(self.lsb) or (self.lsb < 0):
            raise Exception(
                type(self).__name__ + " " + self.id + " LSB " + str(self.lsb) +
                " is out of range"
            )
        if isNaN(self.size) or (self.size < 1):
            raise Exception(
                type(self).__name__ + " " + self.id + " Size " + str(self.size)
                + " is out of range - LSB=" + str(self.lsb)
            )
        if isNaN(self.reset) or (not self.signed and self.reset < 0):
            raise Exception(
                type(self).__name__ + " " + self.id + " Reset Value " +
                str(self.reset) + " is out of range"
            )

    def addEnumValue(self, key, value, description=None):
        """ Create a new named value for the register

        Args:
            key        : Name of the value
            value      : Value to be associated
            description: Human-readable description
        """
        self.enum[key] = DFDefine(key, int(value), description)

    def dumpObject(self, project):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        obj = super(DFCommandField, self).dumpObject(project)

        obj['lsb']    = self.lsb
        obj['size']   = self.size
        obj['reset']  = self.reset
        obj['signed'] = self.signed
        obj['enum']   = {}
        for key in self.enum:
            obj['enum'][key] = self.enum[key].dumpObject(project)

        return obj

    def loadObject(self, obj, root):
        """ Reload this node from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
            types: Map from class name to class definition
        """
        super(DFCommandField, self).loadObject(obj, root)

        self.lsb    = int(obj['lsb'])
        self.size   = int(obj['size'])
        self.reset  = int(obj['reset'])
        self.signed = obj['signed']

        # Reload enumerated values
        self.enum  = convert_to_class({})
        if 'enum' in obj:
            for key in obj['enum']:
                self.enum[key] = DFDefine().loadObject(obj['enum'][key], root)

        # Perform sanity checks
        self.check()

        return self
