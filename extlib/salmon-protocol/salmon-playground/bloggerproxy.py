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

"""Proxy service for Blogger to be used as a demo for Salmon Playground"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import datetime
import hashlib
import logging
import re

import feedparser
import oauth
import atom
import model
import pickle

import dumper

from google.appengine.ext import db

class BlogProxy(db.Model):
  """Record for a proxied blog and its feed.
     Tracks mapping between proxied URI and
     original, manages OAuth tokens, takes
     care of moving bits around.
  """
  blog_id = db.StringProperty(indexed=True)  # ID of the blog
  feed_uri = db.StringProperty(indexed=True) # The blog's (original) feed URL
  pickled_tokens = db.BlobProperty()         # Auth tokens needed to do stuff
  proxy_url = db.StringProperty()            # Full url we used for original proxy setup
  last_crawled = db.DateTimeProperty(default=datetime.datetime.fromtimestamp(0))


def getSalmonizedFeedDataForBlogId(id):
  bp = BlogProxy.all().filter('blog_id =', id).fetch(1)[0]
  feed_to_fetch = bp.feed_uri

  # Change any Blogger proxied feed into its canonical /feeds/posts/default
  # form if atom.xml to start with; then add ?dontredirect to the end.
  # This is fragile but hey, this is just a demo, right?
  p = re.compile('(.*)/atom\.xml')
  m = p.match(feed_to_fetch)
  if m:
    feed_to_fetch = m.group(1)+'/feeds/posts/default'
  feed_to_fetch = feed_to_fetch + '?dontredirect'

  data = feedparser.parse(feed_to_fetch)
  if data.bozo:
    # TODO: Do something about feeds that go bad?
    logging.error("Feed %s is not well formed; soldiering on anyway.",feed_to_fetch)
  else:
    # Augment with a salmon endpoint. TODO: Don't overwrite existing!
    data.feed.links.append({'href' : bp.proxy_url,'type': u'application/atom+xml', 'rel': u'salmon'})

  return data

class BlogProxyHandler(oauth.OAuthHandler):

  def get(self):
    data = getSalmonizedFeedDataForBlogId(self.request.get('id'))
    self.response.headers["Content-Type"] = "application/atom+xml; charset=utf-8"
    self.response.out.write(template.render('atom.xml', data))
    self.response.set_status(200)

  def post(self):
    # Take care of incoming salmon
    # pull out oauth token, fire up OAuth client, identify
    # the particular post in question and its comment stream,
    # create an entry, and post a comment.
    blog_id = self.request.get('id')

    body = self.request.body.decode('utf-8')

    logging.info('Salmon body is:\n%s\n----', body);

    data = feedparser.parse(body)
    logging.info('Data parsed was:\n%s\n----',data)
    if data.bozo:
      logging.error('Bozo feed data. %s: %r',
                     data.bozo_exception.__class__.__name__,
                     data.bozo_exception)
      if (hasattr(data.bozo_exception, 'getLineNumber') and
          hasattr(data.bozo_exception, 'getMessage')):
        line = data.bozo_exception.getLineNumber()
        logging.error('Line %d: %s', line, data.bozo_exception.getMessage())
      return self.response.set_status(400)

    logging.info('Found %d entries', len(data.entries))
    for entry in data.entries:
      s = model.makeEntry(entry)

      referents = model.getTopicsOf(s)

      logging.info('Saw %d parent(s)', referents.count() )
      if referents.count() == 0:
        logging.info('No parent found for %s, returning error to client.',s.entry_id)
        self.response.set_status(400)
        self.response.out.write('Bad Salmon, no parent with id '+unicode(s.in_reply_to)+' found -- rejected.\n');
        return

    # Pull body & other info out of salmon

    # Create an Atom entry and post as a comment
    text = s.content
    # TODO: Fix Blogger so it accepts acct: URIs... sigh...
    name = re.sub("(..\@.+)","...",s.author_name)
    author_uri = "http://example.org/profile/"+name
    #if author_uri.startswith("acct:"):
    #  author_uri = author_uri.replace("acct:","http://")
    text = text + ' by <a href="'+author_uri+'">'+name+'</a>'
    entry = atom.Entry(content=atom.Content(text=text))

    # Grab the entry ID from the in-reply-to element of the salmon
    p = re.compile('tag:blogger\.com,1999:blog-(\d+)\.post-(\d+)')
    m = p.match(s.in_reply_to)
    if not m:
      self.response.set_status(400)
      return
    blog_id = m.group(1)
    post_id = m.group(2)

    logging.info("About to post comment to blog %s, post %s",blog_id,post_id)

    # Grab auth info from DB (this is also an ACL check...)
    bp = BlogProxy.all().filter('blog_id =', blog_id).fetch(1)[0]
    origfeed = bp.feed_uri
    tokens = pickle.loads(bp.pickled_tokens)
    oauth_token = tokens["http://www.blogger.com/feeds/"]
    # TODO: Add some error checking, for Ghu's sake.

    # Let's see if override_token, at least, does what it says in this hall of
    # funhouse mirrors we call a GData client:
    self.client.blogger.override_token = oauth_token
    logging.info("Auth token = %s, override_token = %s",oauth_token,self.client.blogger.override_token)
    self.client.blogger.AddComment(entry, blog_id=blog_id, post_id=post_id)
    self.response.out.write("Salmon accepted, sent upstream to source!\n");
    self.response.set_status(200)

def modifyBlogRedirectUrl(blog_id, proxy_url, client):
  """ Modifies the given blog settings to make the feed redirect to the given proxy. """

  # The basic idea here is to PUT a new value to the Atom entry defined at
  # /feeds/blogid/settings/BLOG_FEED_REDIRECT_URL, which updates it.  I'm not sure
  # why the code also needs to see the BLOG_FEED_REDIRECT_URL name in the id as well
  # as the POSTed URL...  anyway, this works and it's just for demo purposes:
  data = atom.Entry(
      atom_id=atom.Id(text='tag:blogger.com,1999:blog-'+blog_id+'.settings.BLOG_FEED_REDIRECT_URL'),
      content=atom.Content(text=proxy_url)
      ) # The content of the setting is just the proxy URL
  logging.info("Data is: %s",data)
  uri = 'http://www.blogger.com/feeds/'+blog_id+'/settings/BLOG_FEED_REDIRECT_URL'
  client.blogger.Put(data, uri, extra_headers=None, url_params=None)

def addBlogProxy(blog_id,feed_uri,oauth_access_token,proxy_url,client):
  # First clear out any existing proxy entries with this blog_id:
  existing = BlogProxy.all().filter("blog_id = ",blog_id).fetch(100)
  db.delete(existing)

  feed_uri = feed_uri+'?dontredirect'

  # Create an entry for this proxied feed:
  pickled_tokens = pickle.dumps({"http://www.blogger.com/feeds/": oauth_access_token})
  bp = BlogProxy(blog_id=blog_id,
                 feed_uri=feed_uri,
                 pickled_tokens=pickled_tokens,
                 proxy_url=proxy_url)
  bp.put()

  # Now update the original blog to redirect to the proxy:
  modifyBlogRedirectUrl(blog_id,proxy_url,client)

def addNonBloggerBlogProxy(feed_uri):
  # First clear out any existing proxy entries with this uri:
  existing = BlogProxy.all().filter("blog_id = ",feed_uri).fetch(100)
  db.delete(existing)

  bp = BlogProxy(blog_id=feed_uri,
                 feed_uri=feed_uri,
                 proxy_url=feed_uri)
  bp.put()

def crawlFeedAndComments(feedurl,data,hacked_in_reply_to_override=None):
  """Crawl a single feed and all comments on its entries, recursively"""
  if data.bozo:
    logging.warning("Feed %s has errors: %s: %r",feedurl,
                    data.bozo_exception.__class__.__name__,
                    data.bozo_exception)
    if (hasattr(data.bozo_exception, 'getLineNumber') and
        hasattr(data.bozo_exception, 'getMessage')):
      line = data.bozo_exception.getLineNumber()
      logging.warning('Line %d: %s', line, data.bozo_exception.getMessage())

  update_list = []
  for entry in data.entries:
    # TODO: Get rid of this if/when feedparser is fixed
    if hacked_in_reply_to_override:
      entry['in-reply-to'] = hacked_in_reply_to_override

    e = model.makeEntry(entry,data.feed)
    #logging.info("Made an entry, salmon endpoint = %s",e.salmonendpoint)
    update_list.append(e)
    # Now look to see if the entry has comments
    commentfeeds = model.getLinkRel(entry,"replies")
    logging.info("Comments for entry: %s",commentfeeds)
    for f in commentfeeds:
      if f.type == 'application/atom+xml':
        # TODO: Discover most recent comment from this and use to update last active timestamp
        crawlFeedAndComments(f,feedparser.parse(f.href),entry.id)
  db.put(update_list)

def crawlProxiedFeed(feed_id):
  """Crawls and caches the specified proxy feed.

  Args:
    feed_id: db.Key for feed Entry.
  """
  logging.info("Started crawling feed: " + str(feed_id))

  bp = BlogProxy.get(feed_id)

  # Crawl what the proxy _would_ redirect us to, to speed things up.
  data = getSalmonizedFeedDataForBlogId(bp.blog_id)
  logging.info("Sample post links: %s",data.entries[0].links)
  crawlFeedAndComments(bp.feed_uri,data)
