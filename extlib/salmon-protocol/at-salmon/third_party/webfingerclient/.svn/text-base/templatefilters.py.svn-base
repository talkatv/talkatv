#!/usr/bin/python2.5
#
# Custom django template filters.
#
# Copyright 2009 DeWitt Clinton
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from google.appengine.ext.webapp import template

register = template.create_template_register()

@register.filter
def get_from_dict(d, key):
  """Returns a key from a dictionary if set. None otherwise.

  Args:
    d: a dict
    key: a key
  """
  try:
    return d[key]
  except KeyError:
    return None
