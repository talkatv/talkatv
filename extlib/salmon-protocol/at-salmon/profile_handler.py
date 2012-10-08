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

import imports
import magicsig
import webfingerclient.webfinger as webfinger
import simplejson as json
import datamodel

def query_mentions(user_uri):
  mentions = []
  mentionResults = db.GqlQuery("SELECT * FROM Comment where mentions = :user_uri ORDER BY posted_at DESC",
                               user_uri=user_uri)
  for mention in mentionResults:
    mentions.append(decorate_comment(mention))

  return mentions

def decorate_comment(comment):
  comment.decorated_content = comment.content
  comment.author_uri = comment.author_profile.profile_url
  if not comment.author_uri:
    comment.author_uri = 'about:blank'
  logging.info("Author_uri = %s" % comment.author_uri)
  comment.author_display_name = comment.author_profile.display_name
  
  client = webfinger.Client()
  for mention in comment.mentions:
    replacer = re.compile(mention)
    # relying on memcache to make this not painful.  Should probably store this with the original
    # mention information on write. (TODO)
    try:
      # use http://webfinger.net/rel/profile-page rel link from webfinger to get link to profile page.
      xrd_list = client.lookup(mention)
      profile_uris = ['about:blank']
      for item in xrd_list:
        profile_uris = [link.href for link in item.links if link.rel
                                == 'http://webfinger.net/rel/profile-page']
      linkedMention = "<a href='%s' title='Link to profile for %s'>%s</a>" % (profile_uris[0], mention, mention)
      comment.decorated_content = replacer.sub(linkedMention, comment.decorated_content)
    except:
      pass #TODO: log?

  return comment


_LOCAL_PROFILE_PATH_RE = re.compile('/profile/([^/]+)', re.VERBOSE)
_PROFILE_RE = re.compile('https?://([^/]+)/profile/([^/]+)' ,re.VERBOSE)
_ACCT_RE = re.compile('(acct:)?([^@]+)@(.+)', re.VERBOSE)

def ensure_profile(user, host_authority):
  p = get_profile_for_user(user)
  if p:
    return p
  else:
    return create_profile_for_user(user, host_authority)

def get_profile_for_user(user):
  profileResults = db.GqlQuery("SELECT * FROM Profile WHERE local_owner = :owner",
                                 owner=user).fetch(1)
  if len(profileResults) == 0:
    return None
  else:
    return profileResults[0]

def make_profile_url(localname, host_authority):
  return 'http://'+host_authority+'/profile/'+localname   

def get_profile_by_uri(uri):
  # If it's an acct: URI, normalize to expected profile URL:
  # TODO: This may not make sense.
  match = _ACCT_RE.match(uri)
  if match:
    url = make_profile_url(match.group(2), match.group(3))
  else:
    match = _PROFILE_RE.match(uri)
    if match:
      url = uri
    else:
      return None # Syntactically invalid

  profileResults = db.GqlQuery("SELECT * FROM Profile WHERE profile_url = :url",
                                url=url).fetch(1)
  if len(profileResults) == 0:
    return None
  else:
    return profileResults[0]

def create_profile_for_user(user, host_authority):
  p = prepare_profile_for_user(user, host_authority)
  p.put()
  return p

def prepare_profile_for_user(user, host_authority):
  localname_base = user.email().split('@')[0]
  localname = localname_base
  counter = 1
  while True:
    url = make_profile_url(localname, host_authority)
    r = db.GqlQuery("SELECT * FROM Profile WHERE profile_url = :url",
                    url=url).fetch(1)
    if len(r) == 0:
      break  # Does not exist
    
    counter += 1
    localname = localname_base + str(counter)
  
  # (Small race condition here we don't care about for a demo)
  # (Using a default public key here instead of generating one on the fly.  Should
  # probably use None instead until the user writes a comment and then generate one.)
  p = datamodel.Profile(
    local_owner = user,
    foreign_aliases = [],
    profile_url = url,
    display_name = localname,  # Just a default.
    public_key = 'RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
                 'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
                 '.AQAB')
  return p

def ensure_virtual_profile(author_uri):
  # TODO: Do this in a transaction
  r = db.GqlQuery("SELECT * FROM Profile WHERE profile_url = :author_uri",
                  author_uri=author_uri).fetch(1)
  if len(r) == 0:
    p = datamodel.Profile(
      foreign_aliases = [author_uri],
      profile_url = author_uri,
      display_name = author_uri)
    p.put()
  else:
    p = r[0]
    
  return p

class ProfileHandler(webapp.RequestHandler):
  def get(self):
    logging.info("Saw a GET to /profile handler!")
    user = users.get_current_user()
    logging.info("Path = %s" % self.request.path)
    match = _LOCAL_PROFILE_PATH_RE.match(self.request.path)
    if not match:
      self.response.out.write('Badly formed profile URL!')
      self.response.set_status(400) 
      return

    # Grab localname; if it's the special @me metavariable,
    # substitute with the actual users's local profile name
    # (creating a default on the fly if needed.)
    localname = match.group(1)
    if localname == '%40me':
      profile = ensure_profile(user, self.request.host)
    else:
      profile = get_profile_by_uri(make_profile_url(localname, self.request.host))

    if not profile:
      self.response.out.write("Profile not found!")
      self.response.set_status(404)
      return

    # Check to see if currently logged in user is the owner of the profile, and flag if so.
    is_own_profile = False
    if user and profile.local_owner:
      is_own_profile = user.email == profile.local_owner.email  #TODO: Fix this up with a GUID

    # Edit the given profile:
    m = _PROFILE_RE.match(profile.profile_url)
    localname = ''
    if m:
      assert self.request.host == m.group(1)  # Must match local host for now
      host_authority = m.group(1)
      localname = m.group(2)

    fulluserid = localname + '@' + host_authority
    template_values = {
      'fulluserid': fulluserid,
      'is_own_profile': is_own_profile,
      'localname': localname,
      'nickname': profile.display_name,
      'mentions': query_mentions(fulluserid),
      'publickey': profile.public_key,
      'logout_url': users.create_logout_url(self.request.path),
      'login_url' : users.create_login_url(self.request.path) }
    path = os.path.join(os.path.dirname(__file__), 'profile.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    user = users.get_current_user()
    newlocalname = self.request.get('newlocalname')
    oldlocalname = self.request.get('oldlocalname')
    newnickname = self.request.get('newnickname')
    newpublickey = self.request.get('newpublickey')
    
    old_profile_url = make_profile_url(oldlocalname, self.request.host)
    new_profile_url = make_profile_url(newlocalname, self.request.host)
    profileResults = db.GqlQuery("SELECT * FROM Profile WHERE profile_url = :old_profile_url",
                                 old_profile_url=old_profile_url).fetch(1)
    if len(profileResults) == 0:
      # Doesn't exist, so create it:
      logging.info("Creating %s %s %s" % (newlocalname, user, newnickname) )
      p = prepare_profile_for_user(user, self.request.host)
    else:
      # Already exists, update if ACL checks out:
      logging.info("Updating %s with %s %s %s" % (oldlocalname, newlocalname,
                                                  user, newnickname) )
      p = profileResults[0]
      if p.local_owner != user:
        self.response.set_status(403)  #Forbidden!
        return
      
    p.profile_url = new_profile_url
    p.display_name = newnickname
    p.public_key = newpublickey
        
    p.put()  # Create or update existing

    self.redirect(new_profile_url)
