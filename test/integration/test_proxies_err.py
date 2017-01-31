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

# to be reviewed
class TestProxiesErr(KibtoolTestCase):
  def test_proxies_err(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool",
                                   "--proxy", "http://nothere.com:1234",
                                   "--cred", "user:pass",
                                   "--kibfrom", l_srcName,
                                   "--dashid", "dashboard-1",
                                   "--print"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "kibtool-src/dashboard/dashboard-1")
      self.assertEquals(fake_err.getvalue().strip(), "")
