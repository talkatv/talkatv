#!/usr/bin/python2.5
#
# Tests the XFN parser.
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

import unittest
import xfn

class ParserTest(unittest.TestCase):

  def testParseEmptyString(self):
    parser = xfn.Parser()
    try:
      parser.parse('')
      self.fail('ParseError expected.')
    except xfn.ParseError:
      pass  # expected

  def testParse(self):
    parser = xfn.Parser()
    xfn_pb = parser.parse(
        '''<!DOCTYPE html>
           <html>
            <head>
             <title>Sample page</title>
            </head>
            <body>
             <h1>Sample page</h1>
             <p>This is a <a href="demo.html">simple</a> sample.</p>
             <!-- this is a comment -->
             <a href="http://example.com/1">1</a>
             <a href="http://example.com/2" rel="meat">2</a>
             <a href="http://example.com/3" rel="me">3</a>
             <a href="http://example.com/4" rel="notme me">4</a>
             <link href="http://example.com/5"/>
             <link href="http://example.com/6" rel="meat"/>
             <link href="http://example.com/7" type="text/html" rel="me"/>
             <link href="http://example.com/8" type="text/xhtml" rel="me notme" 
                   title="8"/>
            </body>
           </html>''')
    self.assertEquals(4, len(xfn_pb.links))

def suite():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(ParserTest))
  return suite

if __name__ == '__main__':
  unittest.main()
