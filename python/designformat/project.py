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

from datetime import datetime
import re

from designformat import DFConstants

from .base import DFBase
from .block import DFBlock
from .command import DFCommand
from .command_field import DFCommandField
from .common import cleanID, msFromEpoch
from .connection import DFConnection
from .constant_tie import DFConstantTie
from .define import DFDefine
from .interconnect import DFInterconnect, DFInterconnectComponent
from .port import DFPort
from .register_group import DFRegisterGroup
from .register import DFRegister, DFRegisterField

# Define a list of types that can be stored as nodes in a DFProject, or within
# the attributes bundle of any object.
subnode_types = [
    DFBlock, DFConnection, DFConstantTie, DFInterconnect,
    DFInterconnectComponent, DFPort, DFRegisterGroup, DFRegister,
    DFRegisterField, DFDefine, DFCommand, DFCommandField,
]

class DFProject(DFBase):
    """
    DesignFormat top level project container, can collect nodes of different types
    which can be dumped out as a single entity and re-imported, automatically
    classifying the nodes. Nodes can be marked as 'principal' entities, in order
    to specify a focus for downstream tools.
    """

    def __init__(self, id=None, path=None):
        """ Constructor for the project object.

        Args:
            id  : Name for the project
            path: Path to the source file used to create the project
        """
        super(DFProject, self).__init__(id)

        self.created = datetime.utcnow()
        self.path    = path
        self.version = DFConstants.FORMAT.VERSION

        self.nodes   = {}

    def resolvePath(self, path):
        """
        Return a port or block definition based on a hierarchical path, only
        examines principal DFBlock nodes.

        Args:
            path: The hierarchical path to resolve
        """
        # Get all of the root blocks
        root_blocks = self.getAllPrincipalNodes(desired=DFBlock)

        # Now extract lookup path segments
        parts       = re.compile(r"^([\w\.\-]+)?(\[[\w\-]+\])?$").search(path).groups()
        sections    = parts[0].split('.') if parts[0] != None else []
        port_name   = re.sub(r"([\[\]]+)", "", parts[1]) if parts[1] != None else None

        if len(sections) > 0:
            next_id = sections[0]
            found = [x for x in root_blocks if x.id == next_id.strip()]
            if len(found) != 1:
                raise Exception(
                    "Unable to resolve block - 0 or more than 1 child available for path: "
                    + path + " (@ top level)"
                )
            if (len(sections) > 1) or (port_name != None):
                sub_path = ".".join(sections[1:])
                if port_name != None:
                    sub_path += '[' + port_name + ']'
                return found[0].resolvePath(sub_path)
            else:
                return found[0]

        else:
            raise Exception("Unable to resolve block - no path provided")

        return None

    def addPrincipalNode(self, node):
        """
        Add a new principal node to the project. The principal attribute can be
        applied to as many nodes as required, but should be used to provide a
        focus for downstream tools.

        Args:
            node: Any instance inheriting from DFBase
        """
        if not type(node) in subnode_types:
            raise Exception("Unsupported node type " + type(node).__name__)
        if hasattr(node, 'parent'):
            node.parent = self
        if hasattr(node, 'project'):
            node.project = self
        node.setAttribute(DFConstants.ATTRIBUTES.PRINCIPAL, True)
        self.nodes[node.id] = node

    def addReferenceNode(self, node):
        """
        Add a new non-principal node, this should be used for object types that
        are referenced by another object in the design. For example, it can be
        used to store an interconnect definition, which can then be referred to
        by a port.

        Args:
            node: Any instance inheriting from DFBase
        """
        if not type(node) in subnode_types:
            raise Exception("Unsupported node type " + type(node).__name__)
        if hasattr(node, 'parent'):
            node.parent = self
        if hasattr(node, 'project'):
            node.project = self
        self.nodes[node.id] = node

    def findNode(self, id, type):
        """ Return a node matching a specific ID and type

        Args:
            id  : The ID value to match
            type: The class type to match
        """
        return self.nodes[id] if id in self.nodes and isinstance(self.nodes[id], type) else None

    def getAllPrincipalNodes(self, desired=None):
        """
        Return a list of principal nodes held in the project, optionally
        filtering for a specific type of object.

        Args:
            desired: The optional object type to filter for
        """
        principals = [
            x for x in self.nodes.values() if x.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL)
        ]
        if desired != None:
            return [x for x in principals if isinstance(x, desired)]
        else:
            return principals

    def getInterconnectType(self, intc_id):
        """ Return a DFInterconnect matching a specific identifier.

        Args:
            intc_id: The ID to match
        """
        return self.findNode(intc_id, DFInterconnect)

    def getDefinition(self, key):
        """ Return a DFDefine matching a specific identifier

        Args:
            def: The name of the define to match
        """
        return self.findNode(key, DFDefine)

    def getAllUsedInterconnectionTypes(self):
        """
        Return a unique, ordered list of all of the interconnect types used in
        the design. This is not the same as a list of all interconnect types
        stored in the project, as the project may contain interconnects that are
        not instantiated.
        """
        types = []
        for root in self.getAllPrincipalNodes(desired=DFBlock):
            types += root.getInterconnectTypes()
        unique_types = list(set(types))
        return sorted(unique_types)

    def mergeProject(self, project):
        """ Merge another DFProject with this project

        Args:
            project: The DFProject instance to merge with
        """
        if not isinstance(project, DFProject):
            raise Exception("Cannot merge with type other than DFProject")
        if self.version != project.version:
            raise Exception("Cannot merge with incompatible version " + str(project.version))
        if not self.id:
            self.id = project.id
        if not self.created:
            self.created = project.created
        if not self.path:
            self.path = project.path
        for node in project.nodes.values():
            if node.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL):
                self.addPrincipalNode(node)
            else:
                self.addReferenceNode(node)
        return self

    def dumpObject(self):
        """
        Dump out the project into a primitive dictionary, suitable for reloading
        at a later date. This dictionary can be separately saved to file as JSON.
        """
        # Get our base object
        obj = super(DFProject, self).dumpObject(self)

        # Attach attributes
        epoch = datetime.utcfromtimestamp(0)
        obj['created'] = msFromEpoch(self.created)
        obj['path']    = self.path
        obj['version'] = self.version

        # Attach all nodes
        obj['nodes'] = []
        for node in self.nodes.values():
            obj['nodes'].append({
                DFConstants.ATTRIBUTES.TYPE: cleanID(type(node).__name__),
                DFConstants.ATTRIBUTES.DUMP: node.dumpObject(self)
            })

        # Return the object
        return obj

    def loadObject(self, obj):
        """
        Populate this project with data from a primitive dictionary that has been
        previously dumped. This will construct child nodes, and then populate them
        with relevant details.

        Args:
            obj: The dictionary to reload from
        """
        super(DFProject, self).loadObject(obj, None)

        # Check the versions match up
        if not 'version' in obj or self.version != obj['version']:
            raise Exception("Cannot load DFProject with version " + str(obj['version']))

        # Restore attributes
        if 'created' in obj:
            self.created = datetime.utcfromtimestamp(obj['created'] / 1000.0)

        if 'path' in obj:
            self.path = obj['path']

        if 'nodes' in obj:
            df_intc_id = cleanID(DFInterconnect.__name__)
            df_def_id  = cleanID(DFDefine.__name__)

            # NOTE: Root nodes have the 'root=' attribute to loadObject set to
            #       None, so that they correctly identify that they are roots.

            # First reload interconnects (as blocks may reference them)
            for intc in (x for x in obj['nodes'] if cleanID(x[DFConstants.ATTRIBUTES.TYPE]) == df_intc_id):
                new_intc = DFInterconnect().loadObject(intc[DFConstants.ATTRIBUTES.DUMP], self)
                if new_intc.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL):
                    self.addPrincipalNode(new_intc)
                else:
                    self.addReferenceNode(new_intc)

            # Second reload defines (as blocks may reference them)
            for define in (x for x in obj['nodes'] if cleanID(x[DFConstants.ATTRIBUTES.TYPE]) == df_def_id):
                new_def = DFDefine().loadObject(define[DFConstants.ATTRIBUTES.DUMP], None)
                if new_def.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL):
                    self.addPrincipalNode(new_def)
                else:
                    self.addReferenceNode(new_def)

            # Now reload all other nodes
            for node in obj['nodes']:
                # Skip DFDefine or DFInterconnect as already handled
                if cleanID(node[DFConstants.ATTRIBUTES.TYPE]) in [df_intc_id, df_def_id]:
                    continue
                # Identify and construct the node automatically
                node_type = None
                for item in subnode_types:
                    if cleanID(item.__name__) == cleanID(node[DFConstants.ATTRIBUTES.TYPE]):
                        node_type = item
                        break
                if not node_type:
                    raise Exception("Unable to resolve node type " + node[DFConstants.ATTRIBUTES.TYPE])
                new_node = node_type().loadObject(node[DFConstants.ATTRIBUTES.DUMP], None)
                # Associate the node as principal if required
                if new_node.getAttribute(DFConstants.ATTRIBUTES.PRINCIPAL):
                    self.addPrincipalNode(new_node)
                else:
                    self.addReferenceNode(new_node)

        return self
