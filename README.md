![BLADE](https://raw.githubusercontent.com/bluwireless/blade/master/documentation/source/_static/images/BLADE.png)

---

<p align="center">
    A Cross-Language Interchange Format for Hardware Description Based on JSON
    <br>
    <a href="https://designformat.readthedocs.io/en/latest">Documentation</a>
    &bull;
    <a href="https://pypi.org/project/designformat/">PyPI Package</a>
</p>

---

<p align="center">
    <img src="https://readthedocs.org/projects/designformat/badge/?version=latest" />
</p>

# DesignFormat
DesignFormat is a file format for storing fully expanded, hiearchical design data. It is uses JSON as a storage format as many languages offer native and relatively performant JSON parsers - making it easy to share data between different environments. DesignFormat is intended to be used as the interchange format between different tools, eliminating the need for multiple tools to parse the source data - which can introduce inconsistencies and errors.

## Types
 * DFBase: Base class, provides every other object with an ID, a description, and a map of arbitrary attributes (for passing options).
 * DFDefine: Defines a named constant value related to the design.
 * DFBlob: Can carry an arbitrary number of DesignFormat nodes of different types.
 * DFProject: The root node exported to file. Provides interconnect and constant definitions, and holds the root blocks defined in the project.
 * DFInterconnect & DFInterconnectComponent: Represents a connection type, comprised of components which can either be complex (other DFInterconnect instances) or simple (wire connections with a specified width and direction).
 * DFBlock: Represents a block in the design hierarchy with ports, connections, and child blocks. It can also hold a register interface definition.
 * DFPort: Represents a port on a block, with a specified direction (input or output) and a type (referencing a DFInterconnect type).
 * DFConstantTie: A point that can be connected to an input port to hold it at a constant value.
 * DFConnection: Defines a connection between two points (either two ports, or a contant tie and a port).
 * DFRegister: Represents a register with an address, access modes, and a set of fields.
 * DFRegisterField: Represents a single field within the register with a name, a width and a reset value.

## Using the Javascript library

### Loading a DFProject
```javascript
const df_models = require('./javascript/df_models.js');
const fs        = require('fs');

let data    = JSON.parse(fs.readFileSync('./my_file.df_project').toString());
let project = (new df_models.DFProject()).loadObject(data);
```

### Loading a DFBlob
```javascript
const df_models = require('./javascript/df_models.js');
const fs        = require('fs');

let data    = JSON.parse(fs.readFileSync('./my_file.df_blob').toString());
let project = (new df_models.DFBlob()).loadObject(data);
```

## Using the Python library

### Loading a DFProject
```python
from df_models import DFProject
import json

project = None
with open('./my_file.df_project', 'r') as fh:
    project = DFProject().loadObject(json.load(fh))
```

### Loading a DFBlob
```python
from df_models import DFBlob
import json

project = None
with open('./my_file.df_blob', 'r') as fh:
    project = DFBlob().loadObject(json.load(fh))
```

## Generating Documentation
### System Requirements
The following dependencies are not mandatory, but are required for building the documentation:
 * [Sphinx](https://pypi.org/project/Sphinx/) - Powerful documentation generation tool
 * [Recommonmark](https://pypi.org/project/recommonmark/) - Markdown convertor for Sphinx
 * [Sphinx Markdown Tables](https://pypi.org/project/sphinx-markdown-tables/) - Markdown table convertor for Sphinx
 * [Sphinx RTD Theme](https://pypi.org/project/sphinx-rtd-theme/) - Read The Docs theme for Sphinx HTML
 * [Sphinx JS](https://pypi.org/project/sphinx-js/) - Integrates JSDoc output into Sphinx
 * [JSDoc](https://www.npmjs.com/package/jsdoc) - Javascript documentation generator

```bash
$> pip install sphinx recommonmark sphinx-markdown-tables sphinx-rtd-theme sphinx-js
$> npm install -g jsdoc
```

### Building the Documentation
To build the documentation, open this directory in a terminal and execute:

```bash
$> make build
```

HTML documentation will be generated under `documentation/build/html`.
