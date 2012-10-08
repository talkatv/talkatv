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

import mox

import copy
import re
import time
import unittest
try:
  import google3  # GOOGLE local modification
except ImportError:
  pass

import exceptions
import magicsig_hjfreyer as magicsig
import utils


TEST_PUBLIC_KEY = ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
               'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
               '.AQAB'
               '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
               'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')

TEST_PRIVATE_KEY = ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
                    'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
                    '.AQAB'
                    '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
                    'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')

TEST_ATOM = """<?xml version='1.0' encoding='UTF-8'?>
<entry xmlns='http://www.w3.org/2005/Atom'>
  <id>tag:example.com,2009:cmt-0.44775718</id>
  <author><name>test@example.com</name><uri>acct:test@example.com</uri>
  </author>
  <content>Salmon swim upstream!</content>
  <title>Salmon swim upstream!</title>
  <updated>2009-12-18T20:04:03Z</updated>
</entry>
"""

TEST_NON_ATOM = 'Some aribtrary string.'

TEST_ENVELOPE = magicsig.Envelope(
    data="""PD94bWwgdmVyc2lvbj0nMS4wJyBlbmNvZGluZz0nVVRGLTgnPz4KPGVu
    dHJ5IHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20nPgog
    IDxpZD50YWc6ZXhhbXBsZS5jb20sMjAwOTpjbXQtMC40NDc3NTcxODwv
    aWQ-CiAgPGF1dGhvcj48bmFtZT50ZXN0QGV4YW1wbGUuY29tPC9uYW1l
    Pjx1cmk-YWNjdDp0ZXN0QGV4YW1wbGUuY29tPC91cmk-CiAgPC9hdXRo
    b3I-CiAgPGNvbnRlbnQ-U2FsbW9uIHN3aW0gdXBzdHJlYW0hPC9jb250
    ZW50PgogIDx0aXRsZT5TYWxtb24gc3dpbSB1cHN0cmVhbSE8L3RpdGxl
    PgogIDx1cGRhdGVkPjIwMDktMTItMThUMjA6MDQ6MDNaPC91cGRhdGVk
    Pgo8L2VudHJ5Pgo=""",
    data_type='application/atom+xml',
    sig="""RL3pTqRn7RAHoEKwtZCVDNgwHrNB0WJxFt8fq6l0HAGcIN4BLYzUC5hp
    GySsnow2ibw3bgUVeiZMU0dPfrKBFA==""")

TEST_NON_ATOM_ENVELOPE = magicsig.Envelope(
    data='U29tZSBhcmlidHJhcnkgc3RyaW5nLg==',
    data_type='text/plain',
    sig="""hmx89hQgxhGqWHWh_vK8W0_-9agxSkTQ8w1DUXt6BzZ7oY2iZM89p7mS
    TJJfeR4qNTWMGqTtTtmg0Caro1tRgA==""")

