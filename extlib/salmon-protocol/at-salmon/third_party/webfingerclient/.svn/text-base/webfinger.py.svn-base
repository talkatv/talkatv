#!/usr/bin/python2.5
#
# Provides a WebFinger protocol lookup service.
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

import email.utils
import httplib2
import logging
import re
import sys
import urllib
import urlparse
import xrd

# A simplified version of RFC2822 addr-spec parsing
ATEXT = r'[\w\!\#\$\%\&\'\*\+\-\/\=\?\^\_\`\{\|\}\~]'
ATOM = ''.join(['(?:', ATEXT, '+', ')'])
DOT_ATOM_TEXT = ''.join(['(?:', ATOM, '(?:', r'\.', ATOM, ')', '*', ')'])
DOT_ATOM = DOT_ATOM_TEXT
SCHEME='acct:'  #TODO: Handle HTTP(S)!
COLON_NUMBER = r':[0-9]+'
LOCAL_PART = DOT_ATOM
DOMAIN = DOT_ATOM
OPT_PORT = COLON_NUMBER  # Optional port for use with localhost domain only
ADDR_SPEC = ''.join(['(', SCHEME, ')?', '(', LOCAL_PART, ')', '@', '(', DOMAIN,  ')', '(', OPT_PORT, ')?'])
ADDR_SPEC_RE = re.compile(ADDR_SPEC)

# The URL template for domain-level XRD documents (with hook for localhost port development)
DOMAIN_LEVEL_XRD_TEMPLATE = 'http://%s%s/.well-known/host-meta'

# The rel value used to indicate a user lookup service
WEBFINGER_SERVICE_REL_VALUE = 'lrdd'

class ParseError(Exception):
  """Raised in the event an id can not be parsed."""
  pass

class FetchError(Exception):
  """Raised in the event a URL can not be fetched."""
  pass

class UsageError(Exception):
  """Raised on command-line usage errors."""
  pass

class WebfingerError(Exception):
  """Raised if services found are not valid WebFinger documents."""
  pass

class Client(object):

  def __init__(self, http_client=None, xrd_parser=None):
    """Construct a new WebFinger client.

    Args:
      http_client: A httplib2-like instance [optional]
      xrd_parser: An XRD parser [optional]
    """
    if http_client:
      self._http_client = http_client
    else:
      self._http_client = httplib2.Http()
    if xrd_parser:
      self._xrd_parser = xrd_parser
    else:
      self._xrd_parser = xrd.Parser()

  def lookup(self, id):
    """Look up a webfinger resource by (email-like) id.

    Args:
      id: An account identifier
    Returns:
      A list of discovered xrd_pb2.Xrd instances.
    Raises:
      FetchError if a URL can not be retrieved.
      ParseError if a description can not be parsed.
    """
    logging.info('Incoming id is %s' % id)
    id = self._normalize_id(id)
    logging.info('Normalized id to %s' % id)
    try:
      addr, scheme, local_part, domain, opt_port = self._parse_id(id)
    except ParseError:
      r = urlparse.urlparse(id)
      domain = r.netloc
      opt_port = None
    links = self._get_webfinger_service_links(domain, opt_port)
    service_descriptions = list()
    for link in links:
      if link.template:
        service_descriptions.append(
            self._get_service_description(link.template, id))
      if link.href:
        service_descriptions.append(
            self._get_service_description(link.href, id))
    return service_descriptions

  def _normalize_id(self, id):
    """Normalize the account identifier.

    Args:
      id: An account identifier
    Returns:
      A normalized account identifier, if possible.
    """
    #if id.startswith('acct://'):
    #  return id[7:]
    #elif id.startswith('acct:'):
    #  return id[5:]
    return id

  def _get_service_description(self, template, id):
    """Retrieve and XRD or XFN instance from a xrd_pb2.Link.

    Args:
      template: A URI template string or URI string
      id: An account identifier
    Returns:
      Either a xrd_pb2.Xrd or a xfn_pb2.Xfn instance (depending on the
      service type).
    """
    service_url = self._interpolate_webfinger_template(template, id)
    logging.info('Fetching service url %s' % service_url)
    content = self._fetch_url(service_url)
    return self._xrd_parser.parse(content)

  def _interpolate_webfinger_template(self, template, id):
    """Replaces occurances of {id} and {%id} within a webfinger template.

    Args:
      template: A webfinger URI template
      id: A identity string
    Returns:
      The template with {id} and {%id} replaced
    """
    for variable in ['{uri}', '{%uri}', '{id}', '{%id}']:
      template = template.replace(variable, urllib.quote(id))
    return template

  def _get_webfinger_service_links(self, domain, opt_port):
    """Finds potential webfinger service links.

    Args:
      A domain name
      An optional port (only for use in development)
    Returns:
      A list of xrd_pb2.Link instances of the webfinger service type
    """
    if not opt_port:
      opt_port = ''
    domain_url = DOMAIN_LEVEL_XRD_TEMPLATE % (domain, opt_port)
    logging.info('Fetching domain url %s' % domain_url)
    content = self._fetch_url(domain_url)
    domain_xrd = self._xrd_parser.parse(content)
    links = list()
    for link in domain_xrd.links:
      if link.rel == WEBFINGER_SERVICE_REL_VALUE:
        links.append(link)
    return links

  def _parse_id(self, id):
    """Treats an identifier as a restricted RFC2822 addr-spec and splits it.

    Args:
      id: An account identifier
    Returns:
      The tuple (addr_spec, local_part, domain [,port]) if it can be parsed
    Raises:
      ParseError if the id can not be parsed
    """
    #realname, addr_spec = email.utils.parseaddr(id)
    #if not addr_spec:
    #  raise ParseError('Could not parse %s for addr-spec' % id)
    match = ADDR_SPEC_RE.match(id)
    if not match:
      raise ParseError('Could not parse %s for local_part, domain' % id)
    return id, match.group(1), match.group(2), match.group(3), match.group(4)

  def _fetch_url(self, url):
    """Fetch a URL.

    Args:
      url: The URL to fetch
    Returns:
      The content of the URL on successful (200 OK) responses
    Raises:
      FetchError if the URL can not be retrieved
    """
    try:
      response, content = self._http_client.request(url)
    except Exception, e:  # This is hackish
      raise FetchError('Could not fetch %s. Host down? %s' % (url, e))
    if response.status != 200:
      raise FetchError(
        'Could not fetch %s. Status %d.' % (url, response.status))
    return content

def main(argv):
  if len(argv) < 2:
    raise UsageError('Usage webfinger.py id')
  client = Client()
  for description in client.lookup(argv[1]):
    print description

if __name__ == "__main__":
  main(sys.argv)
