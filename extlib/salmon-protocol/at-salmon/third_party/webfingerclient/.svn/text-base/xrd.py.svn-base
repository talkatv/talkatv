#!/usr/bin/python2.5
#
# Parses XRD documents.
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
import xrd_pb2

# As specified in:
#   http://www.oasis-open.org/committees/download.php/33772/xrd-1.0-wd04.html
XRD_NAMESPACE = 'http://docs.oasis-open.org/ns/xri/xrd-1.0'

# As specifed in http://www.w3.org/TR/xml-names/
XML_NAMESPACE = 'http://www.w3.org/XML/1998/namespace'

# As specified in http://www.w3.org/TR/xmlschema-1/
XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'

# The etree syntax for qualified element names
XRD_QNAME              = '{%s}%s' % (XRD_NAMESPACE, 'XRD')
EXPIRES_QNAME          = '{%s}%s' % (XRD_NAMESPACE, 'Expires')
SUBJECT_QNAME          = '{%s}%s' % (XRD_NAMESPACE, 'Subject')
PROPERTY_QNAME         = '{%s}%s' % (XRD_NAMESPACE, 'Property')
ALIAS_QNAME            = '{%s}%s' % (XRD_NAMESPACE, 'Alias')
LINK_QNAME             = '{%s}%s' % (XRD_NAMESPACE, 'Link')
TITLE_QNAME            = '{%s}%s' % (XRD_NAMESPACE, 'Title')

# The etree syntax for qualified attribute names
ID_ATTRIBUTE           = '{%s}%s' % (XML_NAMESPACE, 'id')
LANG_ATTRIBUTE         = '{%s}%s' % (XML_NAMESPACE, 'lang')
NIL_ATTRIBUTE          = '{%s}%s' % (XSI_NAMESPACE, 'nil')

class ParseError(Exception):
  """Raised in the event an XRD document can not be parsed."""
  pass


class Parser(object):
  """Converts XML documents into xrd_pb2.Xrd instances."""

  def __init__(self, etree=None):
    """Constructs a new XRD parser.

    Args:
      etree: The etree module to use [optional]
    """
    if etree:
      self._etree = etree
    else:
      import xml.etree.cElementTree
      self._etree = xml.etree.cElementTree

  def parse(self, string):
    """Converts XML strings into an xrd_pb2.Xrd instances

    Args:
      string: A string containing an XML XRD document.
    Returns:
      A xrd_pb2.Xrd instance.
    Raises:
      ParseError if the element can not be parsed
    """
    if not string:
      raise ParseError('Empty input string.')
    try:
      document = self._etree.fromstring(string)
    except SyntaxError, e:
      raise ParseError('Could not parse %s\nError: %s' % (string, e))
    if document.tag != XRD_QNAME:
      raise ParseError('Root is not an <XRD/> element: %s' % document)
    description = xrd_pb2.Xrd()
    self._parse_id(document, description)
    self._parse_expires(document, description)
    self._parse_subject(document, description)
    self._parse_properties(document, description)
    self._parse_aliases(document, description)
    self._parse_links(document, description)
    return description

  def _parse_id(self, xrd_element, description):
    """Finds a xml:id attribute and adds it to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance to be added to
    """
    id_attribute = xrd_element.get(ID_ATTRIBUTE)
    if id_attribute is not None:
      description.id = id_attribute

  def _parse_expires(self, xrd_element, description):
    """Finds an Expires element and adds it to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance to be added to
    """
    expires_element = xrd_element.find(EXPIRES_QNAME)
    if expires_element is not None:
      description.expires = expires_element.text

  def _parse_subject(self, xrd_element, description):
    """Finds an Subject element and adds it to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance to be added to
    """
    subject_element = xrd_element.find(SUBJECT_QNAME)
    if subject_element is not None:
      description.subject = subject_element.text

  def _parse_properties(self, xrd_element, description):
    """Finds Property elements and adds them to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance to be added to
    """
    for property_element in xrd_element.findall(PROPERTY_QNAME):
      property_pb = description.properties.add()
      property_pb.nil = (property_element.get(NIL_ATTRIBUTE) == 'true')
      property_type = property_element.get('type')
      if property_type != None:
        property_pb.type = property_type
      if property_element.text is not None:
        property_pb.value = property_element.text

  def _parse_aliases(self, xrd_element, description):
    """Finds Alias elements and adds them to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance added to
    """
    for alias_element in xrd_element.findall(ALIAS_QNAME):
      description.aliases.append(alias_element.text)

  def _parse_links(self, xrd_element, description):
    """Finds Link elements and adds them to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance to be added to
    """
    for link_element in xrd_element.findall(LINK_QNAME):
      link = description.links.add()
      rel = link_element.get('rel')
      if rel is not None:
        link.rel = rel
      type_attribute = link_element.get('type')
      if type_attribute is not None:
        link.type = type_attribute
      href = link_element.get('href')
      if href is not None:
        link.href = href
      template = link_element.get('template')
      if template is not None:
        link.template = template
      self._parse_properties(link_element, link)
      self._parse_titles(link_element, link)

  def _parse_titles(self, xrd_element, description):
    """Finds Title elements and adds them to the proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance to be added to
    """
    for title_element in xrd_element.findall(TITLE_QNAME):
      title = description.titles.add()
      lang = title_element.get(LANG_ATTRIBUTE)
      if lang is not None:
        title.lang = lang
      if title_element.text is not None:
        title.value = title_element.text


class JsonMarshaller(object):

  def __init__(self):
    try:
      import simplejson as json
    except ImportError:
      import json
    self._json = json

  def to_json(self, description_or_descriptions, pretty=False):
    if isinstance(description_or_descriptions, list):
      output = list()
      for description in description_or_descriptions:
        output.append(self._to_object(description))
    else:
      output = self._to_object(description_or_descriptions)
    if pretty:
      return self._json.dumps(output, indent=2)
    else:
      return self._json.dumps(output)

  def _to_object(self, description):
    output = dict()
    if description.id:
      output['id'] = description.id
    if description.expires:
      output['expires'] = description.expires
    if description.subject:
      output['subject'] = description.subject
    if description.aliases:
      output['aliases'] = [str(alias) for alias in description.aliases]
    if description.properties:
      for p in description.properties:
        output['properties'].append({'type': p.type, 'value': p.value})
    if description.links:
      output['links'] = list()
      for link in description.links:
        link_dict = dict()
        if link.rel:
          link_dict['rel'] = link.rel
        if link.type:
          link_dict['type'] = link.type
        if link.href:
          link_dict['href'] = link.href
        if link.template:
          link_dict['template'] = link.template
        if link.titles:  # TODO(dewitt): Change spec to have only a single title
          link_dict['titles'] = list()
          for title in link.titles:
            title_dict = dict()
            if title.lang:
              title_dict['lang'] = title.lang
            if title.value:
              title_dict['value'] = title.value
            link_dict['titles'].append(title_dict)
        output['links'].append(link_dict)
    return output
