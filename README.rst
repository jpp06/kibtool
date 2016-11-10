.. _readme:

KibTool
=======

Have a lot of dashboards and visualizations to move from one Kibana to another?
This tool helps you to manage Kibana objects with a command line. It will save
you lots of mouse clicks, and probably avoid error during click sessions!


Compatibility Matrix
====================

No extensive tests have been donne so far, and the dependency matrix represents mys own envrionment.

+--------+-----------+------------+-----------+
|Version | ES 2.4.x  | PyES 1.0.0 | Kib 4.6.1 |
+========+===========+============+===========+
| first  |    yes    |    yes     |    yes    |
+--------+-----------+------------+-----------+

Builds
======


.. image:: https://travis-ci.org/jpparis-orange/kibtool.svg?branch=master
           :target: https://travis-ci.org/jpparis-orange/kibtool


Getting started
---------------

* Fork the repo and run from source.
* If not installed already, you will need
`Python Elasticsearch Client <https://github.com/elastic/elasticsearch-py>`_. I'm currently using 1.0.0.
* In the root directory of the project, run ``kibtool.py --help`` to show usage information.

Examples
--------

* ``./kibtool.py --kibfrom .kibana_src --dash '*' --print`` list IDs of all documents typed ``dashboard``
  found in ``.kibana_src``. ``--dash`` argument is a Lucene query applied on the title of dashboards.
  Kibana index is found on ``localhost:92000`` by default (see ``--esfrom``)
* ``./kibtool.py --kibfrom .kibana_src --dash '*' --print --depend`` list IDs of all documents typed
  ``dashboard`` found in ``.kibana_src``, and all dependencies (visualization, search, config,
  index-pattern).  ``--dash`` argument is a Lucene query applied on the title of dashboards.
* ``./kibtool.py --kibfrom .kibana_src --dash 'my_dashboard' --kibto .kibana_dest --depend --copy --force``
  copy dashboard ``my_dashboard`` and all its dependencies (visualization, search, config, index-pattern)
  from ``.kibana_src`` to ``.kibana_dst``. Existing objects in ``.kibana_dst`` will be overwritten (--force).
  ``--dash`` argument is a Lucene query applied on the title of dashboards.
* ``./kibtool.py --kibfrom .kibana_src --dashid 'my-:-dashboard' --kibto .kibana_dest --copy``
  copy dashboard identified by ``my-:-dashboard`` to ``.kibana_dst``.

