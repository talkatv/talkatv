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

"""Simple subscriber that aggregates all feeds together and demonstrates Salmon."""

import imports

import logging
import random
import datetime
import wsgiref.handlers
import dumper
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api.labs import taskqueue
import feedparser
import userdb

from oauth import OAuthDanceHandler, OAuthHandler, requiresOAuth

# Demos
import magicsigdemo
from magicsig import magicsigalg #TODO get rid of this, should not be used
import rawsignatures

#Data model
import model
import bloggerproxy
from model import Entry
#from signatures import *

from utils import *

class SalmonizeHandler(webapp.RequestHandler):
  """Handles request to salmonize an external feed.

  This is just for testing, in order to get real feed data
  from live feed sources.  However a feed proxy like
  Feedburner could offer Salmon-as-a-service as well.
  """

  def get(self):
    feedurl = self.request.get('feed')
    data = feedparser.parse(feedurl)

    # Augment with a salmon endpoint. Don't overwrite existing!
    foundsalmon = False
    for link in data.feed.links:
      if link.rel.lower() == 'salmon':
        foundsalmon = True
        break
    if foundsalmon == False:
      endpoint = u'http://'+self.request.headers['Host']+'/post'
      data.feed.links.append({'href' : endpoint,'type': u'application/atom+xml', 'rel': u'salmon'})

    # if feedfields.bozo:
    # TODO: Annotate stored data and/or hand back a warning.

    # TODO: Have an alternate template that just shows the Atom with the salmon stuff highlighted in some way.
    self.response.out.write(template.render('atom.xml', data))
    self.response.headers.add_header("Content-Type","application/atom+xml; charset=utf-8")
    self.response.set_status(200)

    # Add a fake BlogProxy entry so that we can fetch updated comments for this feed.
    bloggerproxy.addNonBloggerBlogProxy(feedurl)

    # And store the entries discovered in our own DB for reference.
    for entry in data.entries:
      e = model.makeEntry(entry,data.feed)
      #logging.info('Made %s from %s',e,entry)
      db.put([e])
      logging.info('Remembering entry with title = "%s", id = "%s", '
                   'link = "%s"',
                   e.title, e.entry_id, e.link)

class InputHandler(webapp.RequestHandler):
  """Handles newly posted salmon"""

  def post(self):
    headers = self.request.headers;
    logging.info('Headers =\n%s\n',headers)
    in_reply_to = self.request.get('inreplyto') #Get this from entry thr:in-reply-to if possible; feedparser.py BUG here

    # TODO: Do a check for application/atom+xml and charset
    content_type = headers['Content-Type'];
    body = self.request.body.decode('utf-8')

    logging.info('Post body is %d characters', len(body))
    logging.info('Post body is:\n%s\n----', body);

    data = feedparser.parse(body)
    logging.info('Data returned was:\n%s\n----',data)
    if data.bozo:
      logging.error('Bozo feed data. %s: %r',
                     data.bozo_exception.__class__.__name__,
                     data.bozo_exception)
      if (hasattr(data.bozo_exception, 'getLineNumber') and
          hasattr(data.bozo_exception, 'getMessage')):
        line = data.bozo_exception.getLineNumber()
        logging.error('Line %d: %s', line, data.bozo_exception.getMessage())
        # segment = self.request.body.split('\n')[line-1]
        # logging.info('Body segment with error: %r', segment.decode('utf-8'))
      return self.response.set_status(500)

    update_list = []
    logging.info('Found %d entries', len(data.entries))
    for entry in data.entries:
      s = model.makeEntry(entry)

      referents = model.getTopicsOf(s)

      logging.info('Saw %d parents!', referents.count() )
      if referents.count() == 0:
        logging.info('No parent found for %s, returning error to client.',s.entry_id)
        self.response.set_status(400)
        self.response.out.write('Bad Salmon, no parent with id '+unicode(s.in_reply_to)+' found -- rejected.\n');
        return

      # Look for parents, update thread_updated if necessary
      for parent in referents:
        logging.info('Saw parent: %s\n',parent)
        if parent.thread_updated < s.updated:
          parent.thread_updated = s.updated
          parent.put()

      update_list.append(s)

    db.put(update_list)
    self.response.set_status(200)
    self.response.out.write("Salmon accepted, swimming upstream!\n");

class CreateProxyHandler(OAuthHandler):
  """Displays a configuration page to create a proxy salmonized feed."""

  @aclRequired
  def get(self):
    context = { 'logged': self.client.has_access_token() }

    if context['logged']:
      logging.info("before OAuth token = %s", self.client.blogger.token_store.find_token("htp://www.blogger.com/feeds/default/blogs"))
      feed = self.client.blogger.GetBlogFeed()
      blogs = []
      for entry in feed.entry:
        blogs.append({
          'id': entry.GetBlogId(),
          'title': entry.title.text,
          'link': entry.GetHtmlLink().href,
          'published': entry.published.text,
          'updated': entry.updated.text,
        })
      context['blogs'] = blogs

    logging.info("token_store = %s",self.client.blogger.token_store)
    logging.info("OAuth token = %s", self.client.blogger.token_store.find_token("http://www.blogger.com/feeds/"))

    self.response.out.write(template.render('setup_proxy.html', context))

