#!/usr/bin/python2.5
#
# Implements a simple web-based WebFinger client.
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

import imports  # Must be imported first to fix the third_party path

import html5lib
import html5lib.treebuilders
import httplib2
import logging
import os
import re
import simplejson
import sys
import urllib
import webfinger
import xrd

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api.memcache import Client
from xml.etree import cElementTree as etree

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

template.register_template_library('templatefilters')


# Enable a caching HTTP client
MEMCACHE_CLIENT = Client()
HTTP_CLIENT = httplib2.Http(MEMCACHE_CLIENT)

# Create a reusable HTML5 parser
ETREE_BUILDER = html5lib.treebuilders.getTreeBuilder("etree", etree)
HTML_PARSER = html5lib.HTMLParser(ETREE_BUILDER)

# This is totally nonstandard, but we need something
BINARY_PROTOBUF_MIMETYPE = 'application/x-protobuf'
ASCII_PROTOBUF_MIMETYPE = 'text/plain'
JSON_MIMETYPE = 'application/json'


UNSAFE_HTML_CHARS = re.compile(r'[^\w\,\.\s\'\:\/\-\_\?]')

UNSAFE_JSON_CHARS = re.compile(r'[^\w\d\-\_]')

WELL_KNOWN_REL_VALUES = {
    'http://portablecontacts.net/spec/1.0': 'Portable Contacts',
    'http://webfinger.net/rel/profile-page': 'Profile',
    'http://microformats.org/profile/hcard': 'HCard',
    'http://gmpg.org/xfn/11': 'XFN',
    'http://specs.openid.net/auth/2.0/provider': 'OpenID',
}

def sanitize(string):
  """Allow only very safe chars through."""
  return UNSAFE_HTML_CHARS.sub('', string)


def sanitize_callback(string):
  """Only allow valid json function identifiers through"""
  if UNSAFE_JSON_CHARS.search(string):
    return None
  else:
    return string

# Abstract base class for all page view classes
class AbstractPage(webapp.RequestHandler):

  def _render_template(self, template_name, template_values={}):
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    self.response.out.write(template.render(template_path, template_values))

  def _error(self, message):
    self.redirect("/?error=%s" % urllib.quote(sanitize(message)))


# Renders the main page of the site at '/'
class MainPage(AbstractPage):

  def get(self):
    error = self.request.get('error')
    return self._render_template('main.tmpl', {'error': sanitize(error)})


# Renders the results of the lookup page
class LookupPage(AbstractPage):

  def get(self):
    identifier = self.request.get('identifier')
    if not identifier:
      return self._error('Please enter an address')
    client = webfinger.Client(http_client=HTTP_CLIENT)
    try:
      descriptions = client.lookup(identifier)
    except Exception, e:
      return self._error(str(e))
    format = self.request.get('format')
    template_values = dict()
    template_values['identifier'] = identifier
    template_values['descriptions'] = descriptions
    template_values['relationships'] = WELL_KNOWN_REL_VALUES
    if format == 'html':  # A simple HTML-only response
      self._render_template('xrd-html.tmpl', template_values)
    elif format == 'protoa':  # ASCII protobufs
      self.response.headers['Content-Type'] = ASCII_PROTOBUF_MIMETYPE
      output = '\n'.join([str(p) for p in descriptions])
      self.response.out.write(output)
    elif format == 'proto':  # Binary protobufs
      self.response.headers['Content-Type'] = BINARY_PROTOBUF_MIMETYPE
      output = '\n'.join([p.SerializeToString() for p in descriptions])
      self.response.out.write(output)
    elif format == 'json' or self.request.get('callback'):  # JSON or JSONP
      self.response.headers['Content-Type'] = JSON_MIMETYPE
      marshaller = xrd.JsonMarshaller()
      pretty = self.request.get('pretty') in ['true', 'TRUE', 'pretty', '1']
      output = marshaller.to_json(descriptions, pretty=pretty)
      callback = sanitize_callback(self.request.get('callback'))
      if callback:
        output = '%s(%s)' % (callback, output)
      self.response.out.write(output)
    else:  # format == 'web'
      self._render_template('lookup.tmpl', template_values)

# Global application dispatcher
application = webapp.WSGIApplication(
  [('/', MainPage),
   ('/lookup', LookupPage)],
  debug=True)


def main():
  logging.debug('Initializing.')
  run_wsgi_app(application)

if __name__ == "__main__":
  main()  # run once
