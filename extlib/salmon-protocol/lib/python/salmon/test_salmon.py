#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.
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

"""Tests for salmon library."""

__author__ = 'jpanzer@google.com (John Panzer)'

import re
import unittest
import salmon
import magicsig


def _StripWS(s):
  """Strips all whitespace from a string."""
  return re.sub('\s+', '', s)


class TestSalmonProtocol(unittest.TestCase):
  """Tests Salmon protocol."""

  class MockKeyRetriever(magicsig.PublicKeyRetriever):
    def LookupPublicKey(self, signer_uri=None):
      return  ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
               'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
               '.AQAB'
               '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
               'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')

  salmonizer = None

  test_atom = """<?xml version='1.0' encoding='UTF-8'?>
    <entry xmlns='http://www.w3.org/2005/Atom'>
    <id>tag:example.com,2009:cmt-0.44775718</id>
      <author><name>test@example.com</name><uri>acct:test@example.com</uri>
      </author>
      <content>Salmon swim upstream!</content>
      <title>Salmon swim upstream!</title>
      <updated>2009-12-18T20:04:03Z</updated>
    </entry>
  """

  test_atom_multi_author = """<?xml version='1.0' encoding='UTF-8'?>
    <entry xmlns='http://www.w3.org/2005/Atom'>
    <id>tag:example.com,2009:cmt-0.44775718</id>
      <author><name>alice@example.com</name><uri>acct:alice@example.com</uri>
      </author>
      <author><name>bob@example.com</name><uri>acct:bob@example.com</uri>
      </author>
      <content>Salmon swim upstream!</content>
      <title>Salmon swim upstream!</title>
      <updated>2009-12-18T20:04:03Z</updated>
    </entry>
  """

  def setUp(self):
    self.salmonizer = salmon.SalmonProtocol()
    self.salmonizer.magicenv.key_retriever = self.MockKeyRetriever()

  def testSignSalmon(self):
    out = self.salmonizer.SignSalmon(self.test_atom,
                                     'application/atom+xml',
                                     'acct:test@example.com')

    self.assertTrue(re.search("<me:env", out))
    self.assertTrue(re.search("<me:data", out))

if __name__ == '__main__':
  unittest.main()
