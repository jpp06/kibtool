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

class TestMssingObjects(KibtoolTestCase):
  def test_copy_dash(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--dash", "oups",
                                   "--print"])
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool.execute()
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "*** No dashboard found for 'oups' in index localhost:9200/kibtool-src")

    l_src = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match": {
          "title": "oups"
        }
      }
    })
    self.assertEquals(l_src["hits"]["total"], 0)
    l_dst = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)

  def test_copy_dashid(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--dashid", "oups",
                                   "--copy"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "*** Can not get 'kibtool-src/dashboard/oups' object from 'kibtool-src'")

    l_src = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match": {
          "title": "oups"
        }
      }
    })
    self.assertEquals(l_src["hits"]["total"], 0)
    l_dst = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)

  def test_dash_depend_silent(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--dashid", "oups",
                                   "--depend"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "kibtool-src/dashboard/oups")
      self.assertEquals(fake_err.getvalue().strip(), "*** Can not get 'kibtool-src/dashboard/oups' object from 'kibtool-src'")

  def test_viz_depend_silent(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--visuid", "oups",
                                   "--depend"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "kibtool-src/visualization/oups")
      self.assertEquals(fake_err.getvalue().strip(), "*** Can not get 'kibtool-src/visualization/oups' object from 'kibtool-src'")
