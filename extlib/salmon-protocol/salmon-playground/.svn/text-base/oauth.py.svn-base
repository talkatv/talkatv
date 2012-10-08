"""
Heavily used (copied, modified) resources:
 * http://github.com/tav/tweetapp,
 * Examples of OAuth from GData Python Client written by Eirc Bidelman.
"""


import os
import logging

import gdata.auth
import gdata.alt.appengine
import gdata.blogger.service
import gdata.photos.service

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

SETTINGS = {
  'APP_NAME': 'salmon-playground',
  'CONSUMER_KEY': 'anonymous',
  'CONSUMER_SECRET': 'anonymous',
  'SIG_METHOD': gdata.auth.OAuthSignatureMethod.HMAC_SHA1,
  'SCOPES': [
      'http://www.blogger.com/feeds/',
      'http://picasaweb.google.com/data/',
   ],
  'REDIRECT_TO': '/setup_proxy'
}


# ------------------------------------------------------------------------------
# Data store models.
# ------------------------------------------------------------------------------

class OAuthRequestToken(db.Model):
  """Stores OAuth request token."""

  token_key = db.StringProperty(required=True)
  token_secret = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)

# ------------------------------------------------------------------------------
# OAuth client.
# ------------------------------------------------------------------------------

class OAuthClient(object):
  
  __public__ = ('request_token', 'callback', 'revoke_token')
  
  def __init__(self, handler):
    self.handler = handler
    self.blogger = gdata.blogger.service.BloggerService(
        source=SETTINGS['APP_NAME'])
    self.picasa = gdata.photos.service.PhotosService(
        source=SETTINGS['APP_NAME'])
    self.blogger.SetOAuthInputParameters(SETTINGS['SIG_METHOD'],
        SETTINGS['CONSUMER_KEY'], consumer_secret=SETTINGS['CONSUMER_SECRET'])
    self.picasa.SetOAuthInputParameters(SETTINGS['SIG_METHOD'],
        SETTINGS['CONSUMER_KEY'], consumer_secret=SETTINGS['CONSUMER_SECRET'])
    self.redirect_to = SETTINGS['REDIRECT_TO'] or '/'
    gdata.alt.appengine.run_on_appengine(self.blogger)
    gdata.alt.appengine.run_on_appengine(self.picasa)

  def has_access_token(self):
    """Checks if Blogger GData has access token which means that user is
       authenticated within Blogger."""
    access_token = self.blogger.token_store.find_token('%20'.join(SETTINGS['SCOPES']))
    return isinstance(access_token, gdata.auth.OAuthToken)
    
  def request_token(self):
    """Fetches a request token and redirects the user to the approval page."""  
  
    if users.get_current_user():
      # 1.) REQUEST TOKEN STEP. Provide the data scope(s) and the page we'll
      # be redirected back to after the user grants access on the approval page.
      req_token = self.blogger.FetchOAuthRequestToken(
          scopes=SETTINGS['SCOPES'],
          oauth_callback=self.handler.request.uri.replace('request_token', 'callback'))

      # When using HMAC, persist the token secret in order to re-create an
      # OAuthToken object coming back from the approval page.
      db_token = OAuthRequestToken(token_key = req_token.key,
          token_secret=req_token.secret)
      db_token.put()
      
      # 2.) APPROVAL STEP.  Redirect to user to Google's OAuth approval page.
      self.handler.redirect(self.blogger.GenerateOAuthAuthorizationURL())    

  def callback(self):
    """Invoked after we're redirected back from the approval page."""

    oauth_token = gdata.auth.OAuthTokenFromUrl(self.handler.request.uri)
    if oauth_token:
      # Find request token saved by put() method.
      db_token = OAuthRequestToken.all().filter(
          'token_key =', oauth_token.key).fetch(1)[0]
      oauth_token.secret = db_token.token_secret
      oauth_token.oauth_input_params = self.blogger.GetOAuthInputParameters()
      self.blogger.SetOAuthToken(oauth_token)

      # 3.) Exchange the authorized request token for an access token
      oauth_verifier = self.handler.request.get('oauth_verifier', default_value='')
      access_token = self.blogger.UpgradeToOAuthAccessToken(
          oauth_verifier=oauth_verifier)

      # Remember the access token in the current user's token store
      if access_token and users.get_current_user():
        self.blogger.token_store.add_token(access_token)
      elif access_token:
        self.blogger.current_token = access_token
        self.blogger.SetOAuthToken(access_token)

    self.handler.redirect(self.redirect_to)
    
  def revoke_token(self):
    """Revokes the current user's OAuth access token."""

    try:
      self.blogger.RevokeOAuthToken()
    except gdata.service.RevokingOAuthTokenFailed:
      pass

    self.blogger.token_store.remove_all_tokens()
    self.handler.redirect('self.redirect_to')

# ------------------------------------------------------------------------------
# Request handlers.
# ------------------------------------------------------------------------------

class OAuthDanceHandler(webapp.RequestHandler):
  """Handler for the 3 legged OAuth dance."""

  """This handler is responsible for fetching an initial OAuth request token,
  redirecting the user to the approval page.  When the user grants access, they
  will be redirected back to this GET handler and their authorized request token
  will be exchanged for a long-lived access token."""
  
  def __init__(self):
    super(OAuthDanceHandler, self).__init__()
    self.client = OAuthClient(self)

  def get(self, action=''):
    if action in self.client.__public__:
        self.response.out.write(getattr(self.client, action)())
    else:
        self.response.out.write(self.client.request_token())

class OAuthHandler(webapp.RequestHandler):
  def __init__(self):
    super(OAuthHandler, self).__init__()
    self.client = OAuthClient(self) 

def requiresOAuth(fun):
  def decorate(self, *args, **kwargs):
    if self.client.has_access_token():
      fun(self, *args, **kwargs)
    else:
      self.redirect('/oauth/request_token')
  return decorate