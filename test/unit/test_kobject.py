#! /usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import *
from io import StringIO
from unittest.mock import patch

from elasticsearch import Elasticsearch
from elasticsearch import exceptions

import kibtool


class TestKObject(TestCase):
  def testCtor(self):
    l_obj = kibtool.KObject(None, "an_index", "a_type", "an_id")
    self.assertEquals(str(l_obj), "an_index/a_type/an_id")

  def testBuild(self):
    l_obj = kibtool.KObject.build(None, "an_index", "dashboard", "an_id")
    self.assertEquals(str(l_obj), "an_index/dashboard/an_id")
    l_obj = kibtool.KObject.build(None, "an_index", "visualization", "an_id")
    self.assertEquals(str(l_obj), "an_index/visualization/an_id")
    l_obj = kibtool.KObject.build(None, "an_index", "search", "an_id")
    self.assertEquals(str(l_obj), "an_index/search/an_id")
    l_obj = kibtool.KObject.build(None, "an_index", "index-pattern", "an_id")
    self.assertEquals(str(l_obj), "an_index/index-pattern/an_id")
    l_obj = kibtool.KObject.build(None, "an_index", "config", "an_id")
    self.assertEquals(str(l_obj), "an_index/config/an_id")

  def testBuildErr(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_obj = kibtool.KObject.build(None, "an_index", "a_type", "an_id")
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "*** Unknown Kibana object type 'a_type'")

  def testEq(self):
    l_obj1 = kibtool.KObject(1, "an_index", "a_type", "an_id")
    l_obj2 = kibtool.KObject(2, "an_index", "a_type", "an_id")
    self.assertEquals(l_obj1, l_obj2)

  def testNeq(self):
    l_obj1 = kibtool.KObject(1, "an_index", "a_type", "an_id")
    l_obj2 = kibtool.KObject(2, "an_index1", "a_type", "an_id")
    self.assertNotEquals(l_obj1, l_obj2)
    l_obj1 = kibtool.KObject(1, "an_index", "a_type", "an_id")
    l_obj2 = kibtool.KObject(2, "an_index", "a_type1", "an_id")
    self.assertNotEquals(l_obj1, l_obj2)
    l_obj1 = kibtool.KObject(1, "an_index", "a_type", "an_id")
    l_obj2 = kibtool.KObject(2, "an_index", "a_type", "an_id1")
    self.assertNotEquals(l_obj1, l_obj2)

  @raises(exceptions.ConnectionError)
  def testReadFromEs(self):
    l_es = Elasticsearch(hosts=[{ "host": "nowwhere", "port": 1234}])
    l_obj = kibtool.KObject(l_es, "an_index", "a_type", "an_id")
    l_obj.readFromEs()

  @raises(exceptions.ConnectionError)
  def testCopyToEs(self):
    l_es = Elasticsearch(hosts=[{ "host": "nowwhere", "port": 1234}])
    l_obj = kibtool.KObject(l_es, "an_index", "a_type", "an_id")
    l_obj.m_json = {"_source":{}} # dont readFromEs
    l_obj.readFromEs()
    l_obj.copyToEs(l_es, "dst_index")


class TestConfig(TestCase):
  def testCtor(self):
    l_obj = kibtool.Config(None, "an_index", "an_id")
    self.assertEquals(str(l_obj), "an_index/config/an_id")


class TestIndexPattern(TestCase):
  def testCtor(self):
    l_obj = kibtool.IndexPattern(None, "an_index", "an_id")
    self.assertEquals(str(l_obj), "an_index/index-pattern/an_id")


class TestSearch(TestCase):
  def testCtor(self):
    l_obj = kibtool.Search(None, "an_index", "an_id")
    self.assertEquals(str(l_obj), "an_index/search/an_id")


class TestVisualization(TestCase):
  def testCtor(self):
    l_obj = kibtool.Visualization(None, "an_index", "an_id")
    self.assertEquals(str(l_obj), "an_index/visualization/an_id")
  @raises(exceptions.ConnectionError)
  def testGetDepend(self):
    l_es = Elasticsearch(hosts=[{ "host": "nowwhere", "port": 1234}])
    l_obj = kibtool.Visualization(l_es, "an_index", "an_id")
    l_obj.getDepend()


class TestDashboard(TestCase):
  def testCtor(self):
    l_obj = kibtool.Dashboard(None, "an_index", "an_id")
    self.assertEquals(str(l_obj), "an_index/dashboard/an_id")
  @raises(exceptions.ConnectionError)
  def testGetDepend(self):
    l_es = Elasticsearch(hosts=[{ "host": "nowwhere", "port": 1234}])
    l_obj = kibtool.Visualization(l_es, "an_index", "an_id")
    l_obj.getDepend()

