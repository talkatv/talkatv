#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.
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
#

"""Assorted utilities for magicsig module."""

__author__ = 'hjfreyer@google.com (Hunter Freyer)'


import base64
import re
import sys
import time

# ElementTree is standard with Python >=2.5, needs
# environment support for 2.4 and lower.
try:
  import xml.etree.ElementTree as et  # Python >=2.5
except ImportError:
  try:
    import elementtree as et  # Allow local path override
  except ImportError:
    raise

import exceptions
import magicsigalg


class Namespaces(object):
  ATOM_NS_URL = 'http://www.w3.org/2005/Atom'
  ME_NS_URL = 'http://salmon-protocol.org/ns/magic-env'
  THR_NS_URL = 'http://purl.org/syndication/thread/1.0'
  ATOM_NS='{%s}' % ATOM_NS_URL
  ME_NS='{%s}' % ME_NS_URL


class Mimes(object):
  ATOM = 'application/atom+xml'
  JSON = 'application/json'
  JSON_ME = 'application/magic-env+json'
  XML_ME = 'application/magic-env+xml'


_WHITESPACE_RE = re.compile(r'\s+')
def Squeeze(s):  # Remove all whitespace
  return re.sub(_WHITESPACE_RE, '', s)


class DefaultAuthorExtractor(object):
  def ExtractAuthors(self, text, mime_type):
    if mime_type in [Mimes.ATOM]:
      xml = et.XML(text)

      auth_uris = xml.findall(Namespaces.ATOM_NS+'author/'
                              + Namespaces.ATOM_NS+'uri')

      if auth_uris:
        return [NormalizeUserIdToUri(auth_uri.text) for auth_uri in auth_uris]
      else:
        return []
    elif mime_type in [Mimes.JSON]:
      raise NotImplementedError('JSON parsing not implemented')
    else:
      return []


def NormalizeUserIdToUri(userid):
  """Normalizes a user-provided user id to a reasonable guess at a URI."""
  userid = userid.strip()

  # If already in a URI form, we're done:
  if (userid.startswith('http:') or
      userid.startswith('https:') or
      userid.startswith('acct:')):
    return userid

  if userid.find('@') > 0:
    return 'acct:'+userid

  # Catchall:  Guess at http: if nothing else works.
  return 'http://'+userid


class DefaultEncoder(object):
  """Encodes specified data strings."""

  def Encode(self, raw_text_data, encoding):
    """Encodes raw data into an armored form.

    Args:
      raw_text_data: Textual data to be encoded; should be in utf-8 form.
    Returns:
      The encoded data in the specified format.
    """
    if encoding != 'base64url':
      raise exceptions.UnsupportedEncodingError(
          'Encoding must be "base64url", not ' + encoding)

    return base64.urlsafe_b64encode(
        unicode(raw_text_data).encode('utf-8')).encode('utf-8')

  def Decode(self, encoded_text_data, encoding):
    """Decodes armored data into raw text form.

    Args:
      encoded_text_data: Armored data to be decoded.
      encoding: Encoding to use.
    Raises:
      ValueError: If the encoding is unknown.
    Returns:
      The raw decoded text as a string.
    """
    if encoding != 'base64url':
      raise exceptions.UnsupportedEncodingError(
          'Encoding must be "base64url", not ' + encoding)

    return base64.urlsafe_b64decode(encoded_text_data.encode('utf-8'))


def ToPretty(text, indent, linelength):
  """Makes huge text lines pretty, or at least printable."""
  tl = linelength - indent
  output = ''
  for i in range(0, len(text), tl):
    if output:
      output += '\n'
    output += ' ' * indent + text[i:i+tl]
  return output


def PrettyIndent(elem, level=0):
  """Prettifies an element tree in-place"""
  # TODO(jpanzer): Avoid munging text nodes where it matters?
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
       elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      PrettyIndent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i
