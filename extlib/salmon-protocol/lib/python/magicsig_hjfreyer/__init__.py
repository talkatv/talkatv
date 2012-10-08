#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.
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

"""Implementation of Magic Signatures protocol.

See Magic Signatures RFC for specification.  This module
implements the Magic Signature API on top of the crypto
layer in magicsigalg.py, hiding the low level crypto details.
"""

__author__ = 'jpanzer@google.com (John Panzer)'

import re
import sys
import time
import weakref

# ElementTree is standard with Python >=2.5, needs
# environment support for 2.4 and lower.
try:
  import xml.etree.ElementTree as et  # Python >=2.5
except ImportError:
  try:
    import elementtree as et  # Allow local path override
  except ImportError:
    raise

import exceptions
import magicsigalg
import utils


class KeyRetriever(object):
  """Retrieves public or private keys for a signer identifier (URI)."""

  def LookupPublicKey(self, signer_uri):
    # TODO(jpanzer): Really look this up with Webfinger.
    if not signer_uri:
      return None
    return  ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
             'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
             '.AQAB'
             '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
             'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')

  def LookupPrivateKey(self, signer_uri):
    """Look up signing key for a given signer URI."""
    # TODO(jpanzer): Fix this up to really work, or eliminate.
    return self.LookupPublicKey(signer_uri)


