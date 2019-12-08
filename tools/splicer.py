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
from designformat import DFProject, DFBlock, DFRegisterGroup
from designformat.common import DFShortcutList

class SpliceError(Exception):
    pass

## get_args
#  Handle command line arguments to the inspection tool
#  @returns The argument namespace returned by argparse
#
def get_args():
    # Parse in command line arguments
    parser = argparse.ArgumentParser(
        description="Splices together different DesignFormat databases"
    )
    # - Attribute comparisons
    parser.add_argument("--registers", help="Append a register database - in the form <BLOCK>=<DATABASE>(+<OFFSET>)", default=[], action="append")
    # - Blob handling
    parser.add_argument("input",  help="The input path for the base-line database to load")
    parser.add_argument("output", help="The output path to dump the final database")
    return parser.parse_args()

def load_project(path):
    if not os.path.isfile(path):
        raise SpliceError(f"Could not read file at path: {path}")
    df_root = None
    with open(path, 'r') as fh:
        df_root = DFProject().loadObject(json.load(fh))
    return df_root

def load_tops(path, f_type=DFBlock):
    df_root = load_project(path)
    principals = [x for x in df_root.getAllPrincipalNodes() if isinstance(x, f_type)]
    if len(principals) == 0:
        raise SpliceError(f"Could not identify principal node of type {f_type.__name__} in {path}")
    return principals

## main
#  Parse command line arguments, then respond accordingly.
#
def main():
    # Get arguments
    args = get_args()

    # Load the base-line blob
    print("# Loading base-line blob")
    project = load_project(args.input)
    base    = [x for x in project.getAllPrincipalNodes() if isinstance(x, DFBlock)]
    if len(base) != 1:
        raise SpliceError(f"Should be exactly one top-level module in the base-line (found {len(base)})")
        sys.exit(3)
    base = base[0]

    # Load in each register database
    print(f"# Loading {len(args.registers)} register databases")
    registers = {}
    for entry in args.registers:
        kv_parts = entry.split("=")
        ro_parts = kv_parts[1].split("+")
        registers[kv_parts[0].strip()] = (
            load_tops(ro_parts[0].strip(), f_type=DFRegisterGroup),
            int(ro_parts[1], 0) if len(ro_parts) > 1 else 0
        )

    # Fuse register databases into the base-line
    for key in registers:
        print(f"# Merging register databases into {key}")
        block = base.resolvePath(key)
        if not block:
            raise SpliceError(f"Failed to resolve block at path {key}")
        if block.registers and len(block.registers) > 0:
            print(f"WARNING: Block {block.id} already has some registers - merging anyway")
        # Ensure we have storage for the registers
        if not block.registers: block.registers = DFShortcutList()
        # Append them
        for reg_grp in registers[key][0]:
            print(f"# - Appending register group {reg_grp.id} with offset {hex(registers[key][1])}")
            block.registers.append(reg_grp)
            reg_grp.offset += registers[key][1]

    # Write out the final database
    print("# Writing final database to file")
    with open(args.output, 'w') as fh:
        json_dump = json.dumps(project.dumpObject())
        fh.write(json_dump)


if __name__ == "__main__":
    try:
        main()
    except SpliceError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
