#!/usr/bin/env python
#
# Copyright 2009 Google Inc.
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

"""Quick demo of magic signatures for Salmon."""

import imports

import logging
import random
import datetime
import wsgiref.handlers
import dumper
import cgi
import sys

from string import strip

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
import feedparser
import userdb

import magicsig

from utils import *
import base64

# Just for bootstrapping, use test keypair:

the_test_keypair = "RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww==.AQAB.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q=="

the_test_publickey = "RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww==.AQAB"

class SignThisHandler(webapp.RequestHandler):
  """Handles request to sign an Atom entry.

  Just a demo, that takes as input an arbitrary
  Atom entry and signs it (ultimately, using the
  currently authenticated user's key) and produces
  as output a Magic Signature.
  """

  magicenv = magicsig.MagicEnvelopeProtocol()

  @aclRequired
  def get(self):
    """Handles initial display of page."""
    data = dict()
    self.response.out.write(template.render('magicsigdemo.html', data))
    self.response.set_status(200)

  @aclRequired
  def post(self):
    """Handles posting back of data and returns a result via XHR.
       Just for demo purposes.  Accepts either data (an XML document)
       or env (a magic envelope) and returns output of magic-envelope
       or atom depending on format parameter."""

    # TODO: Verify that current user session matches author of content, or throw
    data = self.request.get('data')
    envText = self.request.get('env')
    format = self.request.get('format') or 'magic-envelope'
    if data:
      logging.info('posted Atom data = %s\n',data)
      userid = magicsig.NormalizeUserIdToUri(
          users.get_current_user().email())

      # Do an ACL check to see if current user is the author:
      if not self.magicenv.IsAllowedSigner(data, userid):
        logging.info("Authorship check failed for user %s\n",userid)
        self.response.set_status(400)
        self.response.out.write("User "+userid+" not first author of entry,"
                                " cannot sign.")
        return

      # Sign the content on behalf of user:
      envelope = magicsig.Envelope(raw_data_to_sign=data,
                                   data_type='application/atom+xml',
                                   signer_uri=userid,
                                   signer_key='TEST')
      #env = self.magicenv.SignMessage(data, 'application/atom+xml', userid)
    elif envText:
      logging.info('posted Magic envelope env = %s\n',envText)
      envelope = magicsig.Envelope(document=envText,
                                   mime_type='applicaton/magic-envelope+xml')
      #env = self.magicenv.Parse(envText)

    logging.info('Created magic envelope: \n%s\n' % envelope)

    self.response.set_status(200) # The default
    if format == 'magic-envelope':
      self.response.out.write(envelope.ToXML())
    elif format == 'atom':
      self.response.out.write(envelope.ToAtom())
    else:
      self.response.set_status(400)
      raise "Unsupported format: "+format

class VerifyThisHandler(webapp.RequestHandler):
  """Handles request to verify a magic envelope or signed Atom entry.
  """

  magicenv = magicsig.MagicEnvelopeProtocol()

  def post(self):
    """  Intended to be called via XHR from magicsigdemo.html. """
    logging.error('MagicSigDemoVerify post')
    data = self.request.get('data').strip()
    logging.info('The data = %s\n',data)
    env = self.magicenv.Parse(data)
    try:
      envelope = magicsig.Envelope(document=data,
                                   mime_type='application/magic-envelope+xml')
      self.response.set_status(200) # The default
      self.response.out.write("OK")
      logging.info("SPLASH! Salmon signature verified!")
    except magicsig.Error:
      self.response.set_status(400)
      info = "Details: Exception %s:\n%s\nTraceback:\n%s" % sys.exc_info()
      logging.info(info)
      self.response.out.write('Signature does not validate. Details: %s' % info)

if __name__ == '__main__':
  main()
