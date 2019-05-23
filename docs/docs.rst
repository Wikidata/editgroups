.. _page-docs:

Documenting
===========

This manual is written using Sphinx and the source files can be found in the `docs` folder 
of the repository for this application.
Any contributions to the docs are of course most welcome, as are any suggestions to improve
the coverage of a particular subject.

Graphs for models can be generated using the ``django-extensions`` library.
When making changes to the models, these diagrams should be updated. They are 
generated as follows::

    ./manage.py graph_models store revert tagging | dot -Tpng -o models.png

