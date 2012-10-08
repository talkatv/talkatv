#!/usr/bin/python
#
# Copyright 2009 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for discovery.py."""

__author__ = 'jpanzer@google.com (John Panzer)'

import unittest
import discovery
#import simplejson as json # TODO(jpanzer): Use or dike out.


class DiscoveryTest(unittest.TestCase):
  def setUp(self):
    # TODO(jpanzer): Set up.
    return

  def testDiscoveryIntegration(self):
    """Tests basic integration with external discovery service."""
    # Fails due to this bug:
    # http://code.google.com/p/webfingerclient-dclinton/issues/detail?id=2
    #s = discovery.discover('does_not_exist_at_all_no_sirree@example.org')
    #self.assertEquals(s,None)

    s = discovery.discover('jpanzer.at.acm@gmail.com')
    self.assertNotEqual(s, None)

  def testPublicKeyDiscoveryIntegration(self):
    """Tests public key discovery integration with external service."""
    si = discovery.discover_signing_info('jpanzer.at.acm@gmail.com')
    self.assertNotEqual(si, None)

    self.assertEqual(si['identity'], 'acct:jpanzer.at.acm@gmail.com')
    self.assertEqual(si['public_keys'], [])

