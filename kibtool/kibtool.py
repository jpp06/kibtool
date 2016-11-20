#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

from elasticsearch import Elasticsearch
from elasticsearch import exceptions
# suppress console err message from http connections
# http://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
import logging
logging.getLogger("elasticsearch").setLevel(logging.ERROR)

from kibtool.kobject import Dashboard


class KibTool(object):
  def __init__(self, p_args = sys.argv):
    self.m_args = self.parseArgs(p_args)

    if self.m_args.debug:
      print("--- debug: arg list", file=sys.stderr)
      for c_arg, c_val in vars(self.m_args).items():
        print(c_arg, c_val, file=sys.stderr)
      print("--- debug: end arg list", file=sys.stderr)

    try:
      self.m_args.hostfrom, self.m_args.portfrom = self.m_args.esfrom.split(":")
    except:
      print("*** bad host:port for Elasticsearch", self.m_args.esfrom, file=sys.stderr)
      sys.exit(1)
    self.m_esfrom = Elasticsearch(hosts=[{ "host": self.m_args.hostfrom, "port": self.m_args.portfrom}],
                                  max_retries=2, timeout=200)
    try:
      self.m_args.hostto, self.m_args.portto = self.m_args.esto.split(":")
    except:
      print("*** bad host:port for Elasticsearch", self.m_args.esto, file=sys.stderr)
      sys.exit(1)
    self.m_esto = Elasticsearch(hosts=[{ "host": self.m_args.hostto, "port": self.m_args.portto}],
                                max_retries=2, timeout=200)

  def toLuceneSyntax(p_req):
    return p_req.replace(":", " ")

  def getDashboards(self, p_luceneReq):
    l_request = {
      "fields": ["_id"],
      "query": {
        "query_string" : {
          "query" : "title:\"" + KibTool.toLuceneSyntax(p_luceneReq) + "\" AND _type:dashboard"
        }
      }
    }
    if self.m_args.debug:
      print("---", l_request)
    try:
      l_response = self.m_esfrom.search(index=self.m_args.kibfrom, doc_type="dashboard", body=l_request)
    except exceptions.NotFoundError:
      print("*** Can't search in unknown index", self.m_args.kibfrom, file=sys.stderr)
      sys.exit(1)
    l_result = []
    if 0 == l_response["hits"]["total"]:
      print("*** No dashboard found for '%s' in index %s/%s" %
            (self.m_args.dash, self.m_args.esfrom, self.m_args.kibfrom), file=sys.stderr)
      sys.exit(1)
    else:
      for c_hit in l_response["hits"]["hits"]:
        l_d = Dashboard(self.m_esfrom, self.m_args.kibfrom, c_hit["_id"])
        l_result.append(l_d)
    return l_result
  def getDashboard(self, p_id):
    return [ Dashboard(self.m_esfrom, self.m_args.kibfrom, p_id) ]

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
          print("*** Can't update default pattern index in '%s'." % (self.m_args.kibto))
          sys.exit(1)

  # MAIN
  def execute(self):
    l_kobjs = []
    if self.m_args.dash:
      for c_dash in self.m_args.dash:
        l_kobjs.extend(self.getDashboards(c_dash))
    if self.m_args.dashid:
      for c_dash in self.m_args.dashid:
        l_kobjs.extend(self.getDashboard(c_dash))

    l_depends = set()
    if self.m_args.depend:
      for c_kobj in l_kobjs:
        l_depends.update(c_kobj.getDepend())

    l_dependsL = list(l_depends)
    if self.m_args.print:
      for c_kobj in l_dependsL + l_kobjs:
        print(c_kobj)

    if self.m_args.copy:
      if self.m_args.kibfrom == self.m_args.kibto and self.m_args.esfrom == self.m_args.esto:
        print("*** Source and destination indices are identical: no copy done.")
        sys.exit(1)
      else:
        for c_obj in l_dependsL + l_kobjs:
          if self.m_args.debug:
            print("---", c_obj.m_type, c_obj.m_id)
          c_obj.copyFromTo(self.m_esto, self.m_args.kibto, self.m_args.force)

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
    l_parser.add_argument(
      "--esfrom", type=str,
      default="localhost:9200",
      help="ElasticSearch source endpoint as host:port.",
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
      default=".kibana",
      help="Kibana destination index name.",
    )
    l_parser.add_argument(
      "--dash", type=str, action='append',
      help="Kibana dashboard name in Lucene query syntax.",
    )
    l_parser.add_argument(
      "--dashid", type=str, action='append',
      help="Kibana dashboard id.",
    )
    l_parser.add_argument(
      "--depend", action='store_true', default=False,
      help="add objects needed by selected objects (recursively).",
    )
    l_parser.add_argument(
      "--copy", action='store_true', default=False,
      help="copy listed objects from source index to destination index. By default, don't replace existing: use '--force'",
    )
    l_parser.add_argument(
      "--print", action='store_true', default=False,
      help="print listed objects",
    )
    l_parser.add_argument(
      "--force", action='store_true', default=False,
      help="force replacement of existing objects.",
    )

    return l_parser.parse_args(p_args[1:])

