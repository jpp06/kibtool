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

class TestMissingIndices(KibtoolTestCase):
  def test_missing_index_read(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", "_my_dummy_index_",
                                   "--dash", "dashboard",
                                   "--print"])
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool.execute()
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "*** Can't search in unknown index _my_dummy_index_")

    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

  def test_missing_index_write(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--kibto", "_my_dummy_index_",
                                   "--dash", "dashboard",
                                   "--copy"])
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool.execute()
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "*** Can't write to unknown index _my_dummy_index_")

    self.assertEquals(
      ['kibtool-dst', 'kibtool-src'],
      sorted(list(self.client.indices.get(self.args["prefix"] + "*").keys()))
    )
