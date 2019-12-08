#!/usr/bin/env python

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

import argparse
import json
import os
import sys

# Work out the path to the DesignFormat area
script_dir = os.path.dirname(os.path.realpath(__file__))
df_py_dir  = os.path.abspath(os.path.join(script_dir, '../python'))

# Allow override if DF is on the path
if 'DESIGN_FORMAT_DIR' in os.environ:
    df_py_dir = os.path.join(os.environ['DESIGN_FORMAT_DIR'], 'python')

# Add DesignFormat to the path
sys.path.append(df_py_dir)

# Import DesignFormat
from designformat import DFProject, DFBlock, DFPort, DFInterconnect, DFConstants
from designformat import DFRegisterGroup

## get_args
#  Define and parse command line arguments
#
def get_args():
    parser = argparse.ArgumentParser(description='Tool for removing unnecessary sections of a DesignFormat blob')
    # Options to control cleaner
    parser.add_argument("--strip-descriptions",    action="store_true", default=False, help="Remove all description fields")
    parser.add_argument("--strip-attributes",      action="store_true", default=False, help="Remove all attribute fields")
    parser.add_argument("--preserve-tree",         action="append",     default=[],    help="Preserve the tree down to a specific node")
    parser.add_argument("--preserve-connectivity", action="append",     default=[],    help="Preserve the entire connectivity tree from a specific port")
    # Options for the blob
    parser.add_argument("input",  help="Path to the blob file to load as input")
    parser.add_argument("output", help="Output path for the cleaned blob file")
    # Parse arguments
    return parser.parse_args()

if __name__ == "__main__":
    # Get the arguments passed to the script
    args = get_args()
    # Load the blob
    print(f"Loading blob {args.input}")
    df_root = None
    with open(args.input, 'r') as fh:
        df_root = DFProject().loadObject(json.load(fh))
    if not df_root:
        print(f"Failed to open blob from path: {args.input}")
        sys.exit(1)
    print(f"Blob loaded: {df_root.id}")

    # Keep track of all of the nodes we want to preserve
    to_preserve = []

    # For every preserved tree, attempt to resolve it
    print("Preserving tree")
    for path in args.preserve_tree:
        # Resolve this path to a block
        node = df_root.getAllPrincipalNodes()[0].resolvePath(path)
        assert isinstance(node, DFBlock)
        # Add every unique block into the preserve list
        while isinstance(node, DFBlock) and node.parent != None:
            if node not in to_preserve:
                to_preserve.append(node)
            node = node.parent

    # For every preserved port attempt to resolve it
    print("Preserving connectivity")
    for path in args.preserve_connectivity:
        # Resolve this path to a port
        node = df_root.getAllPrincipalNodes()[0].resolvePath(path)
        assert isinstance(node, DFPort)
        def chase_port(port, index):
            # Add this port to the preserve list
            if not port in to_preserve:
                to_preserve.append(port)
            # Add the tree of blocks to the preserve list
            block = port.block
            while isinstance(block, DFBlock) and block.parent != None:
                if block not in to_preserve:
                    to_preserve.append(block)
                block = block.parent
            # Chase any direct connectivity
            connections = port.chaseConnection(index)
            for path in connections:
                for point in path:
                    if not point[0] in to_preserve:
                        chase_port(point[0], point[1])
            # Chase any address map connectivity
            if isinstance(port.block, DFBlock) and port.block.address_map and port.block.address_map.getInitiator(port, index):
                init    = port.block.address_map.getInitiator(port, index)
                targets = port.block.address_map.getTargetsForInitiator(init)
                for target in targets:
                    if not target.port in to_preserve:
                        to_preserve.append(target.port)
                    connections = target.port.chaseConnection(target.port_index)
                    for path in connections:
                        for point in path:
                            if not point[0] in to_preserve:
                                chase_port(point[0], point[1])
        for i in range(node.count): chase_port(node, i)

    # Declare a function for stripping attributes
    def strip_attributes(obj):
        attr_keys = list(obj.attributes.keys())[:]
        for key in attr_keys:
            if not key in DFConstants.ATTRIBUTES.keys():
                del obj.attributes[key]

    # Now run through every block in the design
    def chase_block(block):
        # Loop through my ports, see if any of them should be removed
        inputs = block.ports.input[:]
        for port in inputs:
            if not port in to_preserve:
                block.ports.input.remove(port)
        outputs = block.ports.output[:]
        for port in outputs:
            if not port in to_preserve:
                block.ports.output.remove(port)
        inouts = block.ports.inout[:]
        for port in inouts:
            if not port in to_preserve:
                block.ports.inout.remove(port)
        # Should I blank out my description?
        if args.strip_descriptions: block.description = None
        # Should I blank out any non-essential attributes?
        if args.strip_attributes: strip_attributes(block)
        # Loop through my children, see if they should be preserved
        children = block.children[:]
        for child in children:
            if not child in to_preserve:
                block.children.remove(child)
            else:
                chase_block(child)
        # Loop through my connections to see if the end points are preserved
        connections = block.connections[:]
        for conn in connections:
            if not conn.start_port in to_preserve or not conn.end_port in to_preserve:
                block.connections.remove(conn)
        # Loop through my registers and apply any stripping
        for group in block.registers:
            if args.strip_descriptions: group.description = None
            if args.strip_attributes: strip_attributes(group)
            if isinstance(group, DFRegisterGroup):
                for reg in group.registers:
                    if args.strip_descriptions: reg.description = None
                    if args.strip_attributes: strip_attributes(reg)
                    for field in reg.fields:
                        if args.strip_descriptions: field.description = None
                        if args.strip_attributes: strip_attributes(field)
        # Loop through my address map and remove any initiators, targets, or
        # constraints that haven't been preserved
        if block.address_map:
            inits = block.address_map.initiators[:]
            for init in inits:
                if not init.port in to_preserve:
                    block.address_map.initiators.remove(init)
            tgts = block.address_map.targets[:]
            for tgt in tgts:
                if not tgt.port in to_preserve:
                    block.address_map.targets.remove(tgt)
            cons = list(block.address_map.constraints.keys())
            for con_key in cons:
                con = block.address_map.constraints[con_key]
                if not con.initiator.port in to_preserve or not con.target.port in to_preserve:
                    del block.address_map.constraints[con_key]

    print("Starting to clean design")
    chase_block(df_root.getAllPrincipalNodes()[0])

    # Clean up any unnecessary interconnects
    print("Removing unnecessary interconnects")
    req_intcs = df_root.getAllPrincipalNodes()[0].getInterconnectTypes()
    all_intcs = [x for x in df_root.nodes.keys() if isinstance(df_root.nodes[x], DFInterconnect)]
    for intc_key in all_intcs:
        intc = df_root.nodes[intc_key]
        if intc not in req_intcs:
            del df_root.nodes[intc_key]
        else:
            if args.strip_descriptions: intc.description = None
            if args.strip_attributes: strip_attributes(intc)

    # Now we supposedly have a clean design, save it out to file
    print("Dumping out the design")
    json_dump = json.dumps(df_root.dumpObject())
    with open(args.output, 'w') as fh:
        fh.write(json_dump)
