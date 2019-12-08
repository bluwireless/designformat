# Storage Format

DesignFormat uses JSON as it's storage format - the reason for this is two fold:

 * Native support for JSON is common in many programming languages (e.g. Python and Javascript, as just two examples) - so it provides a very low bar with minimal requirements.
 * It is compact, flexible, and relatively easy to read as a human - XML also has widespread support, but is much more verbose and can be difficult to comprehend.

The root object of a DesignFormat dump is always a [DFProject](./schema/project) - this contains some basic information about the project, as well as the list of root DesignFormat nodes:

```json
{
    "id": "my_project",
    "created": 1647107554,
    "path": "/home/user/Work/my_design/my_project.df_blob",
    "version": "1.3",
    "nodes": [ ]
}
```

When reloading a design, the library should check that it is compatible with the version number stated in the [DFProject](./schema/project). As the format is young, changes between versions may be substantial and breaking, so adding speculative forwards compatibility is discouraged. Instead you should detect the version incompatibility and raise an error. Backwards compatibility is encouraged, especially between consecutive versions as this provides an 'upgrade' path for users switching from older versions.

```eval_rst
.. note::
    Any type of DesignFormat node can be attached to the root project's `nodes` list with the exception of DFProject, which can only ever be the root object.
```

Every DesignFormat object attached to the root project is encapsulated with a wrapper layer that describes its type to guide the reloading process:

```json
{
    "id": "my_project",
    "nodes": [
        {
            "__type__": "dfblock",
            "__dump__": {
                "id": "my_root_block",
                "other": "properties"
            }
        },
    ]
}
```

Here we see two special attributes:

 * `__type__` details the type of the node being dumped, this should be one of the list of schema nodes (e.g. [DFBlock](./schema/block), [DFInterconnect](./schema/interconnect), ... - case is unimportant).
 * `__dump__` contains the dumped node.

When reloading the design, the library should use the `__type__` attribute to instantiate and populate the correct DesignFormat node class. It should *not* attempt to determine the correct node class based on the parameters of the node itself, as these may differ between versions.

```eval_rst
.. note::
    Node wrappers are mainly used by DFProject to store the root nodes, this is because in most other cases the child node's type is deterministic (i.e. a DFPort will always be the node used within a DFBlock's `ports` field) and so using an encapsulation would be inefficient.
```