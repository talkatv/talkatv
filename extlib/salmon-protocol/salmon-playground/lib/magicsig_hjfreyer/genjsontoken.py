#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.
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

"""Generate a simple signature from known plaintext."""

import magicsig.magicsigalg as magicsigalg
import base64

__author__ = 'jpanzer@google.com (John Panzer)'

_test_keypair = ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
                 'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
                 '.AQAB'
                 '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
                 'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')

_test_token = unicode('{ "user_id": "12345", "issuer": "server.example.com", "audience": "client.example.com", "not_before": "20101231T235959Z", "not_after": "20110101T001459Z" }'
                     , 'utf-8').encode('utf-8')


def log(s):
  print s

if __name__ == '__main__':
  data = _test_token
  data_type = 'application/oauth-token+json'
  encoding = 'base64url'
  alg = 'RSA-SHA256'
  key_id = ''

  sbs = ( base64.urlsafe_b64encode(data) + '.' 
    + base64.urlsafe_b64encode(data_type) + '.'  
    + base64.urlsafe_b64encode(encoding) + '.' 
    + base64.urlsafe_b64encode(alg) )
  signer = magicsigalg.SignatureAlgRsaSha256(_test_keypair)
  sig = signer.Sign(sbs, log)
  print "Message: [%s]" % sbs 
  print "Key: [%s]" % _test_keypair
  print "Signature: [%s]" % sig

  compactform = key_id + '.' + sig + '.' + sbs 
  print "Signed Token: [%s]" %  compactform

  
