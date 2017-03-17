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

class TestCheck(KibtoolTestCase):
  def test_check_dash(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName,
                                   "--dashid", "dashboard-2",
                                   "--check"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "--- object 'kibtool-src/visualization/no-visu' is missing in 'dashboard-2'")
      self.assertEquals(fake_err.getvalue().strip(), "")

  def test_check_visu(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName,
                                   "--visuid", "visualization-2",
                                   "--check"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "--- object 'kibtool-src/search/no-search' is missing in 'visualization-2'")
      self.assertEquals(fake_err.getvalue().strip(), "")

  def test_check_dash_visu(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName,
                                   "--dashid", "dashboard-2",
                                   "--visuid", "visualization-2",
                                   "--check"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "--- object 'kibtool-src/search/no-search' is missing in 'visualization-2'\n\
--- object 'kibtool-src/visualization/no-visu' is missing in 'dashboard-2'")
      self.assertEquals(fake_err.getvalue().strip(), "")
