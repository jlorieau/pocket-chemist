Development
===========

Setup
-----

1. Clone the `develop` repository

   .. code-block:: console

      $ git clone https://github.com/jlorieau/xamin/tree/develop

2. Install the package in installable mode

   .. code-block:: console

      $ pip install -e .

3. Make sure you're in the default virtual environment for development

   .. code-block:: console

      $ hatch shell

Documentation
-------------

towncrier
^^^^^^^^^

1. Add `towncrier`_ news fragments, and commit these to the repository. 
   (location: `docs/development/newsfragments`)

   .. code-block:: console

      $ towncrier create --content '<message>' <issue>.<type>.rst

   The `<issue>`` is the github `issue`_ number
   The `<type>` is one of either `feature`, `bugfix`, `doc`, `removal` or `misc`

2. Bump a new version

   .. code-block:: console

      $ hatch version
      0.3.0
      $ hatch version <new version>

3. Create the `towncrier` changelog for the new version

   .. code-block:: console

      $ towncrier build

Publish
-------


.. _towncrier: https://towncrier.readthedocs.io/en/stable/index.html
.. _issue: https://github.com/jlorieau/xamin/issues

.. toctree::
    
    roadmap