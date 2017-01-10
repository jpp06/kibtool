# -*- coding: utf-8 -*-

import os
import sys
import json
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

def getTypeIdFromFile(p_filename):
  l_result= []
  with open(p_filename, "r") as w_in:
    l_line = w_in.readline()
    while l_line:
      l_meta = json.loads(l_line)
      l_result.append(l_meta["index"]["_type"] + "/" + l_meta["index"]["_id"])
      l_data = w_in.readline()
      l_line = w_in.readline()
    return l_result

class TestReadWrite(KibtoolTestCase):
  def test_read_err(self):
    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--filefrom"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, " error: argument --filefrom: expected one argument$")

    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))
  def test_write_err(self):
    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--fileto"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, " error: argument --fileto: expected one argument$")

    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

  def test_read_esfrom_err(self):
    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--filefrom", "fake_file", "--esfrom", "localhost:9200", "--dash", "fake_dash"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, " error: arguments --filefrom and --esfrom/--kibfrom are incompatible$")

    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

  def test_read_kibfrom_err(self):
    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--filefrom", "fake_file", "--kibfrom", "fake_index", "--dash", "fake_dash"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, " error: arguments --filefrom and --esfrom/--kibfrom are incompatible$")

    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

  def test_write_esto_err(self):
    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--fileto", "fake_file", "--esto", "localhost:9200", "--dash", "fake_dash"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, " error: arguments --fileto and --esto/--kibto are incompatible$")

    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

  def test_write_kibto_err(self):
    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--fileto", "fake_file", "--kibto", "fake_index", "--dash", "fake_dash"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, " error: arguments --fileto and --esto/--kibto are incompatible$")

    self.assertEquals([], list(self.client.indices.get(self.args["prefix"] + "*").keys()))

  #def test_write_delete_err

  # copy and fileto are incompatible

  def test_write(self):
    (l_srcName, l_dstName) = self.create_indices()
    l_file = "fake_file"

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--kibfrom", l_srcName, "--fileto", l_file, "--visuid", "visualization-1", "--depend"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "")
      self.assertEquals(fake_err.getvalue().strip(), "")
      l_ids = getTypeIdFromFile(l_file)
      self.assertEquals(l_ids, ["index-pattern/index-pattern-1", "search/search-1", "visualization/visualization-1"])

  def test_orphan_with_selector(self):
    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--orphan", "--dash", "zzz"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, "with --orphan, no --dash, --dashid, .* expected$")

    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

  def test_orphan_no_dst(self):
    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--orphan", "--kibto", self.args["prefix"] + "zzz"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, "--orphan and --kibto are incompatible$")

    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )
  def test_orphan_no_check(self):
    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--orphan", "--check"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, "--orphan and --check are incompatible$")

    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )
  def test_orphan_no_copy(self):
    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--orphan", "--copy"])
        self.assertEqual(w_se.exception, "Error")
      self.assertEquals(fake_out.getvalue().strip(), "")
      l_err = fake_err.getvalue().strip()
      self.assertEquals(l_err[:7], "usage: ")
      self.assertRegex(l_err, "--orphan and --copy are incompatible$")

    self.assertEquals(
      [],
      list(self.client.indices.get(self.args["prefix"] + "*").keys())
    )

  def test_orphan(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--orphan", "--kibfrom", l_srcName])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "visualization-2")
      self.assertEquals(fake_err.getvalue().strip(), "")

    self.assertEquals(
      ["kibtool-dst", "kibtool-src"],
      sorted(list(self.client.indices.get(self.args["prefix"] + "*").keys()))
    )

  def test_orphan_delete(self):
    (l_srcName, l_dstName) = self.create_indices()

    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      l_kibtool = kibtool.KibTool(["./test_kibtool", "--orphan", "--kibfrom", l_srcName, "--delete"])
      l_kibtool.execute()
      self.assertEquals(fake_out.getvalue().strip(), "visualization-2")
      self.assertEquals(fake_err.getvalue().strip(), "")

    self.assertEquals(
      ["kibtool-dst", "kibtool-src"],
      sorted(list(self.client.indices.get(self.args["prefix"] + "*").keys()))
    )
    self.client.get(index=l_srcName, doc_type="visualization", id="visualization-1")
    with self.assertRaises(elasticsearch.exceptions.NotFoundError) as w_se:
      l_src = self.client.get(index=l_srcName, doc_type="visualization", id="visualization-2")
      self.assertEqual(w_se.exception, "Error")
