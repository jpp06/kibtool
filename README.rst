.. _readme:

KibTool
=======

Have a lot of dashboards and visualizations to move from one Kibana to another?
This tool helps you to manage Kibana objects with a command line. It will save
you lots of mouse clicks, and probably avoid error during click sessions!


Compatibility Matrix
--------------------

No extensive tests have been donne so far, and the dependency matrix represents my
own envrionment.

+--------+-----------+------------+-----------+
|Version | ES 2.4.x  | PyES 2.4.0 | Kib 4.6.1 |
+========+===========+============+===========+
|  0.1   |    yes    |    yes     |    yes    |
+--------+-----------+------------+-----------+

Builds
------


+--------+----------+-------------+
| Branch | Status   | Coverage    |
+========+==========+=============+
| Master | |master| | |masterCov| |
+--------+----------+-------------+

.. |master| image:: https://travis-ci.org/jpparis-orange/kibtool.svg?branch=master
                    :target: https://travis-ci.org/jpparis-orange/kibtool

.. |masterCov| image:: https://coveralls.io/repos/github/jpparis-orange/kibtool/badge.svg?branch=master
                       :target: https://coveralls.io/github/jpparis-orange/kibtool?branch=master

Getting started
---------------

* Fork the repo and run from source.
* If not installed already, you will need `Python Elasticsearch Client`_. I'm
  currently using 2.4.0.
* In the root directory of the project, ``run_kibtool.py --help`` to show usage
  information.

.. _Python Elasticsearch Client: https://github.com/elastic/elasticsearch-py

Examples
--------

* ``./run_kibtool.py --kibfrom .kibana_src --dash '*' --print`` list IDs of all documents of type ``dashboard``
  found in ``.kibana_src``. ``--dash`` argument is a Lucene query applied on the title of dashboards.
  Kibana index is found on ``localhost:9200`` by default (see ``--esfrom``)
* ``./run_kibtool.py --kibfrom .kibana_src --dash '*' --print --depend`` list IDs of all documents typed
  ``dashboard`` found in ``.kibana_src``, and all dependencies (visualization, search, config,
  index-pattern).  ``--dash`` argument is a Lucene query applied on the title of dashboards.
* ``./run_kibtool.py --kibfrom .kibana_src --dash 'my_dashboard' --kibto .kibana_dest --depend --copy --force``
  copy dashboard ``my_dashboard`` and all its dependencies (visualization, search, config, index-pattern)
  from ``.kibana_src`` to ``.kibana_dst``. Existing objects in ``.kibana_dst`` will be overwritten (--force).
  ``--dash`` argument is a Lucene query applied on the title of dashboards.
* ``./run_kibtool.py --kibfrom .kibana_src --dashid 'my-:-dashboard' --kibto .kibana_dest --copy``
  copy dashboard identified by ``my-:-dashboard`` to ``.kibana_dst``.

Thanks
------

I have copied/adapted lots of things from `curator project`_. Many thanks to `untergeek`_ and other participants:
you've boosted my learning curve.

.. _curator project: https://github.com/elastic/curator/
.. _untergeek: https://github.com/untergeek
