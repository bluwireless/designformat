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

// Provide module exports
try {
    module.exports.DFAddressMap            = require('./address_map.js').DFAddressMap;
    module.exports.DFAddressMapInitiator   = require('./address_map.js').DFAddressMapInitiator;
    module.exports.DFAddressMapTarget      = require('./address_map.js').DFAddressMapTarget;
    module.exports.DFBase                  = require('./base.js').DFBase;
    module.exports.DFBlock                 = require('./block.js').DFBlock;
    module.exports.DFCommand               = require('./command.js').DFCommand;
    module.exports.DFCommandField          = require('./command_field.js').DFCommandField;
    module.exports.DFConnection            = require('./connection.js').DFConnection;
    module.exports.DFConstants             = require('./constants.js').DFConstants;
    module.exports.DFConstantTie           = require('./constant_tie.js').DFConstantTie;
    module.exports.DFDefine                = require('./define.js').DFDefine;
    module.exports.DFInterconnect          = require('./interconnect.js').DFInterconnect;
    module.exports.DFInterconnectComponent = require('./interconnect.js').DFInterconnectComponent;
    module.exports.DFPort                  = require('./port.js').DFPort;
    module.exports.DFProject               = require('./project.js').DFProject;
    module.exports.DFRegister              = require('./register.js').DFRegister;
    module.exports.DFRegisterField         = require('./register.js').DFRegisterField;
    module.exports.DFRegisterGroup         = require('./register_group.js').DFRegisterGroup;
} catch (e) {
    console.error('Error occurred constructing DF models:', e);
}
