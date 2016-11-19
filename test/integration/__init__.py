# -*- coding: utf-8 -*-

import time
import os
import shutil
import tempfile
import random
import string
from datetime import timedelta, datetime, date

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

from unittest import SkipTest, TestCase

# suppress console err message from http connections
import logging
logging.getLogger("urllib3").setLevel(logging.ERROR)

client = None
host, port = os.environ.get('TEST_ES_SERVER', 'localhost:9200').split(':')
port = int(port) if port else 9200

def get_client():
  global client
  if client is not None:
    return client

  client = Elasticsearch([os.environ.get('TEST_ES_SERVER', {})], timeout=300)

  # wait for yellow status
  for _ in range(100):
    time.sleep(.1)
    try:
      client.cluster.health(wait_for_status='yellow')
      return client
    except ConnectionError:
      continue
  else:
    # timeout
    raise SkipTest("Elasticsearch failed to start.")

def setup():
  get_client()


class KibtoolTestCase(TestCase):
  def setUp(self):
    super(KibtoolTestCase, self).setUp()
    self.client = get_client()

    args = {
      "prefix": "kibtool-"
    }
    args['host'], args['port'] = host, port
    self.args = args
  def tearDown(self):
    self.client.indices.delete(index=self.args["prefix"] + '*')


  def create_indices(self):
    l_src = self.args['prefix'] + "src"
    l_dst = self.args['prefix'] + "dst"
    self.create_index(l_src, wait_for_yellow=False)
    self.create_index(l_dst, wait_for_yellow=False)
    self.client.cluster.health(wait_for_status='yellow')
    self.add_kibana_base_docs(l_src)
    self.add_kibana_dashboard_docs(l_src)
    self.add_kibana_visualization_docs(l_src)
    self.add_kibana_search_docs(l_src)
    self.add_kibana_index_pattern_docs(l_src)
    self.add_kibana_base_docs(l_dst)
    self.client.indices.flush(index=l_src, force=True)
    self.client.indices.flush(index=l_dst, force=True)
    return l_src, l_dst


  def create_index(self, name, shards=1, wait_for_yellow=True):
    self.client.indices.create(
      index=name,
      body={'settings': {'number_of_shards': shards, 'number_of_replicas': 0}}
    )
    if wait_for_yellow:
      self.client.cluster.health(wait_for_status='yellow')


  def add_kibana_base_docs(self, p_idx):
    l_body = {
      "buildNum": 10146
    }
    self.client.create(
      index=p_idx, doc_type="config", id="4.6.1", body=l_body,
    )
  def add_kibana_dashboard_docs(self, p_idx):
    l_body = {
      "timeFrom": "now-1y",
      "title": "dashboard 1",
      "uiStateJSON": "{}",
      "timeRestore": True,
      "optionsJSON": "{\"darkTheme\":false}",
      "version": 1,
      "timeTo": "now",
      "description": "",
      "hits": 0,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"filter\":[{\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}}}]}"
      },
      "panelsJSON": "[{\"id\":\"visualization-1\",\"type\":\"visualization\",\"panelIndex\":1,\"size_x\":3,\"size_y\":2,\"col\":1,\"row\":1}]",
    }
    self.client.create(
      index=p_idx, doc_type="dashboard", id="dashboard-1", body=l_body,
    )
  def add_kibana_visualization_docs(self, p_idx):
    l_body = {
      "title": "visualization 1",
      "visState": "{\"title\":\"New Visualization\",\"type\":\"histogram\",\"params\":{\"shareYAxis\":true,\"addTooltip\":true,\"addLegend\":true,\"scale\":\"linear\",\"mode\":\"stacked\",\"times\":[],\"addTimeMarker\":false,\"defaultYExtents\":false,\"setYExtents\":false,\"yAxis\":{}},\"aggs\":[{\"id\":\"1\",\"type\":\"count\",\"schema\":\"metric\",\"params\":{}}],\"listeners\":{}}",
      "uiStateJSON": "{}",
      "description": "",
      "savedSearchId": "search-1",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"filter\":[]}"
      }
    }
    self.client.create(
      index=p_idx, doc_type="visualization", id="visualization-1", body=l_body,
    )
  def add_kibana_search_docs(self, p_idx):
    l_body = {
      "title": "search 1",
      "description": "",
      "hits": 0,
      "columns": [ "field", "_id" ],
      "sort": [ "@timestamp", "desc" ],
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"index-pattern-1\",\"filter\":[],\"highlight\":{\"pre_tags\":[\"@kibana-highlighted-field@\"],\"post_tags\":[\"@/kibana-highlighted-field@\"],\"fields\":{\"*\":{}},\"require_field_match\":false,\"fragment_size\":2147483647},\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}}}"
      }
    }
    self.client.create(
      index=p_idx, doc_type="search", id="search-1", body=l_body,
    )
  def add_kibana_index_pattern_docs(self, p_idx):
    l_body = {
      "title": "index-pattern-1",
      "timeFieldName": "@timestamp",
      "fields": "[{\"name\":\"_index\",\"type\":\"string\",\"count\":0,\"scripted\":false,\"indexed\":false,\"analyzed\":false,\"doc_values\":false},{\"name\":\"field\",\"type\":\"string\",\"count\":1,\"scripted\":false,\"indexed\":true,\"analyzed\":true,\"doc_values\":false},{\"name\":\"_source\",\"type\":\"_source\",\"count\":0,\"scripted\":false,\"indexed\":false,\"analyzed\":false,\"doc_values\":false},{\"name\":\"_id\",\"type\":\"string\",\"count\":1,\"scripted\":false,\"indexed\":false,\"analyzed\":false,\"doc_values\":false},{\"name\":\"_type\",\"type\":\"string\",\"count\":0,\"scripted\":false,\"indexed\":false,\"analyzed\":false,\"doc_values\":false},{\"name\":\"_score\",\"type\":\"number\",\"count\":0,\"scripted\":false,\"indexed\":false,\"analyzed\":false,\"doc_values\":false},{\"name\":\"@timestamp\",\"type\":\"date\",\"count\":0,\"scripted\":false,\"indexed\":true,\"analyzed\":false,\"doc_values\":true}]",
      "fieldFormatMap": "{\"@timestamp\":{\"id\":\"date\",\"params\":{\"pattern\":\"DD/MM/YYYY, HH:mm\"}}}"
    }
    self.client.create(
      index=p_idx, doc_type="index-pattern", id="index-pattern-1", body=l_body,
    )


  def close_index(self, name):
    self.client.indices.close(index=name)
