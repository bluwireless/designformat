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

import inspect

from .common import DFShortcutList, encapsulatedLoad, encapsulatedDump
from .common import CLASS_FROM_DICT

class DFBase(object):
    """ Base class of DesignFormat """

    def __init__(self, id, description=None):
        """ Initialisation for DFBase

        Args:
            id         : Identifier for the object
            description: Human-readable description for the object
        """
        self.id          = id
        self.attributes  = {}
        self.description = description

    def dumpObject(self, project):
        """ Serialise the object into a dictionary

        Args:
            project: Reference to the root DFProject for resolving values

        Returns:
            dict: Serialised dictionary
        """
        obj = {}

        # Attach the basic object properties
        obj['id'] = self.id

        if self.description and len(self.description.strip()) > 0:
            obj['description'] = self.description

        # Attach attributes
        if len(self.attributes.keys()) > 0:
            obj['attributes'] = {}
            for attr in self.attributes:
                obj['attributes'][attr] = encapsulatedDump(self.attributes[attr], project)

        return obj

    def loadObject(self, obj, root):
        """ Load-up a serialised object from a dictionary

        Args:
            obj : The serialised dictionary
            root: Reference to the root node for resolving references

        Returns:
            DFBase: Returns this instance of DFBase after population (for chaining)
        """
        self.id = obj['id']

        if 'description' in obj:
            self.description = obj['description']

        if 'attributes' in obj:
            for key in obj['attributes']:
                value = obj['attributes'][key]
                self.attributes[key] = encapsulatedLoad(obj['attributes'][key], root)

        return self

    def setAttribute(self, key, value):
        """ Set the value of a particular attribute

        Args:
            key  : Key to set
            value: Value to associate (any serialisable item, including a class
                   instance that inherits from DFBase)
        """
        self.attributes[key] = value

    def removeAttribute(self, key):
        """ Remove a particular attribute

        Args:
            key: Remove associated value for key
        """
        del self.attributes[key]

    def getAttribute(self, key):
        """ Return the value matching the provided key.

        Args:
            key: The key to lookup

        Returns:
            any: The item that was associated
        """
        return self.attributes[key] if key in self.attributes else None

    def __str__(self):
        """ Create a representation of this block

        Returns:
            str: Readable representation of this block
         """
        return self.__repr__()

    def __repr__(self, depth=0, max_depth=2, max_list=2):
        """
        Generate an automatic representation of this block when it is converted
        to a string.

        Args:
            depth    : The current depth we're printing at
            max_depth: The maximum depth we should print to
            max_list : The maximum number of array or dictionary entries to print

        Returns:
            str: Readable representation of this block
        """
        members = [
            x for x in inspect.getmembers(self)
            if not '__' in x[0] and type(x[1]) in [
                DFShortcutList, CLASS_FROM_DICT,
                list, dict, map,
                str, int, float, bool
            ]
        ]
        out = [type(self).__name__ + " => " + "{"]
        for item in members:
            if type(item[1]) in [str, int, float, bool]:
                out.append("  %s: %s" % (item[0], str(item[1])))
            elif isinstance(item[1], list) and len(item[1]) > 0:
                out.append("  %s: [" % item[0])
                for i in range(len(item[1])):
                    entry = item[1][i]
                    if i >= max_list or depth >= max_depth:
                        out.append("    ...")
                        break
                    elif isinstance(entry, DFBase):
                        out.append("    "+"    ".join(entry.__repr__(
                            depth=(depth+1), max_depth=max_depth
                        ).splitlines(True)))
                    else:
                        out.append("    "+"    ".join(entry.__repr__().splitlines(True)))
                out.append("  ]")
            elif type(item[1]) in [map, dict, CLASS_FROM_DICT] and len(item[1].keys()) > 0:
                out.append("  %s: {" % item[0])
                for i in range(len(item[1].keys())):
                    key = list(item[1].keys())[i]
                    out.append("    %s:" % key)
                    if i >= max_list or depth >= max_depth:
                        out.append("    ...")
                        break
                    elif isinstance(item[1][key], DFBase):
                        out.append("      "+"      ".join(item[1][key].__repr__(
                            depth=(depth+1), max_depth=max_depth
                        ).splitlines(True)))
                    else:
                        out.append("      "+"      ".join(item[1][key].__repr__().splitlines(True)))
                out.append("  }")
        out.append("}")
        return "\n".join(out)
