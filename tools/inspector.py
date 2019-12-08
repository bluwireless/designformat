#!/usr/bin/env python3.6

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
from designformat import DFProject, DFBlock, DFInterconnect

## get_args
#  Handle command line arguments to the inspection tool
#  @returns The argument namespace returned by argparse
#
def get_args():
    # Parse in command line arguments
    parser = argparse.ArgumentParser(
        description="Checks for presence of a particular attribute on the principal object"
    )
    # - Attribute comparisons
    parser.add_argument("--test",     "-c",                                     help="The argument to test, if no expected value is specified then tests value is present & true")
    parser.add_argument("--present",  "-p", action="append",     default=[],    help="Test to see if all listed attributes are present (AND)")
    parser.add_argument("--absent",   "-a", action="append",     default=[],    help="Test to see if all listed attributes are absent (AND)")
    parser.add_argument("--present-or",     action="store_true", default=False, help="Changes behaviour to see if any listed attributes are present (OR)")
    parser.add_argument("--absent-or",      action="store_true", default=False, help="Changes behaviour to see if any listed attributes are absent (OR)")
    parser.add_argument("--false",    "-n", action="store_true", default=False, help="Test that the specified option is either absent or false.")
    parser.add_argument("--value",    "-v",                                     help="A specific value to test for (number, string, etc).")
    parser.add_argument("--if-true",  "-t",                      default=1,     help="The value to print if the test result is true.")
    parser.add_argument("--if-false", "-f",                                     help="The value to print if the test result is false.")
    parser.add_argument("--exitcode", "-x", action="store_true", default=False, help="Modify the exitcode based on the result of the test - normally returns 0.")
    # - Node listing
    parser.add_argument("--interconnects",     "-i", action="store_true", default=False, help="List all of the DFInterconnects available in the blob")
    parser.add_argument("--top-interconnects",       action="store_true", default=False, help="List only the DFInterconnects of the top level block")
    parser.add_argument("--blocks",            "-b", action="store_true", default=False, help="List all of the principal DFBlocks available in the blob")
    parser.add_argument("--address-map",       "-m",                                     help="Print out an address map from a specified entry point")
    parser.add_argument("--spaced",            "-s", action="store_true", default=False, help="Use space separation in lists rather than newlines")
    # - Blob handling
    parser.add_argument("blob", help="Path to the DFBlob file to test for an attribute")
    return parser.parse_args()

## result_pass
#  Display a pass result and/or exit with exitcode
#  @param true_val     The value to print if the comparison succeeds
#  @param use_exitcode The exitcode to exit with (if != None)
#  @param use_print    Whether to print out a message
#
def result_pass(true_val, use_exitcode=None, use_print=True):
    if use_print and true_val != None and (not isinstance(true_val, str) or len(true_val) > 0):
        print(true_val)
    if use_exitcode != None:
        sys.exit(0)
    return True

## result_fail
#  Display a fail result and/or exit with exitcode
#  @param true_val     The value to print if the comparison fails
#  @param use_exitcode The exitcode to exit with (if != None)
#  @param use_print    Whether to print out a message
#
def result_fail(false_val, use_exitcode=None, use_print=True):
    if use_print and false_val != None and (not isinstance(false_val, str) or len(false_val) > 0):
        print(false_val)
    if use_exitcode != None:
        sys.exit(1)
    return False

## run_attribute_test
#  Perform the requested comparison, and print or exit depending on configuration.
#  @param node         The DF node to examine
#  @param key          The attribute to examine
#  @param is_false     Check for the comparison '!=' - returns true if comparison fails
#  @param value        The specific value to check for
#  @param true_val     Value to print if the comparison succeeds
#  @param false_val    Value to print if the comparison fails
#  @param use_exitcode Use exitcodes to flag comparison pass/fail
#
def run_attribute_test(node, key, is_false=False, value=None, true_val=None, false_val=None, use_exitcode=False, use_print=True):
    # Perform the test
    test_val = node.getAttribute(key)
    result   = ((value == None and test_val) or (value != None and test_val == value))
    # Cope with inversion of the test condition
    if (result ^ is_false):
        return result_pass(true_val, 0 if use_exitcode else None, use_print)
    else:
        return result_fail(false_val, 1 if use_exitcode else None, use_print)

