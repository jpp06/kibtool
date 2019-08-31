#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import json
from elasticsearch import exceptions


# Kibana objects: dashboard, visualization, search, config, index-pattern
class KObject(object):
  def __init__(self, p_es, p_index, p_type, p_id):
    self.m_es = p_es
    self.m_index = p_index
    self.m_type = p_type
    self.m_id = p_id
    self.m_idUtf8 = str(p_id.encode("utf-8"))[1:].strip("'")
    self.m_json = None

  def build(p_es, p_index, p_type, p_id):
    if p_type == "dashboard":
      return Dashboard(p_es, p_index, p_id)
    elif p_type == "visualization":
      return Visualization(p_es, p_index, p_id)
    elif p_type == "search":
      return Search(p_es, p_index, p_id)
    elif p_type == "index-pattern":
      return IndexPattern(p_es, p_index, p_id)
    elif p_type == "config":
      return Config(p_es, p_index, p_id)
    else:
      print("*** Unknown Kibana object type '%s'" % (p_type), file=sys.stderr)
      sys.exit(4)
  def __str__(self):
    return self.m_index + "/" + self.m_type + "/" + self.m_idUtf8
  def __hash__(self):
    return hash((self.m_index, self.m_type, self.m_id))
  def __eq__(self, p_other):
    return self.m_index == p_other.m_index and self.m_type == p_other.m_type and self.m_id == p_other.m_id
  def __lt__(self, p_other):
    if self.m_index < p_other.m_index:
      return True
    if self.m_type < p_other.m_type:
      return True
    if self.m_id < p_other.m_id:
      return True
    return False

  def deleteFromEs(self):
    try:
      self.m_json = self.m_es.delete(index=self.m_index, doc_type=self.m_type, id=self.m_id)
    except exceptions.NotFoundError as e:
      return

  def setJson(self, p_json):
    self.m_json = p_json

  def readFromEs(self):
    if self.m_json:
      return
    try:
      self.m_json = self.m_es.get(index=self.m_index, doc_type=self.m_type, id=self.m_id)
    except exceptions.NotFoundError as e:
      return

  def toKibanaImpExp(self):
    self.readFromEs()
    if not self.m_json:
      print("*** Can not get '%s' object from '%s'" % (self, self.m_index), file=sys.stderr)
      sys.exit(3)
    return {
      "_type" : self.m_type,
      "_id" : self.m_id,
      "_source": self.m_json["_source"]
    }

  def copyToEs(self, p_esTo, p_indexTo, p_force=False):
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
      print("*** Can not create '%s' in index '%s'" % (self.m_idUtf8, p_indexTo), file=sys.stderr)
    except exceptions.RequestError as e:
      print("*** Can't write to unknown index", p_indexTo, file=sys.stderr)
      sys.exit(1)

  def getMissingDepend(self):
    l_deps = self.getDepend(True)
    l_missings = []
    for c_dep in l_deps:
      c_dep.readFromEs()
      if not c_dep.m_json:
        l_missings.append((c_dep, self.m_idUtf8))
    return l_missings

  def getFieldsAndIndicies(self):
    return set()

  def getFieldsFromQueryString(self, p_query):
    l_result = set()
    if "*" == p_query:
      return l_result
    l_query = re.sub(r"\[[^]]*\]", "RANGE", p_query)
    l_query = re.sub(r"\(|\)", "", l_query)
    l_items = l_query.split(" ")
    for c_item in l_items:
      if ":" in c_item:
        l_field, l_value = c_item.split(":")
        if l_field.startswith("_"): # _exists_, _missing_
          l_result.add((l_value, "field"))
        else:
          l_result.add((l_field, "field"))
      elif c_item not in ["AND", "OR", "NOT"]:
        print("***FFQS", json.dumps(l_query), l_result, file=sys.stderr)
        sys.exit(1)
    return l_result

  def getFieldsFromQuery(self, p_query):
    l_result = set()
    if 0 == len(p_query):
      return l_result
    if "match" in p_query:
      l_result |= set([ (_, "field") for _ in p_query["match"].keys() ])
    else:
      print("***FFQ", json.dumps(p_query), file=sys.stderr)
      sys.exit(1)
    return l_result

  def getFaiFromExpression(self, p_expr):
    l_result = set()
    if 0 == len(p_expr):
      return l_result
    l_es = 0
    l_es = p_expr.find(".es(", l_es)
    while -1 != l_es:
      l_paren = p_expr.find(")", l_es)
      l_esExpr = p_expr[l_es + 4:l_paren]
      l_index = re.search(r"index *= *' *([^']+) *'", l_esExpr)
      l_result.add((l_esExpr[l_index.start(1) : l_index.end(1)], "index"))
      l_field = re.search(r"timefield *= *' *([^']+) *'", l_esExpr)
      if l_field:
        l_result.add((l_esExpr[l_field.start(1) : l_field.end(1)], "field"))
      l_es = p_expr.find(".es(", l_paren + 1)
    return l_result

