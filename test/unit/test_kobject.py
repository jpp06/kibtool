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

  def testCmp(self):
    l_obj1 = kibtool.KObject(1, "1", "2", "3")
    l_obj2 = kibtool.KObject(2, "4", "5", "6")
    self.assertTrue(l_obj1 < l_obj2)
    self.assertFalse(l_obj1 > l_obj2)
    self.assertFalse(l_obj1 == l_obj2)

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


class TestFai(TestCase):
  def testString(self):
    l_obj = kibtool.KObject(None, "an_index", "a_type", "an_id")
    self.assertEquals(l_obj.getFieldsAndIndicies(), set())
    l_fai = l_obj.getFieldsFromQueryString("*")
    self.assertEquals(l_fai, set())
    l_fai = l_obj.getFieldsFromQueryString("F:V")
    self.assertEquals(l_fai, set([ ("F", "field") ]))
    l_fai = l_obj.getFieldsFromQueryString("_exists_:F")
    self.assertEquals(l_fai, set([ ("F", "field") ]))
    l_fai = l_obj.getFieldsFromQueryString("_missing_:F")
    self.assertEquals(l_fai, set([ ("F", "field") ]))
    l_fai = l_obj.getFieldsFromQueryString("F1:V1 OR F2:V2")
    self.assertEquals(l_fai, set([ ("F1", "field"), ("F2", "field") ]))
    l_fai = l_obj.getFieldsFromQueryString("F1:V1 AND F2:V2")
    self.assertEquals(l_fai, set([ ("F1", "field"), ("F2", "field") ]))
    l_fai = l_obj.getFieldsFromQueryString("NOT F:V")
    self.assertEquals(l_fai, set([ ("F", "field") ]))
    l_fai = l_obj.getFieldsFromQueryString("(F1:this OR F2:this) AND (F1:that OR F2:that)")
    self.assertEquals(l_fai, set([ ("F1", "field"), ("F2", "field") ]))

  def testStringError(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_obj = kibtool.KObject(None, "an_index", "a_type", "an_id")
      with self.assertRaises(SystemExit) as w_se:
        l_fai = l_obj.getFieldsFromQueryString("F1:this TOTO F2:this")
        self.assertEqual(w_se.exception, "Error")
    self.assertEquals(fake_out.getvalue().strip(), "")
    self.assertEquals(fake_err.getvalue().strip(), "***FFQS \"F1:this TOTO F2:this\" {('F1', 'field')}")

  def testQuery(self):
    l_obj = kibtool.KObject(None, "an_index", "a_type", "an_id")
    l_fai = l_obj.getFieldsFromQuery({})
    self.assertEquals(l_fai, set())
    l_fai = l_obj.getFieldsFromQuery({"match":{"F":"V"}})
    self.assertEquals(l_fai, set([ ("F", "field") ]))

  def testQueryError(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_obj = kibtool.KObject(None, "an_index", "a_type", "an_id")
      with self.assertRaises(SystemExit) as w_se:
        l_fai = l_obj.getFieldsFromQuery({"toto":{"F":"V"}})
        self.assertEqual(w_se.exception, "Error")
    self.assertEquals(fake_out.getvalue().strip(), "")
    self.assertEquals(fake_err.getvalue().strip(), "***FFQ {\"toto\": {\"F\": \"V\"}}")

  def testExpr(self):
    l_obj = kibtool.KObject(None, "an_index", "a_type", "an_id")
    l_fai = l_obj.getFaiFromExpression("")
    self.assertEquals(l_fai, set())
    l_fai = l_obj.getFaiFromExpression(".es(index='I1', timefield='F1',kibana='true').label( 'label0') .es(index=' I2', timefield='F2',kibana='true').label('label3')")
    self.assertEquals(l_fai, set([ ("F1", "field"), ("F2", "field"), ("I1", "index"), ("I2", "index") ]))

#  {“query”: { “match”: { “_all”: “meaning” } } }
