# -*- coding: utf-8 -*-

import os
from nose.tools import *
from io import StringIO
from unittest.mock import patch

import elasticsearch
from elasticsearch import exceptions
import kibtool

from . import KibtoolTestCase

class TestFai(KibtoolTestCase):
  def test_dash1(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--filefrom", "test/integration/v4/dash1.json",
                                     "--fai"])
        l_kibtool.execute()
      l_out = sorted(fake_out.getvalue().strip().split("\n"))
      self.assertEqual(l_out, [
        "--- No fields or indicies needed for the selected objects."
      ])
      self.assertEqual(fake_err.getvalue().strip(), "")

  def test_dash2(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--filefrom", "test/integration/v4/dash2.json",
                                     "--fai"])
        l_kibtool.execute()
      l_out = sorted(fake_out.getvalue().strip().split("\n"))
      self.assertEqual(l_out, [
        "--- field5 field",
        "--- index6 index"
      ])
      self.assertEqual(fake_err.getvalue().strip(), "")

  def test_dash3(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--filefrom", "test/integration/v4/dash3.json",
                                     "--fai"])
        l_kibtool.execute()
      l_out = sorted(fake_out.getvalue().strip().split("\n"))
      self.assertEqual(l_out, [
        "--- field5 field",
        "--- field6 field",
        "--- index6 index",
        "--- index7 index"
      ])
      self.assertEqual(fake_err.getvalue().strip(), "")

  def test_search1(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--filefrom", "test/integration/v4/search1.json",
                                     "--fai"])
        l_kibtool.execute()
      l_out = sorted(fake_out.getvalue().strip().split("\n"))
      self.assertEqual(l_out, [
        "--- field0 field",
        "--- field10 field",
        "--- field12 field",
        "--- field13 field",
        "--- field16 field",
        "--- field20 field",
        "--- field8 field",
        "--- field9 field",
        "--- index2 index"
      ])
      self.assertEqual(fake_err.getvalue().strip(), "")

  def test_search2(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--filefrom", "test/integration/v4/search2.json",
                                     "--fai"])
        l_kibtool.execute()
      l_out = sorted(fake_out.getvalue().strip().split("\n"))
      self.assertEqual(l_out, [
        "--- field0 field",
        "--- field10 field",
        "--- field12 field",
        "--- field13 field",
        "--- field14 field",
        "--- field16 field",
        "--- field17 field",
        "--- field18 field",
        "--- field20 field",
        "--- field4 field",
        "--- field5 field",
        "--- field6 field",
        "--- field7 field",
        "--- field8 field",
        "--- field9 field",
        "--- index2 index",
        "--- index6 index"
      ])
      self.assertEqual(fake_err.getvalue().strip(), "")

  def test_visu1(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--filefrom", "test/integration/v4/visu1.json",
                                     "--fai"])
        l_kibtool.execute()
      l_out = sorted(fake_out.getvalue().strip().split("\n"))
      self.assertEqual(l_out, [
        "--- field13 field",
        "--- index1 index",
        "--- index6 index"
      ])
      self.assertEqual(fake_err.getvalue().strip(), "")

  def test_all(self):
    with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
      with self.assertRaises(SystemExit) as w_se:
        l_kibtool = kibtool.KibTool(["./test_kibtool", "--filefrom", "test/integration/v4/kibana.json",
                                     "--fai"])
        l_kibtool.execute()
      l_out = sorted(fake_out.getvalue().strip().split("\n"))
      self.assertEqual(l_out, [
        "--- field0 field",
        "--- field1 field",
        "--- field10 field",
        "--- field11 field",
        "--- field12 field",
        "--- field13 field",
        "--- field14 field",
        "--- field15 field",
        "--- field16 field",
        "--- field17 field",
        "--- field18 field",
        "--- field19 field",
        "--- field2 field",
        "--- field20 field",
        "--- field21 field",
        "--- field22 field",
        "--- field23 field",
        "--- field3 field",
        "--- field4 field",
        "--- field5 field",
        "--- field6 field",
        "--- field7 field",
        "--- field8 field",
        "--- field9 field",
        "--- index0 index",
        "--- index1 index",
        "--- index2 index",
        "--- index3 index",
        "--- index4 index",
        "--- index5 index",
        "--- index6 index"
      ])
      self.assertEqual(fake_err.getvalue().strip(), "")
