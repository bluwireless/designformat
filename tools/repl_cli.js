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

const fs   = require('fs');
const path = require('path');

const df_js_dir = path.join(__dirname, '../javascript');
const designformat = require(path.join(df_js_dir, 'designformat.js'));
const DFBlob    = designformat.DFBlob;
const DFProject = designformat.DFProject;

if (process.argv.length != 3) {
    console.log("SYNTAX: test_reload.js /path/to/my/blob/file/myfile.df_blob")
    process.exit(0);
}

let df_root = (new DFProject()).loadObject(
    JSON.parse(fs.readFileSync(process.argv[2]).toString())
);

console.log("Got df_root object with ID '%s' of type %s", df_root.id, df_root.constructor.name);
console.log("Access the object properties using df_root.id etc.");

// Start an interactive shell - 'df_root' is exposed to explore
const repl = require('repl');
const r    = repl.start();
r.context.df_root = df_root;
