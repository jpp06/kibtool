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
logging.getLogger("elasticsearch").setLevel(logging.ERROR)

host, port = os.environ.get('TEST_ES_SERVER', 'localhost:9200').split(':')
port = int(port) if port else 9200

class TestNone(KibtoolTestCase):
  def test_none(self):
    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")

    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

  def test_no_index_no_read(self):
    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool",
                                   "--kibfrom", self.args["prefix"] + "zzz",
                                   "--print"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")


    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

  def test_no_index_dashid(self):
    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool",
                                   "--kibfrom", self.args["prefix"] + "zzz",
                                   "--dashid", "zzz",
                                   "--print"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "kibtool-zzz/dashboard/zzz")
      self.assertEquals(fake_err.getvalue().strip(), "")

    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )
  @raises(exceptions.NotFoundError)
  def test_no_index_dash(self):
    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool",
                                   "--kibfrom", self.args["prefix"] + "zzz",
                                   "--dash", "zzz",
                                   "--print"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")

    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )
