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

from designformat import DFConstants

from .common import convert_to_class
from .define import DFDefine

class DFInterconnect(DFBase):
    """ DesignFormat representation of a type of interconnection """

    def __init__(self, id=None, role=None, description="", project=None):
        """ Constructor for the interconnect type

        Args:
            id         : Name of the interconnect type
            role       : The role - one of 'MASTER', 'SLAVE' or 'BIDIR'
            description: Human-readable description of the interconnect
            project    : Reference to the top-level DFProject
        """
        super(DFInterconnect, self).__init__(id, description)

        self.role    = role if role != None else DFConstants.ROLE.MASTER
        self.project = project

        self.components  = [] # Constituent components of the interconnect

        # Sanity check
        self.checkRole()

    def checkRole(self):
        """ Checks that the configured role is valid (SLAVE, MASTER, or BIDIR) """
        if not self.role in DFConstants.ROLE.values():
            raise Exception("Invalid role specified to DFInterconnect: " + self.role)

    def getAllRoles(self):
        """
        Return all of the roles offered by this interconnect type, taking account
        of any child components and interconnects they may reference.
        """
        roles = []
        for comp in self.components:
            comp_roles = comp.getAllRoles()
            # If I have a SLAVE role, then I need to invert my roles
            for role in comp_roles:
                if self.role == DFConstants.ROLE.SLAVE:
                    if role == DFConstants.ROLE.MASTER:
                        roles.append(DFConstants.ROLE.SLAVE)
                    elif role == DFConstants.ROLE.SLAVE:
                        roles.append(DFConstants.ROLE.MASTER)
                    else:
                        roles.append(role)
                else:
                    roles.append(role)
        return set(roles)

    def hasRole(self, role):
        """ Checks that the interconnect has components of the specified role.

        Args:
            role: The role to check for
        """
        return (role in self.getAllRoles())

    def hasMasterRole(self):
        """ Checks that the interconnect has components with the Master role """
        return (DFConstants.ROLE.MASTER in self.getAllRoles())

    def hasSlaveRole(self):
        """ Checks that the interconnect has components with the Slave role """
        return (DFConstants.ROLE.SLAVE in self.getAllRoles())

    def addComponent(self, comp):
        """ Attach a component to the interconnect

        Args:
            comp: The component to attach
        """
        if not isinstance(comp, DFInterconnectComponent):
            raise Exception("Component is not of type DFInterconnectComponent")
        comp.project = self.project
        self.components.append(comp)

    def getMasterComponents(self):
        """ Returns a list of only the components with a master role """
        return [x for x in self.components if x.hasMasterRole()]

    def getSlaveComponents(self):
        """ Returns a list of only the components with a slave role """
        return [x for x in self.components if x.hasSlaveRole()]

    def getBidirectionalComponents(self):
        """ Returns a list of only the components with a bidirectional role """
        return [x for x in self.components if x.hasBidirectionalRole()]

    def getRoleComponents(self, role):
        """ Returns only the components of the interconnect matching a particular role.

        Args:
            role: The role to lookup
        """
        if role.strip().upper() == DFConstants.ROLE.MASTER:
            return self.getMasterComponents()
        elif role.strip().upper() == DFConstants.ROLE.SLAVE:
            return self.getSlaveComponents()
        elif role.strip().upper() == DFConstants.ROLE.BIDIR:
            return self.getBidirectionalComponents()
        else:
            raise KeyError("Unknown role when calling getRoleComponents: " + role)

    def hasSimpleComponents(self):
        """ Checks if the interconnect contains any simple components """
        return (False in (x.isComplex() for x in self.components))

    def hasComplexComponents(self):
        """ Check if the interconnect contains any complex components """
        return (True in (x.isComplex() for x in self.components))

    def getMasterWidth(self):
        """ Get the total width of the interconnect as a master """
        if self.role == DFConstants.ROLE.MASTER:
            return sum([(x.getMasterWidth() * x.count) for x in self.components if x.hasMasterRole()])
        elif self.role == DFConstants.ROLE.SLAVE:
            return sum([(x.getSlaveWidth() * x.count) for x in self.components if x.hasSlaveRole()])

    def getSlaveWidth(self):
        """ Get the total width of the interconnect as a slave """
        if self.role == DFConstants.ROLE.MASTER:
            return sum([(x.getSlaveWidth() * x.count) for x in self.components if x.hasSlaveRole()])
        elif self.role == DFConstants.ROLE.SLAVE:
            return sum([(x.getMasterWidth() * x.count) for x in self.components if x.hasMasterRole()])

    def getBidirectionalWidth(self):
        """ Get the total bidirectional width of the interconnect """
        return sum([(x.getBidirectionalWidth() * x.count) for x in self.components if x.hasBidirectionalRole()])

    def getRoleWidth(self, role):
        """ Get the total width of the interconnect in a particular role

        Args:
            role: The role to lookup
        """
        if role.strip().upper() == DFConstants.ROLE.MASTER:
            return self.getMasterWidth()
        elif role.strip().upper() == DFConstants.ROLE.SLAVE:
            return self.getSlaveWidth()
        elif role.strip().upper() == DFConstants.ROLE.BIDIR:
            return self.getBidirectionalWidth()
        else:
            raise KeyError("Unknown role when calling getRoleWidth: " + role)

    def dumpObject(self, project):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        # Get base object
        obj = super(DFInterconnect, self).dumpObject(project)

        # Attach extra details
        obj['role'] = self.role

        # Attach each component
        obj['components'] = [x.dumpObject(project) for x in self.components]

        return obj

    def loadObject(self, obj, project):
        """ Reload this node from passed in object.

        Args:
            obj  : Description of this node
            root : Root object in the tree
        """
        super(DFInterconnect, self).loadObject(obj, project)

        # Reload attributes
        self.role    = obj['role'] if 'role' in obj else None
        self.project = project

        # Sanity checks
        self.checkRole()

        # Reload each component
        for comp in obj['components']:
            new_comp = DFInterconnectComponent().loadObject(comp, project)
            self.addComponent(new_comp)

        return self

