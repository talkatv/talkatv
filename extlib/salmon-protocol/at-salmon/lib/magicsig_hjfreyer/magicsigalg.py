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

"""Implementation of Magic Signatures low level operations.

See Magic Signatures RFC for specification.  This implements
the cryptographic layer of the spec, essentially signing and
verifying byte buffers using a public key algorithm.
"""

__author__ = 'jpanzer@google.com (John Panzer)'


import base64
import re

# PyCrypto: Note that this is not available in the
# downloadable GAE SDK, must be installed separately.
# See http://code.google.com/p/googleappengine/issues/detail?id=2493
# for why this is most easily installed under the
# project's path rather than somewhere more sane.
import Crypto.PublicKey
import Crypto.PublicKey.RSA
from Crypto.Util import number

import exceptions
import hashlib

# Note that PyCrypto is a very low level library and its documentation
# leaves something to be desired.  As a cheat sheet, for the RSA
# algorithm, here's a decoding of terminology:
#     n - modulus (public)
#     e - public exponent
#     d - private exponent
#     (n, e) - public key
#     (n, d) - private key
#     (p, q) - the (private) primes from which the keypair is derived.

# Thus a public key is a tuple (n,e) and a public/private key pair
# is a tuple (n,e,d).  Often the exponent is 65537 so for convenience
# we default e=65537 in this code.


def GenSampleSignature(text):
  """Demo using a hard coded, test public/private keypair."""
  demo_keypair = ('RSA.mVgY8RN6URBTstndvmUUPb4UZTdwvwmddSKE5z_jvKUEK6yk1'
                  'u3rrC9yN8k6FilGj9K0eeUPe2hf4Pj-5CmHww=='
                  '.AQAB'
                  '.Lgy_yL3hsLBngkFdDw1Jy9TmSRMiH6yihYetQ8jy-jZXdsZXd8V5'
                  'ub3kuBHHk4M39i3TduIkcrjcsiWQb77D8Q==')

  signer = SignatureAlgRsaSha256(demo_keypair)
  return signer.Sign(text)


# Utilities
def _NumToB64(num):
  """Turns a bignum into a urlsafe base64 encoded string."""
  return base64.urlsafe_b64encode(number.long_to_bytes(num))


def _B64ToNum(b64):
  """Turns a urlsafe base64 encoded string into a bignum."""
  return number.bytes_to_long(base64.urlsafe_b64decode(b64))

# Patterns for parsing serialized keys
_WHITESPACE_RE = re.compile(r'\s+')
_KEY_RE = re.compile(
    r"""RSA\.
      (?P<mod>[^\.]+)
      \.
      (?P<exp>[^\.]+)
      (?:\.
        (?P<private_exp>[^\.]+)
      )?""",
    re.VERBOSE)


class DefaultAlgorithms(object):
  """Signs and verifies data."""

  def Sign(self, signing_key, bytes_to_sign, algorithm):
    """Signs given bytes with given algorithm.

    Args:
      signing_key: private key to sign with.
      bytes_to_sign: bytes to sign.
      algorithm: Signing algorithm to use.
    Returns:
      The signature produced by the algorithm.
    Raises:
      UnsupportedAlgorithmError: if algorithm != 'RSA-SHA256'
    """
    if algorithm != 'RSA-SHA256':
      raise exceptions.UnsupportedAlgorithmError(
          'Algorithm must be "RSA-SHA256", not ' + algorithm)

    return SignatureAlgRsaSha256(signing_key).Sign(bytes_to_sign)

  def Verify(self, public_key, signed_bytes, signature_b64, algorithm):
    """Determines the validity of a signature over a signed buffer of bytes.

    Args:
      public_key: string public key which supposedly signed the bytes.
      signed_bytes: string The buffer of bytes the signature_b64 covers.
      signature_b64: string The putative signature, base64-encoded, to check.
    Raises:
      UnsupportedAlgorithmError: if algorithm != 'RSA-SHA256'
    Returns:
      True if the request validated, False otherwise.
    """
    if algorithm != 'RSA-SHA256':
      raise exceptions.UnsupportedAlgorithmError(
          'Algorithm must be "RSA-SHA256", not ' + algorithm)

    return SignatureAlgRsaSha256(public_key).Verify(signed_bytes, signature_b64)


