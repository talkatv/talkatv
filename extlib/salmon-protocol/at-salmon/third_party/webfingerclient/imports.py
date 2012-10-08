#!/usr/bin/python2.5
#
# Adjust the import paths for third_party and using Google protobufs
#
# Copyright 2009 DeWitt Clinton
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import sys

APP_DIR = os.path.abspath(os.path.dirname(__file__))

THIRD_PARTY = os.path.join(APP_DIR, 'third_party')

sys.path.insert(0, THIRD_PARTY)

if 'google' in sys.modules:
  orig_google_module = sys.modules['google']
  del sys.modules['google']
  # Import google from our path, including third_party
  import google
