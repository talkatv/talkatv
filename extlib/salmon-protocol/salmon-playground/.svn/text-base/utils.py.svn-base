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

"""Shared utilities specific to the Salmon Playground"""

#import cgi
#import datetime
#import logging

#from google.appengine.ext import webapp
#from google.appengine.ext import db
from google.appengine.api import users
import userdb

""" Helpers """
def aclRequired(func):
  def wrapper(self, *args, **kw):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
    else:
      if not (users.is_current_user_admin() or userdb.is_registered_user(user)):
        self.response.out.write("Sorry "+user.email()+", you are not on my allowed list.  Talk to John if you want to be added.")
        self.response.out.write("<br><a href=\""+users.create_logout_url(self.request.uri)+"\">logout</a>");
        self.response.set_status(403)
      else:
        func(self, *args, **kw)
  return wrapper
