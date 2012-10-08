#!/usr/bin/python2.5
#
# Parses HTML documents for XFN links.
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

import imports
import xfn_pb2


class ParseError(Exception):
  """Raised in the event an HTML document can not be parsed."""
  pass


class Parser(object):
  """Converts HTML documents into xfn_pb2.Xfn instances."""

  def __init__(self, html_parser=None, etree=None):
    """Constructs a new XFN parser.

    Args:
      html_parser: The HTMLParser instance to use. [optional]
      etree: The etree module to use [optional]
    """
    if etree:
      self._etree = etree
    else:
      import xml.etree.cElementTree
      self._etree = xml.etree.cElementTree
    if html_parser:
      self._html_parser = html_parser
    else:
      import html5lib.treebuilders
      etree_builder = html5lib.treebuilders.getTreeBuilder("etree", self._etree)
      import html5lib
      self._html_parser = html5lib.HTMLParser(etree_builder)

  def parse(self, string):
    """Converts HTML strings into an xfn_pb2.Xfn instances

    Args:
      string: A string containing an HTML document.
    Returns:
      A xfn_pb2.Xfn instance.
    Raises:
      ParseError if the string can not be parsed
    """
    if not string:
      raise ParseError('Empty input string.')
    document = self._html_parser.parse(string)
    if not document:
      raise ParseError('Could not parse document as HTML.')
    # TODO(dewitt): Honor the base attribute/element
    xfn = xfn_pb2.Xfn()
    # Process <a> tags in the HTML document
    for a in document.findall('.//a'):
      href = a.get('href')
      rels = a.get('rel', '').split()
      if href and 'me' in rels:
        xfn_link = xfn.links.add()
        xfn_link.href = href
        if a.text is not None:
          xfn_link.title = a.text
        for rel in rels:
          xfn_link.relations.append(rel)
    # Process <link> tags in the HTML document
    for link in document.findall('.//link'):
      href = link.get('href')
      rels = link.get('rel', '').split()
      type = link.get('type')
      title = link.get('title')
      if href and 'me' in rels:
        xfn_link = xfn.links.add()
        xfn_link.href = href
        if title is not None:
          xfn_link.title = title
        if type is not None:
          xfn_link.type = type
        for rel in rels:
          xfn_link.relations.append(rel)
    return xfn
