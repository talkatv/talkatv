#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.
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

"""Support library for the Salmon Protocol.

See Salmon I-D for specification.  This module
implements a support library for Salmon on top of the
Magic Envelope library and other bits.
"""

__author__ = 'jpanzer@google.com (John Panzer)'


#import base64
#import xml.dom.minidom as dom

import magicsig


class SalmonProtocol(object):
  """Implementation of Salmon Protocol."""

  magicenv = magicsig.MagicEnvelopeProtocol()

  def _GetKeypair(self, signer_uri):
    return self.key_retriever.LookupPublicKey(signer_uri)

  def SignSalmon(self, text, mimetype, requestor_id):
    """Signs a Salmon on behalfo the the current_user.

    Input text must be in a recognized format so authorship can be
    verified.

    Args:
      text: Text of message to be signed.
      mimetype: The MIME type of the message to sign.
      requestor_id: The id of the requestor (usually current logged in user).
    Returns:
      The Magic Envelope parameters from section 3.1 of the
      Magic Signatures spec, as a dict.
    """
    
    assert mimetype == 'application/atom+xml'

    requestor_id = magicsig.NormalizeUserIdToUri(requestor_id)

    if not self.magicenv.CheckAuthorship(text, 
        magicsig.NormalizeUserIdToUri(requestor_id)):
        # TODO: Fix authorship if missing author, raise
        # exception otherwise.
        return

    env = self.magicenv.SignMessage(text, mimetype, requestor_id)

    assert self.magicenv.Verify(env)  # Sanity self-check 
   
    return self.WriteSalmonXML(env)

  def WriteSalmonXML(self, env):
    """Writes a magic enveloped salmon out in XML form.

    Args:
      env: Salmon data in magic envelope dict form.
    Returns:
      The application/magic-envelope+xml textual form of the salmon.
    """

    # TODO: Do nice pretty line breaks for data block, signature, etc.
    return """<?xml version='1.0' encoding='UTF-8'?>
<me:env xmlns:me='http://salmon-protocol.org/ns/magic-env'>
  <me:encoding>"""+env['encoding']+"""</me:encoding>
  <me:data type='"""+env['data_type']+"""'>
    """+env['data']+"""</me:data>
  <me:alg>"""+env['alg']+"""</me:alg>
  <me:sig>"""+env['sig']+"""</me:sig>
</me:env>\n
"""

  def ParseSalmon(self, text, mimetype):
     """Parses a salmon from text with given mimetype.

     Returns:
       The salmon data as a dict, with fields:
     """
     return
