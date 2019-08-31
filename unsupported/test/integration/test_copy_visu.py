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

class TestCopyVisu(KibtoolTestCase):
  def test_copy_visuid(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--visuid", "visualization-1",
                                   "--copy"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")
    l_dst = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)
    l_src = self.client.get(index=l_srcName, doc_type="visualization", id="visualization-1")
    l_srcIdx = l_src.pop("_index")
    l_dst = self.client.get(index=l_dstName, doc_type="visualization", id="visualization-1")
    l_dstIdx = l_dst.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    self.assertEquals(l_dstIdx, l_dstName)
    self.assertEquals(l_src, l_dst)

  def test_copy_visu(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--visu", "visualization 1",
                                   "--copy"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")

    l_dst = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)
    l_src = self.client.get(index=l_srcName, doc_type="visualization", id="visualization-1")
    l_srcIdx = l_src.pop("_index")
    l_dst = self.client.get(index=l_dstName, doc_type="visualization", id="visualization-1")
    l_dstIdx = l_dst.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    self.assertEquals(l_dstIdx, l_dstName)
    self.assertEquals(l_src, l_dst)

  def test_copy_visuid_depend(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--visuid", "visualization-1",
                                   "--depend", "--copy"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")


    l_dst = self.client.search(index=l_dstName, doc_type="dashboard", body={
      "query": {
        "match_all": {
        }
      }
    })
    self.assertEquals(l_dst["hits"]["total"], 0)
    l_src = self.client.get(index=l_srcName, doc_type="visualization", id="visualization-1")
    l_srcIdx = l_src.pop("_index")
    l_dst = self.client.get(index=l_dstName, doc_type="visualization", id="visualization-1")
    l_dstIdx = l_dst.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    self.assertEquals(l_dstIdx, l_dstName)
    self.assertEquals(l_src, l_dst)

    l_src = self.client.get(index=l_srcName, doc_type="search", id="search-1")
    l_srcIdx = l_src.pop("_index")
    l_dst = self.client.get(index=l_dstName, doc_type="search", id="search-1")
    l_dstIdx = l_dst.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    self.assertEquals(l_dstIdx, l_dstName)
    self.assertEquals(l_src, l_dst)

    l_src = self.client.get(index=l_srcName, doc_type="index-pattern", id="index-pattern-1")
    l_srcIdx = l_src.pop("_index")
    l_dst = self.client.get(index=l_dstName, doc_type="index-pattern", id="index-pattern-1")
    l_dstIdx = l_dst.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    self.assertEquals(l_dstIdx, l_dstName)
    self.assertEquals(l_src, l_dst)


# ./test_kibtool --kibfrom kibtool-src --kibto kibtool-dst --visuid visualization-1 --depend --copy
