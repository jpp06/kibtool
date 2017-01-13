#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
from urllib3 import make_headers

from elasticsearch import Elasticsearch, connection
from elasticsearch import exceptions
# suppress console err message from http connections
# http://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
import logging
logging.getLogger("elasticsearch").setLevel(logging.ERROR)

from kibtool.kobject import Dashboard
from kibtool.kobject import Visualization
from kibtool.kobject import Search


class KibTool(object):
  def __init__(self, p_args = sys.argv):
    self.m_args = self.parseArgs(p_args)

    if self.m_args.debug:
      print("--- debug: arg list", file=sys.stderr)
      for c_arg, c_val in vars(self.m_args).items():
        print(c_arg, c_val, file=sys.stderr)
      print("--- debug: end arg list", file=sys.stderr)

    try:
      if self.m_args.esfrom.startswith("http://"):
        self.m_args.esfrom = self.m_args.esfrom[7:]
      self.m_args.hostfrom, self.m_args.portfrom = self.m_args.esfrom.split(":")
    except ValueError as e:
      print("*** bad host:port for Elasticsearch", self.m_args.esfrom, file=sys.stderr)
      sys.exit(1)
    if self.m_args.proxy:
      os.environ['HTTP_PROXY'] = self.m_args.proxy
      self.m_esfrom = Elasticsearch(hosts=[{ "host": self.m_args.hostfrom,
                                             "port": int(self.m_args.portfrom),
                                             "url_prefix": self.m_args.prefixfrom
                                           }],
                                    max_retries=2, timeout=200,
                                    connection_class=connection.RequestsHttpConnection)
      if self.m_args.cred:
        l_header = make_headers(proxy_basic_auth=self.m_args.creds)
        l_cnx = self.m_esfrom.transport.get_connection()
        l_cnx.session.headers['proxy-authorization'] = l_header['proxy-authorization']
        print(self.m_esfrom.transport.get_connection().session.headers)
        print()
    else:
      self.m_esfrom = Elasticsearch(hosts=[{ "host": self.m_args.hostfrom, "port": self.m_args.portfrom}],
                                    max_retries=2, timeout=200)
    try:
      if self.m_args.esto.startswith("http://"):
        self.m_args.esto = self.m_args.esto[7:]
      self.m_args.hostto, self.m_args.portto = self.m_args.esto.split(":")
    except ValueError as e:
      print("*** bad host:port for Elasticsearch", self.m_args.esto, file=sys.stderr)
      sys.exit(1)
    self.m_esto = Elasticsearch(hosts=[{ "host": self.m_args.hostto, "port": self.m_args.portto}],
                                max_retries=2, timeout=200)

  def toLuceneSyntax(p_req):
    return p_req.replace(":", " ")

  def getDashboards(self, p_luceneReq):
    return self.getObjects(p_luceneReq, "dashboard", Dashboard)
  def getVisualizations(self, p_luceneReq):
    return self.getObjects(p_luceneReq, "visualization", Visualization)
  def getSearches(self, p_luceneReq):
    return self.getObjects(p_luceneReq, "search", Search)
  def getObjects(self, p_luceneReq, p_type, p_ctor):
    l_request = {
      "fields": ["_id"],
      "size": self.m_args.count,
      "sort": {
        "_id": {
          "order": "asc"
        }
      },
      "query": {
        "query_string" : {
          "query" : "title:\"" + KibTool.toLuceneSyntax(p_luceneReq) + "\" AND _type:" + p_type
        }
      }
    }
    if self.m_args.debug:
      print("---", l_request)
    try:
      l_response = self.m_esfrom.search(index=self.m_args.kibfrom, doc_type=p_type, body=l_request)
    except exceptions.NotFoundError:
      print("*** Can't search in unknown index", self.m_args.kibfrom, file=sys.stderr)
      sys.exit(1)
    l_result = []
    if 0 == l_response["hits"]["total"]:
      print("*** No %s found for '%s' in index %s/%s" %
            (p_type, p_luceneReq, self.m_args.esfrom, self.m_args.kibfrom), file=sys.stderr)
      sys.exit(1)
    elif self.m_args.count < l_response["hits"]["total"]:
      print("*** Please use a greater --count (%d) to select all %ss" %
            (l_response["hits"]["total"], p_type), file=sys.stderr)
      sys.exit(1)
    else:
      for c_hit in l_response["hits"]["hits"]:
        l_d = p_ctor(self.m_esfrom, self.m_args.kibfrom, c_hit["_id"])
        l_result.append(l_d)
    return l_result

  def getDashboard(self, p_id):
    return [ Dashboard(self.m_esfrom, self.m_args.kibfrom, p_id) ]
  def getVisualization(self, p_id):
    return [ Visualization(self.m_esfrom, self.m_args.kibfrom, p_id) ]
  def getSearch(self, p_id):
    return [ Search(self.m_esfrom, self.m_args.kibfrom, p_id) ]

  def checkDefaultIndexPattern(self, p_indexPattern):
    l_type = "config"
    l_configs = self.m_esto.search(index=self.m_args.kibto, doc_type=l_type)
    if l_configs["hits"]["total"] == 0:
      print("--- '%s' is not a Kibana index. Default index pattern not updated." % (self.m_args.kibto))
      return
    for c_hit in l_configs["hits"]["hits"]:
      if "defaultIndex" not in c_hit["_source"]:
        c_hit["_source"]["defaultIndex"] = p_indexPattern
        l_response = self.m_esto.update(index=self.m_args.kibto, doc_type=l_type, id=c_hit["_id"],
                                        body={ "doc": c_hit["_source"], "doc_as_upsert" : True })
        if "_shards" not in l_response or l_response["_shards"]["total"] != l_response["_shards"]["successful"]:
          print("*** Can't update default pattern index in '%s'." % (self.m_args.kibto), file=sys.stderr)
          sys.exit(1)

  def findOrphans(self):
    l_result = set()
    l_dashboards = self.getDashboards("*")
    l_depends = set()
    for c_dashboard in l_dashboards:
      l_depends.update(c_dashboard.getDepend(True))
    l_visualizations = self.getVisualizations("*")
    for c_visalization in l_visualizations:
      if not c_visalization in l_depends:
        l_result.add(c_visalization)
        print(c_visalization.m_id)
    l_searches = self.getSearches("*")
    for c_search in l_searches:
      if not c_search in l_depends:
        l_result.add(c_search)
        print(c_search.m_id)
    return l_result

  # MAIN
  def execute(self):
    l_kobjs = []
    if self.m_args.dash:
      for c_dash in self.m_args.dash:
        l_kobjs.extend(self.getDashboards(c_dash))
    if self.m_args.dashid:
      for c_dash in self.m_args.dashid:
        l_kobjs.extend(self.getDashboard(c_dash))
    if self.m_args.visu:
      for c_visu in self.m_args.visu:
        l_kobjs.extend(self.getVisualizations(c_visu))
    if self.m_args.visuid:
      for c_visu in self.m_args.visuid:
        l_kobjs.extend(self.getVisualization(c_visu))
    if self.m_args.search:
      for c_search in self.m_args.search:
        l_kobjs.extend(self.getSearches(c_search))
    if self.m_args.searchid:
      for c_search in self.m_args.searchid:
        l_kobjs.extend(self.getSearch(c_search))

    l_depends = set()
    if self.m_args.depend:
      for c_kobj in l_kobjs:
        l_depends.update(c_kobj.getDepend())

    l_dependsL = list(l_depends)
    if not self.m_args.dry:
      if self.m_args.print:
        for c_kobj in l_dependsL + l_kobjs:
          print(c_kobj)

    if self.m_args.orphan:
      l_kobjs.extend(self.findOrphans())

    if self.m_args.check:
      l_missingIds = set()
      for c_kobj in l_dependsL + l_kobjs:
        l_missingIds.update(c_kobj.getMissingDepend())
      for c_missing in sorted(l_missingIds):
        print("--- object '%s' is missing" % (c_missing))

    if self.m_args.copy:
      if self.m_args.kibfrom == self.m_args.kibto and self.m_args.esfrom == self.m_args.esto:
        print("*** Source and destination indices are identical: no copy done.", file=sys.stderr)
        sys.exit(1)
      else:
        for c_obj in sorted(l_dependsL + l_kobjs):
          if self.m_args.dry:
            if self.m_args.force:
              print("+++ Copying '%s/%s' from '%s/%s' and replacing to '%s/%s'" %
                    (c_obj.m_type, c_obj.m_idUtf8, self.m_args.esfrom, self.m_args.kibfrom, self.m_args.esto, self.m_args.kibto))
            else:
              print("+++ Copying '%s/%s' from '%s/%s' to '%s/%s'" %
                    (c_obj.m_type, c_obj.m_idUtf8, self.m_args.esfrom, self.m_args.kibfrom, self.m_args.esto, self.m_args.kibto))
          else:
            if self.m_args.debug:
              print("--- copying", c_obj.m_type, c_obj.m_idUtf8, file=sys.stderr)
            c_obj.copyFromTo(self.m_esto, self.m_args.kibto, self.m_args.force)

    if self.m_args.delete:
      for c_obj in sorted(l_dependsL + l_kobjs):
        if self.m_args.dry:
          print("+++ Deleting '%s/%s' from '%s/%s'" %
                (c_obj.m_type, c_obj.m_idUtf8, self.m_args.esfrom, self.m_args.kibfrom))
        else:
          if self.m_args.debug:
            print("--- deleting", c_obj.m_type, c_obj.m_idUtf8, file=sys.stderr)
          c_obj.deleteFromEs()

    # check for default index pattern
    if self.m_args.depend and self.m_args.copy:
      l_indexPatterns = [ _ for _ in l_depends if _.m_type == "index-pattern" ]
      if 0 != len(l_indexPatterns):
        self.checkDefaultIndexPattern(l_indexPatterns[0].m_id)


  def parseArgs(self, p_args):
    l_parser = argparse.ArgumentParser(
      prog=p_args[0],
      description="Manage Kibana objects",
    )
    l_parser.add_argument(
      "--debug", action='store_true', default=False,
      help="print debug messages",
    )
    # es related options
    l_parser.add_argument(
      "--esfrom", type=str,
      default="localhost:9200",
      help="ElasticSearch source endpoint as host:port.",
    )
    l_parser.add_argument(
      "--prefixfrom", type=str,
      help="ElasticSearch source prefix.",
    )
    l_parser.add_argument(
      "--kibfrom", type=str,
      default=".kibana",
      help="Kibana source index name.",
    )
    l_parser.add_argument(
      "--esto", type=str,
      default="localhost:9200",
      help="ElasticSearch destination endpoint as host:port.",
    )
    l_parser.add_argument(
      "--kibto", type=str,
      help="Kibana destination index name.",
    )
    l_parser.add_argument(
      "--count", type=int, default=100,
      help="Request size limit when querying daashboards.",
    )
    # proxy
    l_parser.add_argument(
      "--proxy", type=str,
      help="Proxy to reach ElasticSearch cluster.",
    )
    l_parser.add_argument(
      "--cred", type=str,
      help="Proxy credentials to reach ElasticSearch cluster.",
    )
    # modifiers
    l_parser.add_argument(
      "--depend", action='store_true', default=False,
      help="add objects needed by selected objects (recursively).",
    )
    l_parser.add_argument(
      "--force", action='store_true', default=False,
      help="force replacement of existing objects.",
    )
    l_parser.add_argument(
      "--dry", action='store_true', default=False,
      help="run without side effects: tell what would have been written.",
    )
    # object selectors
    l_parser.add_argument(
      "--dash", type=str, action='append',
      help="Kibana dashboard name in Lucene query syntax.",
    )
    l_parser.add_argument(
      "--dashid", type=str, action='append',
      help="Kibana dashboard id.",
    )
    l_parser.add_argument(
      "--visu", type=str, action='append',
      help="Kibana visualization name in Lucene query syntax.",
    )
    l_parser.add_argument(
      "--visuid", type=str, action='append',
      help="Kibana visualization id.",
    )
    l_parser.add_argument(
      "--search", type=str, action='append',
      help="Kibana search name in Lucene query syntax.",
    )
    l_parser.add_argument(
      "--searchid", type=str, action='append',
      help="Kibana search id.",
    )
    # actions
    l_parser.add_argument(
      "--print", action='store_true', default=False,
      help="print listed objects",
    )
    l_parser.add_argument(
      "--copy", action='store_true', default=False,
      help="copy listed objects from source index to destination index. By default, don't replace existing: use '--force'",
    )
    l_parser.add_argument(
      "--delete", action='store_true', default=False,
      help="delete listed objects from source index",
    )
    l_parser.add_argument(
      "--check", action='store_true', default=False,
      help="check dependencies of listed objects in source index",
    )
    l_parser.add_argument(
      "--orphan", action='store_true', default=False,
      help="find unsused objects in source index",
    )

    l_result = l_parser.parse_args(p_args[1:])
    if l_result:
      # incompatible args
      if l_result.orphan and l_result.copy:
        l_parser.error("--orphan and --copy are incompatible")
        sys.exit(1)
      if l_result.orphan and l_result.check:
        l_parser.error("--orphan and --check are incompatible")
        sys.exit(1)
      if l_result.orphan and l_result.kibto:
        l_parser.error("--orphan and --kibto are incompatible")
        sys.exit(1)

      # required args
      if not l_result.dash and not l_result.dashid and \
         not l_result.visu and not l_result.visuid and \
         not l_result.search and not l_result.searchid and \
         not l_result.orphan:
        l_parser.error("without --orphan, at least one of --dash, --dashid, --visu, --visuid, --search, --searchid is required")
        sys.exit(1)
      # --orphan exclude selector
      if l_result.orphan and \
         ( l_result.dash or l_result.dashid or \
           l_result.visu or l_result.visuid or \
           l_result.search or l_result.searchid ):
        l_parser.error("with --orphan, no --dash, --dashid, --visu, --visuid, --search, --searchid expected")
        sys.exit(1)
      # print is the default action
      if not l_result.copy and not l_result.delete and not l_result.check:
        l_result.print = True
        if l_result.dry:
          print("+++ No object will be created, checked, or deleted: source index will be read to find and print object list.")
          sys.exit(0)
      # delete all should be forced
      if l_result.delete and l_result.dash and "*" in l_result.dash and not l_result.force:
        print("--- Trying to delete all from source index. Use --force if you are sure", file=sys.stderr)
        sys.exit(1)
    return l_result
