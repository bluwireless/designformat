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

## DFShortcutList
#  Provides a list-like object with the ability to access entries by an attribute
#  on the list object. For example, if the list contains DFBlock objects then I
#  can access entries by going 'my_block_list[0]' or 'my_block_list.my_sub_block'
#
class DFShortcutList(list):

    def __init__(self, shortcut_key="id"):
        super(list, self).__init__()
        self.__shortcut_key = shortcut_key

    ## get_entry
    #  Return an entry by its key
    #  @param key - The key to lookup
    #
    def get_entry(self, key):
        entry = [x for x in self if x.__getattribute__(self.__shortcut_key) == key]
        return entry[0] if len(entry) > 0 else None

    ## __getattribute__
    # By overriding __getattribute__ we can expose any entries within the list
    # as first class attributes.
    #
    def __getattribute__(self, key):
        try:
            result = super(list, self).__getattribute__(key)
            return result
        except AttributeError as e:
            entry = self.get_entry(key)
            if entry: return entry
            else: raise e

    ## __getitem__
    #  Override __getitem__ to allow either indexing of the values, or if a string
    #  is provided then reuse __getattribute__ to lookup by key.
    #
    def __getitem__(self, key):
        if isinstance(key, str):
            entry = self.get_entry(key)
            if entry: return entry
            else: return self.__getattribute__(key)
        else:
            return super(DFShortcutList, self).__getitem__(key)

    ## keys
    #  Return a list of the keying variable for each item in the list.
    #
    def keys(self):
        return [x.__getattribute__(self.__shortcut_key) for x in self]

# ------------------------------------------------------------------------------
# Magic dictionary->namespace conversion
# ------------------------------------------------------------------------------

## CLASS_FROM_DICT
#  Magic dictionary to namespace conversion
#
class CLASS_FROM_DICT (object):
    __raw_dict = None

    def __init__ (self, val_dict):
        self.__raw_dict = val_dict

    def keys(self):
        return self.__raw_dict.keys()

    def values(self):
        return self.__raw_dict.values()

    def dict(self):
        return self.__raw_dict

    def __repr__(self):
        return self.__raw_dict.__repr__()

    # Override the [...] subscript accessor to access values
    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        elif key in self.__raw_dict:
            return self.__raw_dict[key]
        else:
            return None

    # Override the [...] subscript accessor to set values
    def __setitem__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        else:
            self.__raw_dict[key] = value

    # Override the '.' attribute accessor to access values
    def __getattribute__(self, key):
        try:
            result = super(CLASS_FROM_DICT, self).__getattribute__(key)
            return result
        except AttributeError as e:
            if key in self.__raw_dict:
                return self.__raw_dict[key]
            else:
                raise e

    # Override the '.' attribute accessor to set values
    def __setattribute__(self, key, value):
        if self.__raw_dict and key in self.__raw_dict.keys():
            raise AttributeError("%s is a protected property" % key)
        else:
            self.__raw_dict[key] = value

    # Allow the object keys to be iterated
    __last_index = 0
    def __iter__(self):
        self.__last_index = 0
        return self

    def __next__(self):
        item = None
        if self.__last_index < len(self.keys()):
            item = list(self.keys())[self.__last_index]
            self.__last_index += 1
        else:
            raise StopIteration()
        return item
    next = __next__

def convert_to_class (map_in):
    digested = {}
    for key in map_in:
        if type(map_in[key]) is dict:
            digested[key] = convert_to_class(map_in[key])
        elif type(map_in[key]) is list:
            digested[key] = [convert_to_class(x) for x in map_in[key]]
        else:
            digested[key] = map_in[key]
    return CLASS_FROM_DICT(digested)

# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------

def isNaN(val):
    try:
        int(val)
        return False
    except ValueError:
        return True

def msFromEpoch(date):
    epoch  = datetime.utcfromtimestamp(0)
    delta  = (date - epoch)
    milli  = int(delta.microseconds / 1000.0)
    milli += delta.seconds * 1000
    milli += delta.days * 24 * 60 * 60
    return milli

def cleanID(the_str):
    return the_str.lower().strip()

## encapsulatedDump
#  Dump out an object of any type, if it is not a primitive type then encapulate
#  it within a dictionary that describes the type.
#  @param obj The object to dump
#
def encapsulatedDump(obj, project):
    from .base import DFBase
    from designformat import DFConstants
    if isinstance(obj, DFBase):
        return {
            DFConstants.ATTRIBUTES.TYPE: type(obj).__name__,
            DFConstants.ATTRIBUTES.DUMP: obj.dumpObject(project)
        }
    elif isinstance(obj, list):
        return [encapsulatedDump(x, project) for x in obj]
    elif isinstance(obj, dict):
        encapsulated = {}
        for key in obj.keys():
            encapsulated[key] = encapsulatedDump(obj[key], project)
        return encapsulated
    else:
        return obj

## encapsulatedLoad
#  Load up an encapsulated object, if it is not a dictionary and contains an
#  encapsulation marker then it is loaded appropriately.
#  @param dump The dumped object to load
#
def encapsulatedLoad(dump, root):
    from designformat import DFConstants
    from .project import subnode_types
    if isinstance(dump, dict):
        if DFConstants.ATTRIBUTES.TYPE in dump:
            d_type = cleanID(dump[DFConstants.ATTRIBUTES.TYPE])
            d_data = dump[DFConstants.ATTRIBUTES.DUMP]
            # Work out what type to reload this node as
            node_type = None
            for item in subnode_types:
                if cleanID(item.__name__) == d_type:
                    node_type = item
                    break
            if not node_type:
                raise Exception("Unable to resolve node type " + node['type'])
            return node_type().loadObject(d_data, root)
        else:
            loaded = {}
            for key in dump.keys():
                loaded[key] = encapsulatedLoad(dump[key], root)
            return loaded
    elif isinstance(dump, list):
        return [encapsulatedLoad(x, root) for x in dump]
    else:
        return dump
