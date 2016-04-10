#
# This file is part of Export Layers.
#
# Copyright (C) 2013-2015 khalim19 <khalim19@gmail.com>
#
# Export Layers is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Export Layers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Export Layers.  If not, see <http://www.gnu.org/licenses/>.
#

"""
This module can be used to unit-test modules which require GIMP to be running.

All modules starting with the "test_" prefix will be executed as unit tests.

All modules not starting with the "test_" prefix will be loaded/reloaded before
executing the unit tests.

To run unit tests in GIMP:

* Open up the Python-Fu console (Filters -> Python-Fu -> Console).
* Run the following commands (you can copy-paste the lines to the console):


import os
import sys
sys.path.append(os.path.join(gimp.directory, "plug-ins"))
sys.path.append(os.path.join(gimp.directory, "plug-ins", "resources"))
import runtests
_ = lambda s: s
_
runtests.run_tests()


* To repeat the tests, paste the following to the console:


_ = lambda s: s
reload(runtests)
_
runtests.run_tests()


The `_` is vital if you are using the `gettext` module for internationalization.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

str = unicode

import __builtin__
import inspect
import importlib
import os
import pkgutil
import sys
import types
import unittest

#===============================================================================

RESOURCES_PATH = os.path.dirname(inspect.getfile(inspect.currentframe()))
PLUGINS_PATH = os.path.dirname(RESOURCES_PATH)

#===============================================================================


# For `gettext`-aware modules that use "_()" and "N_()" functions, define dummy
# functions that simply return the strings, since it's not desired to translate
# them when unit-testing.

def gettext(s):
  return s

if '_' not in __builtin__.__dict__:
  __builtin__.__dict__['_'] = gettext

if 'N_' not in __builtin__.__dict__:
  __builtin__.__dict__['N_'] = gettext


#===============================================================================


def run_test(module, stream=sys.stderr):
  test_suite = unittest.TestLoader().loadTestsFromModule(module)
  test_runner = unittest.TextTestRunner(stream=stream)
  test_runner.run(test_suite)


def load_module(module_name):
  """
  If not imported, import the module specified by its name.
  If already imported, reload the module.
  """
  
  if module_name not in sys.modules:
    module = importlib.import_module(module_name)
  else:
    module = reload(sys.modules[module_name])
  
  return module


def _fix_streams_for_unittest():
  # In the GIMP Python-Fu console, `sys.stdout` and `sys.stderr` are missing
  # the `flush()` method, which needs to be defined in order for the `unittest`
  # module to work properly.
  def flush(self):
    pass
  
  for stream in [sys.stdout, sys.stderr]:
    flush_func = getattr(stream, 'flush', None)
    if flush_func is None or not callable(stream.flush):
      stream.flush = types.MethodType(flush, stream)


#===============================================================================


def run_tests(path=PLUGINS_PATH, test_module_name_prefix="test_",
              ignored_modules=None, output_stream=sys.stderr):
  """
  Execute all modules containing unit tests located in the `path` directory. The
  names of the unit test modules start with the specified prefix (`test_` by
  default).
  
  `ignored_modules` is a list of unit test modules or packages to ignore. If a
  package is specified, all of its underlying modules are ignored.
  
  `output_stream` prints the unit test output using the specified output stream
  (`sys.stderr` by default).
  """
  
  _fix_streams_for_unittest()
  
  if ignored_modules is None:
    ignored_modules = []
  
  for unused_, module_name, unused_ in pkgutil.walk_packages(path=[path]):
    if any(module_name.startswith(ignored_module_name) for ignored_module_name in ignored_modules):
      continue
    
    module = load_module(module_name)
    
    parts = module_name.split(".")
    if parts[-1].startswith(test_module_name_prefix):
      run_test(module, stream=output_stream)

