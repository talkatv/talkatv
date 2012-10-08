#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Tests for utils."""

__author__ = 'hjfreyer@google.com (Hunter Freyer)'

import re
import unittest
import utils


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

TEST_ATOM_MULTI_AUTHOR = """<?xml version='1.0' encoding='UTF-8'?>
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

class UtilsTest(unittest.TestCase):

  def setUp(self):
    self.extractor = utils.DefaultAuthorExtractor()

  def testSqueeze(self):
    self.assertEquals('qwerty', utils.Squeeze('  q wer t     y  '))

  def testExtractAuthor(self):
    # Trival case of one author:
    a = self.extractor.ExtractAuthors(TEST_ATOM, mime_type=utils.Mimes.ATOM)
    self.assertEquals(['acct:test@example.com'], a)

    # Multi author case:
    a = self.extractor.ExtractAuthors(TEST_ATOM_MULTI_AUTHOR,
                                      mime_type=utils.Mimes.ATOM)
    self.assertEquals(['acct:alice@example.com', 'acct:bob@example.com'], a)

  def testNormalizeUserIds(self):
    id1 = 'http://example.com'
    id2 = 'https://www.example.org/bob'
    id3 = 'acct:bob@example.org'
    em3 = 'bob@example.org'

    self.assertEquals(id1, utils.NormalizeUserIdToUri(id1))
    self.assertEquals(id2, utils.NormalizeUserIdToUri(id2))
    self.assertEquals(id3, utils.NormalizeUserIdToUri(id3))
    self.assertEquals(id3, utils.NormalizeUserIdToUri(em3))
    self.assertEquals(id1, utils.NormalizeUserIdToUri(' '+id1+' '))


if __name__ == '__main__':
  googletest.main()
