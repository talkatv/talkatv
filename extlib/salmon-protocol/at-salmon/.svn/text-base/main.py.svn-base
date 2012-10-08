#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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

import os
import datetime
import re
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import logging

import xml.etree.ElementTree as et
import imports
import magicsig
import webfingerclient.webfinger as webfinger
import simplejson as json
import datamodel
import comment_handler
import profile_handler

class MainHandler(webapp.RequestHandler):

  def get(self):
    self.redirect('/comment');


class RealKeyRetriever(magicsig.KeyRetriever):
  """Retrieves public or private keys for a signer identifier (URI)."""
  client = webfinger.Client()
  
  def LookupPublicKey(self, signer_uri):
    logging.info('Looking up public key for %s' % signer_uri)
    if not signer_uri:
      return None
    xrd_list = self.client.lookup(signer_uri)
    for item in xrd_list:
      logging.info("Got webfinger result for %s: %s" % (id, item))
      # item is a Xrd proto2, not a string, no need to decode.
      subject = item.subject
      key_urls = [link.href for link in item.links if link.rel == 'magic-public-key']
      logging.info('Found magic public keys: subject %s, %s' % (subject, key_urls))    

    # TODO(jpanzer): Yeah, we need key identifiers.
    KEY_RE=re.compile("data:application/magic-public-key,(RSA.+)")
    match = KEY_RE.match(key_urls[0])
    if match:
      return match.group(1)
    else:
      return None

class SalmonSlapHandler(webapp.RequestHandler):
  def post(self):
    # Retrieve putative Salmon from input body.
    body = self.request.body
    mime_type = self.request.headers['Content-Type']

    protocol = magicsig.MagicEnvelopeProtocol()
    protocol.key_retriever = RealKeyRetriever()
    logging.info("Saw body:\n%s\n" % body)
    envelope = magicsig.Envelope(
        protocol,
        document=body,
        mime_type=mime_type)
    # If we got here, the Salmon validated.

    # Grab out the fields of interest:
    entry = envelope.GetParsedData().getroot()

    s = et.tostring(entry,encoding='utf-8')
    logging.info('Saw entry:\n%s\n' % s)

    ns = '{http://www.w3.org/2005/Atom}'
    ans = '{http://activitystrea.ms/spec/1.0/}'
    author=entry.findtext(ns+'author/'+ns+'uri')
    posted_at_str=entry.findtext(ns+'updated')
    content=entry.findtext(ns+'content')
    if not content:
      content=entry.findtext(ans+'object/'+ns+'content')
    if not content:
      content=entry.findtext(ns+'summary')
    if not content:
      content=entry.findtext(ns+'title')
    if not content:
      content=''
    content=content.strip()
    logging.info('Content = %s' % content)

    # Ensure we have a virtual profile for remote user!
    p = profile_handler.ensure_virtual_profile(author)  # TODO: WRITE THIS FUNCTION!!!                                             )

    mentions = comment_handler.extract_mentions(content)

    logging.info('About to add: author=%s, content=%s, mentions=%s' % (author,
                                                                       content,
                                                                       mentions))
    c = datamodel.Comment(
        author_profile=p,
        posted_at=datetime.datetime.now(),  #TODO: should convert posted_at_str,
        content=content,
        mentions=mentions)
    c.put()
    self.response.set_status(202)
    self.response.out.write("Salmon accepted!\n")

# Following handlers implement a ghetto version of lrdd.
# Should package this up and make it more real and make
# it easy to drop into a webapp.

class GhettoHostMeta(webapp.RequestHandler):
  path = os.path.join(os.path.dirname(__file__), 'host-meta.xml')

  def get(self):
    host = self.request.headers['Host']
    vals = dict(hostauthority='http://%s' % host,
                host=re.sub(':[0-9]+','',host))
    self.response.out.write(template.render(self.path,
                                            vals))
    self.response.set_status(200)

class GhettoUserXRD(webapp.RequestHandler):
  path = os.path.join(os.path.dirname(__file__), 'user-xrd.xml')

  def get(self):
    user_uri = self.request.get('q')
    host = self.request.headers['Host']

    # Is the profile one we know about?
    logging.info('Getting profile for %s' % user_uri)
    p = profile_handler.get_profile_by_uri(user_uri)
    key = p.public_key

    # The following will recurse if we have no public keys for our
    # own users, which would be a problem.
    if not key:
      key = magicsig.KeyRetriever().LookupPublicKey(user_uri)

    keyuri = 'data:application/magic-public-key;%s' % key

    vals = dict(subject=user_uri, keyuri=keyuri, host=host)
    self.response.out.write(template.render(self.path,
                                            vals))

# End of ghetto lrdd

def main():
  application = webapp.WSGIApplication(
      [
          ('/', MainHandler),
          ('/comment.*', comment_handler.CommentHandler),
          ('/profile.*', profile_handler.ProfileHandler),
          ('/salmon-slap', SalmonSlapHandler),
          ('/.well-known/host-meta', GhettoHostMeta),
          ('/user', GhettoUserXRD),
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