class Config(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "config", p_id)
class IndexPattern(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "index-pattern", p_id)
class Search(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "search", p_id)
  def getDepend(self, p_silent=False):
    self.readFromEs()
    if not self.m_json:
      if not p_silent:
        print("*** Can not get '%s' object from '%s'" % (self, self.m_index), file=sys.stderr)
      return []
    l_searchSource = json.loads(self.m_json["_source"]["kibanaSavedObjectMeta"]["searchSourceJSON"])
    if "index" in l_searchSource:
      return [ IndexPattern(self.m_es, self.m_index, l_searchSource["index"]) ]
  def getFieldsAndIndicies(self):
    self.readFromEs()
    l_source = self.m_json["_source"]
    #print("---S", json.dumps(l_source, indent=2))
    l_result = set()
    if "columns" in l_source:
      l_result |= set([ (_, "field") for _ in l_source["columns"] ])
    if "sort" in l_source:
      l_result.add((l_source["sort"][0], "field"))
    if "kibanaSavedObjectMeta" in l_source and "searchSourceJSON" in l_source["kibanaSavedObjectMeta"]:
      l_ss = json.loads(l_source["kibanaSavedObjectMeta"]["searchSourceJSON"])
      if "query" in l_ss and "query_string" in l_ss["query"] and "query" in l_ss["query"]["query_string"]:
        l_query = l_ss["query"]["query_string"]["query"]
        l_result |= self.getFieldsFromQueryString(l_query)
      if "index" in l_ss:
        l_result.add((l_ss["index"], "index"))
    return l_result


class Visualization(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "visualization", p_id)
  def getDepend(self, p_silent=False):
    self.readFromEs()
    if not self.m_json:
      if not p_silent:
        print("*** Can not get '%s' object from '%s'" % (self, self.m_index), file=sys.stderr)
      return []
    l_result = set()
    if "savedSearchId" in self.m_json["_source"]:
      l_search = Search(self.m_es, self.m_index, self.m_json["_source"]["savedSearchId"])
      l_result.add(l_search)
      l_result.update(l_search.getDepend(p_silent))
    elif "visState" in self.m_json["_source"]:
      l_visState = json.loads(self.m_json["_source"]["visState"])
      if "type" in l_visState:
        if "kibi_timeline" == l_visState["type"]:
          # kibi timeline
          for c_group in l_visState["params"]["groups"]:
            l_result.add(Search(self.m_es, self.m_index, c_group["savedSearchId"]))
            l_result.add(IndexPattern(self.m_es, self.m_index, c_group["indexPatternId"]))
    l_searchSource = json.loads(self.m_json["_source"]["kibanaSavedObjectMeta"]["searchSourceJSON"])
    if "index" in l_searchSource:
      l_result.add(IndexPattern(self.m_es, self.m_index, l_searchSource["index"]))
    return l_result
  def getFieldsAndIndicies(self):
    self.readFromEs()
    l_result = set()
    l_ss = json.loads(self.m_json["_source"]["kibanaSavedObjectMeta"]["searchSourceJSON"])
    l_visState = json.loads(self.m_json["_source"]["visState"])
    if "type" in l_visState and "timelion" == l_visState["type"]:
      l_result |= self.getFaiFromExpression(l_visState["params"]["expression"])
    if "filter" in l_ss:
      for c_filter in l_ss["filter"]:
        if "query" in c_filter and "query_string" in c_filter["query"] and "query" in c_filter["query"]["query_string"]:
          l_query = c_filter["query"]["query_string"]["query"]
          l_result |= self.getFieldsFromQueryString(l_query)
        else:
          print("***V", json.dumps(c_filter, indent=2), file=sys.stderr)
          sys.exit(1)
    if "query" in l_ss:
      if "query_string" in l_ss["query"] and "query" in l_ss["query"]["query_string"]:
        l_query = l_ss["query"]["query_string"]["query"]
        l_result |= self.getFieldsFromQueryString(l_query)
      else:
        l_result |= self.getFieldsFromQuery(c_filter["query"])
    if "index" in l_ss:
      l_result.add((l_ss["index"], "index"))
    return l_result


class Dashboard(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "dashboard", p_id)
  def getDepend(self, p_silent=False):
    self.readFromEs()
    if not self.m_json:
      if not p_silent:
        print("*** Can not get '%s' object from '%s'" % (self, self.m_index), file=sys.stderr)
      return []
    l_panels = json.loads(self.m_json["_source"]["panelsJSON"])
    l_result = set()
    for c_panel in l_panels:
      if "visualization" == c_panel["type"]:
        l_viz = Visualization(self.m_es, self.m_index, c_panel["id"])
        l_result.add(l_viz)
        l_result.update(l_viz.getDepend(p_silent))
      elif "search" == c_panel["type"]:
        l_result.add(Search(self.m_es, self.m_index, c_panel["id"]))
      else:
        print("*** Unknown object type '%s' in dashboard" % (c_panel["type"]), file=sys.stderr)
        sys.exit(1)
    return l_result
  def getFieldsAndIndicies(self):
    self.readFromEs()
    l_searchSource = json.loads(self.m_json["_source"]["kibanaSavedObjectMeta"]["searchSourceJSON"])
    l_result = set()
    if "filter" in l_searchSource:
      for c_filter in l_searchSource["filter"]:
        if "query" in c_filter:
          if "query_string" in c_filter["query"] and "query" in c_filter["query"]["query_string"]:
            l_query = c_filter["query"]["query_string"]["query"]
            l_result |= self.getFieldsFromQueryString(l_query)
          else:
            l_result |= self.getFieldsFromQuery(c_filter["query"])
        else:
          print("***D", json.dumps(c_filter, indent=2), file=sys.stderr)
          sys.exit(1)
        if "meta" in c_filter:
          l_meta = c_filter["meta"]
          l_result.add((l_meta["index"], "index"))
          l_result.add((l_meta["key"], "field"))
    return l_result