class SalmonizeBlogHandler(OAuthHandler):
  """Handles XHR request to salmonize a particular blog"""

  @aclRequired
  def post(self):
    logging.info('Inside SalmonizeBlogHandler')
    logging.info('Saw body: %s\n',self.request.body.decode('utf-8'))
    blogid = self.request.get('id')
    feeduri = self.request.get('feed')
    # Take blogid, feed, and OAuth token and squirrel them away for
    # later use.  Create a proxy URL for the feed that maps to
    # this salmonized feed, and return it.
    logging.info("In SalmonizeBlogHandler, OAuth token = %s", self.client.blogger.token_store.find_token("http://www.blogger.com/feeds/"))

    # Retrieve OAuth token stored by the current user, and cache it away for later use
    # when posting comments (only).  Wish we had a way to tell the server we want to restrict
    # the token to certain operations only, it'd be safer.
    oauth_token = self.client.blogger.token_store.find_token("http://www.blogger.com/feeds/")
    logging.info('Saw blogid=%s, feeduri=%s, OAuth token=%s',blogid,feeduri,oauth_token)
    bloggerproxy.addBlogProxy(blogid,feeduri,oauth_token,
        'http://'+self.request.headers['Host']+'/blogproxy?id='+blogid,
        self.client)

    # Finally, add the blog to the test aggregator (River of Salmon):

    self.response.set_status(200)

class RiverHandler(webapp.RequestHandler):
  """Displays a very simple river of Salmon aggregator."""

  @aclRequired
  def get(self):
    N = 100
    context = dict(entries=model.getLatestPosts(N))
    if context['entries']:
      for entry in context['entries']:
        replies = model.getRepliesTo(entry,N)
        if replies:
          entry.replies = replies
    self.response.out.write(template.render('ros.html', context))

class ReplyHandler(webapp.RequestHandler):
  """Provides a semi-helpful reply mechanism."""

  @login_required
  def get(self):
    context = dict()
    context['parent'] = model.getEntryById(self.request.get('inreplyto'))
    context['newid'] = "tag:example.com,2009:cmt-%.8f" % random.random();
    u = users.get_current_user();
    context['user'] = dict(nickname=u.nickname(), email=u.email())
    context['timestamp'] = datetime.datetime.utcnow().isoformat()

    # Sign the buffer (XML):
    sig = magicsigalg.GenSampleSignature(template.render('reply.html', context))

    # Add signature to XML & write out augmented XML:
    context['signature'] = sig
    self.response.out.write(template.render('reply.html', context))

class LatestHandler(webapp.RequestHandler):
  """Shows latest entries, salmon or otherwise, seen in a straight list """

  @aclRequired
  def get(self):
    logging.error('ZAWEEBO!')
    stuff=[]
    for salmon in Entry.gql('ORDER BY updated DESC').fetch(10):
      text = cgi.escape(salmon.content if salmon.content else '(no content)')
      text = text[0:30]
      if len(text) > 29:
        text = text + "..."
      stuff.append({'updated': str(salmon.updated),
                    'content': text,
                    'link': salmon.link,
                    'author_name': salmon.author_name,
                    'author_uri': salmon.author_uri,
                    'in_reply_to': salmon.in_reply_to})
    self.response.out.write(template.render('latest.html',dict(salmon=stuff)))

class AddUserHandler(webapp.RequestHandler):
  """Adds a registered user w/param email, iff current user is an admin.."""

  @aclRequired
  def get(self):
    if users.is_current_user_admin():
      e = self.request.get('email')
      if e:
        userdb.add_registered_user(e)
        self.response.out.write("Added "+e+" to registered users!")
        self.response.set_status(200)
        return

    self.response.out.write("Access DENIED!")
    self.response.set_status(400)

class RecrawlHandler(webapp.RequestHandler):
  """Triggers a recrawl of all the subscriptions handled by blogproxy."""

  def get(self):
    feed_id = self.request.get('feed_id')

    if feed_id:
      feed_key = db.Key(feed_id)
      feed = bloggerproxy.BlogProxy.get(feed_key)

      now = datetime.datetime.utcnow()
      if now - feed.last_crawled > datetime.timedelta(seconds=30):
        # Update the time first. Even if the crawl fails, we want to
        # throttle it.
        feed.last_crawled = now
        feed.put()
        bloggerproxy.crawlProxiedFeed(feed_key)
      else:
        logging.info('Feed crawled recently enough. Skipping.')
    else:
      proxied = bloggerproxy.BlogProxy.all().fetch(500)

      for bp in proxied:
        taskqueue.add(url='/recrawl.do',
                      method='GET',
                      params=dict(feed_id=bp.key()))

    self.response.set_status(200)

class MainHandler(webapp.RequestHandler):
  """Main page of the server."""

  @aclRequired
  def get(self):
    context = dict(logouturl=users.create_logout_url(self.request.uri))
    self.response.out.write(template.render('index.html',context))


application = webapp.WSGIApplication(
  [
    (r'/salmonize', SalmonizeHandler),
    (r'/post', InputHandler),
    (r'/latest', LatestHandler),
    (r'/setup_proxy', CreateProxyHandler),
    (r'/salmonize_blog', SalmonizeBlogHandler),
    (r'/ros', RiverHandler),
    (r'/recrawl.do', RecrawlHandler),
    (r'/reply.do', ReplyHandler),
    (r'/adduser', AddUserHandler),
    (r'/', MainHandler),
    (r'/oauth/(.*)', OAuthDanceHandler),
    (r'/blogproxy', bloggerproxy.BlogProxyHandler),
    (r'/magicsigdemo', magicsigdemo.SignThisHandler),
    (r'/magicsigdemoverify', magicsigdemo.VerifyThisHandler),
    (r'/rawsignatures', rawsignatures.RawSignaturesHandler),
  ],
  debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
