
# -*- coding: utf-8 -*-

import os
import re
import sys
from setuptools import setup

# Utility function to read from file.
def fread(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

def get_version():
  VERSIONFILE="kibtool/_version.py"
  verstrline = fread(VERSIONFILE).strip()
  vsre = r"^__version__ = ['\"]([^'\"]*)['\"]"
  mo = re.search(vsre, verstrline, re.M)
  if mo:
    VERSION = mo.group(1)
  else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))
  build_number = os.environ.get('KIBTOOL_BUILD_NUMBER', None)
  if build_number:
    return VERSION + "b{}".format(build_number)
  return VERSION

def get_install_requires():
  res = ['elasticsearch>=2.4.0,<3.0.0' ]
  return res

try:
  ### cx_Freeze ###
  from cx_Freeze import setup, Executable
  # Dependencies are automatically detected, but it might need
  # fine tuning.
  buildOptions = dict(packages = [], excludes = [])

  base = 'Console'
  icon = None

  kibtool_exe = Executable(
    "run_kibtool.py",
    base=base,
    targetName = "kibtool",
    compress = True
  )

  if sys.platform == "win32":
    kibtool_exe = Executable(
      "run_kibtool.py",
      base=base,
      targetName = "kibtool.exe",
      compress = True,
      icon = icon
    )
  setup(
    name = "jpparis-kibtool",
    version = get_version(),
    author = "Jean-Pierre Paris",
    author_email = "jeanpierre.paris@orange.com",
    description = "Manage your Kibana objects",
    long_description=fread('README.rst'),
    url = "http://github.com/jpparis-orange/kibtool",
    download_url = "https://github.com/jpparis-orange/kibtool/tarball/v" + get_version(),
    license = "Apache License, Version 2.0",
    install_requires = get_install_requires(),
    keywords = "kibana objets tool",
    packages = ["kibtool"],
    include_package_data=True,
    entry_points = {
      "console_scripts" : ["kibtool = kibtool.kibtool:main",]
    },
    classifiers=[
      "Intended Audience :: Developers",
      "Intended Audience :: System Administrators",
      "License :: OSI Approved :: Apache Software License",
      "Operating System :: OS Independent",
      "Programming Language :: Python",
      "Programming Language :: Python :: 3.4",
    ],
    test_suite = "test.run_tests.run_all",
    tests_require = ["mock", "nose", "coverage", "nosexcover", "coveralls"],
    options = {"build_exe" : buildOptions},
    executables = [kibtool_exe]
  )
  ### end cx_Freeze ###
except ImportError:
  setup(
    name = "jpparis-kibtool",
    version = get_version(),
    author = "Jean-Pierre Paris",
    author_email = "jeanpierre.paris@orange.com",
    description = "Manage your Kibana objects",
    long_description=fread('README.rst'),
    url = "http://github.com/jpparis-orange/kibtool",
    download_url = "https://github.com/jpparis-orange/kibtool/tarball/v" + get_version(),
    license = "Apache License, Version 2.0",
    install_requires = get_install_requires(),
    keywords = "kibana objets tool",
    packages = ["kibtool"],
    include_package_data=True,
    entry_points = {
        "console_scripts" : ["kibtool = kibtool.kibtool:main",]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
    ],
    test_suite = "test.run_tests.run_all",
    tests_require = ["mock", "nose", "coverage", "nosexcover", "coveralls"]
  )