class DFInterconnectComponent(DFBase):
    """
    DesignFormat representation for a component within a type of interconnection
    """

    def __init__(
        self, id=None, role=None, description="", type=None, width_or_ref=None,
        count=1, default=0, enum=None, project=None
    ):
        """ Constructor for the interconnect component.

        Args:
            id          : Name of the interconnect component
            role        : Whether the port is a slave or master
            description : Description of the component
            type        : Whether this is simple or complex (references another
                          interconnect)
            width_or_ref: For simple connections, how many bits wide is the
                          component. For complex connections, what DFInterconnect
                          is referenced.
            count       : Number of instances of this component
            def         : For simple components, what is the default state of
                          this signal
            enumlist    : Enumeration of values that the component can carry
            project     : Reference to the top level project (used for lookups)
        """
        super(DFInterconnectComponent, self).__init__(id, description)

        self.role    = role if role != None else DFConstants.ROLE.MASTER
        self.type    = type if type != None else DFConstants.COMPONENT.SIMPLE
        self.ref     = width_or_ref if (self.type == DFConstants.COMPONENT.COMPLEX) else None
        self.count   = count if count != None else 1
        self.project = project

        if self.type == DFConstants.COMPONENT.SIMPLE:
            self.width   = width_or_ref if width_or_ref != None else 0
            self.default = default if default else 0
        else:
            self.width   = 0
            self.default = 0

        if isinstance(self.ref, DFInterconnect):
            self.ref = self.ref.id

        self.enum = convert_to_class(enum if isinstance(enum, dict) else {})

        # Sanity checks
        self.checkRole()
        self.checkType()

    def checkRole(self):
        """ Checks that the configured role is valid (SLAVE or MASTER) """
        if not self.role in DFConstants.ROLE.values():
            raise Exception("Invalid role specified to DFInterconnectComponent: " + self.role)

    def checkType(self):
        """ Check that the component type is allowed. """
        if not self.type in DFConstants.COMPONENT.values():
            raise Exception("Unknown DFInterconnectComponent type: " + self.type)
        elif self.type == DFConstants.COMPONENT.COMPLEX and self.ref == None:
            raise Exception("Complex DFInterconnectComponent without reference!")

    def getAllRoles(self):
        """
        Return all the roles that are offered by this interconnect component,
        takes account of the roles of any reference component.
        """
        if self.type == DFConstants.COMPONENT.SIMPLE:
            return [self.role]
        else:
            ref_roles = self.getReference().getAllRoles()
            roles     = []
            for role in ref_roles:
                # If I'm a slave, then the returned roles need to be reversed
                if self.role == DFConstants.ROLE.SLAVE:
                    if role == DFConstants.ROLE.MASTER:
                        roles.append(DFConstants.ROLE.SLAVE)
                    elif role == DFConstants.ROLE.SLAVE:
                        roles.append(DFConstants.ROLE.MASTER)
                    else:
                        roles.append(role)
                else:
                    roles.append(role)
            return roles

    def hasRole(self, role):
        """ Checks that the interconnect component offers a specified role

        Args:
            role: The role to lookup
        """
        return (role in self.getAllRoles())

    def hasMasterRole(self):
        """ Checks that the interconnect component offers a MASTER role """
        return (DFConstants.ROLE.MASTER in self.getAllRoles())

    def hasSlaveRole(self):
        """ Checks that the interconnect component offers a SLAVE role """
        return (DFConstants.ROLE.SLAVE in self.getAllRoles())

    def hasBidirectionalRole(self):
        """ Checks that the interconnect component offers a BIDIR role """
        return (DFConstants.ROLE.BIDIR in self.getAllRoles())

    def getReference(self):
        """ Convert from the string ID reference to a DFInterconnect """
        return self.project.findNode(self.ref, DFInterconnect)

    def isComplex(self):
        """
        Return whether or not the component is complex (whether it references
        another DFInterconnect).
        """
        return (self.type == DFConstants.COMPONENT.COMPLEX)

    def getMasterWidth(self):
        """ Get the total width of the interconnect component as a master """
        if self.isComplex():
            # If this component has a SLAVE role, invert the sense
            if self.role == DFConstants.ROLE.MASTER:
                return self.getReference().getMasterWidth()
            else:
                return self.getReference().getSlaveWidth()
        elif self.role == DFConstants.ROLE.MASTER:
            return self.width
        else:
            return 0

    def getSlaveWidth(self):
        """ Get the total width of the interconnect component as a slave """
        if self.isComplex():
            # If this component has a SLAVE role, invert the sense
            if self.role == DFConstants.ROLE.MASTER:
                return self.getReference().getSlaveWidth()
            else:
                return self.getReference().getMasterWidth()
        elif self.role == DFConstants.ROLE.SLAVE:
            return self.width
        else:
            return 0

    def getBidirectionalWidth(self):
        """ Get the total bidirectional width of the interconnect """
        if self.isComplex():
            return self.getReference().getBidirectionalWidth()
        elif self.role == DFConstants.ROLE.BIDIR:
            return self.width
        else:
            return 0

    def getRoleWidth(self, role):
        """ Get the total width of the interconnect in a particular role

        Args:
            role: The role to resolve
        """
        if role.upper() == DFConstants.ROLE.MASTER:
            return self.getMasterWidth()
        elif role.upper() == DFConstants.ROLE.SLAVE:
            return self.getSlaveWidth()
        elif role.upper() == DFConstants.ROLE.BIDIR:
            return self.getBidirectionalWidth()
        else:
            raise KeyError("Unknown role when calling getRoleWidth: " + role)

    def addEnumValue(self, key, value, description=None):
        """ Add a new enumerated value for the value of this interconnect (if simple)

        Args:
            key        : Name of the value to enumerate
            value      : Value to name
            description: Human-readable description of the value
        """
        self.enum[key] = DFDefine(key, int(value), description)

    def dumpObject(self, project):
        """ Dump out this node so that it can be reloaded

        Args:
            project: Project definition used to calculate references
        """
        obj = super(DFInterconnectComponent, self).dumpObject(project)

        # Attach extra details
        obj['role']  = self.role
        obj['type']  = self.type
        obj['count'] = self.count
        obj['enum']  = {}
        for key in self.enum:
            obj['enum'][key] = self.enum[key].dumpObject(project)

        if self.width != None:
            obj['width'] = self.width

        if self.default != None:
            obj['default'] = self.default

        # For a referenced DFInterconnect, store just the ID
        if self.type == DFConstants.COMPONENT.COMPLEX and self.ref != None:
            obj['ref'] = self.ref

        return obj

    def loadObject(self, obj, project):
        """ Reload this node from passed in object.

        Args:
            obj : Description of this node
            root: Root object in the tree
        """
        super(DFInterconnectComponent, self).loadObject(obj, project)

        # Reload extra details
        self.role    = obj['role'] if 'role' in obj else None
        self.type    = obj['type'] if 'type' in obj else None
        self.width   = obj['width'] if 'width' in obj else None
        self.count   = obj['count'] if 'count' in obj else 1
        self.default = obj['default'] if 'default' in obj else None
        self.ref     = obj['ref'] if 'ref' in obj else None

        # Reload enumerated values
        self.enum    = convert_to_class({})
        if 'enum' in obj:
            for key in obj['enum']:
                self.enum[key] = DFDefine().loadObject(obj['enum'][key], project)

        # Perform a sanity check
        self.checkRole()
        self.checkType()

        # For chaining
        return self