# Implementation of the Magic Envelope signature algorithm
class SignatureAlgRsaSha256(object):
  """Signature algorithm for RSA-SHA256 Magic Envelope."""

  def __init__(self, rsa_key):
    """Initializes algorithm with key information.

    Args:
      rsa_key: Key in either string form or a tuple in the
               format expected by Crypto.PublicKey.RSA.
    Raises:
      ValueError: The input format was incorrect.
    """
    if isinstance(rsa_key, tuple):
      self.keypair = Crypto.PublicKey.RSA.construct(rsa_key)
    else:
      self._InitFromString(rsa_key)

  def ToString(self, full_key_pair=True):
    """Serializes key to a safe string storage format.

    Args:
      full_key_pair: Whether to save the private key portion as well.
    Returns:
      The string representation of the key in the format:

        RSA.mod.exp[.optional_private_exp]

      Each component is a urlsafe-base64 encoded representation of
      the corresponding RSA key field.
    """
    mod = _NumToB64(self.keypair.n)
    exp = '.' + _NumToB64(self.keypair.e)
    private_exp = ''
    if full_key_pair and self.keypair.d:
      private_exp = '.' + _NumToB64(self.keypair.d)
    return 'RSA.' + mod + exp + private_exp

  def _InitFromString(self, text):
    """Parses key from a standard string storage format.

    Args:
      text: The key in text form.  See ToString for description
        of expected format.
    Raises:
      ValueError: The input format was incorrect.
    """
    # First, remove all whitespace:
    text = re.sub(_WHITESPACE_RE, '', text)

    # Parse out the period-separated components
    match = _KEY_RE.match(text)
    if not match:
      raise ValueError('Badly formatted key string: "%s"', text)

    private_exp = match.group('private_exp')
    if private_exp:
      private_exp = _B64ToNum(private_exp)
    else:
      private_exp = None
    self.keypair = Crypto.PublicKey.RSA.construct(
        (_B64ToNum(match.group('mod')),
         _B64ToNum(match.group('exp')),
         private_exp))

  def GetName(self):
    """Returns string identifier for algorithm used."""
    return 'RSA-SHA256'

  def _MakeEmsaMessageSha256(self, msg, modulus_size, logf=None):
    """Algorithm EMSA_PKCS1-v1_5 from PKCS 1 version 2.

    This is derived from keyczar code, and implements the
    additional ASN.1 compatible magic header bytes and
    padding needed to implement PKCS1-v1_5.

    Args:
      msg: The message to sign.
      modulus_size: The size of the key (in bits) used.
    Returns:
      The byte sequence of the message to be signed.
    """
    magic_sha256_header = [0x30, 0x31, 0x30, 0xd, 0x6, 0x9, 0x60, 0x86, 0x48,
                           0x1, 0x65, 0x3, 0x4, 0x2, 0x1, 0x5, 0x0, 0x4, 0x20]

    hash_of_msg = hashlib.sha256(msg).digest() #???

    self._Log(logf, 'sha256 digest of msg %s: [%s]' % (msg, hash_of_msg.encode('hex')))

    encoded = ''.join([chr(c) for c in magic_sha256_header]) + hash_of_msg

    msg_size_bits = modulus_size + 8-(modulus_size % 8)  # Round up to next byte

    pad_string = chr(0xFF) * (msg_size_bits / 8 - len(encoded) - 3)
    return chr(0) + chr(1) + pad_string + chr(0) + encoded

  def _Log(self, logf, s):
    """Append message to log if log exists."""
    if logf:
      logf(s + '\n')

  def Sign(self, bytes_to_sign, logf=None):
    """Signs the bytes using PKCS-v1_5.

    Args:
      bytes_to_sign: The bytes to be signed.
    Returns:
      The signature in base64url encoded format.
    """
    # Implements PKCS1-v1_5 w/SHA256 over the bytes, and returns
    # the result as a base64url encoded bignum.

    self._Log(logf, 'bytes_to_sign = [%s]' % bytes_to_sign.encode('hex'))

    self._Log(logf, 'keypair size : %s' % self.keypair.size())

    # Generate the PKCS1-v1_5 compatible message, which includes
    # magic ASN.1 bytes and padding:
    emsa_msg = self._MakeEmsaMessageSha256(bytes_to_sign, self.keypair.size(), logf)
    # TODO(jpanzer): Check whether we need to use max keysize above
    # or just keypair.size

    self._Log(logf, 'emsa_msg = [%s]' % emsa_msg.encode('hex'))

    # Compute the signature:
    signature_long = self.keypair.sign(emsa_msg, None)[0]

    # Encode the signature as armored text:
    signature_bytes = number.long_to_bytes(signature_long)

    self._Log(logf, 'signature_bytes = [%s]' % signature_bytes.encode('hex'))

    return base64.urlsafe_b64encode(signature_bytes).encode('utf-8')

  def Verify(self, signed_bytes, signature_b64):
    """Determines the validity of a signature over a signed buffer of bytes.

    Args:
      signed_bytes: string The buffer of bytes the signature_b64 covers.
      signature_b64: string The putative signature, base64-encoded, to check.
    Returns:
      True if the request validated, False otherwise.
    """
    # Generate the PKCS1-v1_5 compatible message, which includes
    # magic ASN.1 bytes and padding:
    emsa_msg = self._MakeEmsaMessageSha256(signed_bytes,
                                           self.keypair.size())

    # Get putative signature:
    putative_signature = base64.urlsafe_b64decode(signature_b64.encode('utf-8'))
    putative_signature = number.bytes_to_long(putative_signature)

    # Verify signature given public key:
    return self.keypair.verify(emsa_msg, (putative_signature,))
