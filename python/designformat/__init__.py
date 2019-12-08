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

from .common import convert_to_class

# ------------------------------------------------------------------------------
# Declare DesignFormat constants
# ------------------------------------------------------------------------------
DFConstants = convert_to_class({
    'FORMAT': {
        'VERSION': '1.3'
    },
    'ROLE': {
        'SLAVE'  : 'SLAVE',
        'MASTER' : 'MASTER',
        'UNKNOWN': 'UNKNOWN',
        'BIDIR'  : 'BIDIR',
    },
    'COMPONENT': {
        'SIMPLE' : 'SIMPLE',
        'COMPLEX': 'COMPLEX',
    },
    'DIRECTION': {
        'INPUT' : 'IN',
        'OUTPUT': 'OUT',
        'INOUT' : 'INOUT',
    },
    'ACCESS': {
        'NONE':   '' , # No access
        'RW'  : 'RW' , # Read-write
        'RO'  : 'RO' , # Read only
        'WO'  : 'WO' , # Write only
        'AW'  : 'AW' , # Active write
        'AR'  : 'AR' , # Active read
        'WC'  : 'WC' , # Write clear
        'WS'  : 'WS' , # Write set
        'ARW' : 'ARW', # Active read-write
    },
    'ATTRIBUTES': {
        'PRINCIPAL': 'PRINCIPAL',
        'TYPE'     : '__type__',
        'DUMP'     : '__dump__',
        'LEAF_NODE': 'LEAF_NODE'
    },
})

# ------------------------------------------------------------------------------
# Import all of the components
# ------------------------------------------------------------------------------
from .address_map import DFAddressMapInitiator, DFAddressMapTarget, DFAddressMap
from .base import DFBase
from .block import DFBlock
from .command import DFCommand
from .command_field import DFCommandField
from .connection import DFConnection
from .constant_tie import DFConstantTie
from .define import DFDefine
from .interconnect import DFInterconnect, DFInterconnectComponent
from .port import DFPort
from .project import DFProject
from .register_group import DFRegisterGroup
from .register import DFRegister, DFRegisterField
