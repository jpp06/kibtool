#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
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

  def readFromEs(self):
    if self.m_json:
      return
    try:
      self.m_json = self.m_es.get(index=self.m_index, doc_type=self.m_type, id=self.m_id)
    except exceptions.NotFoundError as e:
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
      print("*** Can not create '%s' in index '%s'" % (self.m_idUtf8, p_indexTo), file=sys.stderr)
    except exceptions.RequestError as e:
      print("*** Can't write to unknown index", p_indexTo, file=sys.stderr)
      sys.exit(1)

class Config(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "config", p_id)
class IndexPattern(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "index-pattern", p_id)
class Search(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "search", p_id)
  def getDepend(self):
    self.readFromEs()
    l_searchSource = json.loads(self.m_json["_source"]["kibanaSavedObjectMeta"]["searchSourceJSON"])
    if "index" in l_searchSource:
      return [ IndexPattern(self.m_es, self.m_index, l_searchSource["index"]) ]

class Visualization(KObject):
  def __init__(self, p_es, p_index, p_id):
    super().__init__(p_es, p_index, "visualization", p_id)
  def getDepend(self):
    self.readFromEs()
    if not self.m_json:
      print("*** Can not get '%s' object from '%s'" % (self, self.m_index), file=sys.stderr)
      return []
    l_result = set()
    if "savedSearchId" in self.m_json["_source"]:
      l_search = Search(self.m_es, self.m_index, self.m_json["_source"]["savedSearchId"])
      l_result.add(l_search)
      l_result.update(l_search.getDepend())
    l_searchSource = json.loads(self.m_json["_source"]["kibanaSavedObjectMeta"]["searchSourceJSON"])
    if "index" in l_searchSource:
      l_result.add(IndexPattern(self.m_es, self.m_index, l_searchSource["index"]))
    return l_result

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
        print("*** Unknown object type '%s' in dashboard" % (c_panel["type"]), file=sys.stderr)
        sys.exit(1)
    return l_result
