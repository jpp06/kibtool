#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib.request
import json
import argparse
from datetime import datetime, tzinfo, date
import unicodedata
import codecs
from collections import defaultdict
import unicodedata
import csv
from dateutil.relativedelta import relativedelta
import re

from elasticsearch import Elasticsearch
from elasticsearch import exceptions

# suppress console err message from http connections
# http://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
import logging
logging.getLogger("elasticsearch").setLevel(logging.ERROR)

######################################################################
# Kibana objects: dashboard, visualization, search, config, index-pattern
class KObject(object):
  def __init__(self, p_es, p_index, p_type, p_id):
    self.m_es = p_es
    self.m_index = p_index
    self.m_type = p_type
    self.m_id = p_id
    self.m_json = None

  def __str__(self):
    return self.m_index + "/" + self.m_type + "/" + self.m_id
  def __hash__(self):
    return hash((self.m_index, self.m_type, self.m_id))
  def __eq__(self, p_other):
    return self.m_index == p_other.m_index and self.m_type == p_other.m_type and self.m_id == p_other.m_id

  def readFromEs(self):
    if self.m_json:
      return
    try:
      self.m_json = self.m_es.get(index=self.m_index, doc_type=self.m_type, id=self.m_id)
    except exceptions.NotFoundError as e:
      print("***", e, file=sys.stderr)
      return {}

  def copyFromTo(self, p_esTo, p_indexTo, p_force=False):
    self.readFromEs()
    if not self.m_json:
      print("*** Can not get '%s' object from '%s'" % (self, self.m_index), file=sys.stderr)
      return
    try:
      if p_force:
        l_response = p_esTo.update(index=p_indexTo, doc_type=self.m_type, id=self.m_id,
                                   body={ "doc": self.m_json["_source"], "doc_as_upsert" : True })
      else:
        l_response = p_esTo.create(index = p_indexTo, doc_type=self.m_type, id=self.m_id, body=self.m_json["_source"])
    except exceptions.ConflictError as e:
      print("*** Can not create '%s' in index '%s'" % (self.m_id, p_indexTo), file=sys.stderr)

class Config(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "config", p_id)
class IndexPattern(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "index-pattern", p_id)
class Search(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "search", p_id)

class Visualization(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "visualization", p_id)
  def getDepend(self):
    self.readFromEs()
    l_searchSource = json.loads(self.m_json["_source"]["kibanaSavedObjectMeta"]["searchSourceJSON"])
    if "index" in l_searchSource:
      return [ IndexPattern(self.m_es, self.m_index, l_searchSource["index"]) ]
    else:
      return []

class Dashboard(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "dashboard", p_id)
  def getDepend(self):
    self.readFromEs()
    l_panels = json.loads(self.m_json["_source"]["panelsJSON"])
    l_result = set()
    for c_panel in l_panels:
      if "visualization" == c_panel["type"]:
        l_viz = Visualization(self.m_es, self.m_index, c_panel["id"])
        l_result.add(l_viz)
        l_result.update(l_viz.getDepend())
      elif "search" == c_panel["type"]:
        l_result.add(Search(self.m_es, self.m_index, c_panel["id"]))
      else:
        print("*** Unknown object type '%s' in dashboard" % (c_panel["type"]),
              file=sys.stderr)
        sys.exit(1)
    return l_result

######################################################################
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
    l_response = self.m_esfrom.search(index=self.m_args.kibfrom, doc_type="dashboard", body=l_request)
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

######################################################################
if __name__ == "__main__":
  l_kibtool = KibTool()
  l_kibtool.execute()


