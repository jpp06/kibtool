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

class TestUtf8(KibtoolTestCase):
  def test_visu_utf8(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName,
                                   "--dashid", "dashboard-8",
                                   "--depend", "--print"])
      l_kibtool.execute()
      l_out = fake_out.getvalue().strip()
      self.assertTrue("\\xc3\\xa0" in l_out, "utf8 char not found")
      self.assertEquals(fake_err.getvalue().strip(), "")

  def test_visu_utf8_copy(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", l_dstName,
                                   "--dashid", "dashboard-8",
                                   "--depend", "--copy", "--print", "--debug"])
      l_kibtool.execute()
      self.assertTrue("\\xc3\\xa0" in fake_out.getvalue().strip(), "utf8 char not found")
      self.assertTrue("\\xc3\\xa0" in fake_err.getvalue().strip(), "utf8 char not found")

# ./test_kibtool --kibfrom kibtool-src --kibto kibtool-dst --dashid dashboard-1 --depend --copy
