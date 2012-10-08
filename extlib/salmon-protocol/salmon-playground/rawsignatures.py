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

"""Test out low level signature API."""

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

import magicsig.magicsigalg as magicsigalg

from utils import *
import base64

class RawSignaturesHandler(webapp.RequestHandler):
  """Handles request to sign a string with a test keypair.

  """

  signing_key =  ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
                  'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
                  '.AQAB'
                  '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
                  'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')

  @aclRequired
  def get(self):
    """Handles initial display of page."""
    data = dict()
    logging.info('Raw signatures')
    self.response.out.write(template.render('rawsignatures.html', data))
    self.response.set_status(200)

  @aclRequired
  def post(self):
    """Handles posting back of data and returns a result via XHR.
       Just for demo purposes.  Accepts a string as data.
    """

    data = self.request.get('data')
    if data:
      logging.info('posted raw string = [%s]', data)
      sig = magicsigalg.SignatureAlgRsaSha256(self.signing_key).Sign(data)

      logging.info('resulting signature: [%s]', sig)

      self.response.set_status(200) # The default
      self.response.out.write('Signed [%s]\n' % data)
      self.response.out.write('With key [%s]\n' % self.signing_key)
      self.response.out.write('Yielding signature [%s]\n' % sig)
    else:
      self.response.set_status(400)