class MagicEnvelopeProtocol(object):
  """Implementation of Magic Envelope protocol."""

  ME_MIME_TYPES = [utils.Mimes.JSON,
                   utils.Mimes.JSON_ME,
                   utils.Mimes.XML_ME,
                   ]

  def __init__(self,
               key_retriever=KeyRetriever(),
               encoder=utils.DefaultEncoder(),
               algs=magicsigalg.DefaultAlgorithms(),
               author_extractor=utils.DefaultAuthorExtractor(),
               auto_verify=True,
               reverify_period=(24 * 3600)):
    self.key_retriever = key_retriever
    self.encoder = encoder
    self.algs = algs
    self.author_extractor = author_extractor
    self.auto_verify = auto_verify
    self.reverify_period = reverify_period

    # Internal caches
    self._last_verified = weakref.WeakKeyDictionary()
    self._decoded_cache = weakref.WeakKeyDictionary()
    self._xml_tree_cache = weakref.WeakKeyDictionary()
    self._atom_cache = weakref.WeakKeyDictionary()
    self._json_cache = weakref.WeakKeyDictionary()

  def WrapAndSign(self,
                  data,
                  data_type,
                  encoding='base64url',
                  alg='RSA-SHA256'):
    """Puts data in an envelope and signs it. It also verifies the signed data.

    Args:
      data: unencoded data to wrap and sign (e.g. a json/XML string).
      data_type: MIME type of data, as a string.
      encoding: Encoding to use in envelope.
      alg: Signing algorithm to use.

    Raises:
      AuthorNotFoundError: If the author's UID could not be extracted
          from the decoded text.
      EnvelopeFormatError: If any of the envelope data is bogus.
      EnvelopeProtocolError: If verification of the envelope fails
          after it is constructed.
      KeyNotFoundError: If the author's public key could not be found.
    """
    author_uris = self.author_extractor.ExtractAuthors(data, data_type)
    if not author_uris:
      raise exceptions.AuthorNotFoundError(
          'Author not extracted from data: ', data)

    # Just uses the first author.
    # TODO: Support multiple signers?
    author_uri = author_uris[0]

    private_key = self.key_retriever.LookupPrivateKey(author_uri)
    if not private_key:
      raise exceptions.KeyNotFoundError(
          'Private Key could not be found for author: ', author_uri)

    data = self.encoder.Encode(data, encoding)
    sig = self.algs.Sign(private_key, data, alg)

    envelope = Envelope(data=data,
                    data_type=data_type,
                    sig=sig,
                    encoding=encoding,
                    alg=alg)

    self._VerifyOrDie(envelope)

    return envelope

  def VerifyEnvelope(self,
                     envelope):
    """Verifies magic envelope data.

    Checks that its signature matches the contents and that the
    author's public key generated the signature.

    Args:
      envelope: The magic envelope to verify.
    Returns:
      True iff the signature is verified.

    Raises:
      AuthorNotFoundError: If the author's UID could not be extracted
          from the decoded text.
      KeyNotFoundError: If the author's public key could not be found.
    """
    decoded_data = self.encoder.Decode(envelope.data, envelope.encoding)

    author_uris = self.author_extractor.ExtractAuthors(
        decoded_data, envelope.data_type)
    if not author_uris:
      raise exceptions.AuthorNotFoundError(
          'Author not extracted from data: ', decoded_data)

    # Just uses the first author.
    # TODO: Support multiple signers?
    author_uri = author_uris[0]

    public_key = self.key_retriever.LookupPublicKey(author_uri)
    if not public_key:
      raise exceptions.KeyNotFoundError(
          'Public Key could not be found for author: ', author_uri)

    result = self.algs.Verify(public_key,
                              envelope.data,
                              envelope.sig,
                              envelope.alg)

    if result:
      self._last_verified[envelope] = time.time()

    return result

  def FromString(self,
                 text,
                 mime_type=utils.Mimes.XML_ME):
    """Parses from arbitrary text, given mime type, and verifies.

    Args:
      text: Text to parse.
      mime_type: Mime type in MagicEnvelopeProtocol.ME_MIME_TYPES for the text.

    Returns:
      A verified instance of Envelope.

    Raises:
      EnvelopeProtocolError: If verification of the envelope fails.
    """
    assert mime_type in MagicEnvelopeProtocol.ME_MIME_TYPES

    if mime_type == utils.Mimes.XML_ME:
      xml = et.XML(text)

      return Envelope.FromXmlElement(xml.get_root())
    elif mime_type == utils.Mimes.ATOM:
      xml = et.XML(text)

      # SECURITY: Note that the information about the Atom entry
      # itself is discarded. Validity decisions are made based on the
      # contents of the me:provenance element alone. Anything outside
      # that element is unsigned and may be bogus.
      provenance = xml.get_root().find(utils.Namespaces.ME_NS+'provenance')

      return Envelope.FromXmlElement(provenance)
    else:
      # TODO: Implement JSON
      raise NotImplementedError('JSON parsing not implemented')

  def FromXmlElement(self, element):
    """Parses an envelope from an elementtree.Element instance.

    Args:
      element: elementtree instance corresponding to a valid envelope.

    Returns:
      A verified instance of Envelope.

    Raises:
      EnvelopeProtocolError: If verification of the envelope fails.
    """
    data_element = element.find('data')
    data = Squeeze(data_element.text)
    data_type = Squeeze(data_element.get('type'))

    sig_element = element.find('sig')
    sig = Squeeze(sig_element.text)
    keyhash = Squeeze(sig_element.get('keyhash'))

    encoding = Squeeze(element.find('encoding').text)
    alg = Squeeze(element.find('alg').text)

    envelope = Envelope(data=data,
                        data_type=data_type,
                        sig=sig,
                        keyhash=keyhash,
                        encoding=encoding,
                        alg=alg)

    self._VerifyOrDie(envelope)

    return envelope

  def GetDateLastVerified(self, envelope):
    """Get the time (in seconds since epoch) when envelope was last verified.

    Args:
      envelope: the envelope for which to check the date.

    Returns:
      The time at which this Protocol object last verified the
      envelope, or 0 if it hasn't.
    """
    return self._last_verified.get(envelope, 0)

  def GetDataAsRawString(self, envelope):
    """Simply decodes the data of the given envelope. Memoized."""
    self._VerifyOrDie(envelope)

    if envelope not in self._decoded_cache:
      self._decoded_cache[envelope] = self.encoder.Decode(
          envelope.data, envelope.encoding)

    return self._decoded_cache[envelope]

  def GetDataAsXmlElementTree(self, envelope):
    """Decode the data of the given envelope and make an XML tree. Memoized."""
    self._VerifyOrDie(envelope)

    if envelope not in self._xml_tree_cache:
      decoded = self.GetDataAsRawString(envelope)

      self._xml_tree_cache[envelope] = et.XML(decoded)

    return self._xml_tree_cache[envelope]

  def ToAtomString(self, envelope, fulldoc=True, indentation=0):
    """Turns envelope into serialized Atom entry.

    Args:
      envelope: the envelope to serialize.
      fulldoc: Return a full XML document with <?xml...
      indentation: Indent each line this number of spaces.
    Returns:
      An Atom entry XML document with an me:provenance element
      containing the original magic signature data.
    """
    self._VerifyOrDie(envelope)

    if envelope.data_type != utils.Mimes.ATOM:
      raise TypeError('mime type of envelope is %s, not %s'
                      % (envelope.data_type, utils.Mimes.ATOM))

    d = self.GetDataAsXmlElementTree(envelope)
    assert d.tag == utils.Namespaces.ATOM_NS + 'entry'

    me_ns = utils.Namespaces.ME_NS

    # Create a provenance and add it in.
    prov_el = et.Element(me_ns + 'provenance')
    data_el = et.SubElement(prov_el, me_ns + 'data')
    data_el.set('type', envelope.data_type)
    data_el.text = '\n'+utils.ToPretty(envelope.data, indentation+6, 60)
    et.SubElement(prov_el, me_ns + 'encoding').text = envelope.encoding
    et.SubElement(prov_el, me_ns + 'sig').text = (
        '\n' + utils.ToPretty(envelope.sig,
                         indentation+6,
                         60))

    # Add in the provenance element:
    d.append(prov_el)

    # Prettify:
    utils.PrettyIndent(d, indentation/2)

    # Turn it back into text for consumption:
    text = et.tostring(d,encoding='utf-8')

    indented_text = ''
    for line in text.strip().split('\n'):
      if line.strip() != '':
        indented_text += ' '*indentation + line + '\n'

    if fulldoc:
      indented_text = ('<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n' +
                       indented_text)
    return indented_text

  def ToJsonString(self, envelope):
    # TODO: Implement JSON
    raise NotImplementedError('JSON not implemented')

  def ToXmlString(self, envelope, fulldoc=True, indentation=0):
    """Turns envelope into serialized XML suitable for transmission.

    Args:
      fulldoc: Return a full XML document with <?xml...
      indentation: Indent each line this number of spaces.
    Returns:
      An XML document or fragment in string form.
    """
    self._VerifyOrDie(envelope)

    # Template for a Magic Envelope:
    if fulldoc:
      template = '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
    else:
      template = ''
    template += """
<me:env xmlns:me='http://salmon-protocol.org/ns/magic-env'>
  <me:encoding>%s</me:encoding>
  <me:data type='%s'>
    %s
  </me:data>
  <me:alg>%s</me:alg>
  <me:sig>
    %s
  </me:sig>
</me:env>
    """
    text = template % (envelope.encoding,
                       envelope.data_type,
                       utils.ToPretty(envelope.data, 4, 60),
                       envelope.alg,
                       utils.ToPretty(envelope.sig, 4, 60))
    indented_text = ''
    for line in text.strip().split('\n'):
      indented_text += ' '*indentation + line + '\n'

    return indented_text

  def _VerifyOrDie(self, envelope):
    if not self.auto_verify:
      return

    last_verified = self._last_verified.get(envelope, 0)
    if time.time() - last_verified > self.reverify_period:
      return

    if not self.VerifyEnvelope(envelope):
      raise exceptions.EnvelopeProtocolError('Envelope does not verify: ',
                                             envelope)

