# Tools

DesignFormat comes with a collection of small tools for accessing and manipulating dumped design hierarchies. They also act as basic example of how you can load, manipulate, and dump DesignFormat objects.

## REPL Command Line Interface

Two REPL (Read-Evaluate-Print-Loop) clients are shipped in the 'tools' folder - one demonstrating the Python library, and the other the Javascript library. They can both be started in a similiar fashion:

```bash
# For Python
$> python3.6 tools/repl_cli.py /path/to/my/design.df_blob
Got df_root object with ID 'my_design' of type DFProject
Access the object properties using df_root.id etc.
--Return--
> /home/myuser/design_format/tools/repl_cli.py(33)<module>()->None
-> import pdb; pdb.set_trace()
(Pdb) ...
```

```bash
# For Javascript
$> node tools/repl_cli.js /path/to/my/design.df_blob
Got df_root object with ID 'my_design' of type DFProject
Access the object properties using df_root.id etc.
> ...
```

Both options give you full access to the DFProject, with the ability to inspect any attribute and call any function - meaning that they're a really neat way to poke around a design from the command line.

To access the top-level of your design, assuming that you have nominated a DFBlock as a principal node, execute:

```bash
# For Python
(Pdb) top = df_root.getAllPrincipalNodes()[0]
(Pdb) print(top.id)
my_top_level

# For Javascript
> top = df_root.getAllPrincipalNodes()[0];
> console.log(top.id)
my_top_level
```

You can refer to the [API's documented for each node's schema](./schema) to work out what functions are available, and how they should be called.

## Inspector
This tool allows you to query basic properties of the DFProject, as well as test for specific attributes of the first principal node. The inspector is written in Python. It can be very useful for driving flows, especially where you need to generate multiple outputs from one project - for example autogenerating code for every stored interconnect.

In the example below, the 'IMP' attribute is being tested to see if its equal to `yes`. If the comparison passes then "It's true" is printed, but if the comparison fails then "It's false" is printed. Additionally using the `-x` option enables a non-zero exitcode to be returned if the test fails.

```bash
$> python3.6 tools/inspector.py /path/to/my/design.df_blob --test IMP --value "yes" --if-true "It's true" --if-false "It's false" -x
```

You can also use it to dump a list of interconnects in the design:

```bash
$> python3.6 tools/inspector.py /path/to/my/design.df_blob --interconnects
clock
reset
enable
axi4
i2c
```

Or you can just query the interconnects required by the top-level block, rather than all of the interconnects stored in the project:

```
$> python3.6 tools/inspector.py /path/to/my/design.df_blob --top-interconnects
clock
reset
i2c
```

You can also get it to list every principal [DFBlock](./schema/block) attached to the [DFProject](./schema/project):

```
$> python3.6 tools/inspector.py --blocks /path/to/my/design.df_blob
soc_core
top_ram
pcie_block
```

Further information on available options can be found by using:

```bash
$> python3.6 tools/inspector.py -h
usage: inspector.py [-h] [--test TEST] [--false] [--value VALUE]
                    [--if-true IF_TRUE] [--if-false IF_FALSE] [--exitcode]
                    [--interconnects] [--top-interconnects] [--blocks]
                    [--spaced]
                    blob

Checks for presence of a particular attribute on the principal object

positional arguments:
  blob                  Path to the DFBlob file to test for an attribute

optional arguments:
  -h, --help            show this help message and exit
...
```

## Cleaner
The cleaner tool can load a design from an input file, strip unnecessary descriptions, attributes, connectivity, and hierarchies from it, and then write it out to a separate file. This can be useful for creating debug tools that leverage the DesignFormat database for address map, register, or connectivity information, but only a small portion is relevant.

The `--preserve-connectivity` option chases connections fanning out from a specified port, and preserves any block, port, or connection that it passes through while stripping all other nodes. The search also fans out through address maps, meaning all targets accessible to a certain initiator port can be kept intact. In the example below, all connectivity stemming from the `cfg` port on the `top_level` block will be kept.

```bash
$> python3.6 tools/cleaner.py /my/input.df_blob /my/output.df_blob --strip-descriptions --strip-attributes --preserve-connectivity top_level[cfg]
```

The `--preserve-tree` resolves the specified block, then preserves the entire parent hierarchy above it - removing all other nodes including siblings. It does not remove any ports or connections from the preserved blocks. In the example below the blocks `top_level`, `my_block`, `my_child`, and `my_subchild` will be kept in their entirety except for any attribute list as this will be removed by `--strip-attributes`.

```bash
$> python3.6 tools/cleaner.py /my/input.df_blob /my/output.df_blob --preserve-tree top_level.my_block.my_child.my_subchild --strip-attributes
```

You can provide as many `--preserve-connectivity` and `--preserve-tree` arguments as required. Each preserved hierarchy or connection map will be determined before any nodes are removed, making the options constructive.