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
      "panelsJSON": "[]"
    }
    self.client.create(
      index=p_idx, doc_type="dashboard", id="dashboard-1", body=l_body,
    )


  def close_index(self, name):
    self.client.indices.close(index=name)
