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

"""Tests for magicsig.py."""

__author__ = 'jpanzer@google.com (John Panzer)'

import re
import unittest
try:
  import google3  # GOOGLE local modification
except ImportError:
  pass
import magicsig

#import sys


def _StripWS(s):
  """Strips all whitespace from a string."""
  return re.sub('\s+', '', s)


class TestMagicEnvelopeProtocol(unittest.TestCase):
  """Tests Magic Envelope protocol."""

  class MockKeyRetriever(magicsig.KeyRetriever):
    def LookupPublicKey(self, signer_uri):
      assert signer_uri
      return  ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
               'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
               '.AQAB'
               '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
               'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')

  magicenv = None
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
    self.magicenv = magicsig.MagicEnvelopeProtocol()
    self.magicenv.key_retriever = self.MockKeyRetriever()

  def testGetSignerURI(self):
    # Trival case of one author:
    a = self.magicenv.GetSignerURI(self.test_atom)
    self.assertEquals(a, 'acct:test@example.com')

    # Multi author case:
    a = self.magicenv.GetSignerURI(self.test_atom_multi_author)
    self.assertEquals(a, 'acct:alice@example.com')

  def testIsAllowedSigner(self):
    # Check that we can recognize the author
    self.assertTrue(self.magicenv.IsAllowedSigner(self.test_atom,
                                                  'acct:test@example.com'))

    # Method requires a real URI
    self.assertFalse(self.magicenv.IsAllowedSigner(self.test_atom,
                                                   'test@example.com'))

    # We recognize only the first of multiple authors
    self.assertTrue(self.magicenv.IsAllowedSigner(self.test_atom_multi_author,
                                                  'acct:alice@example.com'))
    self.assertFalse(self.magicenv.IsAllowedSigner(self.test_atom_multi_author,
                                                   'acct:bob@example.com'))

  def testNormalizeUserIds(self):
    id1 = 'http://example.com'
    id2 = 'https://www.example.org/bob'
    id3 = 'acct:bob@example.org'
    em3 = 'bob@example.org'

    self.assertEquals(magicsig.NormalizeUserIdToUri(id1), id1)
    self.assertEquals(magicsig.NormalizeUserIdToUri(id2), id2)
    self.assertEquals(magicsig.NormalizeUserIdToUri(id3), id3)
    self.assertEquals(magicsig.NormalizeUserIdToUri(em3), id3)
    self.assertEquals(magicsig.NormalizeUserIdToUri(' '+id1+' '), id1)


TEST_PRIVATE_KEY = ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
                    'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
                    '.AQAB'
                    '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
                    'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')


class TestMagicEnvelope(unittest.TestCase):
  """Tests the Envelope class."""

  class MockKeyRetriever(magicsig.KeyRetriever):
    def LookupPublicKey(self, signer_uri):
      assert signer_uri
      return TEST_PRIVATE_KEY

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

  def setUp(self):
    self.protocol = magicsig.MagicEnvelopeProtocol()
    self.protocol.key_retriever = self.MockKeyRetriever()

  def testInvalidEnvelopes(self):
    self.assertRaises(magicsig.EnvelopeError, magicsig.Envelope, 'blah')
    try:
      magicsig.Envelope(foo=5, biff=23)
      # Should never get here
      self.assertTrue(None)
    except magicsig.Error:
      pass
      # e = sys.exc_info()[1]
      #print "Exception: %s" % e
      #print "Invalid envelope: %s" % e.invalid_envelope

  def testSigning(self):
    envelope = magicsig.Envelope(
        self.protocol,
        raw_data_to_sign=self.test_atom,
        signer_uri='acct:test@example.com',
        signer_key=TEST_PRIVATE_KEY,
        data_type='application/atom+xml',
        encoding='base64url',
        alg='RSA-SHA256')

    # Turn envelope into text:
    xml = envelope.ToXML()

    # Now round-trip it:
    magicsig.Envelope(
        self.protocol,
        mime_type='application/magic-envelope+xml',
        document=xml)

    # Getting here without an exception is success.

  def testToAtom(self):
    envelope = magicsig.Envelope(
        self.protocol,
        raw_data_to_sign=self.test_atom,
        signer_uri='acct:test@example.com',
        signer_key=TEST_PRIVATE_KEY,
        data_type='application/atom+xml',
        encoding='base64url',
        alg='RSA-SHA256')

    text = envelope.ToAtom()

    assert re.search('atom:entry',text)
    assert re.search('me:provenance',text)
    assert re.search('test@example\.com',text)

  def testTampering(self):
    envelope = magicsig.Envelope(
        self.protocol,
        raw_data_to_sign=self.test_atom,
        signer_uri='acct:test@example.com',
        signer_key=TEST_PRIVATE_KEY,
        data_type='application/atom+xml',
        encoding='base64url',
        alg='RSA-SHA256')

    xml = envelope.ToXML()

    self.assertRaises(Exception,
                      magicsig.Envelope,
                      self.protocol,
                      mime_type='application/magic-envelope+xml',
                      document=re.sub('U2FsbW9', 'U2GsbW9', xml))

if __name__ == '__main__':
  unittest.main()
