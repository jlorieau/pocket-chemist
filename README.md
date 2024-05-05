Xamin
=====

Xamin (pronounced examine) is a tool for the analysis and processing of scientific
datasets.

Features
--------
- [ ] Plug-in architecture
- [X] Graphical user interface (GUI) and command-line interface (CLI)

Repository Map
--------------

- ``cli``
  
  The command-line interface module. Depends on the ``entry`` and ``utils`` modules.

- ``entry``

  The data entry classes for serializing/deserializing data in different formats to and from files. Depends on the ``utils`` module.

- ``gui``

  The graphica user interface module for rendering the xamin viewer windows

  - ``activities``

    The activities sub-module for group related views, models, sidebars and tasks related to a type of analysis

  

