// Copyright (C) 2019 Blu Wireless Ltd.
// All Rights Reserved.
//
// This file is part of DesignFormat.
//
// DesignFormat is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation, either version 3 of the License, or (at your option) any later
// version.
//
// DesignFormat is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License along with
// DesignFormat. If not, see <https://www.gnu.org/licenses/>.
//

const DFConstants = {
    FORMAT: {
        VERSION: '1.3'
    },
    ROLE: {
        SLAVE  : 'SLAVE',
        MASTER : 'MASTER',
        UNKNOWN: 'UNKNOWN',
        BIDIR  : 'BIDIR'
    },
    COMPONENT: {
        SIMPLE : 'SIMPLE',
        COMPLEX: 'COMPLEX'
    },
    DIRECTION: {
        INPUT : 'IN',
        OUTPUT: 'OUT',
        INOUT : 'INOUT'
    },
    ACCESS: {
        RW : 'RW' , // Read-write
        RO : 'RO' , // Read only
        WO : 'WO' , // Write only
        AW : 'AW' , // Active write
        AR : 'AR' , // Active read
        WC : 'WC' , // Write clear
        WS : 'WS' , // Write set
        ARW: 'ARW'  // Active read-write
    },
    ATTRIBUTES: {
        PRINCIPAL: 'PRINCIPAL',
        TYPE     : '__type__',
        DUMP     : '__dump__',
        LEAF_NODE: 'LEAF_NODE'
    }
};

try {
    module.exports.DFConstants = DFConstants;
} catch (e) {
    // Pass
}