class Envelope(object):
  """Represents a Magic Envelope."""

  def __init__(self,
               data,
               data_type,
               sig,
               keyhash='',
               encoding='base64url',
               alg='RSA-SHA256'):
    """PRIVATE Constructor. Use factory methods from MagicEnvelopeProtocol.

    Args:
      data: The payload data as an encoded string.
      data_type: The MIME type of the payload (when decoded).
      encoding: The encoding to use ("base64url")
      alg: The algorithm used ("RSA-SHA256")
      sig: The signature string

    Raises:
      EnvelopeFormatError: If the envelope is missing data or not supported
          (envelopes that don't verify are accepted at this stage).
    """
    self.data = utils.Squeeze(data)
    self.data_type = utils.Squeeze(data_type)
    self.sig = utils.Squeeze(sig)
    self.keyhash = utils.Squeeze(keyhash)
    self.encoding = utils.Squeeze(encoding)
    self.alg = utils.Squeeze(alg)

    # Sanity checks:
    if not data_type:
      raise EnvelopeFormatError('Missing data_type: ', self)
    if alg != 'RSA-SHA256':
      raise EnvelopeFormatError('Unknown alg %s; must be RSA-SHA256' %
                                self._alg, self)
    if encoding != 'base64url':
      raise EnvelopeFormatError('Unknown encoding %s; must be base64url' %
                                self._encoding, self)

  def __str__(self):
    return str(vars(self))

  def __eq__(self, other):
    return (self.data == other.data and
            self.data_type == other.data_type and
            self.sig == other.sig and
            self.keyhash == other.keyhash and
            self.encoding == other.encoding and
            self.alg == other.alg)
