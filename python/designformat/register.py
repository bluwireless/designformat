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
from .command import DFCommand
from .command_field import DFCommandField
from .common import convert_to_class, DFShortcutList

class DFRegisterField(DFCommandField):
    """
    DesignFormat representation of a register field. This is treated as a
    special case of a DFCommandField. Currently no extra parameters are
    necessary, but the class is created for future extensibility.
    """
    pass

class DFRegister(DFCommand):
    """
    DesignFormat representation of a register. This is treated as a special case
    of DFCommand, with extra parameters for its offset and access conditions.
    However, unlike with commands, register fields should never overlap.
    """

    def __init__(
        self, id=None, offset=None, bus_access=None, block_access=None,
        inst_access=None, group=None, description=None
    ):
        """ Constructor for the register object

        Args:
            id          : Name of the register
            offset      : Offset from the register group's base address
            bus_access  : Type of software access to the register (e.g. RW, RO, WO, etc)
            block_access: Type of hardware access to the register (e.g. RO, WO, ...)
            inst_access : Type of instruction access to the register (e.g. RO, WO, ...)
            group       : The parent group of this register
            description : Human read-able description of the register
        """
        super(DFRegister, self).__init__(id=id, description=description)
        self.fieldtype = DFRegisterField

        self.offset = offset
        self.group  = group
        self.access = convert_to_class({
            "bus"  : bus_access   if bus_access   != None else DFConstants.ACCESS.RW,
            "block": block_access if block_access != None else DFConstants.ACCESS.RW,
            "inst" : inst_access  if inst_access  != None else DFConstants.ACCESS.RW
        })

        for key in self.access:
            if self.access[key] not in DFConstants.ACCESS.values():
                raise Exception("DFRegister does not support access type " + self.access[key])

    def sortFields(self):
        """ Ensures fields are in ascending bit order - also checks for overlaps. """
        # Use the default sorting order
        super(DFRegister, self).sortFields()

        # Walk up the set and check for overlaps
        last_lsb = -1
        for field in self.fields:
            if (field.lsb <= last_lsb):
                raise Exception("LSB of two " + self.fieldtype.__name__ + " overlap!")
            last_lsb = field.lsb + field.size - 1

    @property
    def width(self):
        return max([(x.size + x.lsb) for x in self.fields])

    @width.setter
    def width(self, val):
        # Width is automatically calculated, so ignore attempts to set it
        pass

    def getOffset(self):
        """
        Calculate the total offset of this register from the register bank's base
        address, taking into account the parent group's offset.
        """
        from .register_group import DFRegisterGroup
        offset = self.offset
        if isinstance(self.group, DFRegisterGroup):
            offset += self.group.offset
        return offset

    def getRelativeAddress(self, remote):
        """
        Get the address of this register relative to a port or block somewhere
        else in the design. This leverages connectivity and address maps to
        determine how the two points are related.

        Args:
            remote: DFPort or DFBlock to measure relative address from
        """
        # Sanity checks
        if type(remote).__name__ not in ["DFPort", "DFBlock"]:
            raise Exception("Remote is of invalid type " + type(remote).__name__)
        # Find the handle to the remote block
        remote_block = remote if type(remote).__name__ == "DFBlock" else remote.block
        # Leverage the block's getRelativeAddress function
        base_addr = remote_block.getRelativeAddress(self.group.block)
        if base_addr == None:
            return None
        # Add in the offset of this register from the base of the register set
        return (base_addr + self.getOffset())

    def dumpObject(self, project):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        obj = super(DFRegister, self).dumpObject(project)

        # Remove the injected width, it's not relevant to DFRegister
        del obj['width']

        obj['offset'] = self.offset
        obj['access'] = self.access.dict()

        return obj

    def loadObject(self, obj, root):
        """ Reload this node from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
        """
        super(DFRegister, self).loadObject(obj, root)

        self.offset = obj['offset']
        self.access = convert_to_class(obj['access'])

        return self
