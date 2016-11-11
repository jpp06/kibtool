#! /usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import *

from elasticsearch import Elasticsearch
from elasticsearch import exceptions

import kibtool


class TestKObject(TestCase):
  def testCtor(self):
    l_obj = kibtool.KObject(None, "an_index", "a_type", "an_id")
    self.assertEquals(str(l_obj), "an_index/a_type/an_id")
  def testEq(self):
    l_obj1 = kibtool.KObject(1, "an_index", "a_type", "an_id")
    l_obj2 = kibtool.KObject(2, "an_index", "a_type", "an_id")
    self.assertEquals(l_obj1, l_obj2)
  @raises(exceptions.ConnectionError)
  def testReadFromEs(self):
    l_es = Elasticsearch(hosts=[{ "host": "nowwhere", "port": 1234}])
    l_obj = kibtool.KObject(l_es, "an_index", "a_type", "an_id")
    l_obj.readFromEs()
  @raises(exceptions.ConnectionError)
  def testCopyFromTo(self):
    l_es = Elasticsearch(hosts=[{ "host": "nowwhere", "port": 1234}])
    l_obj = kibtool.KObject(l_es, "an_index", "a_type", "an_id")
    l_obj.m_json = {"_source":{}} # dont readFromEs
    l_obj.copyFromTo(l_es, "dst_index")
