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

__author__ = 'jpanzer@google.com (John Panzer)'

_test_keypair = ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
                 'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
                 '.AQAB'
                 '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
                 'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')

_test_text = unicode('One small splash for a salmon, one giant '
                     'leap for salmonkind!', 'utf-8').encode('utf-8')

def log(s):
  print s

if __name__ == '__main__':
  signer = magicsigalg.SignatureAlgRsaSha256(_test_keypair)
  logger = ''
  sig = signer.Sign(_test_text, log)
  print "Message: [%s]" % _test_text
  print "Key: [%s]" % _test_keypair
  print "Signature: [%s]" % sig
