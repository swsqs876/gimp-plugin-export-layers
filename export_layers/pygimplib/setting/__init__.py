# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2019 khalim19
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This package provides API for handling plug-in settings.
"""

from __future__ import absolute_import, division, print_function, unicode_literals
from future.builtins import *

from .group import *
from .pdbparams import *
from .persistor import *
from .presenter import *
from .presenters_gtk import *
from .settings import *
from .sources import *
from .utils import *

from ._sources_errors import *