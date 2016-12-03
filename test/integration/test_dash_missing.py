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

class TestDashMissing(KibtoolTestCase):
  def test_dash_missing(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", "_my_dummy_index_", "--print"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, "--dash, --dashid, .* required$")

    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))
