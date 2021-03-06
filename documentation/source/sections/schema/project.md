# DFProject

`DFProject` acts as a container for all other schema nodes allowing complex design hierarchies, interconnect definitions, and constants to be transferred between different parts of the workflow. It acts as the root node when dumping out the design, and drives the re-construction of all elements when loading back from file.

The project contains a list of `nodes` - these are separated into two categories:

 * Principal nodes are nominated objects that provide focus to downstream workflow stages (i.e. those that reload a dumped design). For example, it might be used to nominate specific top-level blocks that you want to be automatically generated by a code templating engine.
 * Reference nodes contain further information about the design that is needed to support the principal nodes. For example, these might be used to declare the interconnects used by different ports throughout the hierarchy, as in this case they won't be the primary focus for downstream tools.

Principal nodes are nominated by setting a `PRINCIPAL` attribute to `true` on the node in question.

Just like every other tag, `DFProject` inherits from [DFBase](./base), so has support for all of the core attributes (`id`, `description`, and `attributes`).

```json
{
    "id": "my_design",
    "description": "My fantastic hierarchical design",
    "attributes": { },
    "created": 1562319325309,
    "path": "/path/to/my/root/document.yaml",
    "version": 1.3,
    "nodes": [
        {
            "__type__": "DFBlock",
            "__dump__": {
                "id": "principal_node",
                "attributes": { "PRINCIPAL": true }
            }
        },
        {
            "__type__": "DFInterconnect",
            "__dump__": {
                "id": "reference_node",
                "attributes": { }
            }
        }
    ]
}
```

| Property | Usage |
|----------|-------|
| created  | Date that the project was created, in milliseconds since epoch |
| path     | Path to the source file used to create the project |
| version  | Version of the DesignFormat project, to detect compatibility |
| nodes    | List of encapsulated dumped nodes, see note below on encapsulation |

```eval_rst
.. note::
    As discussed in the `Storage Format` section, dumped nodes in the DFProject definition are encapsulated to help the library identify what type they represent. As shown above `__type__` indicates which schema node the data refers to, while `__dump__` contains the dumped data from the node.
```

## Python API

```eval_rst
.. autoclass:: designformat.project.DFProject
    :members:
    :special-members:
```

## Javascript API

```eval_rst
.. js:autoclass:: DFProject
    :members:
```