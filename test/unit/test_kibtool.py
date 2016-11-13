#! /usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import *

from elasticsearch import Elasticsearch
from elasticsearch import exceptions

import kibtool


class TestKibTool(TestCase):
  def testCtor(self):
    # TODO capture out/err to make more tests
    kibtool.KibTool(["./kibtool"])

  def testToLuceneSyntax(self):
    l_req = ""
    l_luceneReq = kibtool.KibTool.toLuceneSyntax("")
    self.assertEquals(l_req, l_luceneReq)
