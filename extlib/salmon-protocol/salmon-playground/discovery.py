#!/usr/bin/python
#
# Copyright (C) 2009 Google Inc.
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

__author__ = 'jpanzer@google.com (John Panzer)'

"""Handles user identifer discovery for Salmon"""

import imports

from google.appengine.api import urlfetch
import logging
import simplejson as json

def discover(userid):
  """Throw an identifier at a Webfinger service and see what we get back."""
  
  wf_service_url = 'http://webfingerclient-dclinton.appspot.com/lookup?format=json&pretty=true&identifier='+userid

  resp = urlfetch.fetch(wf_service_url)

  if resp.status_code == 200:
    return resp.content
  else:
    return None

def discover_signing_info(userid):
  """Get available information for a given user ID, returning a dict."""

  json_wf_data = discover(userid)
  if json_wf_data:
    data = json.loads(json_wf_data)
    # Format is an array of objects?
    data = data[0]
    #logging.info("Data = %s\n",data);
    subject = data['subject']
    key_urls = [link.href for link in data['links'] if link['rel'] == 'publickey']

    return dict(
       identity = subject,
       public_keys = key_urls
    )

  return None

if __name__ == '__main__':
  main()
