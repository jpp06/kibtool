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

class TestDelete(KibtoolTestCase):
  def test_delete_dashid(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName,
                                   "--dashid", "dashboard-1",
                                   "--delete"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")

    try:
      self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-1")
      self.assertTrue(False, "dashboard-1 still present")
    except exceptions.NotFoundError as e:
      pass
    l_dst = self.client.search(index=l_dstName, doc_type="*", body={"query": {"match_all": {}}})
    self.assertEquals(l_dst["hits"]["total"], 0)


  def test_delete_dash(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName,
                                   "--dash", "dashboard 1",
                                   "--delete"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")

    try:
      self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-1")
      self.assertTrue(False, "dashboard-1 still present")
    except exceptions.NotFoundError as e:
      pass
    l_src = self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-8")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_dst = self.client.search(index=l_dstName, doc_type="*", body={"query": {"match_all": {}}})
    self.assertEquals(l_dst["hits"]["total"], 0)

  def test_delete_dashid_depend(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName,
                                   "--dashid", "dashboard-1",
                                   "--depend", "--delete"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")

    try:
      self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-1")
      self.assertTrue(False, "dashboard-1 still present")
    except exceptions.NotFoundError as e:
      pass

    try:
      self.client.get(index=l_srcName, doc_type="visualization", id="visualization-1")
      self.assertTrue(False, "dashboard-1 still present")
    except exceptions.NotFoundError as e:
      pass

    try:
      self.client.get(index=l_srcName, doc_type="search", id="search-1")
      self.assertTrue(False, "dashboard-1 still present")
    except exceptions.NotFoundError as e:
      pass

    try:
      self.client.get(index=l_srcName, doc_type="index-pattern", id="index-pattern-1")
      self.assertTrue(False, "dashboard-1 still present")
    except exceptions.NotFoundError as e:
      pass

    l_dst = self.client.search(index=l_dstName, doc_type="*", body={"query": {"match_all": {}}})
    self.assertEquals(l_dst["hits"]["total"], 0)


  def test_delete_all(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName,
                                     "--dash", "*",
                                     "--delete"])
        self.assertEqual(w_se.exception, "Error")

      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "--- Trying to delete all from source index. Use --force if you are sure")

    l_src = self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-1")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_dst = self.client.search(index=l_dstName, doc_type="*", body={"query": {"match_all": {}}})
    self.assertEquals(l_dst["hits"]["total"], 0)


  def test_force_delete_all(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName,
                                   "--dash", "*",
                                   "--delete", "--force"])

      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")

    l_src = self.client.get(index=l_srcName, doc_type="dashboard", id="dashboard-1")
    l_srcIdx = l_src.pop("_index")
    self.assertEquals(l_srcIdx, l_srcName)
    l_dst = self.client.search(index=l_dstName, doc_type="*", body={"query": {"match_all": {}}})
    self.assertEquals(l_dst["hits"]["total"], 0)

# ./test_kibtool --kibfrom kibtool-src --dashid dashboard-1 --depend --delete
