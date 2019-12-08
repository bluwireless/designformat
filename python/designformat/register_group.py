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
from .common import DFShortcutList
from .register import DFRegister

class DFRegisterGroup(DFBase):
    """ DesignFormat representation of a named group of registers """

    def __init__(self, id=None, offset=0, block=None, description=None):
        """ Constructor for the register group object.

        Args:
            id         : Name of the group
            offset     : Offset from the register bank's base address
            block      : The DFBlock which is holding this register group
            description: Human-readable description of this group
        """
        super(DFRegisterGroup, self).__init__(id, description)
        self.offset    = offset
        self.block     = block
        self.registers = DFShortcutList('id')

    def addRegister(self, reg):
        """ Add a new register and sort the list by ascending address

        Args:
            reg: The register to add
        """
        if not isinstance(reg, DFRegister):
            raise Exception("Tried to append non-DFRegister to DFRegisterGroup")
        elif reg.offset < 0:
            raise Exception("Invalid offset of %i for register %s" % (reg.offset, reg.id))
        reg.group = self
        self.registers.append(reg)
        self.sortRegisters()

    def sortRegisters(self):
        """
        Ensures the register list is in acsending address order and checks that
        there are no overlaps.
        """
        # Perform sort on address
        self.registers.sort(key=lambda x: x.offset)

        # Now walk up the list and check for overlaps
        last_reg = None
        for reg in self.registers:
            if last_reg != None and reg.offset <= last_reg.offset:
                raise Exception(
                    "Addresses of registers %s and %s overlap!" %
                    (reg.id, last_reg.id)
                )
            last_reg = reg

    def getOffset(self):
        """ Return this register group's offset """
        return self.offset

    def dumpObject(self, project):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        obj = super(DFRegisterGroup, self).dumpObject(project)

        obj['offset'] = self.offset

        obj['registers'] = [x.dumpObject(project) for x in self.registers]

        return obj

    def loadObject(self, obj, root):
        """ Reload this node from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
        """
        super(DFRegisterGroup, self).loadObject(obj, root)

        if 'offset' in obj:
            self.offset = obj['offset']

        if 'registers' in obj:
            for field in obj['registers']:
                self.addRegister((DFRegister()).loadObject(field, root))

        self.sortRegisters()

        return self

    def __getattribute__(self, key):
        """
        By overriding __getattribute__ we can expose all registers as if they
        were first class attributes of this object. Note that this code
        prioritises true class properties.
        """
        try:
            return super(DFRegisterGroup, self).__getattribute__(key)
        except AttributeError as e:
            # Does the key relate to one of our registers?
            if len(self.registers) > 0 and key in self.registers.keys():
                return self.registers[key]
            # Oterhwise, if we get this far without returning raise an exception
            raise e