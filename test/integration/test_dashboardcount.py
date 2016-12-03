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

class TestDashboardCount(KibtoolTestCase):
  def test_copy_dashid(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--dashid", "dashboard-1", "--count", "0",
                                   "--copy"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")

    l_src = self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-1")
    l_srcIdx = l_src.pop("_index")
    l_dst = self.client.get(index=l_dstName, doc_type="dashboard", id="dashboard-1")
    l_dstIdx = l_dst.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    self.assertEquals(l_dstIdx, l_dstName)
    self.assertEquals(l_src, l_dst)

  def test_copy_dash(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--dash", "dashboard 1", "--count", "0",
                                   "--copy"])
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool.execute()
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "*** Please use a greater --count (1) to select all dashboards")

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

  def test_copy_dash2(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--dash", "dashboard", "--count", "1",
                                   "--copy"])
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool.execute()
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "*** Please use a greater --count (3) to select all dashboards")

    l_src = self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-1")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_src = self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-8")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_dst = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)

# ./test_kibtool --kibfrom kibtool-src --kibto kibtool-dst --dashid dashboard-1 --depend --copy
