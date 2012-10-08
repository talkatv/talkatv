#!/usr/bin/env python
# encoding: utf-8
#
# Copyright 2008 Google Inc.
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
"""Handles users for demo aggregator & proxy feed service"""

import sys
import os
import re

from google.appengine.ext import db
import logging

class RegisteredUser(db.Model):
  """Record for a registered user.
  """
  email = db.StringProperty(indexed=True)    


def is_registered_user(u):
  # Just let anybody play in the Playground:
  return True
  
  # Check for trusted domains first:
  if re.match("[a-zA-Z\+_]+@google.com",u.email()):
    return True

  # Next check email address against DB:
  result = RegisteredUser.gql('WHERE email = :1',u.email()).fetch(1)

  logging.info("Saw result: %s",result)
  # Did we find the user?  OK, they're in:
  if result:
    return True

  return False

def add_registered_user(email):
  u = RegisteredUser(email=email)
  u.put()
  
