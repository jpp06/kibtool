#! /usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from unittest.mock import patch
from nose.tools import *
from io import StringIO

from elasticsearch import Elasticsearch
from elasticsearch import exceptions

import kibtool


class TestKibTool(TestCase):
  def testCtor(self):
    # TODO capture out/err to make more tests
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      kibtool.KibTool(["./kibtool", "--dash", "zzz"])
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")

  def testToLuceneSyntax(self):
    l_req = ""
    l_luceneReq = kibtool.KibTool.toLuceneSyntax("")
    self.assertEquals(l_req, l_luceneReq)