class MagicEnvelopeProtocolTest(unittest.TestCase):
  """Tests Magic Envelope protocol."""

  def setUp(self):
    self.mox = mox.Mox()
    self.key_get = self.mox.CreateMock(magicsig.KeyRetriever)
    self.extractor = self.mox.CreateMock(utils.DefaultAuthorExtractor)

    self.protocol = magicsig.MagicEnvelopeProtocol(
        key_retriever=self.key_get,
        author_extractor=self.extractor,
        auto_verify=False)

  def tearDown(self):
    self.mox.VerifyAll()

  def testSigning(self):
    self.extractor.ExtractAuthors(TEST_ATOM,
                                  'application/atom+xml').AndReturn(
        ['acct:test@example.com'])
    self.key_get.LookupPrivateKey('acct:test@example.com').AndReturn(
        TEST_PRIVATE_KEY)
    self.mox.ReplayAll()

    envelope = self.protocol.WrapAndSign(data=TEST_ATOM,
                                         data_type='application/atom+xml')

    self.assertEquals(TEST_ENVELOPE, envelope)

  def testSigningNonAtom(self):
    self.extractor.ExtractAuthors(TEST_NON_ATOM, 'text/plain').AndReturn(
        ['acct:test@example.com'])
    self.key_get.LookupPrivateKey('acct:test@example.com').AndReturn(
        TEST_PRIVATE_KEY)

    self.extractor.ExtractAuthors(TEST_NON_ATOM, 'text/plain').AndReturn(
        ['acct:test@example.com'])
    self.key_get.LookupPublicKey('acct:test@example.com').AndReturn(
        TEST_PUBLIC_KEY)
    self.mox.ReplayAll()

    envelope = self.protocol.WrapAndSign(
        data=TEST_NON_ATOM,
        data_type='text/plain')

    self.assertEquals(TEST_NON_ATOM_ENVELOPE, envelope)

    assert self.protocol.VerifyEnvelope(envelope)

  def testVerify(self):
    self.extractor.ExtractAuthors(TEST_ATOM,
                                  'application/atom+xml'
                                  ).AndReturn(['acct:test@example.com'])
    self.key_get.LookupPublicKey('acct:test@example.com').AndReturn(
        TEST_PUBLIC_KEY)
    self.mox.ReplayAll()

    self.assertTrue(self.protocol.VerifyEnvelope(TEST_ENVELOPE))

  def testVerifyWithWrongPublicKey(self):
    self.extractor.ExtractAuthors(TEST_ATOM,
                                  'application/atom+xml'
                                  ).AndReturn(['acct:test@example.com'])
    self.key_get.LookupPublicKey('acct:test@example.com').AndReturn(
        TEST_PUBLIC_KEY.replace('B', 'b'))
    self.mox.ReplayAll()

    self.assertFalse(self.protocol.VerifyEnvelope(TEST_ENVELOPE))

  def testVerifyNoPublicKeyFound(self):
    self.extractor.ExtractAuthors(TEST_ATOM,
                                  'application/atom+xml'
                                  ).AndReturn(['acct:test@example.com'])
    self.key_get.LookupPublicKey('acct:test@example.com').AndReturn(None)
    self.mox.ReplayAll()

    self.assertRaises(exceptions.KeyNotFoundError,
                      self.protocol.VerifyEnvelope,
                      TEST_ENVELOPE)

  def testTampering(self):
    self.extractor.ExtractAuthors(TEST_ATOM,
                                  'application/atom+xml'
                                  ).AndReturn(['acct:test@example.com'])
    self.key_get.LookupPublicKey('acct:test@example.com').AndReturn(
        TEST_PUBLIC_KEY)
    self.mox.ReplayAll()

    envelope = copy.copy(TEST_ENVELOPE)
    envelope.sig = envelope.sig.replace('DNgwHrN', 'ANgwHrN')

    self.assertFalse(self.protocol.VerifyEnvelope(envelope))

  def testToAtom(self):
    text = self.protocol.ToAtomString(TEST_ENVELOPE)

    assert re.search('atom:entry',text)
    assert re.search('me:provenance',text)
    assert re.search('test@example\.com',text)

  def testToXml(self):
    text = self.protocol.ToXmlString(TEST_ENVELOPE)

    expected = """<?xmlversion='1.0'encoding='UTF-8'?>
    <me:envxmlns:me='http://salmon-protocol.org/ns/magic-env'>
    <me:encoding>base64url</me:encoding>
    <me:datatype='application/atom+xml'>PD94bWwgdmVyc2lvbj0nMS4wJyBlb
    mNvZGluZz0nVVRGLTgnPz4KPGVudHJ5IHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy
    8yMDA1L0F0b20nPgogIDxpZD50YWc6ZXhhbXBsZS5jb20sMjAwOTpjbXQtMC40NDc
    3NTcxODwvaWQ-CiAgPGF1dGhvcj48bmFtZT50ZXN0QGV4YW1wbGUuY29tPC9uYW1l
    Pjx1cmk-YWNjdDp0ZXN0QGV4YW1wbGUuY29tPC91cmk-CiAgPC9hdXRob3I-CiAgP
    GNvbnRlbnQ-U2FsbW9uIHN3aW0gdXBzdHJlYW0hPC9jb250ZW50PgogIDx0aXRsZT
    5TYWxtb24gc3dpbSB1cHN0cmVhbSE8L3RpdGxlPgogIDx1cGRhdGVkPjIwMDktMTI
    tMThUMjA6MDQ6MDNaPC91cGRhdGVkPgo8L2VudHJ5Pgo=</me:data>
    <me:alg>RSA-SHA256</me:alg>
    <me:sig>RL3pTqRn7RAHoEKwtZCVDNgwHrNB0WJxFt8fq6l0HAGcIN4BLYzUC5hpGy
    Ssnow2ibw3bgUVeiZMU0dPfrKBFA==</me:sig>
    </me:env>"""

    self.assertEquals(utils.Squeeze(text), utils.Squeeze(text))

  def testVerifyMakesEnvelopeFresh(self):
    self.extractor.ExtractAuthors(TEST_ATOM,
                                  'application/atom+xml'
                                  ).AndReturn(['acct:test@example.com'])
    self.key_get.LookupPublicKey('acct:test@example.com').AndReturn(
      TEST_PUBLIC_KEY)
    self.mox.ReplayAll()

    self.assertEquals(0, self.protocol.GetDateLastVerified(TEST_ENVELOPE))
    self.protocol.VerifyEnvelope(TEST_ENVELOPE)

    self.assertTrue(0 < self.protocol.GetDateLastVerified(TEST_ENVELOPE))


class ProtocolEndToEndTest(unittest.TestCase):
  """Tests Magic Envelope protocol with default handlers."""
  # TODO: Add tests that actually call webfinger?
  pass


if __name__ == '__main__':
  unittest.main()