## main
#  Parse command line arguments, then respond accordingly.
#
def main():
    # Get arguments
    args = get_args()

    # Read in the DFBlob file
    if not os.path.isfile(args.blob):
        print(f"ERROR: Could not read file at path: {args.blob}")
        sys.exit(255)

    df_root = None
    with open(args.blob, 'r') as fh:
        df_root = DFProject().loadObject(json.load(fh))

    # Identify the first principal node
    try:
        principal = [x for x in df_root.getAllPrincipalNodes() if isinstance(x, DFBlock)][0]
    except:
        print("ERROR: Failed to locate a principal node")
        sys.exit(1)

    # Dump a list of DFInterconnect types
    if args.top_interconnects or args.interconnects:
        intcs = []
        # Dump interconnects only used in the top-level
        if args.top_interconnects:
            block = df_root.getAllPrincipalNodes()[0]
            if not isinstance(block, DFBlock):
                print("ERROR: Failed to locate a principal node")
                sys.exit(1)
            intcs += block.getInterconnectTypes(depth=0)
        # Dump all interconnects included in the DFProject (not just top-level)
        elif args.interconnects:
            intcs = [x for x in df_root.nodes.values() if isinstance(x, DFInterconnect)]
        # If test mode is enabled, filter the interconnects
        if args.test:
            intcs = [x for x in intcs if run_attribute_test(
                x, args.test, args.false, args.value, None, None,
                use_exitcode=False, use_print=False
            )]
        # Chase each interconnect so that we also have all of it's components
        def chase_intc(intc):
            for comp in (x for x in intc.components if x.isComplex()):
                comp_intc = comp.getReference()
                if not comp_intc in intcs:
                    intcs.append(comp_intc)
                chase_intc(comp_intc)
        for intc in intcs[:]:
            chase_intc(intc)
        # Print out all of the interconnects using spaces or newlines
        print((" " if args.spaced else "\n").join([x.id for x in intcs]))

    # Dump the list of root DFBlocks
    elif args.blocks:
        blocks = [x for x in df_root.nodes.values() if isinstance(x, DFBlock)]
        print((" " if args.spaced else "\n").join([x.id for x in blocks]))

    # Dump an address map from a named entry-point
    elif args.address_map:
        entrypoint = df_root.getAllPrincipalNodes()[0].resolvePath(args.address_map)
        if not entrypoint:
            print("ERROR: Failed to identify entrypoint: " + entrypoint)
            sys.exit(1)
        # Declare a function to recursively find all address maps
        def find_maps(port, index=0, maps=None, depth=0):
            maps   = [] if not maps else maps
            prefix = " | ".join(["" for x in range(depth-1)])
            # If this is a newly encountered address map, look through all the targets
            if port.block.address_map and port.block.address_map not in maps:
                maps.append(port.block.address_map)
                # Check this port is actually accessible
                rel_addr = entrypoint.getRelativeAddress(port, remote_index=index)
                if rel_addr == None: return
                # Print out this address
                print(f"{prefix}{' |- ' if (depth > 0) else ''}{port.block.hierarchicalPath()}: {hex(rel_addr)}")
                for target in port.block.address_map.targets:
                    find_maps(target.port, index=target.port_index, maps=maps, depth=(depth+1))
            # Else, if we have a output, chase it
            elif len(port.getOutboundConnections()) > 0:
                pathways = port.chaseConnection(index=index)
                for path in pathways:
                    # Look at the last entry in the path (which is the endpoint)
                    find_maps(path[-1][0], index=path[-1][1], maps=maps, depth=depth)
            # Else this is a termination
            else:
                # Check this port is actually accessible
                rel_addr = entrypoint.getRelativeAddress(port, remote_index=index)
                if rel_addr == None: return
                # Print out this address
                print(f"{prefix}{' |- ' if (depth > 0) else ''}{port.hierarchicalPath()}[{index}]: {hex(rel_addr)}")


        find_maps(entrypoint)

    # If 'present' or 'absent' lists were provided
    elif len(args.present) > 0 or len(args.absent) > 0:
        missing = [x for x in args.present if principal.getAttribute(x) == None]
        extra   = [x for x in args.absent  if principal.getAttribute(x) != None]
        # Allow either AND or OR operations for a list of 'present' tags
        present_result = (
            (len(missing) == 0                                    ) or
            (len(missing) <  len(args.present) and args.present_or)
        )
        # Allow either AND or OR operations for a list of 'absent' tags
        absent_result = (
            (len(extra) == 0                                  ) or
            (len(extra) <  len(args.absent) and args.absent_or)
        )
        if (present_result and absent_result) ^ args.false:
            result_pass(args.if_true, 0 if args.exitcode else None, True)
        else:
            result_fail(args.if_false, 1 if args.exitcode else None, True)
    # If attribute test mode enabled, then run an attribute comparison
    elif args.test:
        run_attribute_test(
            principal, args.test, args.false, args.value, args.if_true,
            args.if_false, args.exitcode
        )

if __name__ == "__main__":
    main()
