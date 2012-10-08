# talkatv - Commenting backend for static pages
# Copyright (C) 2012  talkatv contributors, see AUTHORS
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask import request

from magicsig import Envelope
from lxml import etree
from xml.etree import ElementTree
from StringIO import StringIO

from talkatv import app
from talkatv.tools.cors import jsonify, allow_all_origins


@app.route('/salmon/replies', methods=['POST'])
def salmon_all():
    '''
    Salmon endpoint. See http://www.salmon-protocol.org/
    '''
    # Parse the salmon slap
    envelope = Envelope(
            document=request.data,
            mime_type=request.headers['content-type'])

    # Get the xml.etree.ElementTree for the published entry
    slap_xml = envelope.GetParsedData()
    slap_xml = etree.parse(
            StringIO(ElementTree.tostring(slap_xml.getroot())))

    root_em = slap_xml.getroot()

    ATOM_NS = '{http://www.w3.org/2005/Atom}'

    comment = {
            'author_name': root_em.find(ATOM_NS + 'author').find(
                ATOM_NS + 'name').text,
            'author_uri': root_em.find(ATOM_NS + 'author').find(
                ATOM_NS + 'uri').text,
            'id': root_em.find(ATOM_NS + 'id').text,
            'content': root_em.find(ATOM_NS + 'content').text,
            'title': root_em.find(ATOM_NS + 'title').text,
            'updated': root_em.find(ATOM_NS + 'updated').text}

    return jsonify(_allow_origin_cb=allow_all_origins, **comment)
