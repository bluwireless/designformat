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
from designformat import DFProject

# Check that enough arguments have been passed
if len(sys.argv) != 2 or sys.argv[1] == '-h':
    print("usage: repl_cli.py [-h] blob_path")
    print("repl_cli.py: error: the following arguments are required: blob_path")
    sys.exit(0)

# Get hold of the root node
df_root = None
with open(sys.argv[1], 'r') as fh:
    df_root = DFProject().loadObject(json.load(fh))
print("Got df_root object with ID '" + df_root.id + "' of type " + type(df_root).__name__)
print("Access the object properties using df_root.id etc.")

# Expose all principal nodes from the root node
print("Exposing principal nodes:")
for node in df_root.getAllPrincipalNodes():
    node_var = node.id.replace(" ","_")
    print(" - " + node_var  + ": " + node.id + " of type " + type(node).__name__)
    globals()[node_var] = node

# Start up the REPL
import pdb; pdb.set_trace()
