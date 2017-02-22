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

class TestKibi(KibtoolTestCase):
  def test_kibi(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName,
                                   "--dash", "timeline_d",
                                   "--depend", "--print"])
      l_kibtool.execute()
      l_out = sorted(fake_out.getvalue().strip().split())
      self.assertEquals(l_out, [
        "kibtool-src/dashboard/timeline_d",
        "kibtool-src/index-pattern/gitlab-a-day",
        "kibtool-src/search/timeline_s",
        "kibtool-src/visualization/timeline_v"
      ])
      self.assertEquals(fake_err.getvalue().strip(), "")
