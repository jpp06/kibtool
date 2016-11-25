# -*- coding: utf-8 -*-

import os
from nose.tools import *
from io import StringIO
from unittest.mock import patch

import elasticsearch
from elasticsearch import exceptions
import kibtool

from . import KibtoolTestCase

# suppress console err message from http connections
import logging
logging.getLogger("urllib3").setLevel(logging.ERROR)

host, port = os.environ.get('TEST_ES_SERVER', 'localhost:9200').split(':')
port = int(port) if port else 9200

class TestCopyDry(KibtoolTestCase):
  def test_copy_dashid(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--dashid", "dashboard-1",
                                   "--copy", "--dry"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "+++ Copying 'dashboard/dashboard-1' from 'localhost:9200/kibtool-src' to 'localhost:9200/kibtool-dst'")
      self.assertEquals(fake_err.getvalue().strip(), "")

    l_src = self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-1")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_dst = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)


  def test_copy_dash(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--dash", "dashboard 1",
                                   "--copy", "--dry"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "+++ Copying 'dashboard/dashboard-1' from 'localhost:9200/kibtool-src' to 'localhost:9200/kibtool-dst'")
      self.assertEquals(fake_err.getvalue().strip(), "")

    l_src = self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-1")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_dst = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)


  def test_copy_dashid_depend(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--dashid", "dashboard-1",
                                   "--depend", "--copy", "--dry"])
      l_kibtool.execute()
      self.maxDiff = None
      self.assertEquals(fake_out.getvalue().strip(), "+++ Copying 'dashboard/dashboard-1' from 'localhost:9200/kibtool-src' to 'localhost:9200/kibtool-dst'\n\
+++ Copying 'index-pattern/index-pattern-1' from 'localhost:9200/kibtool-src' to 'localhost:9200/kibtool-dst'\n\
+++ Copying 'search/search-1' from 'localhost:9200/kibtool-src' to 'localhost:9200/kibtool-dst'\n\
+++ Copying 'visualization/visualization-1' from 'localhost:9200/kibtool-src' to 'localhost:9200/kibtool-dst'")
      self.assertEquals(fake_err.getvalue().strip(), "")

    l_src = self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-1")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_dst = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)

    l_src = self.client.get(index=l_srcName, doc_type="visualization", id="visualization-1")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_dst = self.client.search(index=l_dstName, doc_type="visualization", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)

    l_src = self.client.get(index=l_srcName, doc_type="search", id="search-1")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_dst = self.client.search(index=l_dstName, doc_type="search", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)

    l_src = self.client.get(index=l_srcName, doc_type="index-pattern", id="index-pattern-1")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_dst = self.client.search(index=l_dstName, doc_type="index-pattern", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)


# ./test_kibtool --kibfrom kibtool-src --kibto kibtool-dst --dashid dashboard-1 --depend --copy
