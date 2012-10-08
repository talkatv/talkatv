#!/usr/bin/python2.4
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

"""Command line example of magic signatures."""

__author__ = 'jpanzer@google.com (John Panzer)'

import re
import unittest
try:
  import google3  # GOOGLE local modification
except ImportError:
  pass
import magicsig


TEST_PRIVATE_KEY = ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
                    'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
                    '.AQAB'
                    '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
                    'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')


class DemoMagicEnvelope():
  """Demos the Envelope class."""

  class MockKeyRetriever(magicsig.KeyRetriever):
    def LookupPublicKey(self, signer_uri):
      assert signer_uri
      return TEST_PRIVATE_KEY

  test_atom = """<?xml version='1.0' encoding='UTF-8'?>
<entry xmlns='http://www.w3.org/2005/Atom'>
  <id>tag:example.com,2009:cmt-0.44775718</id>
  <author><name>Test</name><uri>acct:test@example.com</uri></author>
  <content>Salmon swim upstream!</content>
  <title>Salmon swim upstream!</title>
  <updated>2009-12-18T20:04:03Z</updated>
</entry>"""

  #def setUp(self):
  #  self.protocol = magicsig.MagicEnvelopeProtocol()
  #  self.protocol.key_retriever = self.MockKeyRetriever()

  def dump(self):
    envelope = magicsig.Envelope(
        raw_data_to_sign=self.test_atom,
        signer_uri='acct:test@example.com',
        signer_key=TEST_PRIVATE_KEY,
        data_type='application/atom+xml',
        encoding='base64url',
        alg='RSA-SHA256')

    # Turn envelope into text:
    xml = envelope.ToXML()

    # And provenanced Atom:
    atom = envelope.ToAtom()

    print "Original data:\n%s\n" % self.test_atom
    print "Magic Envelope:\n%s\n" % xml
    print "Atom with provenance:\n%s\n" % atom


if __name__ == '__main__':
  DemoMagicEnvelope().dump()
