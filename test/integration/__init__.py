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

class Args(dict):
    def __getattr__(self, att_name):
        return self.get(att_name, None)

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

  def create_indices(self, count, unit=None):
    self.create_index(self.args['prefix'] + datetime(d.year, d.month, 1).strftime(format), wait_for_yellow=False)
    self.client.cluster.health(wait_for_status='yellow')

  def create_index(self, name, shards=1, wait_for_yellow=True):
    self.client.indices.create(
      index=name,
      body={'settings': {'number_of_shards': shards, 'number_of_replicas': 0}}
    )
    if wait_for_yellow:
      self.client.cluster.health(wait_for_status='yellow')

  def add_docs(self, idx):
    for i in ["1", "2", "3"]:
      self.client.create(
        index=idx, doc_type='log', id=i,
        body={"doc" + i :'TEST DOCUMENT'},
      )
      # This should force each doc to be in its own segment.
      self.client.indices.flush(index=idx, force=True)

  def close_index(self, name):
    self.client.indices.close(index=name)

  def write_config(self, fname, data):
    with open(fname, 'w') as f:
      f.write(data)
