# DesignFormat

DesignFormat is the interchange format used by BLADE Core to store the fully elaborated design. It is architected to support complex, hierarchical designs with blocks, ports, interconnections, registers, address maps, commands, and defined values. It can be used to drive templating engines for auto-generating code, viewing tools such as BLADE View for inspecting the design, or debugging tools for interacting with the manufactured design.

This documentation details the data format used to store the design. Different libraries exist for creating, reloading, and interacting with designs and they must conform to the standard format.

The libraries that currently exist are:

 * Javascript - used by BLADE View to load and interact with a design in a web browser;
 * Python - used by BLADE Core to elaborate and store the design.

# Contents
```eval_rst
.. toctree::
   :maxdepth: 3

   sections/storage.md
   sections/schema.md
   sections/tools.md
```

# Indices and tables

```eval_rst
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```
